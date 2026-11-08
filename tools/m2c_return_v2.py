"""Complete private return and exact cleanup for the single M2 owned root."""

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local/m2-costed-20261108-v2'
REMOTE = '/home/chaw/curaloop-tasks/m2-costed-20261108-v2'
EXPORT = REMOTE + '-export-v1'
PROFILE = '100.77.149.83'
OPTIONS = ['-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
           '-o', 'ConnectTimeout=10', '-o', 'ConnectionAttempts=1']
PUBLIC = ROOT / 'docs/evidence/m2-costed-20261108-v2'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def ssh(code, timeout=60):
    code='import os,resource;os.sched_setaffinity(0,{69});resource.setrlimit(resource.RLIMIT_CPU,(30,30))\n'+code
    raw = base64.b64encode(code.encode()).decode()
    command = "python3 -B -c 'exec(__import__(\"base64\").b64decode(\"" + raw + "\"))'"
    assert len(command) < 28000
    r = subprocess.run(['rtk', 'proxy', 'ssh', *OPTIONS, PROFILE, command],
                       capture_output=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError('SSH_FAILED: ' + r.stderr.decode(errors='replace')[-1000:])
    return json.loads(next(line for line in r.stdout.decode().splitlines() if line.startswith('{')))


EXPORT_BODY = r'''
import hashlib,json,os,resource,signal,stat,sys,tarfile,time
from pathlib import Path
permit=json.loads(Path(sys.argv[1]).read_text());root=Path(permit['task_root']);p=Path(str(root)+'-export-v1')
started=time.monotonic()
resource.setrlimit(resource.RLIMIT_CPU,(int(permit['reservation_seconds'])-1,int(permit['reservation_seconds'])))
resource.setrlimit(resource.RLIMIT_AS,(permit['memory_bytes'],permit['memory_bytes']))
os.sched_setaffinity(0,{permit['cpu']})
def save(name,data):
 with (p/name).open('x') as f:json.dump(data,f,indent=2);f.write('\n')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
status='FAIL'
try:
 assert root==Path('/home/chaw/curaloop-tasks/m2-costed-20261108-v2') and root.resolve()==root
 assert p.is_dir() and not p.is_symlink() and p.stat().st_uid==os.getuid()
 cg=Path('/sys/fs/cgroup'+next(s.split('::',1)[1] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')))
 proof={k:(cg/k).read_text().strip() for k in ('cpu.max','memory.max','memory.swap.max')}
 assert proof=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
 save('kernel-proof.json',proof)
 rows=[];fold=set()
 for parent,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   f=Path(parent)/name;s=f.lstat();rel=f.relative_to(root).as_posix()
   assert s.st_uid==os.getuid() and not stat.S_ISLNK(s.st_mode)
   assert rel.casefold() not in fold;fold.add(rel.casefold())
   assert stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode)
   if stat.S_ISREG(s.st_mode):rows.append({'path':rel,'bytes':s.st_size,'sha256':sha(f)})
 rows.sort(key=lambda r:r['path'])
 assert len(rows)<100000 and sum(r['bytes'] for r in rows)<4*1024**3
 archive=p/'full-task-v1.tar.gz'
 with tarfile.open(archive,'x:gz',compresslevel=1) as tf:
  for row in rows:tf.add(root/row['path'],arcname=row['path'],recursive=False)
 assert archive.stat().st_size<1024**3
 manifest={'schema':'curaloop.m2_costed.complete_return.v1','root':str(root),'export':str(p),
  'files':rows,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),
  'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive)}
 save('manifest.json',manifest)
 save('result.json',{'status':'PASS_COMPLETE_PRIVATE_EXPORT','file_count':len(rows),
  'archive_bytes':manifest['archive_bytes'],'archive_sha256':manifest['archive_sha256'],
  'manifest_sha256':sha(p/'manifest.json')})
 status='PASS'
finally:
 save('resource.json',{'schema':'curaloop.m2_costed.resources.v1','attempt':permit['attempt'],
  'host':'dr-train','status':status,'cpu_seconds':time.process_time(),
  'wall_seconds':time.monotonic()-started,'reservation_seconds':permit['reservation_seconds'],
  'actual_cpu_affinity':sorted(os.sched_getaffinity(0))})
'''

CLEANUP_BODY = r'''
import hashlib,json,os,resource,shutil,stat,sys,time
from datetime import datetime,timezone
from pathlib import Path
auth=json.loads(sys.argv[1]);root=Path(auth['root']);p=Path(auth['export']);started=time.process_time()
assert root==Path('/home/chaw/curaloop-tasks/m2-costed-20261108-v2') and p==Path(str(root)+'-export-v1')
assert datetime.now(timezone.utc)<datetime.fromisoformat('2026-11-12T08:17:29+00:00')
resource.setrlimit(resource.RLIMIT_CPU,(59,60));resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296))
os.sched_setaffinity(0,{auth['cpu']})
cg=Path('/sys/fs/cgroup'+next(s.split('::',1)[1] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')))
proof={k:(cg/k).read_text().strip() for k in ('cpu.max','memory.max','memory.swap.max')}
assert proof=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
for path in (root,p):
 assert path.resolve()==path and not path.is_symlink() and path.stat().st_uid==os.getuid()
 assert path.parent.resolve()==Path('/home/chaw/curaloop-tasks')
assert sha(p/'manifest.json')==auth['manifest_sha256']
manifest=json.loads((p/'manifest.json').read_text());expected={r['path']:r for r in manifest['files']}
current={}
for parent,dirs,files in os.walk(root,followlinks=False):
 for name in dirs+files:
  path=Path(parent)/name;s=path.lstat()
  assert s.st_uid==os.getuid() and (stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode))
  if stat.S_ISREG(s.st_mode):current[path.relative_to(root).as_posix()]=path
assert set(current)==set(expected)
for rel,path in current.items():assert path.stat().st_size==expected[rel]['bytes'] and sha(path)==expected[rel]['sha256']
assert {f.name for f in p.iterdir()}==set(auth['export_file_pins'])
for name,pin in auth['export_file_pins'].items():
 path=p/name;assert path.is_file() and not path.is_symlink()
 assert path.stat().st_size==pin['bytes'] and sha(path)==pin['sha256']
assert (root/'return-dispatch-v1/cleanup-payload.py').read_text()==auth['cleanup_source']
shutil.rmtree(root);shutil.rmtree(p)
assert not root.exists() and not p.exists()
print(json.dumps({'status':'PASS_EXACT_DELETE_AFTER_FULL_RETURN','root':str(root),'export':str(p),
 'kernel':proof,'actual_cpu_affinity':sorted(os.sched_getaffinity(0)),
 'cpu_seconds':time.process_time()-started,'attempt':auth['attempt'],'host':'dr-train',
 'resource_status':'PASS','utc':datetime.now(timezone.utc).isoformat()}))
'''


def launch(code, *, unit, cpu, wall, working, args):
    return ssh('''import base64,json,os,subprocess
env=os.environ.copy();env['XDG_RUNTIME_DIR']='/run/user/'+str(os.getuid());env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+env['XDG_RUNTIME_DIR']+'/bus'
unit=__UNIT__
r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,env=env,timeout=10)
assert 'LoadState=not-found' in r.stdout
cmd=['systemd-run','--user','--no-ask-password','--wait','--pipe','--service-type=exec','--unit='+unit,'--working-directory='+__WORKING__]
props={'CPUQuota':'100%','CPUQuotaPeriodSec':'100ms','CPUAffinity':str(__CPU__),
 'MemoryMax':'4294967296','MemorySwapMax':'0','Nice':'19','TasksMax':'8',
 'RuntimeMaxSec':str(__WALL__)+'s','TimeoutStopSec':'5s','KillMode':'control-group','Restart':'no','UMask':'0077'}
for k,v in props.items():cmd+=['-p',k+'='+v]
cmd+=__ARGS__
r=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=__WALL__+20)
state=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,env=env,timeout=10)
s=dict(line.split('=',1) for line in state.stdout.splitlines() if '=' in line)
assert s.get('ActiveState')=='inactive' and s.get('SubState')=='dead'
out={'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'unit':unit,'terminal_state':{'active':s.get('ActiveState'),'sub':s.get('SubState')}}
__AFTER__
print(json.dumps(out))
'''.replace('__UNIT__', repr(unit)).replace('__WORKING__', repr(working))
               .replace('__CPU__', repr(cpu)).replace('__WALL__', repr(wall))
               .replace('__ARGS__', repr(args)).replace('__AFTER__', code), timeout=wall + 45)


def export():
    job = LOCAL / 'jobs/return-export-v1'
    permit = json.loads((job / 'permit.json').read_text())
    assert permit['task_root'] == REMOTE and permit['wall_seconds'] == 600
    result = ssh('''import json,os,shutil,subprocess
from pathlib import Path
root=Path(__ROOT__);p=Path(__EXPORT__)
assert root.resolve()==root and root.is_dir() and not root.is_symlink()
assert shutil.disk_usage(root).free>2*1024**3
r=subprocess.run(['systemctl','--user','list-units','--no-legend','--plain','--state=running,activating,deactivating','curaloop-m2c-20261108-v1-*'],capture_output=True,text=True,timeout=10)
assert r.returncode==0 and not r.stdout.strip(),'Owned worker still active'
d=root/'return-dispatch-v1';d.mkdir(exist_ok=False)
(d/'export-payload.py').write_text(__BODY__)
(d/'cleanup-payload.py').write_text(__CLEANUP__)
p.mkdir(exist_ok=False);p.chmod(0o700)
(p/'permit.json').write_text(json.dumps(__PERMIT__,indent=2)+'\\n')
print(json.dumps({'status':'PASS_FROZEN_SOURCE_AND_QUIESCENCE'}))
'''.replace('__ROOT__', repr(REMOTE)).replace('__EXPORT__', repr(EXPORT))
                 .replace('__BODY__', repr(EXPORT_BODY)).replace('__CLEANUP__', repr(CLEANUP_BODY))
                 .replace('__PERMIT__', repr(permit)))
    new(job / 'quiescence.json', result)
    out = launch('''from pathlib import Path
p=Path(__EXPORT__)
for key in ('resource','result','kernel-proof'):
 f=p/(key+'.json')
 if f.exists():out[key]=json.loads(f.read_text())
(p/'terminal.json').write_text(json.dumps(out,indent=2)+'\\n')
'''.replace('__EXPORT__', repr(EXPORT)), unit='curaloop-m2c-return-export-v1',
                 cpu=permit['cpu'], wall=600, working=REMOTE,
                 args=['--', '/usr/bin/python3', '-B', REMOTE + '/return-dispatch-v1/export-payload.py',
                       EXPORT + '/permit.json'])
    new(job / 'remote-terminal.json', out)
    for name in ('resource', 'result', 'kernel-proof'):
        if name in out:
            new(job / (name + '.json'), out[name])
    assert out['exit_code'] == 0 and out['resource']['status'] == 'PASS'
    print(json.dumps(out['result']))


def fetch():
    target=LOCAL/'remote-return';target.mkdir(exist_ok=False)
    export=target/'export';export.mkdir(exist_ok=False)
    data=ssh('''import base64,json,os,resource,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(20,20));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(60)
os.sched_setaffinity(0,{69})
p=Path(__EXPORT__);names={'permit.json','kernel-proof.json','manifest.json','result.json','resource.json','terminal.json','full-task-v1.tar.gz'}
assert p.resolve()==p and not p.is_symlink() and {f.name for f in p.iterdir()}==names
out={}
for name in names-{'full-task-v1.tar.gz'}:
 f=p/name;assert f.is_file() and not f.is_symlink() and f.stat().st_size<16*1024**2
 out[name]=base64.b64encode(f.read_bytes()).decode()
print(json.dumps(out))
'''.replace('__EXPORT__',repr(EXPORT)),timeout=90)
    allowed={'permit.json','kernel-proof.json','manifest.json','result.json','resource.json','terminal.json'}
    assert set(data)==allowed
    for name,encoded in data.items():
        with (export/name).open('xb') as f:f.write(base64.b64decode(encoded))
    manifest=json.loads((export/'manifest.json').read_text())
    result=json.loads((LOCAL/'jobs/return-export-v1/result.json').read_text())
    assert sha(export/'manifest.json')==result['manifest_sha256']
    assert manifest['archive_bytes']<1024**3
    code='''import os,resource,signal,sys
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(59,60));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(1800)
os.sched_setaffinity(0,{69});os.nice(19)
p=Path(__ARCHIVE__);assert p.resolve()==p and not p.is_symlink() and p.stat().st_size==__SIZE__
with p.open('rb') as f:
 for b in iter(lambda:f.read(1048576),b''):sys.stdout.buffer.write(b)
sys.stdout.buffer.flush()
'''.replace('__ARCHIVE__',repr(EXPORT+'/full-task-v1.tar.gz')).replace('__SIZE__',str(manifest['archive_bytes']))
    encoded=base64.b64encode(code.encode()).decode()
    command="python3 -B -c 'exec(__import__(\"base64\").b64decode(\""+encoded+"\"))'"
    archive=export/'full-task-v1.tar.gz'
    with archive.open('xb') as stream:
        r=subprocess.run(['rtk','proxy','ssh',*OPTIONS,PROFILE,command],stdout=stream,stderr=subprocess.PIPE,timeout=1830)
    receipt={'status':'PASS_TRANSFER_PENDING_FULL_REREAD' if r.returncode==0 else 'FAIL_TRANSFER',
             'exit_code':r.returncode,'stderr':r.stderr.decode(errors='replace'),'transport':'binary SSH stream',
             'bytes':archive.stat().st_size,'sha256':sha(archive)}
    new(target/'transport-receipt.json',receipt)
    assert r.returncode==0 and archive.stat().st_size==manifest['archive_bytes'] and sha(archive)==manifest['archive_sha256']
    print(json.dumps({k:v for k,v in receipt.items() if k!='stderr'}))


def verify():
    sys.path.insert(0, str(ROOT))
    from research.m2_costed_v2.guard import CostedGuard
    job = LOCAL / 'jobs/return-verify-v1'
    permit = json.loads((job / 'permit.json').read_text())
    guard = CostedGuard(job / 'resource.json', permit)
    try:
        new(job / 'kernel-proof.json', guard.kernel_proof())
        target = LOCAL / 'remote-return'
        export = target / 'export'
        manifest = json.loads((export / 'manifest.json').read_text())
        terminal = json.loads((export / 'terminal.json').read_text())
        assert terminal['exit_code'] == 0 and terminal['resource']['status'] == 'PASS'
        assert sha(export / 'manifest.json') == terminal['result']['manifest_sha256']
        archive = export / 'full-task-v1.tar.gz'
        assert archive.stat().st_size == manifest['archive_bytes'] and sha(archive) == manifest['archive_sha256']
        pins = {row['path']: row for row in manifest['files']}
        assert len(pins) == manifest['file_count'] and manifest['root'] == REMOTE and manifest['export'] == EXPORT
        files = target / 'files'
        files.mkdir(exist_ok=False)
        seen, total = set(), 0
        with tarfile.open(archive, 'r|gz') as tf:
            for member in tf:
                rel = PurePosixPath(member.name)
                assert member.isfile() and not rel.is_absolute() and '..' not in rel.parts and '\\' not in member.name
                assert all(part and not any(c in '<>:"|?*' or ord(c) < 32 for c in part)
                           and not part.endswith((' ', '.')) for part in rel.parts)
                assert member.name in pins and member.name not in seen
                row = pins[member.name]
                assert member.size == row['bytes']
                path = files.joinpath(*rel.parts)
                assert path.resolve().is_relative_to(files.resolve())
                path.parent.mkdir(parents=True, exist_ok=True)
                with tf.extractfile(member) as source, path.open('xb') as output:
                    shutil.copyfileobj(source, output, 1048576)
                    output.flush()
                    os.fsync(output.fileno())
                assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
                seen.add(member.name)
                total += row['bytes']
        assert seen == set(pins) and total == manifest['total_bytes']
        for rel, row in pins.items():
            assert sha(files / rel) == row['sha256']  # independent second disk reread
        export_pins = {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in export.iterdir()}
        assert all(p.is_file() and not p.is_symlink() for p in export.iterdir())
        assert (files / 'return-dispatch-v1/cleanup-payload.py').read_text() == CLEANUP_BODY
        receipt = {'status': 'PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD',
                   'file_count': len(pins), 'total_bytes': total,
                   'archive_bytes': manifest['archive_bytes'], 'archive_sha256': manifest['archive_sha256'],
                   'manifest_sha256': sha(export / 'manifest.json'), 'export_file_count': len(export_pins),
                   'all_code_dependency_input_output_regular_files_returned': True,
                   'export_file_pins': export_pins}
        new(target / 'verified-v1.json', receipt)
        new(PUBLIC / 'complete-return-verified-v1.json', receipt)
        guard.finish('PASS')
        print(json.dumps({k: v for k, v in receipt.items() if k != 'export_file_pins'}))
    except BaseException:
        guard.finish('FAIL')
        raise


def cleanup():
    job = LOCAL / 'jobs/remote-exact-cleanup-v1'
    permit = json.loads((job / 'permit.json').read_text())
    proof = json.loads((LOCAL / 'remote-return/verified-v1.json').read_text())
    assert proof['status'] == 'PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD'
    for name, pin in proof['export_file_pins'].items():
        path = LOCAL / 'remote-return/export' / name
        assert path.stat().st_size == pin['bytes'] and sha(path) == pin['sha256']
    auth = {'root': REMOTE, 'export': EXPORT, 'cpu': permit['cpu'], 'attempt': permit['attempt'],
            'manifest_sha256': proof['manifest_sha256'], 'export_file_pins': proof['export_file_pins'],
            'cleanup_source': CLEANUP_BODY}
    encoded = base64.b64encode(CLEANUP_BODY.encode()).decode()
    out = launch('', unit='curaloop-m2c-exact-cleanup-v1', cpu=permit['cpu'], wall=120,
                 working='/home/chaw/curaloop-tasks', args=['--', '/usr/bin/python3', '-B', '-c',
                 'import base64;exec(base64.b64decode(' + repr(encoded) + '))', json.dumps(auth)])
    new(job / 'remote-terminal.json', out)
    assert out['exit_code'] == 0
    result = json.loads(next(line for line in out['stdout'].splitlines() if line.startswith('{')))
    new(PUBLIC / 'scoped-delete-v1.json', result)
    new(job / 'resource.json', dict(result, status='PASS'))
    absence = ssh('import json;from pathlib import Path;paths=' + repr([REMOTE, EXPORT]) +
                  ';assert all(not Path(p).exists() and not Path(p).is_symlink() for p in paths);'
                  'print(json.dumps({"status":"PASS_FRESH_EXACT_ABSENCE","paths":paths}))')
    new(PUBLIC / 'fresh-absence-v1.json', absence)
    print(json.dumps(absence))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['export', 'fetch', 'verify', 'cleanup'])
    args = parser.parse_args()
    if args.action=='fetch':
        sys.path.insert(0,str(ROOT))
        from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
        guard=OrchestrationGuard(LOCAL/'return-fetch-orchestration-resource.json',120,'2026-11-12T08:17:29Z')
        try:
            fetch();guard.finish('PASS')
            accounting=json.loads((LOCAL/'return-fetch-orchestration-resource.json').read_text())
            permit=json.loads((LOCAL/'jobs/return-fetch-v1/permit.json').read_text())
            new(LOCAL/'jobs/return-fetch-v1/resource.json',{'schema':'curaloop.m2_costed.resources.v2',
              'attempt':'return-fetch-v1','host':'local','status':'PASS',
              'cpu_seconds':accounting['aggregate_cpu_seconds'],'reservation_seconds':permit['reservation_seconds'],
              'cpu_measurement_scope':'local aggregate controller and SSH clients; remote metadata/stream utilities separately bounded within reservation',
              'local_cpu_envelope_seconds':120,'remote_metadata_cpu_envelope_seconds':30,'remote_stream_cpu_envelope_seconds':60})
        except BaseException:guard.finish('FAIL_TRANSFER');raise
    else:globals()[args.action]()
