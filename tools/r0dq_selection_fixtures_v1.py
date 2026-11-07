"""Constructed anti-degeneracy, dependency and role-leakage checks."""
import sys,json
from r0dq_core_v1 import LocalGuard,ROOT,PRIVATE,save,archive_code
sys.path.insert(0,str(ROOT))
from research.taskfirst_dq_v1.selection import auxiliary_choice,panel,source_components,molecule_role_owners


def main():
    ref={'fixture-m'+str(i) for i in range(200)}
    aux={'A':{'fixture-m'+str(i) for i in range(50)},'B':{'fixture-m'+str(i) for i in range(50,100)}}
    keys=auxiliary_choice(ref,aux);assert keys and len(keys)==2
    sample=panel(ref,{k:aux[k] for k in keys})
    assert len(sample)==128 and len(set(sample)&set.union(*aux.values()))>=64
    assert all(len(set(sample)&v)>=32 for v in aux.values())
    assert sample==panel(ref,{k:aux[k] for k in reversed(keys)})
    assert auxiliary_choice({'one'}, {'A':{'one'}}) is None
    assert panel(ref,{'A':set(list(ref)[:31])}) is None
    assays=[{'family_id':'F1','doc_id':10},{'family_id':'F2','doc_id':10},{'family_id':'F2','doc_id':20},{'family_id':'F3','doc_id':20}]
    mapping,components=source_components(assays,{'F1'})
    assert len(components)==1 and components[0]['role']=='development'
    assert mapping['F3']['forced_development_by_exposure']
    owners=molecule_role_owners({'A':{'shared','exposed'},'B':{'shared','exposed'}},{'A':'development','B':'final'},{'exposed'})
    assert owners['shared']=='final' and owners['exposed']=='development'
    result={'status':'PASS_CONSTRUCTED_SELECTION_FIXTURES','checks':{
        '128_64_32_shared_support_preserved':True,'deterministic_panel_without_values':True,
        'one_molecule_group_rejected':True,'insufficient_auxiliary_support_rejected':True,
        'document_family_transitive_merge':True,'exposure_forces_whole_component_development':True,
        'exact_molecule_role_priority_and_exposure':True},'passed':7,'real_dataset_validated':False}
    save(PRIVATE/'selection-fixtures-v1.json',result)
    for p in (ROOT/'research/taskfirst_dq_v1').glob('*.py'):archive_code(p)
    print(json.dumps(result))


if __name__=='__main__':
    guard=LocalGuard('selection-fixtures-v1',cpu_seconds=30,stage='frame',memory_mib=256)
    try:main()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
