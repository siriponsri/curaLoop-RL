"""In-process ledger calls and one authenticated SSH stream per three-unit batch."""
import base64
import contextlib
import io
import hashlib
import json
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools import m2c_admin_v2 as admin
from tools.m2c_remote_v2 import dispatch,render_dispatch
TASK=ROOT/'.local/m2-costed-20261108-v2'
REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'


def admin_call(action,value):
    previous=sys.argv;out=io.StringIO()
    try:
        sys.argv=['m2c_admin_v2.py',action,str(value)]
        with contextlib.redirect_stdout(out):admin.main()
        return json.loads(out.getvalue())
    finally:sys.argv=previous


def ssh_script(source,timeout=200):
    profile=json.loads((TASK/'ssh-profile.json').read_text())['selected_profile']
    for attempt in range(3):
        r=subprocess.run(['rtk','proxy','ssh','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes',
            '-o','ConnectTimeout=10','-o','ConnectionAttempts=1',profile,'python3 -B -'],input=source.encode(),capture_output=True,timeout=timeout)
        if r.returncode==0:return json.loads(r.stdout)
        error=r.stderr.decode(errors='replace')
        # A TCP connect timeout proves no SSH session/remote command began. Never
        # retry authenticated channel failure, unknown completion or partial output.
        safe=(r.returncode==255 and not r.stdout and 'ssh: connect to host ' in error and 'port 22: Connection timed out' in error)
        with (TASK/'ssh-transport-errors.jsonl').open('a',encoding='utf-8',newline='\n') as f:
            f.write(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
              'connection_attempt':attempt+1,'exit_code':r.returncode,'error':error[-1000:],
              'no_ssh_session_established':safe,'same_payload_retry':safe and attempt<2})+'\n')
        assert safe and attempt<2,error[-1000:]


def collect(names):
    assert len(names)<=3 and all('/'not in n and '..'not in n for n in names)
    code='''import json,os,subprocess
from pathlib import Path
os.sched_setaffinity(0,{69});root=Path(__ROOT__);names=__NAMES__;rows=[]
assert root.resolve()==root and root==Path.home()/'curaloop-tasks/m2-costed-20261108-v2'
for name in names:
 job=root/'jobs'/name;row={'job':name,'job_exists':job.exists()}
 for key in ('resource','kernel-proof','result','failure','controller-result'):
  p=job/(key+'.json')
  if p.exists():row[key]=json.loads(p.read_text())
 env=os.environ.copy();env['XDG_RUNTIME_DIR']='/run/user/'+str(os.getuid());env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+env['XDG_RUNTIME_DIR']+'/bus'
 p=subprocess.run(['systemctl','--user','show','curaloop-m2c-20261108-v1-'+name],capture_output=True,text=True,env=env,timeout=10)
 state=dict(s.split('=',1) for s in p.stdout.splitlines() if '=' in s)
 row['unit_state']={k:state.get(k) for k in ('LoadState','ActiveState','SubState','Result')};rows.append(row)
print(json.dumps({'results':rows}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__NAMES__',repr(names))
    return ssh_script(code,timeout=45)


def save_collected(row):
    job=TASK/'jobs'/row['job']
    with (job/'recovered-controller-result.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(row,f,indent=2);f.write('\n')
    for key in('resource','kernel-proof','result','failure'):
        if key in row:
            p=job/(key+'.json')
            if p.exists():assert json.loads(p.read_text())==row[key]
            else:
                with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(row[key],f,indent=2);f.write('\n')


def batch(names,action='calibration',retained_proof=None):
    proof=json.loads(Path(retained_proof).read_text()) if retained_proof else None
    if proof:
        assert action=='worker' and proof['status']=='PASS_FRESH_V5_LOCAL_ABSENCE_AND_NOT_DISPATCHED'
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(proof['utc'])).total_seconds()
        assert 0<=age<300,'FIRST_DISPATCH_ABSENCE_PROOF_EXPIRED'
    scripts=[]
    for name in names:
        if proof and name in proof['reserved_not_dispatched_jobs']:
            row=next(r for r in proof['fresh_not_dispatched_proofs'] if r['job']==name)
            assert not row['job_exists'] and row['unit_state']['LoadState']=='not-found' and row['unit_state']['ActiveState']=='inactive'
            job=TASK/'jobs'/name;pin=proof['local_prepared_pins'][name]
            assert hashlib.sha256((job/'permit.json').read_bytes()).hexdigest()==pin['permit_sha256']
            source,permit=render_dispatch(action,name);path=job/'remote-command.py'
            if pin['command_sha256']is not None:
                assert hashlib.sha256(path.read_bytes()).hexdigest()==pin['command_sha256']
                assert path.read_text()==source,'RETAINED_COMMAND_DIFFERS_FROM_AUTHENTICATED_PERMIT'
                scripts.append(source)
            else:
                assert not path.exists();scripts.append(dispatch(action,name,prepare_only=True))
        else:scripts.append(dispatch(action,name,prepare_only=True))
    # Each namespace gets its own permit/environment and service; no shared policy state.
    scripts=[s.replace('print(json.dumps(out))','') for s in scripts]
    code='''import base64,concurrent.futures,json,os,resource,time
os.sched_setaffinity(0,{69});os.nice(19);resource.setrlimit(resource.RLIMIT_CPU,(30,30))
resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
scripts=__SCRIPTS__;before=time.process_time();child0=resource.getrusage(resource.RUSAGE_CHILDREN)
def run(encoded):
 scope={};exec(base64.b64decode(encoded),scope);return scope['out']
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(run,scripts))
child1=resource.getrusage(resource.RUSAGE_CHILDREN)
print(json.dumps({'results':rows,'orchestration_cpu_seconds':time.process_time()-before+child1.ru_utime+child1.ru_stime-child0.ru_utime-child0.ru_stime,
 'orchestration_affinity':sorted(os.sched_getaffinity(0))}))
'''.replace('__SCRIPTS__',repr([base64.b64encode(s.encode()).decode() for s in scripts]))
    permits=[json.loads((TASK/'jobs'/name/'permit.json').read_text()) for name in names]
    out=ssh_script(code,timeout=max(p['wall_seconds'] for p in permits)+45)
    with (TASK/'batch-orchestration.jsonl').open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(out)+'\n')
    for name,result in zip(names,out['results']):
        assert result['unit'].endswith(name)
        job=TASK/'jobs'/name
        with (job/'batch-controller-result.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
        for key in('resource','kernel-proof','result','failure'):
            if key in result:
                with (job/(key+'.json')).open('x',encoding='utf-8',newline='\n') as f:json.dump(result[key],f,indent=2);f.write('\n')
    return out
