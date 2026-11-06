"""Additive UI process-tree runner. Frozen scientific guards are not reused."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import math
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if sys.flags.optimize:
    raise RuntimeError('Optimized execution is not permitted for this controller')
sys.path.insert(0, str(ROOT))
from research.longrun_v1.coordinator import Coordinator, ACTIVE

PRIVATE = ROOT / '.local/lrbc-ui-20261106-v1'
PUBLIC = ROOT / 'docs/evidence/ui-modern-bilingual-20261106-v1'
DATABASE = ROOT / '.local/lrbc-c-20261106-v1/coordinator.sqlite'
REMOTE = '/home/chaw/curaloop-rl/lrbc-ui-20261106-v1'
HOST = '100.77.149.83'
OPTIONS = ['-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'IdentitiesOnly=yes', '-o', 'ConnectTimeout=10', '-o', 'ConnectionAttempts=1']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())

def ssh(source, timeout=60):
    result = subprocess.run(['ssh', *OPTIONS, HOST, 'python3 -B -'], input=source.encode(), capture_output=True, timeout=timeout)
    if result.returncode:
        PRIVATE.mkdir(parents=True, exist_ok=True)
        name = 'transport-error-' + datetime.now(timezone.utc).strftime('%H%M%S%f') + '.txt'
        (PRIVATE / name).write_bytes(result.stdout + b'\n' + result.stderr)
        raise RuntimeError('SSH error retained privately: ' + name)
    return json.loads(result.stdout)

def amend():
    PRIVATE.mkdir(parents=True, exist_ok=True)
    db = Coordinator(DATABASE)
    with db.transaction() as con:
        cfg = db._meta(con, 'contract')
        expected = json.loads((ROOT/'research/configs/lrbc_c_execution_v1.json').read_text())
        assert cfg == expected, 'Original contract or migration already differs'
        jobs = [dict(r) for r in con.execute('SELECT * FROM jobs')]
        assert len(jobs) == 4 and all(r['state'] not in ACTIVE for r in jobs)
        assert sum(r['reserved'] for r in jobs) == 3600
        assert cfg['historical_cpu_seconds'] == 28800
        assert cfg['r0_utility_reserve_seconds'] == 1800 and cfg['stage_caps_seconds'] == {'C': 171000}
        # Database is quiescent; backup is made through SQLite, not a live file copy.
        backup = PRIVATE/'coordinator-before-ui.sqlite'
        assert not backup.exists()
        src = sqlite3.connect(DATABASE)
        dst = sqlite3.connect(backup)
        src.backup(dst); dst.close(); src.close()
        before = json.loads(json.dumps(cfg))
        cfg['r0_utility_reserve_seconds'] = 3600
        cfg['stage_caps_seconds']['C'] = 169200
        event = {'schema': 'curaloop.ui.accounting-amendment.v1', 'utc': datetime.now(timezone.utc).isoformat(),
                 'authority_sha256': sha((ROOT/'docs/06_execution/UI_REDESIGN_EXECUTION_20261106.md').read_bytes()),
                 'before_contract': before, 'after_contract': cfg, 'previous_jobs_sha256': sha(json.dumps(jobs,sort_keys=True).encode()),
                 'backup_sha256': sha(backup.read_bytes()), 'c_increment_cap_seconds': 172800,
                 'cumulative_conservative_seconds_before_ui_jobs': 36000}
        con.execute('INSERT INTO meta VALUES(?,?)', ('ui_amendment_v1', json.dumps(event,sort_keys=True)))
        con.execute('UPDATE meta SET value=? WHERE key=?', (json.dumps(cfg,sort_keys=True),'contract'))
    write(PUBLIC/'accounting-amendment-v1.json',event)
    print(json.dumps({'status':'PASS_ADDITIVE_MIGRATION','conservative_cpu_hours':10.0}))

def probe():
    result = ssh('''
import json,os,subprocess,sys
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('Optimized probe prohibited')
p=Path('/sys/fs/cgroup'); c=Path('/proc/self/cgroup').read_text()
manager=subprocess.run(['systemctl','--user','show','--property=Version','--value'],capture_output=True,text=True,timeout=10)
print(json.dumps({'uid':os.getuid(),'manager_exit':manager.returncode,'manager_version':manager.stdout.strip(),
'allowed_cpus':sorted(os.sched_getaffinity(0)),'cgroup':c,'memory_available':next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')),
'new_root_exists':Path(__REMOTE__).exists()}))
'''.replace('__REMOTE__',repr(REMOTE)))
    write(PUBLIC/'preflight-ui-v1.json',result)
    print(json.dumps(result))

BOOTSTRAP = '''
import json,os,subprocess,time,sys
from datetime import datetime,timezone
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('Optimized bootstrap prohibited')
p=Path(sys.argv[1]); permit=json.loads((p/'permit.json').read_text())
deadline=time.monotonic()+30
while not (p/'release.json').exists():
 if time.monotonic()>deadline or datetime.now(timezone.utc)>=datetime.fromisoformat(permit['deadline_utc']): raise SystemExit(124)
 time.sleep(.05)
release=json.loads((p/'release.json').read_text());assert release['token']==permit['token']
assert datetime.now(timezone.utc)<datetime.fromisoformat(permit['deadline_utc'])
assert os.sched_getaffinity(0)=={permit['cpu']} and os.getpriority(os.PRIO_PROCESS,0)==19
env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None)
env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
env.update({k:str(v) for k,v in permit['environment'].items()})
result=subprocess.run(permit['argv'],cwd=permit['cwd'],env=env)
(p/'payload-exit.json').write_text(json.dumps({'token':permit['token'],'exit_code':result.returncode}))
raise SystemExit(result.returncode)
'''

def run(attempt, argv, cwd, environment=None):
    assert attempt.replace('-','').isalnum() and attempt.startswith('ui-')
    db = Coordinator(DATABASE)
    with db.transaction() as con:
        amendment=db._meta(con,'ui_amendment_v1');cfg=db._meta(con,'contract')
        assert cfg==amendment['after_contract'] and cfg['r0_utility_reserve_seconds']==3600
        authority=sha((ROOT/'docs/06_execution/UI_AGGREGATE_CPU_AUTHORIZATION_20261106.md').read_bytes())
        prior=con.execute('SELECT value FROM meta WHERE key=?',('ui_aggregate_cpu_authority_v1',)).fetchone()
        if prior: assert json.loads(prior[0])['sha256']==authority
        else: con.execute('INSERT INTO meta VALUES(?,?)',('ui_aggregate_cpu_authority_v1',json.dumps({'sha256':authority,'utc':datetime.now(timezone.utc).isoformat()})))
    available = ssh("from pathlib import Path;import json;print(json.dumps({'bytes':next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))}))")['bytes']
    payload = {'argv': argv, 'cwd': cwd, 'bootstrap_sha256': sha(BOOTSTRAP.encode()), 'environment': environment or {}}
    permit = db.reserve(attempt,'C','dr-train',sha(json.dumps(payload,sort_keys=True).encode()),available)
    runtime = min(840, math.floor((datetime.fromisoformat(permit['deadline_utc'])-datetime.now(timezone.utc)).total_seconds())-30)
    assert runtime >= 60, 'Too little time remains; reservation stays held'
    with db.transaction() as con:
        row = con.execute('SELECT * FROM jobs WHERE attempt=?',(attempt,)).fetchone()
        assert row['state']=='RESERVED' and json.loads(row['permit'])==permit
        permit.update(payload, schema='curaloop.ui.cgroup-permit.v2', child_processes_allowed=True,
                      aggregate_cpu_authority_sha256=authority, hard_cpuset=False,
                      unit='curaloop-'+attempt+'.service', remote_root=REMOTE, runtime_seconds=runtime)
        con.execute('UPDATE jobs SET permit=? WHERE attempt=?',(json.dumps(permit,sort_keys=True),attempt))
    write(PRIVATE/'permits'/(attempt+'.json'),permit)
    source='''
import json,os,time,subprocess,hashlib,sys,math
from datetime import datetime,timezone
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('Optimized remote control prohibited')
root=Path(__REMOTE__);parent=root.parent
assert parent.resolve()==Path('/home/chaw/curaloop-rl') and parent.stat().st_uid==os.getuid()
if not root.exists():
 os.umask(0o077);root.mkdir();(root/'runs').mkdir()
assert root.resolve()==root and root.stat().st_uid==os.getuid()
permit=__PERMIT__;p=root/'runs'/permit['attempt'];p.mkdir(exist_ok=False)
remaining=math.floor((datetime.fromisoformat(permit['deadline_utc'])-datetime.now(timezone.utc)).total_seconds())
actual_runtime=min(permit['runtime_seconds'],remaining-30);assert actual_runtime>=60
(p/'permit.json').write_text(json.dumps(permit,sort_keys=True));(p/'bootstrap.py').write_text(__BOOTSTRAP__)
unit=permit['unit'];cpu=permit['cpu']
existing=subprocess.run(['systemctl','--user','show',unit,'--property=LoadState','--value'],capture_output=True,text=True,timeout=10)
assert existing.stdout.strip()=='not-found', 'Unit collision: no stop or mutation permitted'
props={'ExitType':'cgroup','CPUAccounting':'yes','CPUQuota':'100%','CPUQuotaPeriodSec':'100ms',
'CPUAffinity':str(cpu),'MemoryAccounting':'yes','MemoryMax':'4294967296','MemorySwapMax':'0',
'Nice':'19','TasksMax':'256','RuntimeMaxSec':str(actual_runtime)+'s','TimeoutStartSec':'10s','TimeoutStopSec':'5s',
'KillMode':'control-group','SendSIGKILL':'yes','Restart':'no','OOMPolicy':'kill','UMask':'0077',
'StandardOutput':'append:'+str(p/'stdout-private.txt'),'StandardError':'append:'+str(p/'stderr-private.txt')}
cmd=['systemd-run','--user','--no-ask-password','--unit='+unit,'--service-type=exec','--remain-after-exit','--working-directory='+str(root)]
for k,v in props.items():cmd+=['-p',k+'='+v]
cmd+=['--','/usr/bin/python3','-B',str(p/'bootstrap.py'),str(p)]
start=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
(p/'systemd-start-private.json').write_text(json.dumps({'argv':cmd,'status':start.returncode,'stdout':start.stdout,'stderr':start.stderr}))
def show():
 r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
 return dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
state=show();cg=Path('/sys/fs/cgroup'+state.get('ControlGroup',''))
proof={'permit':permit,'launch_properties':state,'start_status':start.returncode,'caps_verified':False,'owned_invocation':False}
try:
 assert start.returncode==0 and int(state['MainPID'])>0 and state['InvocationID']
 assert cg!=Path('/sys/fs/cgroup') and cg.is_dir()
 pid=int(state['MainPID']);birth=Path('/proc/'+str(pid)+'/stat').read_text().rsplit(')',1)[1].split()[19]
 assert str(p/'bootstrap.py').encode() in Path('/proc/'+str(pid)+'/cmdline').read_bytes().split(bytes([0]))
 proof.update(pid=pid,birth_id=birth,invocation_id=state['InvocationID'])
 proof['owned_invocation']=True
 kernel={n:(cg/n).read_text().strip() for n in ['cpu.max','memory.max','memory.swap.max']}
 proof['kernel']=kernel
 assert kernel=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
 assert os.sched_getaffinity(pid)=={cpu} and os.getpriority(os.PRIO_PROCESS,pid)==19
 proof['caps_verified']=True
 (p/'release.json').write_text(json.dumps({'token':permit['token']}))
 deadline=time.monotonic()+permit['runtime_seconds']+10
 while time.monotonic()<deadline:
  current=show()
  if current.get('SubState') in ['exited','failed','dead'] or current.get('ActiveState') in ['failed','inactive']:break
  time.sleep(.5)
 else:raise RuntimeError('Payload supervision deadline')
except Exception as e:
 proof['error']=type(e).__name__+': '+str(e)
finally:
 final=show();proof['terminal_properties']=final
 assert proof['owned_invocation'] and final.get('InvocationID')==proof['invocation_id'], 'Unowned or changed unit: no stop'
 proof['terminal_cgroup_absent']=not cg.exists()
 if cg.is_dir() and cg!=Path('/sys/fs/cgroup'):
  proof['terminal_kernel']={n:(cg/n).read_text().strip() for n in ['cgroup.events','cpu.stat','memory.peak','memory.events'] if (cg/n).is_file()}
 stop=subprocess.run(['systemctl','--user','stop',unit],capture_output=True,text=True,timeout=15)
 proof['stop_status']=stop.returncode;proof['after_stop']=show()
 proof['populated_after_stop']=(cg/'cgroup.events').read_text().strip() if (cg/'cgroup.events').is_file() else 'CGROUP_ABSENT'
 proof['payload_exit']=json.loads((p/'payload-exit.json').read_text()) if (p/'payload-exit.json').exists() else None
 proof['utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
 (p/'tree-proof.json').write_text(json.dumps(proof,sort_keys=True))
print(json.dumps(proof))
'''.replace('__REMOTE__',repr(REMOTE)).replace('__PERMIT__',repr(permit)).replace('__BOOTSTRAP__',repr(BOOTSTRAP))
    try:
        result=ssh(source,timeout=890)
        write(PRIVATE/'runs'/attempt/'tree-proof.json',result)
        assert result['after_stop'].get('ActiveState') in ['inactive','failed'] or result['after_stop'].get('LoadState')=='not-found'
        assert result['populated_after_stop']=='CGROUP_ABSENT' or 'populated 0' in result['populated_after_stop']
        # Different proof semantics from frozen per-process finish(); never fabricate its receipt.
        terminal=result['terminal_properties']
        natural=(terminal.get('Result')=='success' and terminal.get('SubState')=='exited'
                 and terminal.get('ExecMainStatus')=='0' and terminal.get('InvocationID')==result.get('invocation_id')
                 and terminal.get('ExitType')=='cgroup'
                 and ('populated 0' in result.get('terminal_kernel',{}).get('cgroup.events','')
                      or result.get('terminal_cgroup_absent') is True))
        passed=(result['caps_verified'] and not result.get('error') and natural
                and result['payload_exit'] and result['payload_exit']['token']==permit['token']
                and result['payload_exit']['exit_code']==0)
        raw_usage=result['terminal_properties'].get('CPUUsageNSec')
        assert raw_usage is not None and raw_usage.isdigit(), 'Aggregate CPU accounting unavailable'
        usage=int(raw_usage)/1e9
        cpu_stat=dict(line.split() for line in result.get('terminal_kernel',{}).get('cpu.stat','').splitlines())
        if cpu_stat:
            assert 'usage_usec' in cpu_stat and abs(int(cpu_stat['usage_usec'])/1e6-usage)<1, 'CPU counters disagree'
        else:
            assert terminal.get('ExitType')=='cgroup' and result.get('terminal_cgroup_absent') is True, 'No cgroup-exit proof'
        assert 0<=usage<=permit['reserved_cpu_seconds']
        with db.transaction() as con:
            row=con.execute('SELECT * FROM jobs WHERE attempt=?',(attempt,)).fetchone()
            assert row['state']=='RESERVED' and json.loads(row['permit'])==permit
            con.execute('UPDATE jobs SET state=?,pid=?,birth_id=?,receipt_sha256=?,completion=? WHERE attempt=?',
               ('COMPLETED' if passed else 'FAILED_RECONCILED',result.get('pid'),result.get('birth_id'),sha(json.dumps(result,sort_keys=True).encode()),json.dumps(result,sort_keys=True),attempt))
        safe={'schema':'curaloop.ui.cgroup-result.v1','attempt':attempt,'status':'PASS' if passed else 'FAIL',
              'caps_verified':result['caps_verified'],'unit':permit['unit'],'cpu':permit['cpu'],
              'aggregate_cpu_seconds':usage,'retained_cpu_seconds':900,'all_descendants_absent':True,
              'payload_exit':result['payload_exit'],'error':result.get('error'),'utc':result['utc']}
        write(PUBLIC/(attempt+'-process.json'),safe)
        print(json.dumps(safe))
        return safe
    except BaseException:
        db.mark_unknown(permit)
        raise

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['probe','amend','canary'])
    args=parser.parse_args()
    if args.mode=='probe':probe()
    elif args.mode=='amend':amend()
    else:run('ui-tree-canary-v3',['/usr/bin/python3','-B','-c',"import subprocess,sys;subprocess.run([sys.executable,'-c','import os;print(os.getpid(),sorted(os.sched_getaffinity(0)),os.getpriority(os.PRIO_PROCESS,0))'],check=True)"],REMOTE)
