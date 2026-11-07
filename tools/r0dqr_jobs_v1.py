"""Sequential owned remote stages, gated by actual kernel limits."""
import argparse,hashlib,io,json,subprocess,tarfile
from pathlib import Path
from r0dqr_core_v1 import ROOT,PRIVATE,REMOTE,HOST,SSH_OPTIONS,DEADLINE,save,reserve,archive_code,now
from r0dqr_remote_boot_v1 import BOOT
from r0dqr_rpc_v1 import ssh
from r0dqr_transport_guard_v1 import TransportGuard

SPECS={
    'prepare-v1':('source_return',600,7200,'r0dqr_prepare_worker_v1.py'),
    'inventory-v1':('metadata',600,7200,'r0dqr_inventory_worker_v1.py'),
    'nominal-v1':('metadata',1800,10800,'r0dqr_nominal_worker_v1.py'),
    'context-v1':('context',300,7200,'r0dqr_context_worker_v1.py'),
    'return-v1':('source_return',3600,10800,'r0dqr_export_worker_v1.py'),
}

def launch(name):
    stage,cpu_limit,wall,filename=SPECS[name]
    status=json.loads((PRIVATE/'archive-transport-v1.json').read_text())
    assert status['status']=='PASS_SOURCE_ARCHIVE_TRANSPORT_PENDING_REMOTE_DIGEST'
    reserve(name,cpu_limit,stage)
    files={}
    for source,destination in [(ROOT/'tools'/filename,'payload.py'),
        (ROOT/'tools/r0dqr_projection_v1.py','r0dqr_projection_v1.py'),
        (ROOT/'tools/r0dqr_context_projection_v1.py','r0dqr_context_projection_v1.py'),
        (ROOT/'research/taskfirst_dqr_v1/rules.py','research/taskfirst_dqr_v1/rules.py'),
        (ROOT/'research/taskfirst_dqr_v1/selection.py','research/taskfirst_dqr_v1/selection.py'),
        (ROOT/'research/taskfirst_dqr_v1/__init__.py','research/taskfirst_dqr_v1/__init__.py')]:
        files[destination]=source.read_text(encoding='utf-8');archive_code(source)
    files['frame-rules-frozen.json']=(PRIVATE/'frame-rules-v1.json').read_text()
    files['vendor-manifest.json']=(PRIVATE/'vendor-manifest-v1.json').read_text()
    files['input-transfer.json']=(PRIVATE/'input-transfer-v1.json').read_text()
    cpu=json.loads((PRIVATE/'ssh-admission-v1.json').read_text())['least_busy_cpu']
    p=REMOTE+'/jobs/'+name
    permit={'root':REMOTE,'job':name,'unit':'curaloop-dqr-'+name+'-20261107.service',
        'cpu':cpu,'cpu_limit_seconds':cpu_limit,'runtime_seconds':wall,'deadline_utc':DEADLINE.isoformat(),
        'token':hashlib.sha256((name+now()).encode()).hexdigest(),
        'environment':{'PYTHONPATH':REMOTE+'/vendor:'+p},
        'argv':['/usr/bin/python3','-B',p+'/payload.py',p]}
    if name=='return-v1':
        p=REMOTE+'-export-v1'
        permit.update(job_directory=p,environment={'PYTHONPATH':p},argv=['/usr/bin/python3','-B',p+'/payload.py',p])
        files={'payload.py':files['payload.py'],'cleanup-payload.py':(ROOT/'tools/r0dqr_cleanup_worker_v1.py').read_text()}
        archive_code(ROOT/'tools/r0dqr_cleanup_worker_v1.py')
    save(PRIVATE/(name+'-permit.json'),permit)
    package=PRIVATE/(name+'-code-v1.tar.gz');assert not package.exists()
    pins={}
    with tarfile.open(package,'w:gz',compresslevel=1) as tar:
        for rel,source in files.items():
            raw=source.encode('utf-8');info=tarfile.TarInfo(rel);info.size=len(raw);info.mode=0o600
            tar.addfile(info,io.BytesIO(raw));pins[rel]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    bundle={'filename':package.name,'bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'files':pins}
    remote_package=REMOTE+'/'+package.name
    ssh('import json,os;from pathlib import Path;r=Path('+repr(REMOTE)+');p=Path('+repr(remote_package)+');assert r.resolve()==r and r.stat().st_uid==os.getuid() and not p.exists() and not p.is_symlink();print(json.dumps({"status":"FRESH_STAGE_CODE_TRANSFER"}))')
    ret=subprocess.run(['scp',*SSH_OPTIONS,str(package),HOST+':'+remote_package],capture_output=True,timeout=40)
    assert ret.returncode==0,'Stage code transfer failed; no payload released'
    save(PRIVATE/(name+'-code-pin.json'),bundle)
    # Reuse the verified launch template; only predeclared stage files/permit
    # differ. No existing service or job directory can be reused.
    code=r'''
import os,json,subprocess,hashlib,time,shutil,tarfile
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
root=Path(__ROOT__);permit=__PERMIT__;bundle=__BUNDLE__
assert root.resolve()==root and root.stat().st_uid==os.getuid()
assert datetime.now(timezone.utc)<datetime.fromisoformat(permit['deadline_utc'])
assert shutil.disk_usage(root).free>=16*1024**3
# A prior job must be terminal before any heavy payload is released.
for prior in (root/'jobs').iterdir():
 if not (prior/'permit.json').exists():continue
 old=json.loads((prior/'permit.json').read_text());unit=old.get('unit')
 if not unit:continue
 r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
 state=dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
 assert state.get('SubState') not in {'running','start','start-post','stop','stop-sigterm','stop-sigkill'},'Other heavy job active'
 if state.get('ActiveState') in {'active','failed'}:
  proof=json.loads((prior/'launch-proof.json').read_text())
  assert state.get('InvocationID')==proof['invocation_id']
  terminal={k:state.get(k) for k in ['ActiveState','SubState','Result','ExecMainStatus','CPUUsageNSec','MemoryPeak','InvocationID']}
  (prior/'terminal-before-stop.json').write_text(json.dumps(terminal))
  subprocess.run(['systemctl','--user','stop',unit],check=True,capture_output=True,timeout=10)
p=Path(permit.get('job_directory',str(root/'jobs'/permit['job'])))
if p!=root/'jobs'/permit['job']:
 assert permit['job']=='return-v1' and p==Path(str(root)+'-export-v1')
 assert p.parent.resolve()==root.parent and p.parent.stat().st_uid==os.getuid()
 assert not p.exists() and not p.is_symlink()
p.mkdir(exist_ok=False)
package=root/bundle['filename'];assert package.is_file() and not package.is_symlink() and package.stat().st_size==bundle['bytes']<2097152
assert hashlib.sha256(package.read_bytes()).hexdigest()==bundle['sha256']
seen=set()
with tarfile.open(package,'r:gz') as tar:
 for member in tar:
  rel=PurePosixPath(member.name)
  assert member.isfile() and not rel.is_absolute() and '..' not in rel.parts and '\\' not in member.name
  assert member.name in bundle['files'] and member.name not in seen;seen.add(member.name)
  pin=bundle['files'][member.name];assert member.size==pin['bytes']<=1048576
  raw=tar.extractfile(member).read();assert hashlib.sha256(raw).hexdigest()==pin['sha256']
  target=p.joinpath(*rel.parts);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
assert seen==set(bundle['files'])
(p/'permit.json').write_text(json.dumps(permit));(p/'bootstrap.py').write_text(__BOOT__)
if permit['job']=='return-v1':
 # Freeze the export/cleanup code and permit in the task snapshot as well.
 archive=root/'return-dispatch-v1';archive.mkdir(exist_ok=False)
 for name in ['payload.py','cleanup-payload.py','permit.json','bootstrap.py']:
  (archive/name).write_bytes((p/name).read_bytes())
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
r=subprocess.run(cmd,capture_output=True,text=True,timeout=15);state=show()
proof={'status':'STARTED_NOT_RELEASED','owned_invocation':False,'caps_verified':False,'unit':unit}
try:
 assert r.returncode==0 and int(state['MainPID'])>0 and state['InvocationID']
 pid=int(state['MainPID']);cg=Path('/sys/fs/cgroup'+state['ControlGroup'])
 assert str(p/'bootstrap.py').encode() in Path('/proc/'+str(pid)+'/cmdline').read_bytes().split(bytes([0]))
 proof.update(owned_invocation=True,invocation_id=state['InvocationID'])
 kernel={n:(cg/n).read_text().strip() for n in ['cpu.max','memory.max','memory.swap.max']}
 assert kernel=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
 assert os.sched_getaffinity(pid)=={permit['cpu']} and os.getpriority(os.PRIO_PROCESS,pid)==19
 proof.update(kernel=kernel,caps_verified=True,status='RELEASED_UNDER_VERIFIED_LIMITS')
 (p/'release.json').write_text(json.dumps({'token':permit['token']}))
except Exception:
 if proof['owned_invocation'] and show().get('InvocationID')==proof['invocation_id']:
  subprocess.run(['systemctl','--user','stop',unit],capture_output=True,timeout=10)
 raise
(p/'launch-proof.json').write_text(json.dumps(proof));print(json.dumps(proof))
'''.replace('__ROOT__',repr(REMOTE)).replace('__PERMIT__',repr(permit)).replace('__BUNDLE__',repr(bundle)).replace('__BOOT__',repr(BOOT))
    proof=ssh(code);save(PRIVATE/(name+'-launch.json'),proof);print(json.dumps(proof))

def poll(name):
    permit=json.loads((PRIVATE/(name+'-permit.json')).read_text())
    proof=json.loads((PRIVATE/(name+'-launch.json')).read_text())
    code=r'''
import json,subprocess
from pathlib import Path
p=Path(__PATH__)
r=subprocess.run(['systemctl','--user','show',__UNIT__],capture_output=True,text=True,timeout=10)
s=dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
assert s.get('InvocationID')==__INVOCATION__
data={'state':{k:s.get(k) for k in ['ActiveState','SubState','Result','ExecMainStatus','CPUUsageNSec','MemoryCurrent','MemoryPeak']}}
for name in ['progress.json','result.json','payload-exit.json']:
 data[name]=json.loads((p/name).read_text()) if (p/name).exists() else None
if p.name.endswith('-export-v1'):
 try:data['export_archive_partial_bytes']=(p/'full-task-v1.tar.gz.part').stat().st_size
 except FileNotFoundError:pass
print(json.dumps(data))
'''.replace('__PATH__',repr(permit.get('job_directory',REMOTE+'/jobs/'+name))).replace('__UNIT__',repr(permit['unit'])).replace('__INVOCATION__',repr(proof['invocation_id']))
    result=ssh(code);save(PRIVATE/(name+'-status.json'),result);print(json.dumps(result))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['launch','poll']);parser.add_argument('name',choices=SPECS);args=parser.parse_args()
    guard=TransportGuard('stage-control-'+now().replace(':','').replace('.','').replace('+',''),cpu_seconds=10 if args.action=='poll' else 60,wall=60,memory_mib=256)
    try:launch(args.name) if args.action=='launch' else poll(args.name)
    except Exception as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
