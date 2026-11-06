"""Filtered development observation canary and fixed-population qualification."""

import hashlib
import json
from collections import Counter, defaultdict

from .audit import write_new
from .contracts import (QualificationError, exact_sid_filter, normalize_observations,
                        public_aggregate, replicate_state, coverage)
from .network import Client, read


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_plan(release, config):
    rows = []
    if not 0 < len(release['pairs']) <= config['maximum_pairs']:
        raise QualificationError('Fixed pair roster required')
    seen = set()
    for pair in release['pairs']:
        allowed = pair['cleared_sids']
        if not allowed:
            continue
        # The private release hash binds source metadata and completed structure decisions.
        exact_sid_filter(allowed, pair['sampled_sids'], config['maximum_sids_per_pair'])
        for sid in allowed:
            cids = release['sid_cids'].get(sid, [])
            if len(cids) != 1 or release['cid_properties'].get(cids[0], {}).get('verdict') != 'CLEARED_EXACT_CANONICAL_CONTROL':
                raise QualificationError('Uncleared structure in observation release')
        for stage in ('primary', 'confirmation'):
            aid = pair[stage + '_aid']
            if aid in seen:
                raise QualificationError('Duplicate AID would require separately reviewed endpoint consolidation')
            seen.add(aid)
            bindings = pair['metadata_binding'][stage + '_bindings']
            if not bindings or pair['metadata_binding']['metadata_admitted'] is not True:
                raise QualificationError('Admitted endpoint bindings required')
            version = config['source_versions'][aid]
            rows.append({'script': pair['script'], 'stage': stage, 'aid': aid, 'sids': allowed,
                         'bindings': bindings, 'version': version['version'], 'revision': version['revision'],
                         'specification': {'path': 'assay/aid/' + aid + '/JSON',
                                           'params': exact_sid_filter(allowed, allowed)}})
    return {'role': 'DEVELOPMENT_EXPOSED', 'requests': rows,
            'identifier_release_sha256': config['identifier_release_sha256'],
            'scientific_campaigns': 0, 'historical_rows_equivalent': 'NOT_CERTIFIED'}


def complete_canary(observation, sids):
    return set(observation['returned_sids']) == set(sids)


def admit_fixed_plan(expected, persisted, report, manifest_sha256):
    if (report['status'] != 'PASS_FILTERED_OBSERVATION_CANARY'
            or manifest_sha256 != report['qualification_manifest_sha256'] or persisted != expected):
        raise QualificationError('Unchanged pre-canary population and passed canary required')


def ambiguous_qualifier(observation):
    return any(row.get('comment_state') in ('VALUE', 'NULL')
               or any(cell['state'] in ('QUALIFIER_REVIEW', 'QUALITATIVE_OR_UNRESOLVED_TEXT')
                      for cell in row['readouts'].values()) for row in observation['records'])


def aggregate(observation, sids):
    report = public_aggregate(observation, sids)
    by_sid = defaultdict(list)
    for row in observation['records']:
        by_sid[row['sid']].append(row)
    states = Counter(replicate_state(by_sid[sid]) for sid in sids)
    exact = [sid for sid, rows in by_sid.items() if replicate_state(rows) == 'CONSISTENT_OBSERVATION'
             and all(c['state'] == 'EXACT_NUMERIC' for row in rows for c in row['readouts'].values())]
    report['replicate_state_counts'] = dict(states)
    report['exact_numeric_coverage'] = coverage(sids, observation['returned_sids'], exact)
    report['source_outcomes_are_not_numeric_potencies'] = True
    report['replicate_conflict_interpretation'] = 'CONSERVATIVE_SOURCE_REPRESENTATION_CONFLICT_NOT_PROOF_OF_ACTIVITY_DIFFERENCE'
    return report


def run_checks(root, output, config):
    from .reconciliation_checks_v1 import rejected
    fixture = output / 'observation-fixtures'
    fixture.mkdir()
    write_new(fixture / 'definitions.json', config)
    binding = {'name': 'Synthetic', 'tid': 1, 'type': 1, 'unit_present': True, 'unit': 5,
               'sunit_present': False, 'sunit': None}
    pair = {'script': 'synthetic', 'primary_aid': '1', 'confirmation_aid': '2', 'sampled_sids': ['10', '20'],
            'cleared_sids': ['10'], 'metadata_binding': {'metadata_admitted': True,
                'primary_bindings': [binding], 'confirmation_bindings': [binding]}}
    release = {'pairs': [pair], 'sid_cids': {'10': ['100']},
               'cid_properties': {'100': {'verdict': 'CLEARED_EXACT_CANONICAL_CONTROL'}}}
    synthetic = dict(config, source_versions={'1': {'version': 1, 'revision': 1}, '2': {'version': 1, 'revision': 1}})
    plan = make_plan(release, synthetic)
    assert all(r['specification']['params'] == {'sid': '10'} for r in plan['requests'])
    protected = json.loads(json.dumps(release))
    protected['cid_properties']['100']['verdict'] = 'PROTECTED_EXACT_CANONICAL'
    rejected(lambda: make_plan(protected, synthetic))
    write_new(fixture / 'release.json', release)
    frozen = fixture / 'fixed-plan.json'
    write_new(frozen, plan)
    before = digest(frozen)
    try:
        write_new(frozen, {'replacement': True})
    except FileExistsError:
        pass
    else:
        raise AssertionError('Frozen qualification manifest overwritten')
    assert digest(frozen) == before
    admitted = {'status': 'PASS_FILTERED_OBSERVATION_CANARY', 'qualification_manifest_sha256': before}
    admit_fixed_plan(plan, read(frozen), admitted, before)
    changed = json.loads(json.dumps(plan))
    changed['requests'][0]['sids'] = ['20']
    rejected(lambda: admit_fixed_plan(changed, read(frozen), admitted, before))
    changed = json.loads(json.dumps(plan))
    changed['observation_config_sha256'] = 'changed'
    rejected(lambda: admit_fixed_plan(changed, read(frozen), admitted, before))
    rejected(lambda: admit_fixed_plan(plan, read(frozen), dict(admitted, status='NO_GO_CANARY_INCOMPLETE_COVERAGE'), before))
    assert complete_canary({'returned_sids': ['10']}, ['10'])
    assert not complete_canary({'returned_sids': []}, ['10'])
    observation = {'aid': '1', 'role': 'DEVELOPMENT_EXPOSED', 'source_sha256': 'synthetic',
                   'returned_sids': ['10'], 'records': [
                       {'sid': '10', 'source_outcome': 1, 'readouts': {'1': {'state': 'EXACT_NUMERIC', 'value': 1}}},
                       {'sid': '10', 'source_outcome': 2, 'readouts': {'1': {'state': 'MISSING_TID'}}}]}
    result = aggregate(observation, ['10', '20'])
    assert result['replicate_state_counts'] == {'CONFLICTING_REPLICATES': 1, 'NO_RETURNED_OBSERVATION_NOT_PROOF_UNTESTED': 1}
    assert result['exact_numeric_coverage']['eligible'] == 0
    assert not ambiguous_qualifier(observation)
    ambiguous = json.loads(json.dumps(observation))
    ambiguous['records'][0]['readouts']['1']['state'] = 'QUALIFIER_REVIEW'
    assert ambiguous_qualifier(ambiguous)
    write_new(fixture / 'ambiguous-qualifier.json', ambiguous)
    from .contracts import strict_json, MetadataError
    from .public_receipts_v1 import worker_failure, process_receipt
    sentinel = 'PRIVATE_MALFORMED_RESPONSE_SENTINEL'
    malformed = ('{"' + sentinel + '":1,"' + sentinel + '":2}').encode()
    try:
        strict_json(malformed)
    except MetadataError as error:
        assert sentinel in str(error)
        safe = worker_failure(error)
        receipt = process_receipt('synthetic', 1, {'status': 'FAIL'})
        assert sentinel not in json.dumps([safe, receipt])
        write_new(fixture / 'private-parser-failure.json', {'error': str(error)})
    else:
        raise AssertionError('Duplicate private JSON key accepted')
    for error in [UnicodeDecodeError('utf8', sentinel.encode(), 0, 1, 'synthetic'), ValueError(sentinel)]:
        assert sentinel not in json.dumps(worker_failure(error))
    write_new(fixture / 'observation.json', observation)
    ids = ['O01', 'O02', 'O03']
    assert ids == [c['id'] for c in config['cases']]
    write_new(output / 'observation-checks.json', {'status': 'PASS_THREE_OBSERVATION_RELEASE_CHECKS',
              'actual_case_ids': ids, 'actual_external_requests': 0, 'fixtures_preserved_under_task': True})


def execute(mode, root, output):
    if mode not in ('canary', 'qualify'):
        raise QualificationError('Unapproved observation phase')
    config_path = root / 'research/configs/goal4r2a3_observation_v1.json'
    config = read(config_path)
    run_checks(root, output, config)
    register_path = root / 'docs/evidence/goal4r2a2-20261106-v1/metadata-register-v1.json'
    if digest(register_path) != config['a2_metadata_register_sha256']:
        raise QualificationError('Pinned A2 source-version register differs')
    source_records = {r['requested_aid']: r for r in read(register_path)['records']}
    for aid, expected in config['source_versions'].items():
        source_version = source_records[aid]
        if (source_version['comparison']['version_revision_verdict'] != 'MATCH_OBSERVED_VERSION_METADATA'
                or expected != {'version': source_version['version']['value'], 'revision': source_version['revision']['value']}):
            raise QualificationError('Configured source version/revision differs from pinned register')
    source = root / 'runs/identifier-structure-v1'
    release_path = source / 'structure-qualification-private.json'
    if (read(source / 'results.json')['status'] != 'PASS_IDENTIFIER_AND_EXACT_STRUCTURE_CONTROL'
            or digest(release_path) != config['identifier_release_sha256']):
        raise QualificationError('Verified structure release required')
    release = read(release_path)
    plan = make_plan(release, config)
    plan['observation_config_sha256'] = digest(config_path)
    client = None
    reports, private, missing, unresolved = [], [], [], []
    if mode == 'canary':
        # This complete population/endpoint plan is immutable before first outcomes.
        manifest_path = output / 'qualification-manifest-private.json'
        write_new(manifest_path, plan)
        requests = []
        for row in plan['requests']:
            if row['script'] == config['canary_pair']:
                row = dict(row, sids=row['sids'][:config['canary_maximum_sids_per_aid']])
                row['specification'] = {'path': 'assay/aid/' + row['aid'] + '/JSON',
                                        'params': exact_sid_filter(row['sids'], row['sids'], 16)}
                requests.append(row)
        if len(requests) != 2 or any(not r['sids'] for r in requests):
            raise QualificationError('Fixed two-stage canary required')
    else:
        canary = root / 'runs/observation-canary-v1'
        report = read(canary / 'results.json')
        manifest_path = canary / 'qualification-manifest-private.json'
        admit_fixed_plan(plan, read(manifest_path), report, digest(manifest_path))
        requests = plan['requests']
    write_new(output / 'phase-request-manifest-private.json', {'role': 'DEVELOPMENT_EXPOSED', 'requests': requests,
              'qualification_manifest_sha256': digest(manifest_path), 'config_sha256': digest(config_path)})
    # Exposure is recorded before any response, including failed/quarantined intake.
    write_new(output / 'exposure-private.json', {'role': 'DEVELOPMENT_EXPOSED',
              'aids': [r['aid'] for r in requests], 'allowed_sids': {r['aid']: r['sids'] for r in requests},
              'future_untouched_evaluation': False, 'final_outcomes_authorized': False})
    try:
        client = Client(root, output, 'pubchem', [r['specification'] for r in requests])
        for i, row in enumerate(requests):
            raw, _ = client.request(row['specification'], 'observation-' + str(i).zfill(3))
            observation = normalize_observations(raw, row['aid'], set(row['sids']), row['bindings'],
                role='DEVELOPMENT_EXPOSED', expected_version=row['version'], expected_revision=row['revision'])
            private.append(observation)
            reports.append(dict(aggregate(observation, row['sids']), script=row['script'], stage=row['stage']))
            if ambiguous_qualifier(observation):
                unresolved.append(row['aid'])
                # The fixed contract stops ambiguous qualifiers. No further
                # response is fetched; neither impute nor replace the population.
                client.stop('AMBIGUOUS_QUALIFIER_INTAKE_STOP')
                break
            if mode == 'canary' and not complete_canary(observation, row['sids']):
                missing.append(row['aid'])
                client.stop('INCOMPLETE_CANARY_COVERAGE')
                break
    except Exception as error:
        if client is not None:
            client.stop('FILTERED_OBSERVATION_ACCESS_IDENTITY_OR_SCHEMA_FAILURE')
        write_new(output / 'results.json', {'status': 'NO_GO_FILTERED_OBSERVATION_ACCESS_IDENTITY_OR_SCHEMA',
                  'error_type': type(error).__name__, 'completed_validated_assays': len(reports),
                  'role': 'DEVELOPMENT_EXPOSED', 'scientific_campaigns': 0,
                  'qualification_manifest_sha256': digest(manifest_path)})
        raise
    write_new(output / 'observations-private.json', {'records': private, 'role': 'DEVELOPMENT_EXPOSED'})
    write_new(output / 'observation-aggregates.json', {'records': reports, 'raw_outcomes_or_values_included': False})
    status = ('PASS_FILTERED_OBSERVATION_CANARY' if not missing else 'NO_GO_CANARY_INCOMPLETE_COVERAGE') if mode == 'canary' else 'PASS_FIXED_DEVELOPMENT_OBSERVATION_QUALIFICATION'
    if unresolved:
        status = 'NO_GO_AMBIGUOUS_QUALIFIER_INTAKE_STOP'
    result = {'status': status, 'role': 'DEVELOPMENT_EXPOSED', 'validated_assay_requests': len(reports),
              'canary_missing_coverage_aids': missing, 'ambiguous_qualifier_aids': unresolved,
              'scientific_eligibility': 'NOT_ESTABLISHED_BY_ENGINEERING_OR_NORMALIZATION',
              'qualification_manifest_sha256': digest(manifest_path),
              'observation_config_sha256': digest(config_path), 'scientific_campaigns': 0,
              'raw_outcomes_or_values_included': False, 'historical_rows_equivalent': 'NOT_CERTIFIED'}
    write_new(output / 'results.json', result)
    return result
