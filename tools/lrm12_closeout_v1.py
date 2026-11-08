"""Aggregate the frozen M1 diagnostics and close the conditional release honestly."""

import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local/lr-m12-20261108-v1'
PUBLIC = ROOT / 'docs/evidence/lr-m12-20261108-v1'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def main():
    ledger = json.loads((PRIVATE / 'ledger.json').read_text())
    assert ledger['status'] == 'ACTIVE' and not ledger['m2_release']
    assert all(row['state'] == 'PASS' for row in ledger['jobs'])
    freeze = json.loads((PUBLIC / 'm1-freeze-v2.json').read_text())
    for path, pin in freeze['code_sha256'].items():
        assert sha(ROOT / path) == pin
    pins = json.loads((PRIVATE / 'old-ledger-pins-v1.json').read_text())
    old_rows = pins['records']
    old_result = []
    for pin in old_rows:
        path, expected = pin['path'], pin['sha256']
        assert sha(ROOT / path) == expected
        old_result.append({'path': path, 'sha256': expected, 'status': 'UNCHANGED'})
    returned = PRIVATE / 'remote-return/files'
    files = sorted((returned / 'diagnostics').glob('*.json'))
    assert len(files) == 2
    cases = [case for path in files for case in json.loads(path.read_text())['cases']]
    assert len(cases) == 12 and sum(len(c['acquisition']) for c in cases) == 36
    grouped = {}
    for variant in ('nominal', 'point_min', 'confidence_min'):
        rows = [a for c in cases for a in c['acquisition'] if a['variant'] == variant]
        grouped[variant] = {
            'calls': len(rows), 'deviations_from_greedy': sum(a['candidate_id'] != a['baseline_id'] for a in rows),
            'interrupted_calls': sum(a['interrupted'] for a in rows),
            'wall_ms_min': min(a['wall_seconds'] for a in rows) * 1000,
            'wall_ms_median': statistics.median(a['wall_seconds'] for a in rows) * 1000,
            'wall_ms_max': max(a['wall_seconds'] for a in rows) * 1000,
            'paired_traces_min': min(a['paired_traces'] for a in rows),
            'paired_traces_max': max(a['paired_traces'] for a in rows),
            'score_is_realized_molecular_gain': False}
    learned = [c for c in cases if c['initial_count'] == 16]
    summary = {
        'schema': 'curaloop.lr_m12.m1_summary.v1', 'm1_gate': 'NO_GO_METHOD_DISTINCTION_UNRESOLVED',
        'm1_investigation': 'COMPLETE', 'm2_status': 'NOT_RUN_GATE_NOT_PASSED',
        'm2_campaigns': 0, 'm3_status': 'NOT_RELEASED',
        'admitted_development_tasks': 6, 'admitted_task_rows': 1285,
        'diagnostic_tasks': 2, 'diagnostic_cases': 12, 'timing_calls': 36,
        'pool_sizes': [32, 64, 128], 'initial_counts': [0, 16], 'seeds': [101],
        'constructed_checks': 17, 'constructed_checks_status': 'PASS',
        'fit_wall_ms_min': min(c['fit_wall_seconds'] for c in cases) * 1000,
        'fit_wall_ms_max': max(c['fit_wall_seconds'] for c in cases) * 1000,
        'gp_fit_fallbacks': sum(bool(f) for c in cases for f in c['fit_fallbacks']),
        'gp_context_fits': 36,
        'initial16_brier': {'cases': 6, 'mean': statistics.mean(c['brier'] for c in learned),
                            'min': min(c['brier'] for c in learned), 'max': max(c['brier'] for c in learned),
                            'worse_than_constant_half': sum(c['brier'] > .25 for c in learned)},
        'calibration_or_gp_approximation_error_certified': False,
        'variants': grouped, 'independent_novelty_review': 'NOT_RUN',
        'reserved_final_feature_label_or_presence_decode': False,
        'old_exposed_validation_decode': False,
        'new_split_or_source_intake': False,
        'case_metrics': [{k: c[k] for k in ('task_id', 'pool_size', 'initial_count', 'seed',
                                           'fit_wall_seconds', 'fit_cpu_seconds', 'query_rows', 'brier', 'log_loss')}
                         for c in cases],
        'diagnostic_file_sha256': {p.name: sha(p) for p in files}}
    new(PUBLIC / 'm1-summary-v1.json', summary)
    new(PUBLIC / 'old-ledgers-unchanged-v1.json', {'status': 'PASS', 'ledgers': old_result})
    for name in ('complete-return-verified-v1.json', 'fresh-absence-v1.json'):
        assert (PUBLIC / name).is_file()
    resources = []
    for row in ledger['jobs']:
        path = PRIVATE / 'jobs' / row['job'] / 'resource.json'
        receipt = json.loads(path.read_text())
        assert receipt['status'] == 'PASS' and sha(path) == row['resource_sha256']
        resources.append({'job': row['job'], 'host': row['host'], 'cpu': row['cpu'],
                          'reserved_seconds': row['reservation_seconds'],
                          'reported_cpu_seconds': receipt['cpu_seconds'],
                          'reported_wall_seconds': receipt.get('wall_seconds'), 'resource_sha256': sha(path),
                          'status': receipt['status']})
    new(PUBLIC / 'resource-summary-v1.json', {'schema': 'curaloop.lr_m12.resources_summary.v1',
        'jobs': resources, 'cpu_cap_seconds': 86400,
        'retained_reservation_seconds': sum(ledger['bucket_reserved_seconds'].values()),
        'reported_job_cpu_seconds': sum(r['reported_cpu_seconds'] for r in resources),
        'utilities_delivery_seconds_reserved': 3600,
        'job_cpu_excludes_controller_transport_and_delivery_cpu': True,
        'active_owned_jobs': 0, 'no_reservation_refunds': True})
    ledger.update(status='CLOSED_OWNER_CHECKPOINT', closed_utc=datetime.now(timezone.utc).isoformat(),
                  m1_gate=summary['m1_gate'], m2_release=False,
                  close_reason='M1 novelty/credible-benefit gate not passed; conditional M2 withheld')
    with (PRIVATE / 'ledger.json').open('w', encoding='utf-8', newline='\n') as f:
        json.dump(ledger, f, indent=2)
        f.write('\n')
    new(PUBLIC / 'ledger-closeout-v1.json', ledger)
    status = {'schema': 'curaloop.lr_m12.status.v1', 'current_as_of': ledger['closed_utc'],
              'owner_destination': 'METHOD_PAPER_WITH_RD_PLUGIN_USING_EXISTING_BENCHMARKS',
              'm1_status': 'COMPLETE_INVESTIGATION_NO_GO', 'm1_gate': summary['m1_gate'],
              'm2_status': summary['m2_status'], 'm3_status': 'NOT_RELEASED',
              'novel_algorithm': 'NOT_ESTABLISHED_PRIOR_ART_OVERLAP',
              'adapter': 'EXECUTED_SMALL_POOL_ENGINEERING_ONLY_CALIBRATION_REVISE',
              'molecular_efficacy': 'NOT_TESTED_BY_LR_M12', 'scientific_release_open': False,
              'final_outcomes_opened': False, 'benchmark_publication_fallback': False,
              'next_actor': 'OWNER', 'previous_m0_status_is_historical':
              'research/configs/method_first_status_20261108_v1.json'}
    new(ROOT / 'research/configs/lr_m12_status_20261108_v1.json', status)
    print(json.dumps({'gate': summary['m1_gate'], 'variants': grouped,
                      'brier': summary['initial16_brier'], 'retained_seconds':
                      sum(ledger['bucket_reserved_seconds'].values()), 'jobs': len(resources)}))


if __name__ == '__main__':
    main()
