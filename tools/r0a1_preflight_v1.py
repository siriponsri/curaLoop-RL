"""Pin old bytes and freeze complete permitted metadata before PDF identifiers."""
import hashlib
from r0a1_core_v1 import Guard,ROOT,PRIVATE,save,load,read_input,archive_code
from r0a1_context_mask_v1 import description_features,safety_checks


def run():
    old=ROOT/'docs/evidence/r0r-chembl-20261107-v1'
    pins=[]
    for index_path in [ROOT/'docs/evidence/r0-chembl-20261107-v1/private-artifact-index-v1.json',old/'private-artifact-index-v4.json']:
        index=load(index_path)
        for record in index['artifacts']:
            assert hashlib.sha256(read_input(ROOT/record['path'])).hexdigest()==record['sha256']
        pins.append({'path':str(index_path.relative_to(ROOT)),'sha256':hashlib.sha256(index_path.read_bytes()).hexdigest(),'files_verified':len(index['artifacts'])})
    selection=load(old/'selection-freeze-v1.json')['cases']
    accepted=load(old/'projected-readout-metadata-v1.json')['records']
    assert len(selection)==12 and len(accepted)==86
    permitted={'activity_id','assay_chembl_id','document_chembl_id','molecule_chembl_id','standard_type','standard_units','type','units'}
    assert all(set(r)==permitted for r in accepted)
    assay_path=ROOT/'.local/r0-chembl-20261107-v1/014-chembl37-selected-assays.html'
    assays=load(assay_path)['assays']
    by_id={r['assay_chembl_id']:r for r in assays}
    projection=[]
    for case in selection:
        row=by_id[case['assay_chembl_id']]
        safe={key:row[key] for key in ['assay_chembl_id','document_chembl_id','target_chembl_id','assay_type','bao_format','assay_organism','assay_tissue','assay_cell_type','assay_subcellular_fraction']}
        for key in ['assay_organism','assay_tissue','assay_cell_type','assay_subcellular_fraction']:
            if safe[key] is not None:
                features=description_features(str(safe[key]))
                # Structured labels are short; no complete arbitrary field is
                # emitted if it carries a numeric/outcome clause.
                safe[key]=str(safe[key]) if features['quarantined_clauses']==0 and len(str(safe[key]))<120 else 'QUARANTINE_FIELD'
        safe['description_features']=description_features(row.get('description'))
        safe['accepted_records']=sum(r['assay_chembl_id']==case['assay_chembl_id'] for r in accepted)
        safe['review']='AUTHOR_DRAFT_NOT_GOLD'
        projection.append(safe)
    sources=load(old/'owner-source-manifest-v1.json')['records']
    mains=[r for r in sources if r['source_part']=='main']
    assert len(mains)==3
    for row in mains:
        assert hashlib.sha256(read_input(ROOT/row['source_path'])).hexdigest()==row['source_sha256']
    save(PRIVATE/'preflight-pins-v1.json',{'old_indexes':pins,'three_main_sources':mains,
        'assay_metadata_sha256':hashlib.sha256(assay_path.read_bytes()).hexdigest(),
        'safety_checks':safety_checks(),'source_roles_unchanged':True,'new_http_requests':0})
    save(PRIVATE/'metadata-before-paper-identifiers-v1.json',{'cases':projection,
        'freeze_order':'Before R0-A1 identifier-preserving PDF extraction; after prior broad masked-method exposure',
        'analysis_design':'EXPLORATORY_FEASIBILITY_NOT_PREREGISTERED_COMPARISON'})
    archive_code(ROOT/'tools/r0a1_context_mask_v1.py')
    archive_code(ROOT/'tools/r0r_owner_methods_mask_v2.py')
    print('PASS: prior R0/R0-R hashes, three source hashes and six masking fixtures; twelve metadata cases frozen')


if __name__=='__main__':
    guard=Guard('preflight-v1',cpu_seconds=60)
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
