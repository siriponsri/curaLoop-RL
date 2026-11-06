"""Summarize verified returned description metadata, without assay or benchmark rows."""

import collections
import csv
import hashlib
import json
from datetime import datetime, timezone

from tools.goal4r2a2_remote_v1 import LOCAL, PACKET, write_new


def main():
    folder = LOCAL / 'remote-return/full-v1'
    proof = json.loads((folder / 'local-verification-with-manifest.json').read_text())
    manifest_path = folder / 'manifest.json'
    assert proof['status'] == 'PASS_LOCAL_ALL_FILES_VERIFIED'
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == proof['manifest_sha256']
    manifest = json.loads(manifest_path.read_text())
    rel = 'runs/metadata-acquire-v1/normalized-metadata-private.json'
    entry = next(row for row in manifest['files'] if row['path'] == rel)
    source = folder / 'files' / rel
    assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256']
    records = json.loads(source.read_text())['records']
    roster = json.loads((PACKET / 'metadata-register-v1.json').read_text())
    si = json.loads((folder / 'files/docs/evidence/goal4r2a-20261106-v1/si-metadata-audit-v1.json').read_text())
    expected = {row['aid']: row for row in si['versions']}
    providers = collections.defaultdict(list)
    register = []
    unit_counts = collections.Counter()
    with (PACKET / 'readout-definitions-v1.csv').open('x', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['aid', 'tid', 'readout_name', 'unit_state', 'raw_unit_enum', 'unit_pointer',
                         'unit_semantics', 'scientific_endpoint_selection', 'response_sha256'])
        for record in records:
            aid = record['requested_aid']
            provider = record['provider']['value']['db']
            providers[provider['name']].append(aid)
            register.append({'aid': aid, 'published': expected[aid],
                'observed_version': record['version'], 'observed_revision': record['revision'],
                'observed_date': record['last_data_change'], 'comparison': record['comparison'],
                'retrieval_utc': record['retrieval_utc'], 'response_sha256': record['response_sha256'],
                'provider_name': provider['name'], 'provider_source_id': provider.get('source_id'),
                'provider_url_observed': provider.get('url'), 'provider_terms': 'NOT_CERTIFIED',
                'target_state': record['targets']['state'],
                'target_identifiers': [t['mol_id'] for t in (record['targets']['value'] or [])
                                       if type(t) is dict and type(t.get('mol_id')) is dict],
                'readout_definition_count': len(record['readout_definitions']),
                'scientific_endpoint_binding': 'NOT_SELECTED_OR_CLEARED'})
            for readout in record['readout_definitions']:
                unit = readout['unit']
                unit_counts[(unit['state'], str(unit['value']))] += 1
                writer.writerow([aid, readout['tid'], readout['name'], unit['state'],
                    unit['value'] if unit['state'] == 'VALUE' else '', unit['source_pointer'],
                    'NOT_DECODED', 'NOT_SELECTED_OR_CLEARED', record['response_sha256']])
    controls = roster['selector_controls']
    assert len(controls) == 2 and {c['label'] for c in controls} == {'published', 'invalid'}
    by_label = {c['label']: c for c in controls}
    first = next(r for r in records if r['requested_aid'] == by_label['published']['aid'])
    equal = len({first['response_sha256'], *(c['response_sha256'] for c in controls)}) == 1
    result = {
        'status': 'PASS_METADATA_READINESS_AUDIT_SCIENTIFIC_NO_GO',
        'input_tree_sha256': proof['tree_sha256'], 'private_normalized_source_sha256': entry['sha256'],
        'current_aids_observed': len(records), 'version_revision_matches': roster['comparison_counts'],
        'date_field_states': dict(collections.Counter(r['last_data_change']['state'] for r in records)),
        'target_field_states': dict(collections.Counter(r['targets']['state'] for r in records)),
        'provider_count': len(providers),
        'provider_register': [{'provider': name, 'aid_count': len(aids), 'aids': aids,
            'terms_url': None, 'terms_evidence': 'NOT_REVIEWED_PROVIDER_SPECIFIC',
            'local_analysis': 'NOT_CERTIFIED', 'adaptation': 'NOT_CERTIFIED',
            'redistribution': 'NOT_CERTIFIED', 'commercial_reuse': 'NOT_CERTIFIED',
            'attribution': 'PRESERVE_SOURCE_IDENTITY_PENDING_EXACT_TERMS'}
            for name, aids in sorted(providers.items())],
        'readout_definitions': sum(len(r['readout_definitions']) for r in records),
        'unit_observations': [{'state': key[0], 'raw_value': key[1], 'count': value}
                              for key, value in sorted(unit_counts.items())],
        'selector_control': {'aid': first['requested_aid'],
            'requested_published': by_label['published']['option'],
            'requested_invalid': by_label['invalid']['option'],
            'both_http_200': all(c['result'].get('status_code') == 200 for c in controls),
            'current_published_invalid_responses_byte_equal': equal,
            'returned_version': first['version']['value'], 'returned_revision': first['revision']['value'],
            'verdict': 'NOT_VALIDATED_NEGATIVE_CONTROL_RETURNED_CURRENT_METADATA',
            'scope': 'Description operation on AID 873; not a claim about every PubChem operation'},
        'historical_rows_equivalent': 'NOT_CERTIFIED', 'eligible_scientific_cohort': 'UNKNOWN',
        'certified_biological_groups': 0, 'zero_is_clearance_count_not_biological_absence': True,
        'scientific_pilot': 'NO_GO', 'register': register,
        'readout_csv_sha256': hashlib.sha256((PACKET / 'readout-definitions-v1.csv').read_bytes()).hexdigest(),
        'activity_rows_requested_or_processed': 0, 'benchmark_task_gold_rows_intaken': 0,
    }
    write_new(PACKET / 'readiness-audit-v1.json', result)
    resources = [json.loads((PACKET / name).read_text()) for name in
                 ('probe-resources-v1.json', 'contract-resources-v1.json', 'metadata-resources-v1.json')]
    ledger = json.loads((PACKET / 'remote-launch-ledger-v1.json').read_text())
    assert len(ledger) == 3 and all(r['status'] == 'COMPLETED' for r in ledger)
    verify = json.loads((folder / 'verification-resources.json').read_text())
    snapshot = json.loads((PACKET / 'remote-snapshot-v1.json').read_text())
    absence = json.loads((PACKET / 'remote-absence-v1.json').read_text())
    assert absence['status'] == 'PASS_SCOPED_ROOTS_ABSENT'
    reserved = sum(r['reserved_cpu_seconds'] for r in ledger)
    write_new(PACKET / 'budget-closeout-v1.json', {
        'status': 'PASS_CONSERVATIVE_BUDGET_WITH_EXPLICIT_ACCOUNTING_LIMITS',
        'start_utc': '2026-11-06T01:05:41Z', 'deadline_utc': '2026-11-06T13:05:41Z',
        'evidence_created_utc': datetime.now(timezone.utc).isoformat(),
        'cpu_cap_seconds': 14400, 'maximum_workers': 2, 'observed_remote_worker_overlap': 1,
        'worker_jobs': len(ledger), 'unresolved_reservations': 0,
        'measured_worker_cpu_seconds': sum(r['cpu_seconds'] for r in resources),
        'retained_worker_reservations_seconds': reserved,
        'utility_reserve_seconds': 3600, 'conservative_charge_seconds': reserved + 3600,
        'conservative_charge_cpu_hours': (reserved + 3600) / 3600,
        'snapshot_cpu_seconds': snapshot['snapshot_cpu_seconds'],
        'inner_verification_cpu_seconds': proof['verification_cpu_seconds'],
        'complete_guarded_verification': verify,
        'preservation_measurements_included_in_utility_reserve': True,
        'remote_return_helper_hard_cpu_guard': 'NOT_IMPLEMENTED',
        'exact_exhaustive_host_cpu_accounting': 'NOT_CERTIFIED',
        'remote_absence_utc': absence['utc'],
        'gpu_or_new_paid_service': False})
    print(json.dumps({k: result[k] for k in ('status', 'current_aids_observed', 'provider_count', 'readout_definitions', 'selector_control')}))


if __name__ == '__main__':
    main()
