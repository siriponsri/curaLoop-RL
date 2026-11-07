"""Create only the fresh owned root and verify a real bounded cgroup canary."""
import base64
import json
import shlex
import subprocess
from r0dqr_core_v1 import ROOT,PRIVATE,REMOTE,HOST,SSH_OPTIONS,DEADLINE,save,archive_code
from r0dqr_transport_guard_v1 import TransportGuard

BOOT=r'''
import json,sys,os,time,resource
from pathlib import Path
from datetime import datetime,timezone
p=Path(sys.argv[1]);permit=json.loads((p/'permit.json').read_text())
resource.setrlimit(resource.RLIMIT_CPU,(20,21))
deadline=time.monotonic()+30
while not (p/'release.json').exists():
 if time.monotonic()>deadline:raise SystemExit(124)
 time.sleep(.05)
assert json.loads((p/'release.json').read_text())['token']==permit['token']
assert datetime.now(timezone.utc)<datetime.fromisoformat(permit['deadline_utc'])
assert os.sched_getaffinity(0)=={permit['cpu']} and os.getpriority(os.PRIO_PROCESS,0)==19
start=time.process_time()
while time.process_time()-start<.25:pass
(p/'payload-exit.json').write_text(json.dumps({'exit_code':0,'token':permit['token'],'affinity':sorted(os.sched_getaffinity(0))}))
'''


def main():
    admission=json.loads((PRIVATE/'ssh-admission-v1.json').read_text())
    cpu=admission['least_busy_cpu']
    permit={'cpu':cpu,'deadline_utc':DEADLINE.isoformat(),'token':'r0dqr-canary-20261107-v1','runtime_seconds':45}
    code=r'''
import os,json,subprocess,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
root=Path(__ROOT__);home=Path.home()
assert root==home/'curaloop-runs/chembl-taskfirst-dqr-20261107-v1'
assert not root.exists() and home.resolve()==home and home.stat().st_uid==os.getuid()
parent=root.parent
if not parent.exists():parent.mkdir(mode=0o700)
assert parent.resolve()==parent and parent.stat().st_uid==os.getuid()
os.umask(0o077);root.mkdir();(root/'jobs').mkdir()
p=root/'jobs/resource-canary-v1';p.mkdir();permit=__PERMIT__
(p/'permit.json').write_text(json.dumps(permit));(p/'bootstrap.py').write_text(__BOOT__)
unit='curaloop-dqr-canary-20261107-v1.service'
def show():
 r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
 return dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
assert show().get('LoadState')=='not-found'
props={'ExitType':'cgroup','CPUAccounting':'yes','CPUQuota':'100%','CPUQuotaPeriodSec':'100ms','CPUAffinity':str(permit['cpu']),
'MemoryAccounting':'yes','MemoryMax':'4294967296','MemorySwapMax':'0','Nice':'19','TasksMax':'32',
'RuntimeMaxSec':'45s','TimeoutStartSec':'10s','TimeoutStopSec':'5s','KillMode':'control-group',
'SendSIGKILL':'yes','Restart':'no','OOMPolicy':'kill','UMask':'0077',
'StandardOutput':'append:'+str(p/'stdout-private.txt'),'StandardError':'append:'+str(p/'stderr-private.txt')}
cmd=['systemd-run','--user','--no-ask-password','--unit='+unit,'--service-type=exec','--remain-after-exit','--working-directory='+str(root)]
for k,v in props.items():cmd+=['-p',k+'='+v]
cmd+=['--','/usr/bin/python3','-B',str(p/'bootstrap.py'),str(p)]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
proof={'unit':unit,'start_status':r.returncode,'start_stderr':r.stderr,'caps_verified':False,'owned_invocation':False}
state=show();proof['launch_properties']=state
try:
 assert r.returncode==0 and int(state['MainPID'])>0 and state['InvocationID']
 pid=int(state['MainPID']);cg=Path('/sys/fs/cgroup'+state['ControlGroup'])
 assert cg!=Path('/sys/fs/cgroup') and cg.is_dir()
 assert str(p/'bootstrap.py').encode() in Path('/proc/'+str(pid)+'/cmdline').read_bytes().split(bytes([0]))
 proof.update(owned_invocation=True,invocation_id=state['InvocationID'])
 kernel={n:(cg/n).read_text().strip() for n in ['cpu.max','memory.max','memory.swap.max']}
 assert kernel=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
 assert os.sched_getaffinity(pid)=={permit['cpu']} and os.getpriority(os.PRIO_PROCESS,pid)==19
 proof.update(caps_verified=True,kernel=kernel)
 (p/'release.json').write_text(json.dumps({'token':permit['token']}))
 until=time.monotonic()+40
 while time.monotonic()<until:
  state=show()
  if state.get('SubState') in ['exited','failed','dead'] or state.get('ActiveState') in ['failed','inactive']:break
  time.sleep(.1)
 else:raise RuntimeError('Canary supervision timeout')
 proof['payload_exit']=json.loads((p/'payload-exit.json').read_text())
 assert proof['payload_exit']['exit_code']==0
 assert state.get('Result')=='success' and state.get('ExecMainStatus')=='0'
 proof['status']='PASS_REAL_QUOTA_CANARY'
except Exception as e:
 proof.update(status='FAIL_CANARY',error_type=type(e).__name__,error=str(e))
finally:
 current=show();proof['terminal_properties']=current
 if proof['owned_invocation']:
  assert current.get('InvocationID')==proof['invocation_id']
  stop=subprocess.run(['systemctl','--user','stop',unit],capture_output=True,text=True,timeout=10)
  proof['stop_status']=stop.returncode;proof['after_stop']=show()
 (p/'quota-proof.json').write_text(json.dumps(proof,sort_keys=True))
print(json.dumps(proof))
'''.replace('__ROOT__',repr(REMOTE)).replace('__PERMIT__',repr(permit)).replace('__BOOT__',repr(BOOT))
    payload=base64.b64encode(code.encode()).decode()
    command='python3 -c '+shlex.quote('import base64;exec(base64.b64decode('+repr(payload)+'))')
    result=subprocess.run(['ssh',*SSH_OPTIONS,HOST,command],capture_output=True,timeout=65)
    assert result.returncode==0,result.stderr.decode(errors='replace')[:700]
    proof=json.loads(result.stdout)
    save(PRIVATE/'remote-quota-canary-v1.json',proof)
    archive_code(ROOT/'tools/r0dqr_transport_guard_v1.py')
    print(json.dumps({k:proof.get(k) for k in ['status','caps_verified','kernel','stop_status','error']}))
    assert proof['status']=='PASS_REAL_QUOTA_CANARY'


if __name__=='__main__':
    guard=TransportGuard('remote-quota-canary-v1',cpu_seconds=60,wall=80,memory_mib=256)
    try:main()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
