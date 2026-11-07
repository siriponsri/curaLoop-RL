"""Read-only representation check after an empty metadata-only frame."""
import json
from r0dq_core_v1 import PRIVATE,REMOTE,save
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard

if __name__=='__main__':
    guard=TransportGuard('frame-representation-diagnosis-v1',cpu_seconds=30,wall=60,memory_mib=256)
    try:
        code=r'''
import os,sys,resource,json,sqlite3
from pathlib import Path
os.nice(19);os.sched_setaffinity(0,{0});resource.setrlimit(resource.RLIMIT_CPU,(10,11));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
root=Path(__ROOT__);sys.path.insert(0,str(root/'jobs/frame-v1'))
from r0dq_projection_v1 import protect_metadata_connection
db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True);protect_metadata_connection(db)
rows=[{'target_type':r[0],'catalog_targets':r[1]} for r in db.execute('SELECT target_type,COUNT(*) FROM target_dictionary GROUP BY target_type')]
frame=json.loads((root/'jobs/frame-v1/frame-frozen.json').read_text())
print(json.dumps({'target_type_catalog':rows,'prior_frame_attrition':frame['attrition'],'numeric_source_columns_read':False}))
'''.replace('__ROOT__',repr(REMOTE))
        result=ssh(code);save(PRIVATE/'frame-representation-diagnosis-v1.json',result);print(json.dumps(result))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
