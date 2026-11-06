"""Reconcile resource/preservation metadata; no scientific result analysis."""

import json
from datetime import datetime, timezone

from tools.goal4r2a_remote_v1 import LOCAL, PACKET, write_new


def main():
    ledger = json.loads((PACKET / 'remote-launch-ledger-v2.json').read_text())
    if len(ledger) != 5 or any(r['status'] != 'COMPLETED' or r['exit_code'] != 0 for r in ledger):
        raise ValueError('Expected all five bounded jobs with no unresolved reservation')
    returned = LOCAL / 'remote-return/full-v1'
    intervals, resources = [], []
    begin = datetime(2026, 11, 5, 23, 57, 53, tzinfo=timezone.utc)
    end = datetime(2026, 11, 6, 11, 57, 53, tzinfo=timezone.utc)
    for row in ledger:
        receipt = json.loads((returned / 'files/runs' / row['attempt'] / 'resources.json').read_text())
        if receipt['status'] != 'PASS' or not 0 <= receipt['cpu_seconds'] <= row['reserved_cpu_seconds']:
            raise ValueError('Worker resource discrepancy')
        start, finish = map(datetime.fromisoformat, (receipt['start_utc'], receipt['finish_utc']))
        if not begin <= start <= finish <= end:
            raise ValueError('Worker outside owner window')
        intervals += [(start, 1), (finish, -1)]
        resources.append({'attempt': row['attempt'], **receipt})
    active = maximum = 0
    for _, change in sorted(intervals, key=lambda value: (value[0], value[1])):
        active += change
        maximum = max(maximum, active)
    if maximum > 2:
        raise ValueError('Too many concurrent workers')
    proof = json.loads((PACKET / 'local-full-return-verification-v1.json').read_text())
    absence = json.loads((PACKET / 'remote-absence-v1.json').read_text())
    snapshot = json.loads((PACKET / 'remote-snapshot-v1.json').read_text())
    if proof['status'] != 'PASS_LOCAL_ALL_FILES_VERIFIED' or absence['status'] != 'PASS_SCOPED_ROOTS_ABSENT':
        raise ValueError('Preservation/deletion not closed')
    charge = sum(r['reserved_cpu_seconds'] for r in ledger) + 1800 + 1200 + 600
    if charge > 14400:
        raise ValueError('CPU charge exceeds owner cap')
    result = {'status': 'PASS_BOUNDED_FEASIBILITY_AND_PRESERVATION',
              'utc': datetime.now(timezone.utc).isoformat(), 'remote_jobs': len(ledger),
              'worker_resources': resources, 'recorded_worker_cpu_seconds': sum(r['cpu_seconds'] for r in resources),
              'conservative_worker_reservations_seconds': sum(r['reserved_cpu_seconds'] for r in ledger),
              'utility_reserves_seconds': {'preparation_retrieval_transport_checks': 1800,
                                          'preservation_and_local_verification': 1200, 'administration_and_startup': 600},
              'conservative_total_charge_seconds': charge, 'conservative_cpu_hours': charge / 3600,
              'owner_cap_cpu_hours': 4, 'maximum_recorded_worker_overlap': maximum,
              'owner_worker_limit': 2, 'snapshot_cpu_seconds_inside_reserve': snapshot['snapshot_cpu_seconds'],
              'local_verification_cpu_seconds_inside_reserve': proof['verification_cpu_seconds'],
              'exact_exhaustive_host_cpu_accounting': 'NOT_CERTIFIED; conservative reserves remain charged',
              'scientific_campaigns': 0, 'llm_calls': 0, 'live_team_writes': 0,
              'publication_metadata_gate': 'PASS_60_PAIRS_AND_105_VERSION_TUPLES',
              'scientific_method_claim': 'NO_GO', 'actual_eligible_dataset_count': 'UNKNOWN',
              'retained_regular_files': proof['file_count'], 'retained_bytes': proof['bytes'],
              'archive_bytes': (returned / 'task.zip').stat().st_size,
              'remote_absence_utc': absence['utc']}
    write_new(PACKET / 'budget-closeout-v1.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'worker_resources'}, indent=2))


if __name__ == '__main__':
    main()
