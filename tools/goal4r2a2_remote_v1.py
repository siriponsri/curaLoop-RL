"""Bounded new-root transport/controller; no activity inputs or credential changes."""

import argparse
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from tools.remote_goal4_control_v1 import HOST, OPTIONS, PREFLIGHT, ssh_script
from tools.goal4r1_remote_v1 import decode_helper_output

ROOT = Path(__file__).resolve().parents[1]
REMOTE = '/home/chaw/curaloop-rl/goal4r2a2-20261106-v1'
PACKET = ROOT / 'docs/evidence/goal4r2a2-20261106-v1'
LOCAL = ROOT / '.local/goal4r2a2-20261106-v1'
DEADLINE = datetime(2026, 11, 6, 13, 5, 41, tzinfo=timezone.utc)


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')


def bundle(name):
    files = [ROOT / 'research/__init__.py',
             ROOT / 'research/configs/goal4r2a2_cases_v1.json',
             ROOT / 'research/configs/goal4r2a2_requests_v1.json',
             ROOT / 'research/manifests/goal4r2a2_benchmark_readiness_v1.json',
             ROOT / 'docs/evidence/goal4r2a-20261106-v1/si-metadata-audit-v1.json',
             PACKET / 'cases-freeze-v1.json', ROOT / 'tools/goal4r2a2_worker_v1.py',
             ROOT / 'tools/remote_task_archive_v1.py', ROOT / 'tools/goal4r2a2_return_v1.py']
    files += sorted((ROOT / 'research/readiness_v1').glob('*.py'))
    if (ROOT / 'tests/research/test_readiness_v1.py').exists():
        files += [ROOT / 'tests/research/test_readiness_v1.py']
    inputs = [(p, p.relative_to(ROOT).as_posix()) for p in files]
    inputs += [(LOCAL / 'private-tools/pubchem_rest_request.py', 'private-tools/pubchem_rest_request.py')]
    rows = []
    LOCAL.mkdir(parents=True, exist_ok=True)
    archive = LOCAL / (name + '.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as zipped:
        for path, rel in inputs:
            data = path.read_bytes()
            rows.append({'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
            zipped.writestr(rel, data)
    manifest = {'status': 'SOURCE_AND_FIXTURE_BUNDLE_NO_ACTIVITY_ROWS', 'files': rows,
                'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                'utc': datetime.now(timezone.utc).isoformat()}
    write_new(LOCAL / (name + '.json'), manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['preflight', 'create', 'bundle', 'upload', 'unpack', 'run', 'return', 'absence'])
    parser.add_argument('--name')
    parser.add_argument('--attempt')
    parser.add_argument('--mode', choices=['probe', 'acquire', 'validate'], default='probe')
    parser.add_argument('--operation', choices=['snapshot', 'delete'])
    args = parser.parse_args()
    if datetime.now(timezone.utc) >= DEADLINE and args.action not in ('return', 'absence'):
        raise RuntimeError('No new processing after owner deadline')
    if args.name and not args.name.replace('-', '').isalnum():
        raise ValueError('Explicit safe bundle name required')
    if args.action == 'preflight':
        result = decode_helper_output(ssh_script(PREFLIGHT.replace('/home/chaw/curaloop-rl/plan-a-20261105-v2', REMOTE)))
        write_new(PACKET / 'remote-preflight-v1.json', result)
    elif args.action == 'create':
        pre = json.loads((PACKET / 'remote-preflight-v1.json').read_text())
        if pre['status'] != 'PASS_READ_ONLY_PREFLIGHT' or pre['task_root_exists']:
            raise ValueError('Fresh root preflight required')
        source = "import os,json; from pathlib import Path; p=Path(" + repr(REMOTE) + "); assert p.parent.resolve()==p.parent and p.parent.stat().st_uid==os.getuid(); os.umask(0o077); p.mkdir(exist_ok=False); print(json.dumps({'status':'PASS_NEW_OWNED_ROOT','root':str(p)}))"
        result = decode_helper_output(ssh_script(source))
        write_new(PACKET / 'remote-created-v1.json', result)
    elif args.action == 'bundle':
        result = bundle(args.name)
    elif args.action == 'upload':
        subprocess.run(['scp', *OPTIONS, str(LOCAL / (args.name + '.zip')),
                        str(LOCAL / (args.name + '.json')), HOST + ':' + REMOTE + '/'], check=True)
        result = {'status': 'PASS_SOURCE_BUNDLE_TRANSFER', 'name': args.name}
    elif args.action == 'unpack':
        expected = json.loads((LOCAL / (args.name + '.json')).read_text())['archive_sha256']
        source = '''
import hashlib,json,os,shutil,zipfile
from pathlib import Path,PurePosixPath
root=Path(REMOTE)
assert root.resolve()==root and root.stat().st_uid==os.getuid()
manifest=json.loads((root/(NAME+'.json')).read_text())
assert hashlib.sha256((root/(NAME+'.zip')).read_bytes()).hexdigest()==EXPECTED==manifest['archive_sha256']
rows={r['path']:r for r in manifest['files']}
assert len(rows)==len(manifest['files'])<=100
with zipfile.ZipFile(root/(NAME+'.zip')) as archive:
 assert len(archive.infolist())==len(rows) and set(archive.namelist())==set(rows)
 assert sum(i.file_size for i in archive.infolist())<=5*1024**2
 for info in archive.infolist():
  rel=PurePosixPath(info.filename)
  assert not rel.is_absolute() and '..' not in rel.parts and '\\\\' not in info.filename and not info.is_dir()
  data=archive.read(info)
  assert len(data)==rows[info.filename]['bytes']<=1024**2 and hashlib.sha256(data).hexdigest()==rows[info.filename]['sha256']
  path=root/info.filename
  assert path.resolve().is_relative_to(root) and not path.is_symlink()
  if path.exists():
   if path.read_bytes()==data: continue
   old=root/'source-history'/NAME/info.filename
   old.parent.mkdir(parents=True,exist_ok=True)
   assert not old.exists()
   shutil.copy2(path,old)
  path.parent.mkdir(parents=True,exist_ok=True)
  path.write_bytes(data)
print(json.dumps({'status':'PASS_CLOSED_SOURCE_UNPACK','name':NAME,'files':len(rows),'sha256':EXPECTED}))
'''
        prefix = 'REMOTE=' + repr(REMOTE) + '\nNAME=' + repr(args.name) + '\nEXPECTED=' + repr(expected) + '\n'
        result = decode_helper_output(ssh_script(prefix + source))
        write_new(PACKET / (args.name + '-unpacked.json'), result)
    elif args.action == 'run':
        if not args.attempt or not args.attempt.replace('-', '').isalnum():
            raise ValueError('Explicit immutable attempt name required')
        source = '''
import fcntl,json,os,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
root=Path(REMOTE)
assert root.resolve()==root and root.stat().st_uid==os.getuid()
os.chdir(root)
with (root/'.execution.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 ledgerpath=root/'launch-ledger.json'
 ledger=json.loads(ledgerpath.read_text()) if ledgerpath.exists() else []
 assert datetime.now(timezone.utc).isoformat()<'2026-11-06T13:05:41+00:00'
 assert len(ledger)<6 and not any(r['attempt']==ATTEMPT or r['status']=='RESERVED' for r in ledger)
 assert sum(r.get('mode','legacy')==MODE for r in ledger)<3
 assert sum(r['reserved_cpu_seconds'] for r in ledger)+120<=10800
 record={'attempt':ATTEMPT,'bundle':NAME,'mode':MODE,'reserved_cpu_seconds':120,'status':'RESERVED','utc':datetime.now(timezone.utc).isoformat()}
 ledger.append(record)
 def save():
  temporary=ledgerpath.with_suffix('.tmp')
  with temporary.open('w') as handle: json.dump(ledger,handle,indent=2);handle.flush();os.fsync(handle.fileno())
  os.replace(temporary,ledgerpath)
 save()
 try:
  command=['python3','-B','-m','tools.goal4r2a2_worker_v1','--attempt',ATTEMPT,'--bundle',NAME,'--mode',MODE]
  p=subprocess.run(command,cwd=root,timeout=620,capture_output=True,text=True)
 except BaseException:
  # No receipt/ambiguous launch keeps its full unresolved reservation.
  raise
 receipt=root/'runs'/ATTEMPT/'resources.json'
 assert receipt.is_file()
 measured=json.loads(receipt.read_text())
 record.update(status='COMPLETED',exit_code=p.returncode,actual_cpu_seconds=measured['cpu_seconds'])
 save()
 print(json.dumps({'status':'PASS' if p.returncode==0 else 'FAIL','attempt':ATTEMPT,'exit_code':p.returncode,'resources':measured,'stdout':p.stdout,'stderr':p.stderr}))
'''
        prefix = 'REMOTE=' + repr(REMOTE) + '\nNAME=' + repr(args.name) + '\nATTEMPT=' + repr(args.attempt) + '\nMODE=' + repr(args.mode) + '\n'
        result = decode_helper_output(ssh_script(prefix + source, timeout=650))
        write_new(PACKET / (args.attempt + '-remote.json'), result)
    elif args.action == 'return':
        source = "import os,subprocess; os.chdir('/home/chaw/curaloop-rl'); p=subprocess.run(['flock','-n'," + repr(REMOTE + '/.execution.lock') + ",'python3'," + repr(REMOTE + '/tools/goal4r2a2_return_v1.py') + "," + repr(args.operation) + "]); raise SystemExit(p.returncode)"
        result = decode_helper_output(ssh_script(source, timeout=300))
        write_new(PACKET / ('remote-' + args.operation + '-v1.json'), result)
    else:
        source = "import json; from datetime import datetime,timezone; from pathlib import Path; paths=[Path(" + repr(REMOTE) + "),Path(" + repr(REMOTE + '-return') + ")]; print(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'status':'PASS_SCOPED_ROOTS_ABSENT' if all(not p.exists() and not p.is_symlink() for p in paths) else 'FAIL','paths':{str(p):{'exists':p.exists(),'is_symlink':p.is_symlink()} for p in paths}}))"
        result = decode_helper_output(ssh_script(source))
        write_new(PACKET / 'remote-absence-v1.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
