"""Fresh M2 cgroup transport/calibration launcher, using the existing SSH profile."""
import base64
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'.local/m2-selective-compute-20261108-v1'
REMOTE='/home/chaw/curaloop-tasks/m2-selective-compute-20261108-v1'

BARE='''import hashlib,json,os,resource,signal,sys,time
from pathlib import Path
permit=__PERMIT__;root=Path(permit['task_root']);job=root/'jobs'/permit['attempt']
resource.setrlimit(resource.RLIMIT_CPU,(permit['guard_cpu_seconds'],permit['guard_cpu_seconds']))
resource.setrlimit(resource.RLIMIT_AS,(permit['memory_bytes'],permit['memory_bytes']))
os.sched_setaffinity(0,{permit['cpu']});os.nice(19)
started=time.monotonic()
def new(name,value):
 with (job/name).open('x') as f:json.dump(value,f,indent=2);f.write('\\n')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
status='FAIL'
try:
 cg=Path('/sys/fs/cgroup'+next(s.split('::',1)[1] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')))
 proof={k:(cg/k).read_text().strip() for k in ('cpu.max','memory.max','memory.swap.max')}
 assert proof=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
 new('kernel-proof.json',proof)
__BODY__
 status='PASS'
except BaseException as e:
 new('failure.json',{'type':type(e).__name__,'message':str(e)[:240]});raise
finally:
 new('resource.json',{'schema':'curaloop.m2.resources.v1','attempt':permit['attempt'],'host':'dr-train',
  'status':status,'cpu_seconds':time.process_time(),'wall_seconds':time.monotonic()-started,
  'reservation_seconds':permit['reservation_seconds'],'affinity':sorted(os.sched_getaffinity(0))})
'''

RECEIVE=''' dest=root/'transport-synthetic-v1.tar.gz'
 count=0;h=hashlib.sha256()
 with dest.open('xb') as f:
  for block in iter(lambda:sys.stdin.buffer.read(1048576),b''):
   count+=len(block);assert count<=permit['arguments']['archive_bytes'];f.write(block);h.update(block)
 assert count==permit['arguments']['archive_bytes'] and h.hexdigest()==permit['arguments']['archive_sha256']
 new('result.json',{'status':'PASS_SYNTHETIC_ONLY_RECEIVE','bytes':count,'sha256':h.hexdigest()})
'''

BOOTSTRAP=''' import tarfile
 assert sys.version_info[:2]==(3,12)
 archive=root/'transport-synthetic-v1.tar.gz';assert sha(archive)==permit['arguments']['archive_sha256']
 with tarfile.open(archive,'r:gz') as tf:
  manifest=json.load(tf.extractfile('transport-manifest.json'))
  assert manifest['biological_inputs_included'] is False
  expected={r['path']:r for r in manifest['files']};seen=set()
  for member in tf:
   name=member.name
   assert member.isfile() and not Path(name).is_absolute() and '..' not in Path(name).parts
   assert name=='transport-manifest.json' or name in expected
   assert name not in seen;seen.add(name)
   dest=(root/name).resolve();assert dest.is_relative_to(root.resolve())
   dest.parent.mkdir(parents=True,exist_ok=True)
   count=0;h=hashlib.sha256()
   with tf.extractfile(member) as source,dest.open('xb') as out:
    for block in iter(lambda:source.read(1048576),b''):out.write(block);h.update(block);count+=len(block)
   if name in expected:assert count==expected[name]['bytes'] and h.hexdigest()==expected[name]['sha256']
   dest.chmod(0o600)
  assert seen==set(expected)|{'transport-manifest.json'}
 new('result.json',{'status':'PASS_AUTHENTICATED_OFFLINE_BOOTSTRAP','files':len(seen),'biological_inputs_included':False})
'''


def remote(code,stdin=None,timeout=180):
    profile=json.loads((LOCAL/'existing-ssh-profile.json').read_text())['selected_profile']
    b64=base64.b64encode(code.encode()).decode()
    command="python3 -c 'exec(__import__(\"base64\").b64decode(\""+b64+"\"))'"
    return subprocess.run(['rtk','proxy','ssh','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
        '-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-o','ConnectionAttempts=1',profile,command],
        stdin=stdin,capture_output=True,timeout=timeout)


def main():
    action,name=sys.argv[1:3]
    assert action in ('receive','bootstrap','calibration','checks','install')
    job=LOCAL/'jobs'/name;permit=json.loads((job/'permit.json').read_text())
    assert permit['host']=='dr-train' and permit['task_root']==REMOTE
    install=''' import base64
 data=base64.b64decode(permit['arguments']['source_b64'])
 assert hashlib.sha256(data).hexdigest()==permit['arguments']['source_sha256']
 assert permit['arguments']['filename']=='calibration_v2.py'
 dest=root/'code/research/m2_v1/calibration_v2.py'
 with dest.open('xb') as f:f.write(data)
 new('result.json',{'status':'PASS_TECHNICAL_TIMER_REPAIR_INSTALL','source_sha256':sha(dest),'scientific_design_changed':False})
'''
    body=None if action in ('calibration','checks') else BARE.replace('__PERMIT__',repr(permit)).replace('__BODY__',RECEIVE if action=='receive' else install if action=='install' else BOOTSTRAP)
    if body:compile(body,'<m2-bare>','exec')
    unit='curaloop-m2-20261108-v1-'+name
    code='''import base64,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
permit=__PERMIT__;root=Path(__REMOTE__);unit=__UNIT__
assert root==Path.home()/'curaloop-tasks/m2-selective-compute-20261108-v1'
if __CREATE__:root.mkdir(parents=True,exist_ok=False);root.chmod(0o700)
assert root.is_dir() and not root.is_symlink() and shutil.disk_usage(root).free>2*1024**3
job=root/'jobs'/permit['attempt'];job.mkdir(parents=True,exist_ok=False)
(job/'permit.json').write_text(json.dumps(permit,indent=2)+'\\n')
if __ACTION__=='checks':
 data=base64.b64decode(permit['arguments']['checks_source_b64'])
 assert hashlib.sha256(data).hexdigest()==permit['arguments']['checks_sha256']
 dest=root/'code/research/m2_v1/checks.py'
 with dest.open('xb') as f:f.write(data)
env=os.environ.copy();env['XDG_RUNTIME_DIR']='/run/user/'+str(os.getuid())
env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+env['XDG_RUNTIME_DIR']+'/bus'
def show():
 r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,env=env)
 return dict(s.split('=',1) for s in r.stdout.splitlines() if '=' in s)
assert show().get('LoadState')=='not-found'
body=__BODY__
if body is not None:
 (job/'controller.py').write_text(body)
 command=['/usr/bin/python3','-B',str(job/'controller.py')];working=root
else:
 module=permit['module'] if __ACTION__=='calibration' else 'research.m2_v1.checks'
 assert module in ('research.m2_v1.calibration','research.m2_v1.calibration_v2','research.m2_v1.checks')
 command=['/usr/bin/python3','-B','-m',module,str(job/'permit.json')];working=root/'code'
properties={'ExitType':'cgroup','CPUAccounting':'yes','CPUQuota':'100%','CPUQuotaPeriodSec':'100ms',
 'CPUAffinity':str(permit['cpu']),'MemoryAccounting':'yes','MemoryMax':'4294967296','MemorySwapMax':'0',
 'Nice':'19','TasksMax':'32','RuntimeMaxSec':str(permit['wall_seconds'])+'s','TimeoutStartSec':'10s',
 'TimeoutStopSec':'5s','KillMode':'control-group','SendSIGKILL':'yes','Restart':'no','OOMPolicy':'kill','UMask':'0077'}
prefix=['systemd-run','--user','--no-ask-password','--unit='+unit,'--service-type=exec','--wait','--pipe','--working-directory='+str(working)]
for k,v in properties.items():prefix+=['-p',k+'='+v]
variables={'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1',
 'MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','PYTHONPATH':str(root/'vendor')+':'+str(root/'code')}
for k,v in variables.items():prefix+=['--setenv='+k+'='+v]
run=subprocess.run(prefix+['--']+command,stdin=sys.stdin.buffer,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
 env=env,timeout=permit['wall_seconds']+30)
state=show()
out={'exit_code':run.returncode,'stdout':run.stdout.decode(errors='replace'),'stderr':run.stderr.decode(errors='replace'),
 'unit':unit,'unit_state':{k:state.get(k) for k in ('InvocationID','ActiveState','SubState','Result','ExecMainStatus','CPUUsageNSec','MemoryPeak')}}
for field in ('resource','kernel-proof','result','failure'):
 path=job/(field+'.json')
 if path.exists():out[field]=json.loads(path.read_text())
(job/'controller-result.json').write_text(json.dumps(out,indent=2)+'\\n')
print(json.dumps(out))
'''
    for key,value in {'__PERMIT__':repr(permit),'__REMOTE__':repr(REMOTE),'__UNIT__':repr(unit),
                      '__CREATE__':repr(action=='receive'),'__BODY__':repr(body),'__ACTION__':repr(action)}.items():
        code=code.replace(key,value)
    compile(code,'<m2-controller>','exec')
    with (job/'remote-command.py').open('x',encoding='utf-8') as f:f.write(code)
    if action=='receive':
        with (LOCAL/'transport-synthetic-v1.tar.gz').open('rb') as stream:run=remote(code,stream,permit['wall_seconds']+60)
    else:run=remote(code,timeout=permit['wall_seconds']+60)
    with (job/'ssh-raw.json').open('x') as f:json.dump({'exit_code':run.returncode,'stdout':run.stdout.decode(errors='replace'),'stderr':run.stderr.decode(errors='replace')},f,indent=2)
    assert run.returncode==0,'SSH_CONTROLLER_FAILED_SEE_RETAINED_ERROR'
    data=json.loads(next(s for s in run.stdout.decode().splitlines() if s.startswith('{')))
    with (job/'remote-control.json').open('x') as f:json.dump(data,f,indent=2)
    for field in ('resource','kernel-proof','result','failure'):
        if field in data:
            with (job/(field+'.json')).open('x') as f:json.dump(data[field],f,indent=2)
    print(json.dumps({'job':name,'exit_code':data['exit_code'],'resource_status':data.get('resource',{}).get('status'),
        'result':data.get('result'),'unit_state':data['unit_state']}))
    assert data['exit_code']==0,'REMOTE_WORKER_FAILED_SEE_RETAINED_RECEIPT'


if __name__=='__main__':main()
