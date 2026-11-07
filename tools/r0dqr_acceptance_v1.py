"""Real returned-artifact invariants plus synthetic support boundary tests."""
import ast,collections,hashlib,json,sys
from r0dqr_core_v1 import ROOT,PRIVATE,PUBLIC,LocalGuard,save,sha,ARCHIVE_SHA,DB_SHA
sys.path.insert(0,str(ROOT))
from research.taskfirst_dqr_v1.selection import auxiliary_choice,panel,known_family_map

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    files=PRIVATE/'remote-return/files';j=files/'jobs';checks=[]
    complete=load(PUBLIC/'complete-return-verified-v1.json');assert complete['all_regular_files_completely_hashed_locally'];checks.append('full_return_stream_hash')
    manifest=load(PRIVATE/'remote-return/export-terminal/manifest.json');pins={r['path']:r for r in manifest['files']}
    assert pins['source/chembl_37_sqlite.tar.gz']['sha256']==ARCHIVE_SHA and pins['source/chembl_37_sqlite.tar.gz']['bytes']==5764252857
    assert pins['source/chembl_37.db']['sha256']==DB_SHA and pins['source/chembl_37.db']['bytes']==30480314368
    checks.append('returned_source_bytes_match_original_archive_and_database_pins')
    for pin in load(PRIVATE/'inputs/old-ledger-pins-and-stops-v1.json')['records']:assert sha(ROOT/pin['path'])==pin['sha256']
    for name in ['family-registry-v3.json','protected-identities.json','exposure-register-v1.json','additional-exposure-v1.json','r0dq-carried-exposure-v1.json']:
        assert (files/'inputs'/name).read_bytes()==(PRIVATE/'inputs'/name).read_bytes()
    checks.append('inherited_identity_roles_and_old_ledgers_unchanged')
    inventory=load(j/'inventory-v1/taxonomy-inventory.json');frame=load(j/'nominal-v1/frame-frozen.json');topology=load(j/'nominal-v1/topology-outcome-free.json')
    cases=load(j/'nominal-v1/candidates-frozen.json');dispositions=load(j/'nominal-v1/identity-dispositions.json')['records']
    assert len(inventory['targets'])==11055 and len(frame['targets'])<=200 and len(frame['assays'])<=4000
    assert len(topology['rows'])<=2000000 and len(dispositions)<=100000 and len(cases['candidates'])<=120
    checks.append('bounded_full_inventory_and_frozen_frame')
    assert len(topology['assay_states'])==len(frame['assays']) and all(s['status']=='COMPLETE' for s in topology['assay_states'])
    counts=collections.Counter(r['assay_id'] for r in topology['rows'])
    assert all(s['rows']==counts[s['assay_id']] for s in topology['assay_states']);checks.append('complete_graphs_no_prefix_support')
    allowed={'activity_id','assay_id','molregno','doc_id','standard_type','standard_relation','standard_units'}
    assert all(set(r)==allowed for r in topology['rows']);checks.append('topology_has_only_authorized_outcome_free_fields')
    protection=load(files/'inputs/protected-identities.json');protected={hashlib.sha256(s.encode()).hexdigest() for s in protection['canonical_smiles']}
    admitted={r['molregno']:r['canonical_sha256'] for r in dispositions if r['status']=='ADMITTED_IDENTITY'}
    assert not protected&set(admitted.values());checks.append('protected_canonical_hashes_absent_from_admitted_identity_map')
    amap={a['assay_id']:a for a in frame['assays']};fmap,roles,_=known_family_map(load(files/'inputs/family-registry-v3.json'))
    byaid=collections.defaultdict(set)
    for r in topology['rows']:
        if r['molregno'] in admitted and r['standard_relation']=='=' and r['standard_units'] in ['M','mM','uM','μM','nM','pM','fM']:
            byaid[(r['assay_id'],r['standard_type'])].add(admitted[r['molregno']])
    for c in cases['candidates']:
        chosen=set(c['panel_canonical_hashes']);ref=c['reference'];aux=c['auxiliary']
        assert len(chosen)==128 and ref['type'] in {'Ki','Kd'} and c['role']=='development'
        assert c['family_id'] is None and c['final_status']=='QUARANTINE_UNCERTIFIED_BIOLOGICAL_MAPPING'
        refs=set().union(*(byaid[(aid,ref['type'])] for aid in ref['assay_ids']));assert chosen<=refs
        overlaps=[]
        for u in aux:
            assert not set(ref['assay_ids'])&set(u['assay_ids'])
            values=set().union(*(byaid[(aid,u['type'])] for aid in u['assay_ids']));assert len(chosen&values)>=32
            assert len(chosen&values)==c['panel_shared_per_auxiliary'][u['unit_id']];overlaps.append(values)
        assert len(chosen&set().union(*overlaps))==c['panel_shared_union']>=64 and not chosen&protected
        assert c['numerical_support']=='NOT_QUERIED';assert c['procedure_reference_gold']=='NOT_ESTABLISHED'
    checks.append('real_nominal_panels_recomputed_from_id_topology_without_values')
    pools=load(j/'nominal-v1/pooling-diagnostics.json');assert pools['accepted_source_verified_pools']==0
    assert all(not u['eligible_pool'] for u in pools['pending_signature_pools']);checks.append('unknown_procedures_never_accepted_as_pools')
    for target in frame['targets']:
        assert target['family_id']==fmap.get(target['accession'])
        assert target['inherited_role']==roles.get(target['family_id'])
        if target['family_id'] is None:assert target['final_status']=='QUARANTINE_UNCERTIFIED_BIOLOGICAL_MAPPING' and target['role']!='final'
    checks.append('exact_inherited_crosswalk_retained_unknown_final_mapping_quarantined')
    packet=load(j/'context-v1/development-packet.json');assert len(packet['documents'])<=12 and all(c['role']=='development' for c in packet['bundles'])
    assert load(PRIVATE/'methods-source-frame-v1.json')['candidate_freeze_sha256']==sha(j/'nominal-v1/candidates-frozen.json')
    checks.append('development_source_intent_frozen_before_interpretation')
    ref=set(map(str,range(128)));a=set(map(str,range(64)));b=set(map(str,range(64,96)))
    assert panel(ref,{'a':a}) and not panel(set(map(str,range(127))),{'a':a})
    assert panel(ref,{'a':a,'b':b}) and not auxiliary_choice(ref,{'a':set(map(str,range(63)))})
    checks.append('synthetic_128_64_32_boundaries')
    for path in list((ROOT/'tools').glob('r0dqr*.py'))+list((ROOT/'research/taskfirst_dqr_v1').glob('*.py')):ast.parse(path.read_text(encoding='utf-8'))
    checks.append('new_module_syntax')
    for pin in load(PRIVATE/'small-return-nominal-v1.json')['files']:assert sha(files/pin['path'])==pin['sha256']
    checks.append('ongoing_review_bytes_match_complete_return')
    result={'status':'PASS_REAL_ARTIFACT_AND_SYNTHETIC_BOUNDARY_CHECKS','checks':checks,'check_count':len(checks),
        'source_db_or_activity_value_queries':0,'independent_biology_or_reference_validation':False,
        'runtime_app_suite':'NOT_RUN_NO_PRODUCT_RUNTIME_CHANGE'}
    save(PUBLIC/'acceptance-v1.json',result);print(json.dumps(result))
if __name__=='__main__':
    guard=LocalGuard('returned-artifact-acceptance-v1',cpu_seconds=120,wall=180,stage='metadata',memory_mib=512)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
