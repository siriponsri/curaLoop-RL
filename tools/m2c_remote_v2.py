"""Synthetic-only profile transport/launch under an enforced one-core cgroup."""
import base64,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'.local/m2-costed-20261108-v2'
REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'

BOOTSTRAP='''import hashlib,json,os,resource,sys,tarfile,tempfile,time
from pathlib import Path
permit=__PERMIT__;root=Path(permit['task_root']);job=root/'jobs'/permit['attempt'];start=time.monotonic()
resource.setrlimit(resource.RLIMIT_CPU,(59,60));resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296));os.sched_setaffinity(0,{permit['cpu']});os.nice(19)
def new(name,value):
 with (job/name).open('x') as f:json.dump(value,f,indent=2);f.write('\\n')
status='FAIL'
try:
 cg=Path('/sys/fs/cgroup'+next(s.split('::',1)[1] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')))
 proof={k:(cg/k).read_text().strip() for k in('cpu.max','memory.max','memory.swap.max')}
 assert proof=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'};new('kernel-proof.json',proof)
 assert sys.version_info[:2]==(3,12)
 # The local authenticated transport archive is retained; no duplicate archive is left remotely.
 with tempfile.TemporaryFile(dir=root) as archive:
  h=hashlib.sha256();count=0
  for block in iter(lambda:sys.stdin.buffer.read(1048576),b''):
   count+=len(block);assert count<=permit['arguments']['archive_bytes'];archive.write(block);h.update(block)
  assert count==permit['arguments']['archive_bytes'] and h.hexdigest()==permit['arguments']['archive_sha256']
  archive.seek(0)
  with tarfile.open(fileobj=archive,mode='r:gz') as tf:
   manifest=json.load(tf.extractfile('transport-manifest.json'));assert manifest['biological_inputs_included'] is False
   expected={r['path']:r for r in manifest['files']};seen=set()
   assert len(expected)<5000 and sum(r['bytes'] for r in expected.values())<512*1024**2
   for member in tf:
    name=member.name;assert member.isfile() and not Path(name).is_absolute() and '..' not in Path(name).parts
    assert name=='transport-manifest.json' or name in expected
    assert name not in seen;seen.add(name);dest=(root/name).resolve();assert dest.is_relative_to(root.resolve())
    dest.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();length=0
    with tf.extractfile(member) as inp,dest.open('xb') as out:
     for b in iter(lambda:inp.read(1048576),b''):out.write(b);h.update(b);length+=len(b)
    if name in expected:assert length==expected[name]['bytes'] and h.hexdigest()==expected[name]['sha256']
    dest.chmod(0o600)
   assert seen==set(expected)|{'transport-manifest.json'}
 new('result.json',{'status':'PASS_AUTHENTICATED_STREAM_BOOTSTRAP','files':len(seen),
  'archive_sha256':permit['arguments']['archive_sha256'],'transport_archive_retained_locally':True,'biological_inputs_included':False})
 status='PASS'
except BaseException as e:
 new('failure.json',{'type':type(e).__name__,'message':str(e)[:240]});raise
finally:
 new('resource.json',{'schema':'curaloop.m2_profile.resources.v1','attempt':permit['attempt'],'host':'dr-train',
  'status':status,'cpu_seconds':time.process_time(),'wall_seconds':time.monotonic()-start,'reservation_seconds':permit['reservation_seconds']})
'''


def remote(code,stdin=None,timeout=300):
    profile=json.loads((TASK/'ssh-profile.json').read_text())['selected_profile']
    encoded=base64.b64encode(code.encode()).decode()
    cmd="python3 -B -c 'exec(__import__(\"base64\").b64decode(\""+encoded+"\"))'"
    return subprocess.run(['rtk','proxy','ssh','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes',
        '-o','ConnectTimeout=10','-o','ConnectionAttempts=1',profile,cmd],stdin=stdin,capture_output=True,timeout=timeout)


def dispatch(action,name,prepare_only=False):
    assert action in('bootstrap','calibration','worker')
    job=TASK/'jobs'/name;permit=json.loads((job/'permit.json').read_text())
    assert permit['host']=='dr-train' and permit['task_root']==REMOTE
    body=BOOTSTRAP.replace('__PERMIT__',repr(permit)) if action=='bootstrap' else None
    if body:compile(body,'<profile-bootstrap>','exec')
    code='''import json,os,shutil,subprocess,sys
from pathlib import Path
permit=__PERMIT__;root=Path(__REMOTE__);unit=__UNIT__
assert root==Path.home()/'curaloop-tasks/m2-costed-20261108-v2'
if __CREATE__:root.mkdir(parents=True,exist_ok=False);root.chmod(0o700)
assert root.resolve()==root and root.is_dir() and not root.is_symlink() and shutil.disk_usage(root).free>1024**3
job=root/'jobs'/permit['attempt'];job.mkdir(parents=True,exist_ok=False)
(job/'permit.json').write_text(json.dumps(permit,indent=2)+'\\n')
env=os.environ.copy();env['XDG_RUNTIME_DIR']='/run/user/'+str(os.getuid());env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+env['XDG_RUNTIME_DIR']+'/bus'
def show():
 r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,env=env,timeout=10)
 return dict(s.split('=',1) for s in r.stdout.splitlines() if '=' in s)
assert show().get('LoadState')=='not-found'
body=__BODY__
if body is not None:
 (job/'controller.py').write_text(body);command=['/usr/bin/python3','-B',str(job/'controller.py')];working=root
else:
 command=['/usr/bin/python3','-B','-m',__MODULE__,str(job/'permit.json')];working=root/permit.get('code_directory','code')
props={'ExitType':'cgroup','CPUQuota':'100%','CPUQuotaPeriodSec':'100ms','CPUAffinity':str(permit['cpu']),
 'MemoryMax':'4294967296','MemorySwapMax':'0','Nice':'19','TasksMax':'32','RuntimeMaxSec':str(permit['wall_seconds'])+'s',
 'TimeoutStartSec':'10s','TimeoutStopSec':'5s','KillMode':'control-group','SendSIGKILL':'yes','Restart':'no','OOMPolicy':'kill','UMask':'0077'}
prefix=['systemd-run','--user','--no-ask-password','--wait','--pipe','--service-type=exec','--unit='+unit,'--working-directory='+str(working)]
for k,v in props.items():prefix+=['-p',k+'='+v]
for k,v in {'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1',
 'MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','PYTHONPATH':str(root/'vendor')+':'+str(working)}.items():prefix+=['--setenv='+k+'='+v]
r=subprocess.run(prefix+['--']+command,stdin=sys.stdin.buffer,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=permit['wall_seconds']+30)
state=show();out={'exit_code':r.returncode,'stdout':r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace'),
 'unit':unit,'unit_state':{k:state.get(k) for k in('ActiveState','SubState','Result','ExecMainStatus')}}
for field in('resource','kernel-proof','result','failure'):
 p=job/(field+'.json')
 if p.exists():out[field]=json.loads(p.read_text())
(job/'controller-result.json').write_text(json.dumps(out,indent=2)+'\\n');print(json.dumps(out))
'''
    module='research.m2_costed_v2.worker' if action=='worker' else 'research.m2_costed_v2.calibration'
    mapping={'__PERMIT__':repr(permit),'__REMOTE__':repr(REMOTE),'__UNIT__':repr('curaloop-m2c-20261108-v1-'+name),
             '__CREATE__':repr(action=='bootstrap'),'__BODY__':repr(body),'__MODULE__':repr(module)}
    for key,value in mapping.items():code=code.replace(key,value)
    compile(code,'<profile-launcher>','exec')
    with (job/'remote-command.py').open('x',encoding='utf-8') as f:f.write(code)
    if prepare_only:return code
    if action=='bootstrap':
        with (TASK/'transport-technical-v1.tar.gz').open('rb') as f:r=remote(code,stdin=f,timeout=permit['wall_seconds']+60)
    else:r=remote(code,timeout=permit['wall_seconds']+60)
    with (job/'ssh-raw.json').open('x') as f:json.dump({'exit_code':r.returncode,'stdout':r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace')},f,indent=2)
    assert r.returncode==0,'REMOTE_CONTROLLER_FAILED_SEE_RETAINED_ERROR'
    data=json.loads(r.stdout)
    with (job/'controller-result.json').open('x') as f:json.dump(data,f,indent=2)
    for field in('resource','kernel-proof','result','failure'):
        if field in data:
            with (job/(field+'.json')).open('x') as f:json.dump(data[field],f,indent=2)
    result=data.get('result',{})
    print(json.dumps({'job':name,'exit_code':data['exit_code'],'resource_status':data.get('resource',{}).get('status'),
        'status':result.get('status'),'scientific_cpu_seconds':result.get('scientific_cpu_seconds')}))
    assert data['exit_code']==0,'PROFILE_WORKER_FAILURE_RETAINED'


def main():dispatch(*sys.argv[1:3])


if __name__=='__main__':main()
