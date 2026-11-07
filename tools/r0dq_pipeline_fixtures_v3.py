"""Exercise the real stage code on a small fictional SQLite release."""
import contextlib,io,json,runpy,sqlite3,sys
from pathlib import Path
from r0dq_core_v1 import LocalGuard,ROOT,PRIVATE,save,archive_code
sys.path.insert(0,str(ROOT))
from research.taskfirst_dq_v1.rules import RULES

def main():
    sys.path.insert(0,str(ROOT/'.venv/Lib/site-packages'))
    from rdkit import rdBase
    assert rdBase.rdkitVersion=='2026.09.1'
    base=PRIVATE/'fixtures/pipeline-v3';(base/'source').mkdir(parents=True)
    (base/'inputs').mkdir();(base/'jobs/unpack-v1').mkdir(parents=True)
    save(base/'jobs/unpack-v1/result.json',{'status':'PASS_VERIFIED_EXTRACTION_AND_SCHEMA'})
    reg={'assays':[{'uniprot_accession':'FIXTURE_ACCESSION','family_id':'FICTIONAL_FAMILY','role':'development'}]}
    save(base/'inputs/family-registry-v3.json',reg)
    save(base/'inputs/protected-identities.json',{'family_ids':[],'uniprot_accessions':[],'assay_ids':[],'canonical_smiles':['C']})
    save(base/'inputs/exposure-register-v1.json',{'old_r0_assay_ids':[],'old_r0_target_ids':[],'old_r0_document_ids':[],
        'old_r0r_molecule_ids':[],'planning_exposed_ids':[]})
    save(base/'inputs/additional-exposure-v1.json',{'canonical_smiles':['CCC']})
    db=sqlite3.connect(base/'source/chembl_37.db')
    db.executescript('''
    CREATE TABLE target_dictionary(tid INTEGER,chembl_id TEXT,target_type TEXT,organism TEXT,tax_id INTEGER);
    CREATE TABLE target_components(tid INTEGER,component_id INTEGER);
    CREATE TABLE component_sequences(component_id INTEGER,accession TEXT,tax_id INTEGER,organism TEXT);
    CREATE TABLE docs(doc_id INTEGER,chembl_id TEXT,doi TEXT,pubmed_id TEXT,year INTEGER);
    CREATE TABLE assays(assay_id INTEGER,chembl_id TEXT,tid INTEGER,doc_id INTEGER,assay_type TEXT,assay_test_type TEXT,
      assay_category TEXT,assay_organism TEXT,assay_tax_id INTEGER,assay_strain TEXT,assay_tissue TEXT,assay_cell_type TEXT,
      assay_subcellular_fraction TEXT,confidence_score INTEGER,relationship_type TEXT,bao_format TEXT,assay_group INTEGER,
      variant_id INTEGER,cell_id INTEGER,tissue_id INTEGER,src_id INTEGER);
    CREATE TABLE activities(activity_id INTEGER PRIMARY KEY,assay_id INTEGER,molregno INTEGER,standard_type TEXT,
      standard_units TEXT,standard_relation TEXT,doc_id INTEGER,standard_value REAL);
    CREATE TABLE molecule_dictionary(molregno INTEGER,chembl_id TEXT);
    CREATE TABLE compound_structures(molregno INTEGER,canonical_smiles TEXT);
    ''')
    db.execute("INSERT INTO target_dictionary VALUES(1,'FICTIONAL_TARGET','SINGLE_PROTEIN','Fictional organism',999)")
    db.execute('INSERT INTO target_components VALUES(1,1)')
    db.execute("INSERT INTO component_sequences VALUES(1,'FIXTURE_ACCESSION',999,'Fictional organism')")
    for aid in [1,2,3]:
        db.execute('INSERT INTO docs VALUES(?,?,?,?,?)',(aid,'FICTIONAL_DOC_'+str(aid),'10.fixture/paper'+str(aid),'0',2000))
        row=[aid,'FICTIONAL_ASSAY_'+str(aid),1,aid,'B',None,None,'Fictional organism',999,None,None,None,None,9,'D',None,None,None,None,None,1]
        db.execute('INSERT INTO assays VALUES('+','.join('?' for _ in row)+')',row)
    for mol in range(1,132):
        db.execute('INSERT INTO molecule_dictionary VALUES(?,?)',(mol,'FICTIONAL_MOL_'+str(mol)))
        db.execute('INSERT INTO compound_structures VALUES(?,?)',(mol,'C'*mol))
        for aid in [1,2,3]:
            # Mol1 is protected. Mol2 is missing, never an inactivity label.
            db.execute('INSERT INTO activities VALUES(?,?,?,?,?,?,?,?)',(aid*1000+mol,aid,mol,'Ki','nM','=',aid,None if mol==2 else 1.0))
    db.commit();db.close()
    frame=base/'jobs/frame-v1';frame.mkdir();save(frame/'frame-rules-frozen.json',RULES)
    support=base/'jobs/support-v1';support.mkdir()
    previous=sys.argv[:]
    try:
        for filename,job in [('r0dq_frame_worker_v1.py',frame),('r0dq_support_worker_v1.py',support)]:
            sys.argv=[str(ROOT/'tools'/filename),str(job)]
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                runpy.run_path(str(ROOT/'tools'/filename),run_name='__main__')
            archive_code(ROOT/'tools'/filename)
    finally:sys.argv=previous
    result=json.loads((support/'result.json').read_text())
    allow=json.loads((support/'numeric-query-allowlist.json').read_text())['activity_ids']
    assert result['finite_panel_candidates']==3 and result['reserved_bundles']==2
    assert result['reserved_group_roles']=={'development':1}
    assert result['known_exposed_canonical_identity_count']==1
    assert all(aid*1000+1 not in allow for aid in [1,2,3])
    cases=json.loads((support/'cohort-support-frozen.json').read_text())['reserved']
    assert all(c['panel_compounds']==128 and c['panel_shared_union']>=64 and min(c['panel_shared_per_auxiliary'].values())>=32 for c in cases)
    assert all(c['reference_construct']=='PENDING_SOURCE_REVIEW' for c in cases)
    # Synthetic magnitudes never enter any returned support object.
    assert 'standard_value' not in (support/'restricted-support-booleans.json').read_text()
    save(PRIVATE/'pipeline-fixtures-v3.json',{'status':'PASS_SYNTHETIC_STAGE_INTEGRATION','checks':7,
        'scope':['actual metadata-role SQL','frame-before-topology','candidate-before-values','protected molecule excluded before value query',
                 'missing support distinct from inactivity','128/64/32 after pruning','no fabricated reference/context certification'],
        'real_dataset_validated':False,'rdkit':rdBase.rdkitVersion})
    print(json.dumps({'status':'PASS_SYNTHETIC_STAGE_INTEGRATION','checks':7,'real_dataset_validated':False}))

if __name__=='__main__':
    guard=LocalGuard('pipeline-fixtures-v3',cpu_seconds=120,wall=240,memory_mib=512)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
