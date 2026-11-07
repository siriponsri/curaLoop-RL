"""Verify DOI/protocol bridges and missing-group semantics before real use."""
import json,sys
from r0dq_core_v1 import LocalGuard,ROOT,PRIVATE,save,archive_code
sys.path.insert(0,str(ROOT))
from research.taskfirst_dq_v1.selection import source_components


def main():
    rows=[{'family_id':'F1','doc_id':1,'doi':'https://doi.org/10.fixture/ABC','assay_group':None},
          {'family_id':'F2','doc_id':2,'doi':'10.fixture/abc','assay_group':77},
          {'family_id':'F3','doc_id':3,'doi':'10.fixture/def','assay_group':77}]
    mapping,components=source_components(rows,{'F1'})
    assert len(components)==1 and mapping['F3']['role']=='development'
    separate=[{'family_id':'F4','doc_id':4,'assay_group':0},{'family_id':'F5','doc_id':5,'assay_group':None}]
    assert len(source_components(separate,set())[1])==2
    result={'status':'PASS_ADDITIONAL_SOURCE_LINEAGE_FIXTURES','checks':{
        'normalized_doi_merges_distinct_document_ids':True,'assay_group_links_protocol_lineage':True,
        'forced_exposure_propagates_transitively':True,'missing_zero_assay_groups_do_not_bridge':True},
        'passed':4,'real_dataset_validated':False}
    save(PRIVATE/'selection-fixtures-v2.json',result)
    archive_code(ROOT/'research/taskfirst_dq_v1/selection.py');archive_code(ROOT/'tools/r0dq_projection_v1.py')
    print(json.dumps(result))


if __name__=='__main__':
    guard=LocalGuard('selection-fixtures-v2',cpu_seconds=30,stage='frame',memory_mib=256)
    try:main()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
