"""Reconcile and seal the bounded R0 metadata evidence, without new requests."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from r0_chembl_audit_v1 import source_payload
from r0_chembl_metadata_v1 import MetadataGuard, PRIVATE, ROOT, save

def restore_source_snapshots():
    folder = PRIVATE / 'code'
    base = (folder / '6f2147a95f5384fb9605cbc4f619129ebdb2fb23951a31c4a111279b759d45a8.py').read_text()
    # These are byte reconstructions of observed revisions, accepted only when
    # their SHA-256 matches an actual resource receipt. No result is reconstructed.
    first = '\n'.join(line for line in base.split('\n') if not any("'" + key + "':" in line for key in
                    ('chembl35-license','chembl35-readme','chembl35-checksums','chembl35-schema','chembl35-attribution')))
    first = first.replace("expected = 'text/html' if args.source.endswith('directory') else 'text/plain'\n            if expected not in record['content_type']:",
                          "if 'text/html' not in record['content_type']:")
    first = first.replace('STOP_UNEXPECTED_METADATA_CONTENT_TYPE', 'STOP_NOT_METADATA_LISTING')
    typed = base.replace("if expected not in record['content_type']:",
                         "allowed_type = (expected in record['content_type'] or\n                            (not args.source.endswith('directory') and\n                             record['content_type'] in ('', 'application/octet-stream')))\n            if not allowed_type:")
    typed = typed.replace("        raw_path = PRIVATE / f'{stem}.html'", "        text = body.decode('utf-8')\n        if '\\x00' in text:\n            raise RuntimeError('STOP_NON_TEXT_METADATA')\n        raw_path = PRIVATE / f'{stem}.html'")
    status = typed.replace("    'chembl35-attribution':", "    'chembl-current-status': 'https://www.ebi.ac.uk/chembl/api/data/status.json',\n    'chembl35-attribution':")
    # Preserve original key order in that revision.
    status = status.replace("    'chembl-current-status': 'https://www.ebi.ac.uk/chembl/api/data/status.json',\n", '')
    status = status.replace("\n}\n", "\n    'chembl-current-status': 'https://www.ebi.ac.uk/chembl/api/data/status.json',\n}\n", 1)
    status = status.replace("expected = 'text/html' if args.source.endswith('directory') else 'text/plain'", "expected = ('application/json' if args.source.endswith('status') else\n                        'text/html' if args.source.endswith('directory') else 'text/plain')")
    status = status.replace("        print(json.dumps({'record': record, 'links': re.findall(r'href=\"([^\"]+)\"', listing)}, indent=2))", "        output = {'record': record, 'links': re.findall(r'href=\"([^\"]+)\"', listing)}\n        if args.source.endswith('status'):\n            output['service_status'] = json.loads(text)\n        print(json.dumps(output, indent=2))")
    observed = {json.loads(path.read_text())['worker_sha256'] for path in PRIVATE.glob('*-resource.json')}
    restored = []
    for candidate in (first, typed, status):
        data = candidate.encode()
        digest = hashlib.sha256(data).hexdigest()
        if digest in observed and not (folder / (digest + '.py')).exists():
            (folder / (digest + '.py')).write_bytes(data)
            restored.append(digest)
    missing = sorted(digest for digest in observed if not (folder / (digest + '.py')).exists())
    return {'restored_exact_hash_snapshots': restored, 'missing_executed_fetch_source_snapshots': missing}

def main():
    guard = MetadataGuard(PRIVATE / 'finalize-resource-v1.json')
    reconstruction = restore_source_snapshots()
    summary = json.loads((PRIVATE / 'metadata-summary-v2.json').read_text())
    ledger = json.loads((PRIVATE / 'ledger.json').read_text())
    classes = {}
    for row in ledger['attempts']:
        if row['status'] == 'PASS_METADATA_LISTING' and (row['source'] == 'chembl37-selected-classifications' or row['source'].startswith('chembl37-class-parents-')):
            classes.update({entry['protein_class_id']: entry for entry in json.loads((ROOT / row['raw_path']).read_text())['protein_classifications']})
    assert all(row['parent_id'] is None or row['parent_id'] in classes for row in classes.values())
    assert source_payload('chembl-current-status') == source_payload('chembl37-status-final')
    levels = Counter(str(row['class_level']) for row in classes.values())
    lineage = summary['targets'] + summary['target_components'] + len(classes)
    assert lineage <= 100
    parser_tree = ast.parse((ROOT / 'tools/r0_chembl_audit_v1.py').read_text(encoding='utf-8'))
    literals = {}
    for node in ast.walk(parser_tree):
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name == 'endpoint_patterns':
                literals[name] = ast.literal_eval(node.value)
            elif name in ('quantitative', 'categorical_outcome'):
                literals[name] = ast.literal_eval(node.value.args[0])
    checks = {
        'endpoint_examples': all(re.search(pattern, example, re.I) for name, pattern in literals['endpoint_patterns'].items() for example in {'IC50':['IC50','IC_50'],'EC50':['EC50','EC-50'],'Ki':['Ki'],'KD':['Kd']}[name]),
        'quantitative_outcome_flag': bool(re.search(literals['quantitative'], 'Example IC50 = 12 nM', re.I)),
        'condition_also_flagged_conservatively': bool(re.search(literals['quantitative'], 'Binding with 3 nM tracer', re.I)),
        'plain_method_not_flagged': not re.search(literals['quantitative'], 'Binding assay', re.I),
        'categorical_outcome_flag': bool(re.search(literals['categorical_outcome'], 'Compound was inactive', re.I)),
        'source_stops_retained': ledger['stopped_sources'] == ['chembl35-license'],
        'zero_activity_endpoints': not any('/api/data/activity' in row['url'] for row in ledger['attempts']),
        'request_cap': len(ledger['attempts']) <= 32,
        'byte_cap': ledger['decoded_bytes'] <= 16 * 1024**2,
        'cpu_reservations_cap': ledger['worker_reserved_seconds'] + ledger['utility_charge_seconds'] <= 1800,
        'source_snapshot_coverage': not reconstruction['missing_executed_fetch_source_snapshots'],
    }
    summary.update({
        'audit_revision': 'v3', 'classification_ancestry_closed': True,
        'protein_classification_ids_initial': 18, 'classification_nodes_with_ancestors': len(classes),
        'lineage_records_counted': lineage, 'classification_parent_ids_not_in_sample': 0,
        'classification_level_counts': dict(levels),
        'classification_level_1_names': sorted(row['pref_name'] for row in classes.values() if row['class_level'] == 1),
        'http_attempts': len(ledger['attempts']),
        'successful_metadata_responses': sum(row['status'] == 'PASS_METADATA_LISTING' for row in ledger['attempts']),
        'decoded_bytes': ledger['decoded_bytes'],
        'conservative_cpu_charge_seconds': ledger['worker_reserved_seconds'] + ledger['utility_charge_seconds'],
        'source_reconstruction': reconstruction,
        'offline_guard_checks': checks,
        'scientific_phase_decision': 'REVISE_BEFORE_NEXT_PHASE',
        'certified_independent_family_count': None,
        'whole_field_null_is_data_defect': False,
        'feasibility_exposure': 'All 50 assay/document identities are metadata-exposed; no final-role reassignment',
    })
    save(PRIVATE / 'metadata-summary-v3.json', summary)
    save(PRIVATE / 'classification-review-v3.json', {'classifications': list(classes.values()), 'certified_family_count': None})
    guard.finish('PASS_FINAL_RECONCILIATION' if all(checks.values()) else 'FAIL_SOURCE_SNAPSHOT_COVERAGE',
                 charged_to='300-second utility reservation',
                 audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    if (PRIVATE / 'finalize-resource-v1.json').exists():
        raise RuntimeError('Finalization receipt already exists')
    main()
