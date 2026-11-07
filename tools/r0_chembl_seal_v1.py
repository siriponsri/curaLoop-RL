"""Seal R0 evidence and export only aggregates, IDs and audit metadata."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from r0_chembl_metadata_v1 import PRIVATE, ROOT, save

evidence = ROOT / 'docs/evidence/r0-chembl-20261107-v1'
evidence.mkdir(parents=True, exist_ok=True)
summary = json.loads((PRIVATE / 'metadata-summary-v3.json').read_text())
ledger_path = PRIVATE / 'ledger.json'
ledger = json.loads(ledger_path.read_text())
assert ledger.get('status') != 'CLOSED'
assert not (PRIVATE / 'worker.lock').exists()
assert all(summary['offline_guard_checks'].values())
receipts = [json.loads(path.read_text()) for path in sorted(PRIVATE.glob('*resource*.json'))]
assert all(row['status'] != 'RUNNING' for row in receipts)
summary['audit_revision'] = 'v4-sealed'
summary['resource_receipts'] = len(receipts)
summary['receipt_cpu_seconds_sum_partial_measurement'] = sum(row['cpu_seconds'] for row in receipts)
summary['receipt_cpu_sum_excludes_unmeasured_setup_utilities'] = True
summary['phase_work_status'] = 'READOUT_COMPLETE_SCIENTIFIC_GATE_REVISE'
summary['next_phase_released'] = False
summary['snapshot_is_full_release_archive'] = False
summary['biological_family_oracle'] = 'NOT_ESTABLISHED'
ledger.update(status='CLOSED', closed_utc=datetime.now(timezone.utc).isoformat(),
              scientific_phase_decision='REVISE_BEFORE_NEXT_PHASE')
save(ledger_path, ledger)
save(PRIVATE / 'metadata-summary-v4.json', summary)
exports = {
    'metadata-summary-v4.json': summary,
    'source-ledger-v1.json': ledger,
    'selection-v1.json': json.loads((PRIVATE / 'selection-v1.json').read_text()),
    'dispositions-v1.json': json.loads((PRIVATE / 'metadata-dispositions-v1.json').read_text()),
    'resource-receipts-v1.json': {'receipts': receipts},
}
for name, payload in exports.items():
    save(evidence / name, payload)
index = []
for path in sorted(PRIVATE.rglob('*')):
    if path.is_file():
        data = path.read_bytes()
        index.append({'path': str(path.relative_to(ROOT)), 'bytes': len(data),
                      'sha256': hashlib.sha256(data).hexdigest()})
assert sum(row['bytes'] for row in index) < 64 * 1024**2
assert sum(row['bytes'] for row in index if row['path'].endswith('.html')) == ledger['decoded_bytes']
for row in index:
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
save(evidence / 'private-artifact-index-v1.json', {'status':'PASS_FULL_LOCAL_REREAD',
     'files': len(index), 'bytes': sum(row['bytes'] for row in index), 'artifacts': index,
     'raw_source_response_payloads_publicly_exported': False,
     'structural_ids_and_derived_metadata_exported': True,
     'remote_jobs': 0, 'remote_cleanup': 'NOT_APPLICABLE'})
print(json.dumps({'status':'SEALED_WITH_REVISE_DECISION','attempts':len(ledger['attempts']),
                  'decoded_bytes':ledger['decoded_bytes'], 'resource_receipts':len(receipts),
                  'receipt_cpu_seconds_sum_partial_measurement':summary['receipt_cpu_seconds_sum_partial_measurement'],
                  'conservative_cpu_charge_seconds':summary['conservative_cpu_charge_seconds'],
                  'private_files_reread':len(index), 'private_bytes_reread':sum(row['bytes'] for row in index)}, indent=2))
