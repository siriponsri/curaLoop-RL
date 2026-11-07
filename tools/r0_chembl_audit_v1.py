"""Outcome-free structural audit; text is summarized without emitting passages."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from r0_chembl_metadata_v1 import MetadataGuard, PRIVATE, ROOT, save

def source_payload(source):
    ledger = json.loads((PRIVATE / 'ledger.json').read_text())
    matches = [row for row in ledger['attempts'] if row['source'] == source and row['status'] == 'PASS_METADATA_LISTING']
    assert len(matches) == 1, source
    path = ROOT / matches[0]['raw_path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == matches[0]['sha256']
    return json.loads(path.read_text())

def audit():
    selection = json.loads((PRIVATE / 'selection-v1.json').read_text())
    assays = source_payload('chembl37-selected-assays')['assays']
    documents = source_payload('chembl37-selected-documents')['documents']
    targets = source_payload('chembl37-selected-targets')['targets']
    expected_assays = set(selection['assay_ids'])
    assert len(assays) == 50 and {row['assay_chembl_id'] for row in assays} == expected_assays
    assert {row['document_chembl_id'] for row in documents} == set(selection['document_ids'])
    assert {row['target_chembl_id'] for row in targets} == set(selection['target_ids'])
    assert len(documents) <= 20 and len(targets) <= 50
    expected_fields = {'assay_chembl_id','document_chembl_id','target_chembl_id','assay_type','confidence_score','src_id',
                       'description','assay_organism','assay_tax_id','assay_cell_type','assay_tissue',
                       'assay_subcellular_fraction','bao_format','relationship_type'}
    assert all(set(row) == expected_fields for row in assays)
    assert all(row['confidence_score'] == 9 and row['src_id'] == 1 for row in assays)
    assert Counter(row['assay_type'] for row in assays) == {'B': 25, 'F': 25}
    missing = {field: sum(row.get(field) is None or row.get(field) == '' for row in assays)
               for field in ('description','assay_organism','assay_tax_id','assay_cell_type','assay_tissue',
                             'assay_subcellular_fraction','bao_format','relationship_type')}
    endpoint_patterns = {'IC50': r'\bIC[ _-]?50\b', 'EC50': r'\bEC[ _-]?50\b',
                         'Ki': r'\bK[_ ]?i\b', 'KD': r'\bK[_ ]?d\b'}
    quantitative = re.compile(r'(?:\d+(?:\.\d+)?\s*(?:[npumµμ]?M|%|mol\b|nmol\b)|[<>≤≥]\s*\d)', re.I)
    categorical_outcome = re.compile(r'\b(?:was|were|is|are)\s+(?:inactive|active|potent)\b', re.I)
    dispositions = []
    for row in assays:
        text = row.get('description') or ''
        risky = bool(quantitative.search(text) or categorical_outcome.search(text))
        mentions = [name for name, pattern in endpoint_patterns.items() if re.search(pattern, text, re.I)]
        dispositions.append({'assay_id': row['assay_chembl_id'], 'document_id': row['document_chembl_id'],
                             'target_id': row['target_chembl_id'], 'assay_type': row['assay_type'],
                             'description_disposition': 'QUARANTINE_POSSIBLE_OUTCOME_OR_CONDITION' if risky else 'NO_PATTERN_FLAG_NOT_ADJUDICATED',
                             'endpoint_mentions': mentions, 'endpoint_ground_truth': 'NOT_ADJUDICATED',
                             'description_sha256': hashlib.sha256(text.encode()).hexdigest()})
    document_title_flags = sum(bool(quantitative.search(row.get('title') or '') or categorical_outcome.search(row.get('title') or '')) for row in documents)
    component_ids, class_ids = set(), set()
    class_keys, component_keys = set(), set()
    classifications = {}
    for target in targets:
        for component in target.get('target_components') or []:
            component_keys.update(component)
            component_ids.add(component['component_id'])
            for entry in component.get('protein_classifications') or []:
                class_keys.update(entry)
                class_id = entry.get('protein_classification_id', entry.get('protein_class_id'))
                if class_id is not None:
                    class_ids.add(class_id)
                    classifications[str(class_id)] = entry
    lineage_record_count = len(targets) + len(component_ids) + len(class_ids)
    assert lineage_record_count <= 100
    parents = {row['assay_chembl_id']: row['assay_chembl_id'] for row in assays}
    def find(value):
        while parents[value] != value:
            value = parents[value]
        return value
    for field in ('document_chembl_id', 'target_chembl_id'):
        anchor = {}
        for row in assays:
            value = row.get(field)
            if value:
                if value in anchor:
                    parents[find(row['assay_chembl_id'])] = find(anchor[value])
                else:
                    anchor[value] = row['assay_chembl_id']
    components = Counter(find(row['assay_chembl_id']) for row in assays)
    summary = {
        'schema_version': 1, 'source_release': 'ChEMBL_37',
        'status': 'PASS_STRUCTURAL_METADATA_ONLY', 'sample_type': 'DETERMINISTIC_CONVENIENCE',
        'assays': len(assays), 'assay_types': dict(Counter(row['assay_type'] for row in assays)),
        'document_metadata': len(documents), 'targets': len(targets),
        'target_components': len(component_ids), 'protein_classification_ids': len(class_ids),
        'lineage_records_counted': lineage_record_count,
        'component_field_names': sorted(component_keys), 'classification_field_names': sorted(class_keys),
        'missing_assay_fields': missing,
        'doi_present': sum(bool(row.get('doi')) for row in documents),
        'document_year_range': [min(row['year'] for row in documents if row.get('year')), max(row['year'] for row in documents if row.get('year'))],
        'document_titles_with_possible_outcome_or_condition_pattern': document_title_flags,
        'descriptions_quarantined': sum(row['description_disposition'].startswith('QUARANTINE') for row in dispositions),
        'description_endpoint_mentions': dict(Counter(name for row in dispositions for name in row['endpoint_mentions'])),
        'descriptions_without_endpoint_pattern': sum(not row['endpoint_mentions'] for row in dispositions),
        'document_or_target_connected_components': len(components),
        'component_sizes': sorted(components.values(), reverse=True),
        'verified_independent_biological_families': None,
        'observed_measurement_support': 'NOT_READ_NOT_ESTABLISHED',
        'natural_ambiguity_gold': 'NOT_ADJUDICATED',
        'text_screen_is_semantic_guarantee': False,
        'activity_endpoint_requests': 0, 'final_outcome_access': False,
        'method_gain': 'NOT_TESTED', 'independent_review': 'NOT_RUN'
    }
    save(PRIVATE / 'metadata-summary-v1.json', summary)
    save(PRIVATE / 'metadata-dispositions-v1.json', {'records': dispositions})
    save(PRIVATE / 'classification-ids-v1.json', {'classifications': classifications})
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    receipt = PRIVATE / 'audit-resource-v1.json'
    if receipt.exists():
        raise RuntimeError('Audit receipt already exists')
    guard = MetadataGuard(receipt)
    try:
        audit()
    except Exception as exc:
        guard.finish('FAIL', error_type=type(exc).__name__)
        raise
    else:
        guard.finish('PASS_STRUCTURAL_METADATA_ONLY', charged_to='300-second utility reservation')
