"""Finalize the metadata audit after component/classification retrieval."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from r0_chembl_audit_v1 import source_payload
from r0_chembl_metadata_v1 import MetadataGuard, PRIVATE, ROOT, save

def audit():
    summary = json.loads((PRIVATE / 'metadata-summary-v1.json').read_text())
    components = source_payload('chembl37-selected-components')['target_components']
    classifications = source_payload('chembl37-selected-classifications')['protein_classifications']
    targets = source_payload('chembl37-selected-targets')['targets']
    expected_components = {entry['component_id'] for row in targets for entry in row['target_components']}
    assert {row['component_id'] for row in components} == expected_components
    class_ids = {entry['protein_classification_id'] for row in components for entry in row['protein_classifications']}
    assert {row['protein_class_id'] for row in classifications} == class_ids
    before = source_payload('chembl-current-status')
    after = source_payload('chembl37-status-after')
    assert before == after and before['chembl_db_version'] == 'ChEMBL_37'
    class_mapping = {row['protein_class_id']: row for row in classifications}
    missing_parents = {row['parent_id'] for row in classifications if row['parent_id'] is not None and row['parent_id'] not in class_mapping}
    count = len(targets) + len(components) + len(classifications)
    assert count <= 100
    ledger = json.loads((PRIVATE / 'ledger.json').read_text())
    assert len(ledger['attempts']) <= 32 and ledger['decoded_bytes'] <= 16 * 1024**2
    assert all('/api/data/activity' not in row['url'] for row in ledger['attempts'])
    assert ledger['worker_reserved_seconds'] + ledger['utility_charge_seconds'] <= 1800
    for row in ledger['attempts']:
        if 'raw_path' in row:
            data = (ROOT / row['raw_path']).read_bytes()
            assert len(data) == row['decoded_bytes']
            assert hashlib.sha256(data).hexdigest() == row['sha256']
    summary.update({
        'audit_revision': 'v2', 'status': 'PASS_BOUNDED_METADATA_NOT_SCIENTIFIC_GO',
        'target_components': len(components), 'protein_classification_ids': len(classifications),
        'lineage_records_counted': count,
        'classification_field_names': sorted(classifications[0]),
        'classification_level_counts': dict(Counter(str(row['class_level']) for row in classifications)),
        'classification_parent_ids_not_in_sample': len(missing_parents),
        'classification_ancestry_closed': not missing_parents,
        'target_types': dict(Counter(row['target_type'] for row in targets)),
        'target_organisms': dict(Counter(row['organism'] for row in targets)),
        'service_status_before_after_equal': True,
        'http_attempts': len(ledger['attempts']),
        'successful_metadata_responses': sum(row['status'] == 'PASS_METADATA_LISTING' for row in ledger['attempts']),
        'stopped_sources': ledger['stopped_sources'],
        'decoded_bytes': ledger['decoded_bytes'],
        'conservative_cpu_charge_seconds': ledger['worker_reserved_seconds'] + ledger['utility_charge_seconds'],
        'resource_receipts': len(list(PRIVATE.glob('*-resource*.json'))),
        'raw_passages_in_agent_context': False,
        'current_data_license_source': 'ChEMBL37 README and LICENSE pinned separately',
        'commercial_product_rights': 'NOT_CLEARED_AS_A_BLANKET_CLAIM',
        'scientific_phase_decision': 'REVISE_BEFORE_NEXT_PHASE',
    })
    save(PRIVATE / 'metadata-summary-v2.json', summary)
    save(PRIVATE / 'classification-review-v2.json', {'classifications': classifications,
          'missing_parent_ids': sorted(missing_parents), 'certified_family_count': None})
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    receipt = PRIVATE / 'audit-resource-v2.json'
    if receipt.exists():
        raise RuntimeError('Audit receipt already exists')
    guard = MetadataGuard(receipt)
    try:
        audit()
    except Exception as exc:
        guard.finish('FAIL', error_type=type(exc).__name__)
        raise
    else:
        guard.finish('PASS_BOUNDED_METADATA_ONLY', charged_to='300-second utility reservation',
                     audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
