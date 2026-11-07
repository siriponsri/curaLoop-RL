"""Collect frozen, outcome-free frame diagnostics without another SQL query."""
import json
from r0dq_core_v1 import PRIVATE,REMOTE,save
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard

if __name__=='__main__':
    guard=TransportGuard('frozen-frame-readout-v1',cpu_seconds=10,wall=60,memory_mib=256)
    try:
        code=r'''
import json
from pathlib import Path
root=Path(__ROOT__);frame=json.loads((root/'jobs/frame-v3/frame-frozen.json').read_text())
registry=json.loads((root/'inputs/family-registry-v3.json').read_text())
families={r['family_id']:r for r in registry['family_records']}
frozen=sorted({a['family_id'] for a in frame['assays']})
data={'attrition_counts_partial_release_catalog_diagnostics':frame['attrition'],
'catalog_candidate_targets':frame['catalog_candidate_target_count'],'selected_target_count':len(frame['targets']),
'selected_assay_count':len(frame['assays']),
'selected_targets':[{k:v for k,v in t.items() if k in ['tid','chembl_id','accession','reference_capable_assays','document_diversity','family_id']} for t in frame['targets']],
'family_grouping':[{'family_id':f,'broad_names_merged_count':len(families[f]['broad_names_merged']),
'prior_role':families[f]['role'],'biological_family_certification':'NOT_RUN'} for f in frozen],
'incidental_exposure_reconciliation':frame['incidental_exposure_reconciliation'],
'new_query_executed':False,'numeric_values_read':False}
print(json.dumps(data))
'''.replace('__ROOT__',repr(REMOTE))
        result=ssh(code);save(PRIVATE/'frame-readout-v1.json',result);print(json.dumps(result))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
