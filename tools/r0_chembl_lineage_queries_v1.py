"""Append source-ID-only lineage queries; preserve prior registry revisions."""
import hashlib
import json
from pathlib import Path
import urllib.parse

root = Path(__file__).resolve().parents[1]
private = root / '.local/r0-chembl-20261107-v1'
registry = private / 'allowed-followup-v1.json'
before = registry.read_bytes()
(private / ('allowed-followup-' + hashlib.sha256(before).hexdigest() + '.json')).write_bytes(before)
allowed = json.loads(before)
ledger = json.loads((private / 'ledger.json').read_text())
def payload(source):
    rows = [row for row in ledger['attempts'] if row['source'] == source and row['status'] == 'PASS_METADATA_LISTING']
    assert len(rows) == 1
    return json.loads((root / rows[0]['raw_path']).read_text())

components = sorted({component['component_id'] for row in payload('chembl37-selected-targets')['targets']
                     for component in row.get('target_components', [])})
assert len(components) <= 50
if 'chembl37-selected-components' not in allowed:
    parameters = {'component_id__in': ','.join(map(str, components)),
                  'only': 'component_id,protein_classifications', 'limit': 50,
                  'order_by': 'component_id'}
    allowed['chembl37-selected-components'] = 'https://www.ebi.ac.uk/chembl/api/data/target_component.json?' + urllib.parse.urlencode(parameters)
    print(json.dumps({'status': 'FROZEN_COMPONENT_QUERY', 'components': len(components)}))
else:
    rows = payload('chembl37-selected-components')['target_components']
    class_ids = sorted({entry['protein_classification_id'] for row in rows for entry in row.get('protein_classifications', [])})
    assert len(components) * 2 + len(class_ids) <= 100
    parameters = {'protein_class_id__in': ','.join(map(str, class_ids)),
                  'only': 'protein_class_id,parent_id,pref_name,short_name,class_level,l1,l2,l3,l4,l5,l6',
                  'limit': len(class_ids), 'order_by': 'protein_class_id'}
    allowed['chembl37-selected-classifications'] = 'https://www.ebi.ac.uk/chembl/api/data/protein_classification.json?' + urllib.parse.urlencode(parameters)
    print(json.dumps({'status': 'FROZEN_CLASSIFICATION_QUERY', 'classes': len(class_ids)}))
registry.write_text(json.dumps(allowed, indent=2) + '\n', encoding='utf-8')
