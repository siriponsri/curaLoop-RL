"""Bounded metadata acquisition and engineering validation, not benchmark runs."""

import collections
import hashlib
import importlib.util
import io
import json
import time
import unittest
from pathlib import Path

from .contracts import MetadataError, benchmark_blockers, compare_version, normalize_description, registry_coverage


def write_new(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def summarize_record(record):
    provider = record['provider']['value']
    database = provider.get('db', {}) if type(provider) is dict else {}
    if type(database) is not dict:
        database = {}
    raw_targets = record['targets']['value'] if record['targets']['state'] == 'VALUE' else []
    targets = []
    for target in raw_targets:
        if type(target) is dict and type(target.get('mol_id')) is dict:
            targets.append(target['mol_id'])
    return {'requested_aid': record['requested_aid'], 'response_sha256': record['response_sha256'],
            'retrieval_utc': record['retrieval_utc'], 'version': record['version'], 'revision': record['revision'],
            'date_state': record['last_data_change']['state'], 'last_data_change': record['last_data_change'],
            'date_meaning': record['date_meaning'],
            'comparison': record['comparison'], 'provider_name': database.get('name'),
            'provider_field_state': record['provider']['state'],
            'provider_terms': 'NOT_CERTIFIED', 'provider_homepage': database.get('url'),
            'target_identifiers': targets, 'target_field_state': record['targets']['state'],
            'readout_definitions_field_state': record['readout_definitions_field']['state'],
            'readout_definition_count': len(record['readout_definitions']) if record['readout_definitions_field']['state'] == 'VALUE' else None,
            'readout_unit_observations': [row['unit'] for row in record['readout_definitions']],
            'readout_unit_enum_semantics': 'UNRESOLVED_WITHOUT_PINNED_SCHEMA',
            'scientific_plan_ready': False}


def acquire(root, output, plan, begin, load_client, request_description):
    client = load_client(plan)
    si = json.loads((root / 'docs/evidence/goal4r2a-20261106-v1/si-metadata-audit-v1.json').read_text())
    expected = {row['aid']: row for row in si['versions']}
    records, failures, requests = [], [], []

    def accept(request):
        aid = request['requested_aid']
        requests.append(request)
        if not request['result'].get('ok'):
            failures.append({'aid': aid, 'status': 'ACCESS_FAILED', 'error': request['result'].get('error')})
            return False
        path = Path(request['request']['raw_output_path'])
        if (path.is_symlink() or not path.resolve().is_relative_to(root / 'runs')
                or path.stat().st_size != request['response_bytes']
                or hashlib.sha256(path.read_bytes()).hexdigest() != request['response_sha256']):
            raise MetadataError('Response path/hash/size differs from immutable request receipt')
        try:
            record = normalize_description(path.read_bytes(), aid, request['request_utc'])
        except MetadataError as exc:
            failures.append({'aid': aid, 'status': 'SCHEMA_REJECTED', 'reason': str(exc)})
            return False
        record['comparison'] = compare_version(record, expected[aid])
        records.append(record)
        return True

    probe_path = root / 'runs/metadata-probe-v1/results.json'
    probe = json.loads(probe_path.read_text())['request']
    good_probe = accept(probe)
    stopped = None
    if good_probe:
        for aid in plan['allowed_aids']:
            if aid == plan['probe_aid']:
                continue
            if time.monotonic() - begin >= 480:
                stopped = 'WALL_MARGIN_REACHED'
                break
            time.sleep(plan['minimum_interval_seconds'])
            request = request_description(client, plan, aid, output)
            okay = accept(request)
            if not okay:
                error = str(request['result'].get('error', ''))
                if any(code in error for code in ('403', '429')) or failures[-1]['status'] == 'SCHEMA_REJECTED':
                    stopped = 'DENIED_RATE_LIMIT_OR_UNEXPECTED_SCHEMA'
                    break
            with (output / 'progress.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps({'observed': len(records), 'failed': len(failures), 'last_aid': aid}) + '\n')
    else:
        stopped = 'INITIAL_PROBE_FAILED_NO_ROSTER_FANOUT'
    controls = []
    if records and not stopped and time.monotonic() - begin < 540:
        selected = next((r for r in records if r['comparison']['version_revision_verdict'] == 'DIFFERENT'), records[0])
        aid = selected['requested_aid']
        version = str(expected[aid]['version']) + '.' + str(expected[aid]['revision'])
        for label, option in [('published', version), ('invalid', '999999.999999')]:
            time.sleep(plan['minimum_interval_seconds'])
            request = request_description(client, plan, aid, output, '-' + label, {'version': option})
            detail = {'label': label, 'aid': aid, 'option': option, 'result': request['result'],
                      'response_sha256': request['response_sha256']}
            if request['result'].get('ok'):
                try:
                    parsed = normalize_description(Path(request['request']['raw_output_path']).read_bytes(), aid, request['request_utc'])
                    detail['comparison'] = compare_version(parsed, expected[aid])
                    detail['returned_version'] = parsed['version']
                    detail['returned_revision'] = parsed['revision']
                except MetadataError as exc:
                    detail['schema_error'] = str(exc)
            controls.append(detail)
            if 'schema_error' in detail or any(code in str(request['result'].get('error', '')) for code in ('403', '429')):
                break
    coverage = registry_coverage(records, plan['allowed_aids'])
    providers = collections.defaultdict(list)
    summaries = [summarize_record(record) for record in records]
    for row in summaries:
        providers[row['provider_name'] or 'UNRESOLVED_PROVIDER'].append(row['requested_aid'])
    result = {'status': 'METADATA_ROSTER_COMPLETED' if coverage['description_roster_complete'] else 'PARTIAL_OR_ACCESS_FAILED',
              'coverage': coverage, 'current_request_count': len(requests), 'selector_control_requests': len(controls),
              'comparison_counts': dict(collections.Counter(r['comparison']['version_revision_verdict'] for r in records)),
              'records': summaries, 'failures': failures, 'stopped_reason': stopped,
              'selector_controls': controls, 'historical_selector_support': 'UNVERIFIED_REQUIRES_RETURNED_IDENTITY_AND_CONTROLS',
              'provider_register': [{'provider': key, 'aids': values, 'terms': 'NOT_CERTIFIED'} for key, values in sorted(providers.items())],
              'scientific_pilot': 'NO_GO', 'actual_eligible_dataset_count': 'UNKNOWN',
              'certified_biological_groups': 0, 'activity_rows_requested': False,
              'full_record_fallback': False, 'raw_semantics': plan['raw_semantics']}
    write_new(output / 'normalized-metadata-private.json', {'records': records})
    return result


def validate(root, output):
    case_path = root / 'research/configs/goal4r2a2_cases_v1.json'
    freeze = json.loads((root / 'docs/evidence/goal4r2a2-20261106-v1/cases-freeze-v1.json').read_text())
    if hashlib.sha256(case_path.read_bytes()).hexdigest() != freeze['cases_sha256']:
        raise MetadataError('Pre-implementation case freeze differs')
    path = root / 'tests/research/test_readiness_v1.py'
    spec = importlib.util.spec_from_file_location('readiness_contract_checks', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    class Recorded(unittest.TextTestResult):
        executed_ids = []
        def startTest(self, test):
            super().startTest(test)
            self.executed_ids.append(test._testMethodName.split('_')[1])
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Recorded).run(suite)
    (output / 'checks.log').write_text(stream.getvalue(), encoding='utf-8')
    cases = json.loads(case_path.read_text())['cases']
    if (result.testsRun != len(cases) or not result.wasSuccessful()
            or sorted(result.executed_ids) != sorted(row['id'] for row in cases)):
        raise MetadataError('Ten fixed contract checks did not pass; retain log')
    manifest = json.loads((root / 'research/manifests/goal4r2a2_benchmark_readiness_v1.json').read_text())
    return {'status': 'PASS_METADATA_AND_COMPATIBILITY_CONTRACTS', 'checks': result.testsRun,
            'frozen_cases': [row['id'] for row in cases],
            'actual_executed_case_ids': result.executed_ids,
            'benchmark_blockers': benchmark_blockers(manifest),
            'external_benchmark_execution': 'NOT_RUN', 'scientific_campaigns': 0,
            'actual_holdout_roster': 'NOT_FROZEN'}


def execute(mode, root, output, plan, begin, load_client, request_description):
    return acquire(root, output, plan, begin, load_client, request_description) if mode == 'acquire' else validate(root, output)
