"""Offline-only native ASN.1 submit envelope adapter; stopped service stays stopped."""

import hashlib
import json

from .audit import write_new
from .contracts import QualificationError, strict_json, normalize_observations, exact_sid_filter
from .network import read, Client
from .observations_v1 import aggregate, ambiguous_qualifier, complete_canary


def normalize_submit(raw, request):
    obj = strict_json(raw, byte_limit=16 * 1024**2)
    if type(obj) is not dict or set(obj) != {'PC_AssaySubmit'}:
        raise QualificationError('Expected exact native submit envelope')
    submit = obj['PC_AssaySubmit']
    if type(submit) is not dict or set(submit) != {'assay', 'data'}:
        raise QualificationError('Unexpected native submit fields or suppression semantics')
    # PC-AssayContainer is SEQUENCE OF PC-AssaySubmit in the pinned schema.
    wrapped = json.dumps({'PC_AssayContainer': [submit]}, allow_nan=False).encode()
    observation = normalize_observations(wrapped, request['aid'], set(request['sids']), request['bindings'],
                  role='DEVELOPMENT_EXPOSED', expected_version=request['version'], expected_revision=request['revision'])
    observation['adapter_wrapped_sha256'] = observation['source_sha256']
    observation['source_sha256'] = hashlib.sha256(raw).hexdigest()
    observation['source_envelope'] = 'PC_AssaySubmit'
    observation['adapter_semantics'] = 'STRUCTURAL_WRAPPING_ONLY_NO_VALUE_OR_ROLE_TRANSFORM'
    return observation


def run_checks(root, output, config):
    from .reconciliation_checks_v1 import rejected
    fixture = output / 'native-submit-fixtures'
    fixture.mkdir()
    write_new(fixture / 'definitions.json', config)
    binding = {'name': 'Synthetic', 'tid': 1, 'type': 1, 'unit_present': True, 'unit': 5,
               'sunit_present': False, 'sunit': None}
    request = {'aid': '1', 'sids': ['10'], 'bindings': [binding], 'version': 1, 'revision': 1}
    submit = {'PC_AssaySubmit': {'assay': {'descr': {'aid': {'id': 1, 'version': 1}, 'revision': 1,
                'results': [{'tid': 1, 'name': 'Synthetic', 'type': 1, 'unit': 5}]}},
              'data': [{'sid': 10, 'outcome': 2, 'data': [{'tid': 1, 'value': {'fval': 1.5}}]}]}}
    raw = json.dumps(submit).encode()
    normalized = normalize_submit(raw, request)
    assert normalized['records'][0]['readouts']['1']['value'] == 1.5
    assert normalized['source_sha256'] == hashlib.sha256(raw).hexdigest()
    write_new(fixture / 'submit.json', submit)
    write_new(fixture / 'request.json', request)
    invalid = json.loads(raw)
    invalid['PC_AssaySubmit']['revoke'] = []
    rejected(lambda: normalize_submit(json.dumps(invalid).encode(), request))
    invalid = json.loads(raw)
    invalid['PC_AssaySubmit']['data'][0] = {'sid': 20, 'data': 'POISON_VALUE_NOT_TO_BE_INTERPRETED'}
    try:
        normalize_submit(json.dumps(invalid).encode(), request)
    except QualificationError as error:
        assert str(error) == 'Unexpected or protected row identifier; values not interpreted'
    else:
        raise AssertionError('Unexpected SID accepted')
    write_new(fixture / 'unexpected-sid.json', invalid)
    # This must reject before construction/dispatch; it is not a retry.
    before = (root / 'network-ledger.json').read_bytes()
    rejected(lambda: Client(root, output, 'pubchem', []))
    assert (root / 'network-ledger.json').read_bytes() == before
    ids = ['S01', 'S02', 'S03']
    assert ids == [c['id'] for c in config['cases']]
    write_new(output / 'submit-checks.json', {'status': 'PASS_THREE_OFFLINE_SUBMIT_CHECKS', 'actual_case_ids': ids,
              'actual_external_requests': 0, 'fixtures_preserved_under_task': True})


def execute(root, output):
    config = read(root / 'research/configs/goal4r2a3_offline_submit_v1.json')
    before = (root / 'network-ledger.json').read_bytes()
    if 'pubchem' not in json.loads(before)['stopped_services']:
        raise QualificationError('Original stopped-service latch required')
    schema = root / 'private-inputs/source-evidence/pcassay2.asn'
    if hashlib.sha256(schema.read_bytes()).hexdigest() != config['ncbi_schema_sha256']:
        raise QualificationError('Pinned native submit schema differs')
    run_checks(root, output, config)
    source = root / 'runs/observation-canary-v1'
    if set(config['original_source_files']) != {'observation-000.txt', 'observation-000-receipt.json', 'phase-request-manifest-private.json', 'results.json'}:
        raise QualificationError('Complete original offline source pin roster required')
    for name, pin in config['original_source_files'].items():
        if name not in {'observation-000.txt', 'observation-000-receipt.json', 'phase-request-manifest-private.json', 'results.json'}:
            raise QualificationError('Unapproved original source path')
        original_path = source / name
        if (original_path.stat().st_size != pin['bytes']
                or hashlib.sha256(original_path.read_bytes()).hexdigest() != pin['sha256']):
            raise QualificationError('Pinned original source bytes differ')
    manifest_path = source / 'qualification-manifest-private.json'
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != config['pre_canary_manifest_sha256']:
        raise QualificationError('Original pre-canary population manifest differs')
    original_result = read(source / 'results.json')
    if (original_result['status'] != config['original_canary_status']
            or original_result['qualification_manifest_sha256'] != config['pre_canary_manifest_sha256']):
        raise QualificationError('Original canary failure verdict or manifest binding differs')
    phase = read(source / 'phase-request-manifest-private.json')
    if phase['qualification_manifest_sha256'] != config['pre_canary_manifest_sha256']:
        raise QualificationError('Canary phase binding differs')
    request = phase['requests'][0]
    original_plan = read(manifest_path)
    original_config = root / 'research/configs/goal4r2a3_observation_v1.json'
    if (hashlib.sha256(original_config.read_bytes()).hexdigest() != original_plan['observation_config_sha256']
            or phase['config_sha256'] != original_plan['observation_config_sha256']):
        raise QualificationError('Original observation configuration differs')
    fixed = [r for r in original_plan['requests'] if r['aid'] == request['aid']]
    if (len(fixed) != 1 or request['sids'] != fixed[0]['sids'][:16]
            or any(request[k] != fixed[0][k] for k in ('aid', 'bindings', 'version', 'revision', 'script', 'stage'))):
        raise QualificationError('Original canary filter or endpoint differs')
    exact = {'path': 'assay/aid/' + request['aid'] + '/JSON',
             'params': exact_sid_filter(request['sids'], fixed[0]['sids'], 16)}
    if request['specification'] != exact:
        raise QualificationError('Original canary request specification differs from exact derived filter')
    receipt = read(source / 'observation-000-receipt.json')
    raw = (source / 'observation-000.txt').read_bytes()
    if (receipt['response_sha256'] != hashlib.sha256(raw).hexdigest()
            or receipt['response_bytes'] != len(raw) or receipt['transport']['http_status'] != 200
            or receipt['request']['method'] != 'GET' or receipt['request']['base_url'] != 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
            or receipt['request']['path'] != request['specification']['path']
            or receipt['request']['params'] != request['specification']['params']):
        raise QualificationError('Original filtered response receipt differs')
    try:
        observation = normalize_submit(raw, request)
    except QualificationError:
        write_new(output / 'results.json', {'status': 'NO_GO_OFFLINE_NATIVE_SUBMIT_VALIDATION',
                  'additional_network_requests': 0, 'scientific_campaigns': 0, 'activity_values_interpreted_by_agent': False})
        raise
    report = aggregate(observation, request['sids'])
    write_new(output / 'observations-private.json', observation)
    write_new(output / 'observation-aggregate.json', report)
    assert (root / 'network-ledger.json').read_bytes() == before
    result = {'status': 'PASS_OFFLINE_NATIVE_SUBMIT_NORMALIZATION_ONLY', 'validated_assays': 1,
              'requested_sids': len(request['sids']), 'returned_sids': len(observation['returned_sids']),
              'complete_original_request_coverage': complete_canary(observation, request['sids']),
              'unresolved_qualifier': ambiguous_qualifier(observation), 'additional_network_requests': 0,
              'network_ledger_unchanged_sha256': hashlib.sha256(before).hexdigest(),
              'paired_stage_qualification': 'NOT_RUN', 'scientific_eligibility': 'NOT_ESTABLISHED',
              'original_canary_verdict_preserved': 'NO_GO_FILTERED_OBSERVATION_ACCESS_IDENTITY_OR_SCHEMA',
              'role': 'DEVELOPMENT_EXPOSED', 'scientific_campaigns': 0, 'historical_rows_equivalent': 'NOT_CERTIFIED'}
    write_new(output / 'results.json', result)
    return result
