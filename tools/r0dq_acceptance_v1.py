"""Real derived-artifact invariants after return; no SQLite/value access."""
import ast,hashlib,json
from r0dq_core_v1 import ROOT,PRIVATE,PUBLIC,LocalGuard,save

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    files=PRIVATE/'remote-return/files';support=files/'jobs/support-v1'
    framepath=files/'jobs/frame-v3/frame-frozen.json';frame=load(framepath)
    frozenpath=support/'candidates-frozen-before-values.json';frozen=load(frozenpath)
    allowed=load(support/'numeric-query-allowlist.json');ids=set(allowed['activity_ids'])
    assert allowed['candidate_freeze_sha256']==hashlib.sha256(frozenpath.read_bytes()).hexdigest()
    assert frozen['frame_sha256']==hashlib.sha256(framepath.read_bytes()).hexdigest()
    assert frozen['outcome_values_or_flags_used_for_selection'] is False and frozen['refill_after_validation'] is False
    protection=load(files/'inputs/protected-identities.json')
    assert len(protection['canonical_smiles'])==4723
    assert not {a['chembl_id'] for a in frame['assays']}&set(protection['assay_ids'])
    assert not {a['accession'] for a in frame['assays']}&set(protection['uniprot_accessions'])
    assert not {a['family_id'] for a in frame['assays']}&set(protection['family_ids'])
    dispositions=load(support/'identity-dispositions.json')['records']
    blocked={r['molregno'] for r in dispositions if r['status']!='ADMITTED_IDENTITY'}
    topology=load(support/'topology-outcome-free.json')
    assert not any(r['activity_id'] in ids and r['molregno'] in blocked for r in topology['rows'])
    assert all(set(r)=={'activity_id','assay_id','molregno','standard_type','standard_units','standard_relation','doc_id'} for r in topology['rows'])
    flags=load(support/'restricted-support-booleans.json')['records']
    assert {r['activity_id'] for r in flags}==ids and all(set(r)=={'activity_id','exact_positive_finite_support'} for r in flags)
    valid={r['activity_id'] for r in flags if r['exact_positive_finite_support']}
    cohort=load(support/'cohort-support-frozen.json');assert len(cohort['reserved'])==2
    for case in cohort['reserved']:
        panel=case['reference_panel'];assert len(panel)==len({r['canonical_sha256'] for r in panel})==128
        assert case['panel_shared_union']>=64 and all(n>=32 for n in case['panel_shared_per_auxiliary'].values())
        assert all(r['reference_activity_id'] in valid and set(r['auxiliary_activity_ids'].values())<=valid for r in panel)
        assert case['role']=='development' and case['reference'][1] in {'Ki','Kd'}
        assert case['context_distinctness']=='PENDING_SOURCE_REVIEW' and case['reference_construct']=='PENDING_SOURCE_REVIEW'
    assert cohort['reserved_group_roles']=={'development':1} and cohort['certified_biological_families']==0
    full=load(PUBLIC/'complete-return-verified-v1.json');assert full['status']=='PASS_FULL_PRIVATE_RETURN_AND_STREAMED_LOCAL_REREAD'
    assert load(PUBLIC/'fresh-absence-v1.json')['status']=='PASS_FRESH_SCOPED_ABSENCE'
    assert full['file_count']==1777 and full['total_bytes']==36533325290
    for path in list((ROOT/'tools').glob('r0dq_*.py'))+list((ROOT/'research/taskfirst_dq_v1').glob('*.py')):ast.parse(path.read_text(encoding='utf-8'))
    for name,job in [('frame_worker_v3','frame-v3'),('support_worker_v3','support-v1'),('context_worker_v3','context-v2')]:
        assert (ROOT/'tools'/('r0dq_'+name+'.py')).read_text()==(files/'jobs'/job/'payload.py').read_text()
    assert (ROOT/'tools/r0dq_context_projection_v1.py').read_text()==(files/'jobs/context-v2/r0dq_context_projection_v1.py').read_text()
    old=load(PRIVATE/'inherited-source-stops-v1.json')
    for pin in old['old_ledgers']:assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256']
    result={'status':'PASS_REAL_DERIVED_ARTIFACT_INVARIANTS','checks':12,
        'scope':['freeze hash chain','no value-driven refill','old assay/protein/family gates','blocked structures outside numeric allowlist',
        'outcome-free topology schema','boolean-only validity schema','128 unique panel identities','64/32 shared support',
        'selected IDs have finite support','no invented final/reference certification','full return and fresh absence',
        'executed scientific code matches current source and old ledgers unchanged'],
        'sqlite_or_activity_values_opened_by_this_check':False,'independent_scientific_review':False,
        'model_or_clinical_efficacy_tested':False}
    save(PRIVATE/'qualification-acceptance-v1.json',result);save(PUBLIC/'qualification-acceptance-v1.json',result);print(json.dumps(result))

if __name__=='__main__':
    guard=LocalGuard('derived-artifact-acceptance-v1',cpu_seconds=30,wall=120,memory_mib=256)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
