"""Freeze identity and abstract-free source discovery after metadata projection."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import urllib.parse
from r0r_chembl_core_v1 import Guard, PRIVATE, ROOT, save

def run():
    book=json.loads((PRIVATE/'ledger.json').read_text())
    selection=json.loads((PRIVATE/'selection-freeze-v1.json').read_text())
    specs_path=PRIVATE/'request-registry.json'
    before=specs_path.read_bytes()
    save(PRIVATE/'request-registry-before-followups-v1.json',json.loads(before))
    specs=json.loads(before)
    rows=[]
    case_metadata={}
    for item in book['attempts']:
        if item['source'].startswith('projection-') and item['status']=='PASS':
            payload=json.loads((ROOT/item['output_path']).read_text())
            assert len(payload['activities'])<=20
            rows.extend(payload['activities'])
            case_metadata[item['source'].removeprefix('projection-')]=payload['activities']
    assert len(rows)<=240
    assert all(not any('value' in key or 'comment' in key for key in row) for row in rows)
    molecules=sorted({row['molecule_chembl_id'] for row in rows if row['molecule_chembl_id']})
    assert len(molecules)<=240
    parameters={'molecule_chembl_id__in':','.join(molecules),'only':'molecule_chembl_id,molecule_structures',
                'limit':len(molecules),'order_by':'molecule_chembl_id'}
    specs['molecule-identities']={'url':'https://www.ebi.ac.uk/chembl/api/data/molecule.json?'+urllib.parse.urlencode(parameters)}
    old=ROOT/'.local/r0-chembl-20261107-v1'
    docs=json.loads((old/'015-chembl37-selected-documents.html').read_text())['documents']
    selected_docs={row['document_chembl_id'] for row in selection['cases']}
    document_records=[row for row in docs if row['document_chembl_id'] in selected_docs]
    for doc in document_records:
        assert doc['doi']
        parameters={'query':'DOI:'+doc['doi'],'format':'json','resultType':'lite','pageSize':2}
        specs['paper-access-'+doc['document_chembl_id']]={'url':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(parameters)}
    save(specs_path,specs)
    questions=[]
    for case in selection['cases']:
        activities=case_metadata.get(case['assay_chembl_id'])
        pairs=sorted({(row['standard_type'] or 'UNKNOWN',row['standard_units'] or 'UNKNOWN') for row in activities or []})
        questions.append({'assay_id':case['assay_chembl_id'],'document_id':case['document_chembl_id'],
            'target_id':case['target_chembl_id'],'assay_type':case['assay_type'],
            'readout_metadata_available':activities is not None,'readout_pairs':[list(pair) for pair in pairs],
            'metadata_only_unqualified_pooling':'NOT_JUSTIFIED_WITHOUT_CONTEXT_COMPATIBILITY',
            'question':'Does a source-methods passage resolve assay-system/endpoint compatibility beyond the available typed metadata?',
            'requested_reference_fields':['assay_system','readout_interpretation','unit_compatibility','unresolved_conditions'],
            'molecular_decision_gain':'NOT_TESTED','reference_status':'PENDING_SOURCE_AND_OWNER_REVIEW'})
    save(PRIVATE/'pre_evidence_questions_v1.json',{'frozen_before_methods':True,'cases':questions})
    save(PRIVATE/'accepted-projection-index-v1.json',{'records':rows,'molecule_ids':molecules,
          'accepted_rows':len(rows),'failed_response_record_counts':'NOT_RETAINED; each request limited to20',
          'source_docs':document_records})
    print(json.dumps({'status':'FOLLOWUPS_AND_CASE_QUESTIONS_FROZEN','accepted_activity_metadata_rows':len(rows),
          'distinct_molecule_ids':len(molecules),'source_documents':len(document_records),
          'readout_pairs':dict(Counter(str((row['standard_type'],row['standard_units'])) for row in rows)),
          'numeric_activity_fields_requested':False},indent=2))

if __name__=='__main__':
    guard=Guard('followup-preparation-v1')
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS',charged_to='600-second utility reservation')
