"""Create a reference review packet without publishing source-method passages."""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
from r0r_chembl_core_v1 import Guard,PRIVATE,ROOT,save

def run():
    book=json.loads((PRIVATE/'ledger.json').read_text())
    selection=json.loads((PRIVATE/'selection-freeze-v1.json').read_text())['cases']
    accepted=json.loads((PRIVATE/'accepted-projection-index-v1.json').read_text())
    identities=json.loads((PRIVATE/'molecule-dispositions-v1.json').read_text())['records']
    identity_gate={row['molecule_id']:row['status'] for row in identities}
    assert len(identities)==80 and all(row['status']=='NO_EXACT_PROTECTED_CANONICAL_MATCH' for row in identities)
    method_sources={}
    for item in book['attempts']:
        if item['source'].startswith('methods-') and item['status']=='PASS':
            data=json.loads((ROOT/item['output_path']).read_text())
            if data.get('status')=='MASKED_METHODS_AVAILABLE_NOT_ADJUDICATED':
                method_sources[item['source'].removeprefix('methods-')]=item
    doc_map={row['document_chembl_id']:row for row in accepted['source_docs']}
    rows_by_assay=defaultdict(list)
    for row in accepted['records']:
        assert not any('value' in key or 'comment' in key for key in row)
        assert identity_gate[row['molecule_chembl_id']]=='NO_EXACT_PROTECTED_CANONICAL_MATCH'
        rows_by_assay[row['assay_chembl_id']].append(row)
    records=[]
    for case in selection:
        rows=rows_by_assay.get(case['assay_chembl_id'],[])
        source=method_sources.get(case['document_chembl_id'])
        records.append({'assay_id':case['assay_chembl_id'],'document_id':case['document_chembl_id'],
            'target_id':case['target_chembl_id'],'assay_type':case['assay_type'],
            'accepted_projection_records':len(rows),'readout_pairs':sorted({str((row['standard_type'],row['standard_units'])) for row in rows}),
            'methods_available':bool(source),'reference_status':'PENDING_OWNER_REVIEW' if source else 'SOURCE_NOT_AVAILABLE_FOR_REVIEW',
            'metadata_only_pooling':'NOT_JUSTIFIED_WITHOUT_CONTEXT_COMPATIBILITY',
            'post_source_pooling_draft':'UNRESOLVED' if source else 'NOT_EVALUABLE',
            'molecular_decision_gain':'NOT_TESTED','numeric_activity_values_in_reference':False})
    incoming=ROOT/'research/raw_data/external-benchmarks/chembl-37-r0r/owner-methods'
    assert incoming.resolve().is_relative_to(ROOT.resolve())
    incoming.mkdir(parents=True,exist_ok=True)
    missing=[]
    for document_id,doc in doc_map.items():
        if document_id in method_sources:continue
        stopped=[row for row in book['attempts'] if row['source']=='methods-'+document_id and row['status']=='STOP']
        missing.append({'document_id':document_id,'doi':doc['doi'],'url':'https://doi.org/'+doc['doi'],
            'target_path':str(incoming/(document_id+'.pdf')),
            'status':'PUBLISHER_HTTP403' if stopped else 'NO_ADMISSIBLE_OPEN_METHODS_LOCATED',
            'bytes_per_file_max':4194304,'source_permission':'Owner must have legitimate access; no new purchases requested'})
    save(PRIVATE/'reference-candidates-v1.json',{'status':'PENDING_OWNER_REVIEW','cases':records,
        'independent_gold_established':False,'source_note_id':'S1','methods_available_documents':list(method_sources)})
    save(PRIVATE/'owner-download-requests-v1.json',{'records':missing,'full_results_must_not_enter_agent_context':True})
    save(PRIVATE/'reference-draft-analysis-v1.json',{
        'source_note_id':'S1','source_document':'CHEMBL1138492','source_doi':'10.1021/jm900186m',
        'source_url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC2708097/',
        'draft_assay_system':'biochemical ligand-competition binding',
        'shared_context_factor':'alternative lipid preparations mentioned in methods',
        'specific_lipid_regime_per_assay':'UNRESOLVED',
        'reference_adjudication':'PENDING_OWNER_REVIEW',
        'verified_molecular_recommendation_change':'NOT_ESTABLISHED',
        'parent_is_independent_reviewer':False})
    summary={'status':'REFERENCE_PACKET_PREPARED_SOURCE_LIMITED',
        'selected_assays':len(selection),'source_documents':len(doc_map),
        'accepted_projection_assays':len(rows_by_assay),'accepted_projection_records':len(accepted['records']),
        'projected_records_requested_max':len(selection)*20,
        'molecules_checked':len(identities),'protected_exact_matches':0,
        'methods_documents_available':len(method_sources),'cases_with_methods':sum(row['methods_available'] for row in records),
        'documents_needing_owner_source':len(missing),
        'readout_pair_counts':dict(Counter(str((row['standard_type'],row['standard_units'])) for row in accepted['records'])),
        'standard_unit_null_records':sum(row['standard_units'] is None for row in accepted['records']),
        'reference_gold_established':False,'verified_decision_changes':'NOT_ESTABLISHED',
        'final_outcomes_opened':False,'training_runs':0,'next_phase_released':False}
    save(PRIVATE/'review-preparation-summary-v1.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    guard=Guard('review-preparation-v1')
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS',charged_to='600-second utility reservation')
