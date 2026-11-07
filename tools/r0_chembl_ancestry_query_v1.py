"""Freeze the next bounded parent-classification query from observed parents."""
import hashlib
import json
from pathlib import Path
import urllib.parse

root = Path(__file__).resolve().parents[1]
private = root / '.local/r0-chembl-20261107-v1'
ledger = json.loads((private / 'ledger.json').read_text())
classes = {}
for item in ledger['attempts']:
    if (item['source'] == 'chembl37-selected-classifications' or item['source'].startswith('chembl37-class-parents-')) and item['status'] == 'PASS_METADATA_LISTING':
        payload = json.loads((root / item['raw_path']).read_text())
        classes.update({row['protein_class_id']: row for row in payload['protein_classifications']})
missing = sorted({row['parent_id'] for row in classes.values() if row['parent_id'] is not None and row['parent_id'] not in classes})
if not missing:
    print(json.dumps({'status': 'ANCESTRY_COMPLETE', 'classification_nodes': len(classes)}))
    raise SystemExit(0)
assert 44 + len(classes) + len(missing) <= 100
registry = private / 'allowed-followup-v1.json'
before = registry.read_bytes()
(private / ('allowed-followup-' + hashlib.sha256(before).hexdigest() + '.json')).write_bytes(before)
allowed = json.loads(before)
source = 'chembl37-class-parents-' + str(len(classes))
assert source not in allowed
parameters = {'protein_class_id__in': ','.join(map(str, missing)),
              'only': 'protein_class_id,parent_id,pref_name,short_name,class_level',
              'limit': len(missing), 'order_by': 'protein_class_id'}
allowed[source] = 'https://www.ebi.ac.uk/chembl/api/data/protein_classification.json?' + urllib.parse.urlencode(parameters)
registry.write_text(json.dumps(allowed, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'FROZEN_PARENT_QUERY', 'source': source, 'requested_parents': len(missing),
                  'maximum_lineage_records_after': 44 + len(classes) + len(missing)}))
