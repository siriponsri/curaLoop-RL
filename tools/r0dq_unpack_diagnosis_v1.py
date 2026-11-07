"""Read-only offline dependency diagnosis; no source SQLite opened."""
import json
from r0dq_core_v1 import PRIVATE,REMOTE,save
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard

if __name__=='__main__':
    guard=TransportGuard('unpack-diagnosis-v1',cpu_seconds=30,wall=60,memory_mib=256)
    try:
        code=r'''
import os,sys,resource,json,importlib.util
from pathlib import Path
os.nice(19);os.sched_setaffinity(0,{0});resource.setrlimit(resource.RLIMIT_CPU,(15,16));resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
root=Path(__ROOT__);vendor=root/'vendor';sys.path.insert(0,str(vendor))
data={'python':sys.version,'vendor_exists':vendor.is_dir(),'rdkit_init_exists':(vendor/'rdkit/__init__.py').exists(),
'numpy_init_exists':(vendor/'numpy/__init__.py').exists(),'top_level_entries':[p.name for p in vendor.iterdir()] if vendor.exists() else [],'sqlite_opened':False}
try:
 from rdkit import Chem,rdBase
 data.update(import_status='PASS',rdkit=rdBase.rdkitVersion)
except Exception as exc:
 data.update(import_status='FAIL',error_type=type(exc).__name__,missing_module=getattr(exc,'name',None),error_message=str(exc)[:300])
print(json.dumps(data))
'''.replace('__ROOT__',repr(REMOTE))
        result=ssh(code);save(PRIVATE/'unpack-diagnosis-v1.json',result);print(json.dumps(result))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
