"""Owned transient-job controller; payload starts only after kernel proof."""
import argparse,base64,hashlib,json,shlex,subprocess
from pathlib import Path
from r0dq_core_v1 import ROOT,PRIVATE,REMOTE,HOST,SSH_OPTIONS,DEADLINE,save,reserve,archive_code,now
from r0dq_transport_guard_v1 import TransportGuard

BOOT=r'''
import json,sys,os,time,subprocess,signal
from pathlib import Path
from datetime import datetime,timezone
p=Path(sys.argv[1]);permit=json.loads((p/'permit.json').read_text())
until=time.monotonic()+30
while not (p/'release.json').exists():
 if time.monotonic()>until:raise SystemExit(124)
 time.sleep(.05)
assert json.loads((p/'release.json').read_text())['token']==permit['token']
assert datetime.now(timezone.utc)<datetime.fromisoformat(permit['deadline_utc'])
assert os.sched_getaffinity(0)=={permit['cpu']} and os.getpriority(os.PRIO_PROCESS,0)==19
cg=Path('/sys/fs/cgroup'+next(l.split('::',1)[1] for l in Path('/proc/self/cgroup').read_text().splitlines() if l.startswith('0::')))
def usage():return int(dict(l.split() for l in (cg/'cpu.stat').read_text().splitlines())['usage_usec'])/1000000
baseline=usage();start=time.monotonic();env=os.environ.copy()
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:env[key]='1'
env['PYTHONDONTWRITEBYTECODE']='1';env.update(permit.get('environment',{}))
child=subprocess.Popen(permit['argv'],cwd=permit['root'],env=env,start_new_session=True)
limited=None
while child.poll() is None:
 if usage()-baseline>=permit['cpu_limit_seconds']-.5:limited='CPU'
 if time.monotonic()-start>=permit['runtime_seconds']-5 or datetime.now(timezone.utc)>=datetime.fromisoformat(permit['deadline_utc']):limited='WALL'
 if limited:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=2)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  break
 time.sleep(.2)
data={'token':permit['token'],'exit_code':child.returncode,'resource_limit':limited,'cpu_seconds_tree':usage()-baseline,'wall_seconds':time.monotonic()-start}
(p/'payload-exit.json').write_text(json.dumps(data));raise SystemExit(child.returncode or (124 if limited else 0))
'''


def ssh(code,timeout=40):
    payload=base64.b64encode(code.encode()).decode()
    command='python3 -c '+shlex.quote('import base64;exec(base64.b64decode('+repr(payload)+'))')
    result=subprocess.run(['ssh',*SSH_OPTIONS,HOST,command],capture_output=True,timeout=timeout)
    if result.returncode:raise RuntimeError('Remote control error: '+result.stderr.decode(errors='replace')[:1000])
    return json.loads(result.stdout)


def launch_download():
    book=json.loads((PRIVATE/'ledger.json').read_text())
    assert not any(r['name']=='chembl37-bulk-archive' for r in book['http_attempts'])
    pin=json.loads((PRIVATE/'archive-source-pin-v1.json').read_text())
    reserve('download-archive-v1',3600,'source')
    book=json.loads((PRIVATE/'ledger.json').read_text())
    book['http_attempts'].append({'name':'chembl37-bulk-archive','url':pin['archive_url'],'kind':'bulk_archive','status':'ADMITTED','utc':now()})
    save(PRIVATE/'ledger.json',book)
    worker=ROOT/'tools/r0dq_download_worker_v1.py';raw=worker.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    cpu=json.loads((PRIVATE/'ssh-admission-v1.json').read_text())['least_busy_cpu']
    permit={'root':REMOTE,'job':'download-archive-v1','unit':'curaloop-dq-download-20261107-v1.service',
        'cpu':cpu,'cpu_limit_seconds':3600,'runtime_seconds':21600,'deadline_utc':DEADLINE.isoformat(),
        'token':hashlib.sha256((now()+digest).encode()).hexdigest(),'source_pin':pin,
        'argv':['/usr/bin/python3','-B',REMOTE+'/code/'+digest+'.py',REMOTE+'/jobs/download-archive-v1']}
    save(PRIVATE/'download-permit-v1.json',permit)
    code=r'''
import os,json,subprocess,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
root=Path(__ROOT__);permit=__PERMIT__
assert root.resolve()==root and root.stat().st_uid==os.getuid()
assert datetime.now(timezone.utc)<datetime.fromisoformat(permit['deadline_utc'])
release=__RELEASE__;marker=root/'phase-release.json'
if marker.exists():assert json.loads(marker.read_text())==release
else:marker.write_text(json.dumps(release))
(root/'code').mkdir(exist_ok=True);raw=__WORKER__.encode()
digest=hashlib.sha256(raw).hexdigest();target=root/'code'/(digest+'.py')
if target.exists():assert target.read_bytes()==raw
else:target.write_bytes(raw)
p=root/'jobs'/permit['job'];p.mkdir(exist_ok=False)
(p/'permit.json').write_text(json.dumps(permit));(p/'bootstrap.py').write_text(__BOOT__)
unit=permit['unit']
def show():
 r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
 return dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
assert show().get('LoadState')=='not-found'
props={'ExitType':'cgroup','CPUAccounting':'yes','CPUQuota':'100%','CPUQuotaPeriodSec':'100ms','CPUAffinity':str(permit['cpu']),
'MemoryAccounting':'yes','MemoryMax':'4294967296','MemorySwapMax':'0','Nice':'19','TasksMax':'32',
'RuntimeMaxSec':str(permit['runtime_seconds'])+'s','TimeoutStartSec':'10s','TimeoutStopSec':'5s',
'KillMode':'control-group','SendSIGKILL':'yes','Restart':'no','OOMPolicy':'kill','UMask':'0077',
'StandardOutput':'append:'+str(p/'stdout-private.txt'),'StandardError':'append:'+str(p/'stderr-private.txt')}
cmd=['systemd-run','--user','--no-ask-password','--unit='+unit,'--service-type=exec','--remain-after-exit','--working-directory='+str(root)]
for k,v in props.items():cmd+=['-p',k+'='+v]
cmd+=['--','/usr/bin/python3','-B',str(p/'bootstrap.py'),str(p)]
result=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
state=show();proof={'status':'STARTED_NOT_RELEASED','start_status':result.returncode,'properties':state,'owned_invocation':False,'caps_verified':False}
try:
 assert result.returncode==0 and int(state['MainPID'])>0 and state['InvocationID']
 pid=int(state['MainPID']);cg=Path('/sys/fs/cgroup'+state['ControlGroup'])
 assert str(p/'bootstrap.py').encode() in Path('/proc/'+str(pid)+'/cmdline').read_bytes().split(bytes([0]))
 proof.update(owned_invocation=True,invocation_id=state['InvocationID'])
 kernel={n:(cg/n).read_text().strip() for n in ['cpu.max','memory.max','memory.swap.max']}
 assert kernel=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
 assert os.sched_getaffinity(pid)=={permit['cpu']} and os.getpriority(os.PRIO_PROCESS,pid)==19
 proof.update(kernel=kernel,caps_verified=True,status='RELEASED_UNDER_VERIFIED_LIMITS')
 (p/'release.json').write_text(json.dumps({'token':permit['token']}))
except Exception:
 if proof['owned_invocation'] and show().get('InvocationID')==proof['invocation_id']:subprocess.run(['systemctl','--user','stop',unit],capture_output=True,timeout=10)
 raise
(p/'launch-proof.json').write_text(json.dumps(proof));print(json.dumps(proof))
'''.replace('__ROOT__',repr(REMOTE)).replace('__PERMIT__',repr(permit)).replace('__RELEASE__',repr(json.loads((PRIVATE/'release.json').read_text()))).replace('__WORKER__',repr(raw.decode())).replace('__BOOT__',repr(BOOT))
    proof=ssh(code)
    save(PRIVATE/'download-launch-proof-v1.json',proof)
    archive_code(worker)
    print(json.dumps({k:proof[k] for k in ['status','caps_verified','kernel']}))


def poll_download():
    permit=json.loads((PRIVATE/'download-permit-v1.json').read_text())
    proof=json.loads((PRIVATE/'download-launch-proof-v1.json').read_text())
    code=r'''
import json,subprocess
from pathlib import Path
root=Path(__ROOT__);p=root/'jobs/download-archive-v1';unit=__UNIT__
r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
state=dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
assert state.get('InvocationID')==__INVOCATION__
data={'state':{k:state.get(k) for k in ['ActiveState','SubState','Result','ExecMainStatus','CPUUsageNSec','MemoryCurrent','MemoryPeak']}}
for name in ['progress.json','result.json','payload-exit.json']:
 data[name]=json.loads((p/name).read_text()) if (p/name).exists() else None
print(json.dumps(data))
'''.replace('__ROOT__',repr(REMOTE)).replace('__UNIT__',repr(permit['unit'])).replace('__INVOCATION__',repr(proof['invocation_id']))
    result=ssh(code)
    save(PRIVATE/'download-status-latest.json',result)
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['download','poll']);args=parser.parse_args()
    # Each read-only poll gets its own retained utility receipt.
    name='remote-'+args.action+'-'+now().replace(':','').replace('.','').replace('+','')
    guard=TransportGuard(name,cpu_seconds=5 if args.action=='poll' else 60,wall=60,memory_mib=256)
    try:
        launch_download() if args.action=='download' else poll_download()
        archive_code(ROOT/'tools/r0dq_transport_guard_v1.py')
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
