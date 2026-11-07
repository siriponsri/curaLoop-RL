"""Stop only the owned metadata job after a verified inefficient query plan."""
import json
from r0dq_core_v1 import PRIVATE,REMOTE,save
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard

if __name__=='__main__':
    guard=TransportGuard('stop-inefficient-frame-v2',cpu_seconds=30,wall=60,memory_mib=256)
    try:
        proof=json.loads((PRIVATE/'frame-v2-launch.json').read_text())
        code=r'''
import json,subprocess
from pathlib import Path
unit='curaloop-dq-frame-v2-20261107.service';p=Path(__ROOT__)/'jobs/frame-v2'
r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
s=dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
assert s.get('InvocationID')==__INVOCATION__ and s.get('SubState')=='running'
record={'status':'CONTROLLER_STOPPED_METADATA_QUERY_PLAN','reason':'Verified optimizer scans endpoint-wide activity index for each target; no values queried',
'state_before_stop':{k:s.get(k) for k in ['InvocationID','ActiveState','SubState','CPUUsageNSec','MemoryPeak']},'candidate_frame_completed':False,'numeric_values_queried':False}
(p/'controller-stop.json').write_text(json.dumps(record))
subprocess.run(['systemctl','--user','stop',unit],check=True,capture_output=True,timeout=10)
r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
after=dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
assert after.get('ActiveState') not in {'active','activating','deactivating'}
print(json.dumps(record))
'''.replace('__ROOT__',repr(REMOTE)).replace('__INVOCATION__',repr(proof['invocation_id']))
        result=ssh(code);save(PRIVATE/'frame-v2-controller-stop.json',result);print(json.dumps(result))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
