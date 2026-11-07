"""Read-only SQLite index/query-plan diagnosis; never execute the activity query."""
import json
from r0dq_core_v1 import PRIVATE,REMOTE,save
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard

if __name__=='__main__':
    guard=TransportGuard('metadata-query-plan-v1',cpu_seconds=30,wall=60,memory_mib=256)
    try:
        code=r'''
import os,sys,resource,json,sqlite3
from pathlib import Path
os.nice(19);os.sched_setaffinity(0,{0});resource.setrlimit(resource.RLIMIT_CPU,(10,11));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
root=Path(__ROOT__);sys.path.insert(0,str(root/'jobs/frame-v2'))
from r0dq_projection_v1 import protect_metadata_connection
db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True);protect_metadata_connection(db)
indexes={name:[list(r) for r in db.execute('PRAGMA index_list('+name+')')] for name in ['activities','assays','target_dictionary']}
query="EXPLAIN QUERY PLAN SELECT ac.assay_id,ac.standard_type,COUNT(DISTINCT ac.molregno) FROM activities ac JOIN assays a ON a.assay_id=ac.assay_id WHERE a.tid=? AND a.confidence_score=9 AND a.relationship_type='D' AND a.assay_type IN ('B','F') AND ac.standard_type IN ('Ki','Kd','IC50') AND ac.standard_relation='=' AND ac.standard_units IN ('M','mM','uM','μM','nM','pM','fM') GROUP BY ac.assay_id,ac.standard_type"
plan=[list(r) for r in db.execute(query,(1,))]
print(json.dumps({'indexes':indexes,'query_plan':plan,'activity_query_executed':False,'numeric_source_columns_read':False}))
'''.replace('__ROOT__',repr(REMOTE))
        result=ssh(code);save(PRIVATE/'metadata-query-plan-v1.json',result);print(json.dumps(result))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
