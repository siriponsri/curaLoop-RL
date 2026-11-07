"""Freeze outcome-blind metadata identities and bounded follow-up queries."""
import hashlib
import json
from pathlib import Path
import urllib.parse

root = Path(__file__).resolve().parents[1]
private = root / '.local/r0-chembl-20261107-v1'
plan_id = 'phase-r0-chembl-readiness-20261107-v1'
records = []
for ordinal, category in ((12, 'B'), (13, 'F')):
    payload = json.loads((private / f'{ordinal:03d}-chembl37-{category}-ids.html').read_text())
    rows = payload['assays']
    assert len(rows) == 25
    assert all(row['assay_type'] == category and row['confidence_score'] == 9 and row['src_id'] == 1 for row in rows)
    assert all(set(row) == {'assay_chembl_id','document_chembl_id','target_chembl_id','assay_type','confidence_score','src_id'} for row in rows)
    records.extend(rows)
ids = sorted(row['assay_chembl_id'] for row in records)
assert len(set(ids)) == 50
documents = sorted({row['document_chembl_id'] for row in records if row['document_chembl_id']},
                   key=lambda value: hashlib.sha256((plan_id + value).encode()).hexdigest())[:20]
targets = sorted({row['target_chembl_id'] for row in records if row['target_chembl_id']})
assert len(targets) <= 50
selection = {'plan_id': plan_id, 'release': 'ChEMBL_37',
             'sample_type': 'deterministic_convenience', 'assay_ids': ids,
             'records': records, 'document_ids': documents, 'target_ids': targets,
             'outcome_filter_used': False}
selection_path = private / 'selection-v1.json'
if selection_path.exists():
    raise RuntimeError('Freeze already exists')
selection_path.write_text(json.dumps(selection, indent=2) + '\n', encoding='utf-8')

def query(resource, fields, key, values, limit):
    parameters = {'only': ','.join(fields), key + '__in': ','.join(values),
                  'limit': limit, 'order_by': key}
    return 'https://www.ebi.ac.uk/chembl/api/data/' + resource + '.json?' + urllib.parse.urlencode(parameters)

assay_fields = ['assay_chembl_id','document_chembl_id','target_chembl_id','assay_type','confidence_score','src_id',
                'description','assay_organism','assay_tax_id','assay_cell_type','assay_tissue',
                'assay_subcellular_fraction','bao_format','relationship_type']
queries = {
    'chembl37-selected-assays': query('assay', assay_fields, 'assay_chembl_id', ids, 50),
    'chembl37-selected-documents': query('document', ['document_chembl_id','doi','title','year','src_id'], 'document_chembl_id', documents, 20),
    'chembl37-selected-targets': query('target', ['target_chembl_id','target_type','organism','tax_id','target_components'], 'target_chembl_id', targets, 50),
    'chembl37-status-after': 'https://www.ebi.ac.uk/chembl/api/data/status.json',
}
(private / 'allowed-followup-v1.json').write_text(json.dumps(queries, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status':'FROZEN_BEFORE_DESCRIPTIONS','assays':len(ids),
                  'documents':len(documents),'targets':len(targets),
                  'selection_sha256':hashlib.sha256(selection_path.read_bytes()).hexdigest()}, indent=2))
