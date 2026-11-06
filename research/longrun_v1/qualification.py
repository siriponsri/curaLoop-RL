"""Released R1 bounded intake. Values stay private; no model, threshold or pilot."""

import hashlib
import importlib.util
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

from research.qualification_v1.contracts import (QualificationError, strict_json, normalize_observations,
                                                public_aggregate, replicate_state, exact_sid_filter)


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())


def normalize(raw, request):
    original_sha256 = hashlib.sha256(raw).hexdigest()
    obj = strict_json(raw, byte_limit=1048576)
    if set(obj) == {'PC_AssaySubmit'}:
        submit = obj['PC_AssaySubmit']
        if type(submit) is not dict or set(submit) != {'assay', 'data'}:
            raise QualificationError('Unexpected native submit fields')
        raw = json.dumps({'PC_AssayContainer': [submit]}, allow_nan=False).encode()
        rows = submit['data']
    else:
        rows = obj['PC_AssayContainer'][0]['data']
    # Complete identity and duplicate pass before value normalization.
    identifiers = []
    for row in rows:
        if type(row) is not dict or type(row.get('sid')) is not int or str(row['sid']) not in request['sids']:
            raise QualificationError('Unexpected identifier; readouts not interpreted')
        identifiers.append(row['sid'])
    if len(identifiers) != len(set(identifiers)):
        raise QualificationError('Duplicate source SID representation; qualification stopped')
    observation = normalize_observations(raw, request['aid'], set(request['sids']), request['bindings'],
             role='DEVELOPMENT_EXPOSED', expected_version=request['version'], expected_revision=request['revision'])
    observation['adapter_wrapped_sha256'] = observation['source_sha256']
    observation['source_sha256'] = original_sha256
    return observation


def exact_sids(observation):
    groups = defaultdict(list)
    for row in observation['records']:
        groups[row['sid']].append(row)
    return {sid for sid, records in groups.items() if replicate_state(records) == 'CONSISTENT_OBSERVATION'
            and all(cell['state'] == 'EXACT_NUMERIC' for row in records for cell in row['readouts'].values())}


def ambiguous(observation):
    return any(row.get('comment_state') in ('VALUE', 'NULL')
               or any(c['state'] in ('QUALIFIER_REVIEW', 'QUALITATIVE_OR_UNRESOLVED_TEXT')
                      for c in row['readouts'].values()) for row in observation['records'])


def fixtures(root, output):
    from .fixtures import rejected
    b = dict(tid=1, name='Synthetic', type=1, unit_present=True, unit=15, sunit_present=False, sunit=None)
    r = dict(aid='1', version=1, revision=1, sids=['10'], bindings=[b])
    native = {'PC_AssaySubmit': {'assay': {'descr': {'aid': {'id': 1, 'version': 1}, 'revision': 1,
               'results': [dict(tid=1, name='Synthetic', type=1, unit=15)]}},
               'data': [{'sid': 10, 'outcome': 2, 'data': [{'tid': 1, 'value': {'fval': 0}}]}]}}
    raw = json.dumps(native).encode()
    observation = normalize(raw, r)
    assert exact_sids(observation) == {'10'}
    wrapped = json.dumps({'PC_AssayContainer': [native['PC_AssaySubmit']]}).encode()
    assert exact_sids(normalize(wrapped, r)) == {'10'}
    changed = json.loads(raw); changed['PC_AssaySubmit']['assay']['descr']['results'][0]['unit'] = 5
    rejected(lambda: normalize(json.dumps(changed).encode(), r))
    concentration_request = dict(r, bindings=[dict(b, unit=5)])
    assert exact_sids(normalize(json.dumps(changed).encode(), concentration_request)) == set()
    changed = json.loads(raw); changed['PC_AssaySubmit']['data'] *= 2
    rejected(lambda: normalize(json.dumps(changed).encode(), r))
    cases = ['Q01']
    changed = json.loads(raw); changed['PC_AssaySubmit']['data'].append(dict(sid=99, data='POISON'))
    rejected(lambda: normalize(json.dumps(changed).encode(), r))
    cases.append('Q02')
    changed = json.loads(raw); changed['PC_AssaySubmit']['data'][0]['data'] = []
    assert exact_sids(normalize(json.dumps(changed).encode(), r)) == set()
    changed = json.loads(raw); changed['PC_AssaySubmit']['data'][0]['data'][0]['value']['fval'] = None
    assert exact_sids(normalize(json.dumps(changed).encode(), r)) == set()
    from research.qualification_v1.contracts import value_state
    assert value_state('<1')['state'] == 'CENSORED'
    assert value_state('1.0')['state'] == 'QUALITATIVE_OR_UNRESOLVED_TEXT'
    cases.append('Q03')
    allocation = json.loads((root / 'inputs/r1-allocation.json').read_text())
    assert allocation['historical_pug_calls'] == 24 and allocation['new_reserved_calls'] == 20
    assert allocation['historical_decoded_bytes'] + allocation['new_reserved_decoded_bytes'] <= 268435456
    assert allocation['old_stop_preserved'] is True and allocation['new_phase_maximum_attempts_per_specification'] == 1
    # Exercise the actual transport stop with a synthetic denied provider.
    from research.qualification_v1.transport import BoundedTransport, SafeSession
    import requests as requests_package
    calls = []
    class Denied:
        status_code = 403
        headers = {'content-type': 'application/json'}
        def raise_for_status(self): raise requests_package.HTTPError('PRIVATE_SYNTHETIC_403')
        def close(self): pass
    class FakeSession:
        def __init__(self): self.headers = {}; self.trust_env = False
        def request(self, *args, **kwargs): calls.append(1); return Denied()
        def close(self): pass
    envelope = BoundedTransport('https://pubchem.ncbi.nlm.nih.gov/rest/pug',
                   [{'path': 'synthetic', 'params': {}}], 1, 100, 100, interval=0, session_factory=FakeSession)
    boundary = SafeSession(envelope)
    try: boundary.request('GET', envelope.base_url + '/synthetic', params={}, timeout=1)
    except requests_package.HTTPError: pass
    else: raise AssertionError('Synthetic denied response admitted')
    rejected(lambda: boundary.request('GET', envelope.base_url + '/synthetic', params={}, timeout=1))
    assert len(calls) == 1
    from .coordinator_v2 import Coordinator
    cfg = json.loads((root / 'research/configs/lrbc_execution_v1.json').read_text())
    authority = Coordinator.initialize(output / 'r1-authority-fixture.sqlite', cfg, {'local': [0], 'dr-train': [1, 2, 3, 4]})
    release = authority.release_r1('a' * 64, 'b' * 64)
    rejected(lambda: authority.release_r1('a' * 64, 'b' * 64))
    permit = authority.reserve('synthetic-r1', 'R1', 'dr-train', 'c' * 64, 64 * 1024**3)
    assert permit['deadline_utc'] == release['deadline_utc']
    rejected(lambda: authority.reserve('expired-r1', 'R1', 'dr-train', 'c' * 64, 64 * 1024**3,
                                        now=release['deadline_utc']))
    cases.append('Q04')
    requests = json.loads((root / 'inputs/r1-requests.json').read_text())
    assert len(requests['canary']) == len(requests['full']) == 10
    assert sum(len(r['sids']) for r in requests['full']) == 1178
    for small, full in zip(requests['canary'], requests['full']):
        assert small['sids'] == full['sids'][:16]
        assert all(small[k] == full[k] for k in ('aid', 'bindings', 'version', 'revision', 'script', 'stage'))
        assert small['specification']['params'] == exact_sid_filter(small['sids'], full['sids'], 16)
    cases.append('Q05')
    sentinel = 'PRIVATE_R1_RESPONSE_ERROR_SENTINEL'
    from .worker import public_failure
    assert sentinel not in json.dumps(public_failure(ValueError(sentinel)))
    cases.append('Q06')
    frozen = json.loads((root / 'research/configs/lrbc_r1_cases_v1.json').read_text())
    assert cases == [c['id'] for c in frozen['cases']]
    return {'status': 'PASS', 'cases': cases, 'case_count': len(cases), 'source_requests': 0,
            'numeric_string_coercion': 'NOT_ADDED', 'scientific_eligibility': 'NOT_ESTABLISHED'}


def execute(root, output, mode):
    from research.qualification_v1.transport import BoundedTransport
    allocation = json.loads((root / 'inputs/r1-allocation.json').read_text())
    plan = json.loads((root / 'inputs/r1-requests.json').read_text())
    requests = plan[mode]
    if mode == 'full':
        canary = json.loads((root / 'inputs/r1-canary-result.json').read_text())
        if canary['status'] != 'PASS_SOURCE_CANARY_ONLY' or canary['request_plan_sha256'] != hashlib.sha256((root / 'inputs/r1-requests.json').read_bytes()).hexdigest():
            raise QualificationError('Full phase requires the unchanged complete source canary')
    skill = root / 'inputs/pubchem_rest_request.py'
    if hashlib.sha256(skill.read_bytes()).hexdigest() != '78ddae6460e3dd701cda67df4454532899d20851f8212a74ec8d5b6e2988b690':
        raise QualificationError('Pinned skill client differs')
    spec = importlib.util.spec_from_file_location('lrbc_pubchem_skill', skill)
    client = importlib.util.module_from_spec(spec); spec.loader.exec_module(client)
    guard = BoundedTransport('https://pubchem.ncbi.nlm.nih.gov/rest/pug', [r['specification'] for r in requests],
                             len(requests), 1048576 - 65536, len(requests) * (1048576 - 65536), interval=1.1)
    client = guard.bind(client)
    ledger = {'allocation_sha256': hashlib.sha256((root / 'inputs/r1-allocation.json').read_bytes()).hexdigest(),
              'mode': mode, 'requests': [], 'stopped': False}
    ledger_path = output / 'network-ledger-private.json'
    def save():
        temp = ledger_path.with_suffix('.tmp')
        with temp.open('w', encoding='utf-8', newline='\n') as handle:
            json.dump(ledger, handle, indent=2, allow_nan=False); handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, ledger_path)
    private, reports = [], []
    stop = None
    # Exposure manifest exists before dispatch, including any eventual failed rows.
    write(output / 'exposure-private.json', {'role': 'DEVELOPMENT_EXPOSED', 'requests': requests,
                                            'final_outcomes_authorized': False, 'future_untouched_evaluation': False})
    for i, request in enumerate(requests):
        entry = {'index': i, 'aid': request['aid'], 'state': 'RESERVED', 'charged_decoded_bytes': 1048576}
        ledger['requests'].append(entry); save()
        path = output / ('response-' + str(i).zfill(2) + '.json')
        payload = {'base_url': 'https://pubchem.ncbi.nlm.nih.gov/rest/pug', **request['specification'],
                   'method': 'GET', 'response_format': 'text', 'save_raw': True,
                   'raw_output_path': str(path), 'timeout_sec': 30, 'max_items': 1}
        try:
            reason = 'SOURCE_REQUEST_OR_TRANSPORT'
            result = client.execute(payload)
            if not result.get('ok'):
                raise QualificationError('Source denial or transport failure; no retry')
            raw = path.read_bytes()
            trace = guard.attempts[-1]
            assert len(raw) == trace['decoded_bytes_observed']
            assert hashlib.sha256(raw).hexdigest() == trace['decoded_sha256']
            entry.update(state='FETCHED', bytes_observed=len(raw), response_sha256=hashlib.sha256(raw).hexdigest())
            write(output / ('receipt-' + str(i).zfill(2) + '-private.json'), {'request': payload, 'transport': trace})
            reason = 'SOURCE_IDENTITY_OR_SCHEMA'
            observation = normalize(raw, request)
            private.append(observation)
            summary = public_aggregate(observation, request['sids'])
            summary.update(script=request['script'], stage=request['stage'], exact_complete_sids=len(exact_sids(observation)))
            reports.append(summary)
            if ambiguous(observation):
                reason = 'AMBIGUOUS_QUALIFIER'
                raise QualificationError('Ambiguous qualifier; intake stopped')
            if mode == 'canary' and set(observation['returned_sids']) != set(request['sids']):
                reason = 'INCOMPLETE_CANARY_SID_COVERAGE'
                raise QualificationError('Incomplete source canary SID coverage; intake stopped')
            entry['state'] = 'VALIDATED'; save()
        except Exception as error:
            entry.update(state='FAILED', error_type=type(error).__name__)
            ledger['stopped'] = True; save()
            (output / 'error-private.txt').write_text(__import__('traceback').format_exc(), encoding='utf-8')
            stop = {'request_index': i, 'aid': request['aid'], 'error_type': type(error).__name__,
                    'reason': reason, 'http_status': guard.attempts[-1].get('http_status') if guard.attempts else None}
            break
    write(output / 'observations-private.json', private)
    paired = []
    if mode == 'full' and stop is None:
        for i in range(0, len(private), 2):
            shared = exact_sids(private[i]) & exact_sids(private[i + 1])
            paired.append({'script': requests[i]['script'], 'cleared_sids': len(requests[i]['sids']),
                           'primary_exact_complete': len(exact_sids(private[i])),
                           'confirmation_exact_complete': len(exact_sids(private[i + 1])),
                           'paired_exact_complete': len(shared)})
    return {'status': 'NO_GO_R1_INTAKE_STOP' if stop else 'PASS_SOURCE_CANARY_ONLY' if mode == 'canary' else 'PASS_FIXED_POPULATION_QUALIFICATION_ONLY',
            'mode': mode, 'source_attempts': len(ledger['requests']), 'stop': stop, 'assays': reports, 'paired': paired,
            'decoded_bytes_observed': guard.total_bytes, 'reserved_calls_retained': 20,
            'request_plan_sha256': hashlib.sha256((root / 'inputs/r1-requests.json').read_bytes()).hexdigest(),
            'role': 'DEVELOPMENT_EXPOSED', 'independent_components': 1, 'pilot_released': False,
            'scientific_eligibility': 'NOT_ESTABLISHED_BY_SOURCE_CANARY', 'historical_rows_equivalent': 'NOT_CERTIFIED',
            'old_stop_preserved': True, 'raw_values_or_identifiers_included': False}
