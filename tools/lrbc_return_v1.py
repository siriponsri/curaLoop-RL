"""Complete owned B return, full reread, then exact guarded remote cleanup."""

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.lrbc_admin_v3 import PRIVATE, PUBLIC, REMOTE, HOST, OPTIONS, ssh, write
from research.longrun_v1.coordinator import Coordinator

EXPORT = REMOTE + '-return'

CHECK = '''
import os,json,hashlib,stat,time
from pathlib import Path
root=Path(__TASK_ROOT__);export=Path(__EXPORT_ROOT__)
assert root==Path('/home/chaw/curaloop-rl/lrbc-20261106-v1') and export==Path('/home/chaw/curaloop-rl/lrbc-20261106-v1-return')
assert root.resolve()==root and not root.is_symlink() and root.stat().st_uid==os.getuid()
active=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  cmd=(p/'cmdline').read_bytes().split(bytes([0]))
  if any(str(root).encode() in value for value in cmd):active.append(int(p.name))
 except (OSError,ValueError):pass
assert not active,'Owned task process still active'
rows=[];fold=set()
reserved={'CON','PRN','AUX','NUL'}|{a+str(i) for a in ['COM','LPT'] for i in range(1,10)}
for parent,dirs,files in os.walk(root,followlinks=False):
 for name in dirs+files:
  p=Path(parent)/name;s=p.lstat();assert s.st_uid==os.getuid() and not stat.S_ISLNK(s.st_mode)
  rel=p.relative_to(root).as_posix()
  assert not any(part.endswith((' ','.')) or part.split('.')[0].upper() in reserved or any(ord(c)<32 or c in '<>:"\\\\|?*' for c in part) for part in rel.split('/'))
  assert stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode)
  if stat.S_ISREG(s.st_mode):
   assert rel.casefold() not in fold;fold.add(rel.casefold())
   raw=p.read_bytes();rows.append({'path':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
rows.sort(key=lambda r:r['path'])
assert len(rows)<10000 and sum(r['bytes'] for r in rows)<50*1024**2
'''.replace('__TASK_ROOT__', repr(REMOTE)).replace('__EXPORT_ROOT__', repr(EXPORT))


def preserve():
    snap = Coordinator(PRIVATE / 'coordinator.sqlite').snapshot()
    assert all(r['state'] in ('COMPLETED', 'FAILED', 'FAILED_RECONCILED') for r in snap['jobs'])
    source = sqlite3.connect(PRIVATE / 'coordinator.sqlite')
    destination = sqlite3.connect(PRIVATE / 'coordinator-before-c.sqlite')
    with destination: source.backup(destination)
    destination.close(); source.close()
    code = CHECK + '''
import zipfile
assert not export.exists() and not export.is_symlink()
assert export.parent.resolve()==Path('/home/chaw/curaloop-rl') and export.parent.stat().st_uid==os.getuid()
os.umask(0o077);export.mkdir()
archive=export/'full-v1.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for row in rows:z.write(root/row['path'],row['path'])
manifest={'schema':'curaloop.lrbc.complete-return.v1','root':str(root),'export':str(export),
 'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'files':rows,'file_count':len(rows),
 'total_bytes':sum(r['bytes'] for r in rows),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
(export/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\\n')
print(json.dumps(manifest))
'''
    manifest = ssh(code)
    write(PRIVATE / 'remote-return-manifest.json', manifest)
    archive = PRIVATE / 'remote-return-full-v1.zip'
    result = subprocess.run(['scp', *OPTIONS, HOST + ':' + EXPORT + '/full-v1.zip', str(archive)], capture_output=True, timeout=60)
    if result.returncode:
        (PRIVATE / 'return-transport-error.txt').write_bytes(result.stderr)
        raise RuntimeError('Complete return transport failed; no deletion authorized')
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    target = PRIVATE / 'remote-return/full-v1/files'
    target.mkdir(parents=True, exist_ok=False)
    pins = {r['path']: r for r in manifest['files']}
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist()) == len(set(z.namelist())) and set(z.namelist()) == set(pins)
        for info in z.infolist():
            name = PurePosixPath(info.filename)
            assert not name.is_absolute() and '..' not in name.parts and '\\' not in info.filename
            assert not info.is_dir() and ((info.external_attr >> 16) & 0o170000) in (0, 0o100000)
            raw = z.read(info)
            assert len(raw) == pins[info.filename]['bytes'] and hashlib.sha256(raw).hexdigest() == pins[info.filename]['sha256']
            path = target / info.filename; path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as handle: handle.write(raw)
    # Complete second pass from extracted local disk, not archive metadata alone.
    assert {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()} == set(pins)
    for name, pin in pins.items():
        raw = (target / name).read_bytes()
        assert len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256']
    write(PUBLIC / 'complete-return-verified-v1.json', {'status': 'PASS_COMPLETE_RETURN_AND_LOCAL_REREAD',
          'file_count': manifest['file_count'], 'total_bytes': manifest['total_bytes'],
          'archive_sha256': manifest['archive_sha256'], 'manifest_sha256': hashlib.sha256((PRIVATE / 'remote-return-manifest.json').read_bytes()).hexdigest(),
          'raw_source_inputs_private': True, 'all_owned_code_inputs_outputs_archives_logs_included': True,
          'preexisting_os_libraries_not_owned_or_deleted': True})
    print('Complete return and full local reread verified', manifest['file_count'], manifest['total_bytes'])


def cleanup():
    proof = json.loads((PUBLIC / 'complete-return-verified-v1.json').read_text())
    assert proof['status'] == 'PASS_COMPLETE_RETURN_AND_LOCAL_REREAD'
    manifest = json.loads((PRIVATE / 'remote-return-manifest.json').read_text())
    # Reread retained files again immediately before authorizing remote deletion.
    target = PRIVATE / 'remote-return/full-v1/files'
    for row in manifest['files']:
        p = target / row['path']; assert p.is_file() and not p.is_symlink()
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']
    code = CHECK + '''
import shutil
assert export.resolve()==export and export.stat().st_uid==os.getuid() and not export.is_symlink()
old=json.loads((export/'manifest.json').read_text())
assert rows==old['files'] and old['archive_sha256']==__ARCHIVE_SHA__
assert hashlib.sha256((export/'full-v1.zip').read_bytes()).hexdigest()==__ARCHIVE_SHA__
assert set(p.name for p in export.iterdir())=={'manifest.json','full-v1.zip'}
shutil.rmtree(root);shutil.rmtree(export)
print(json.dumps({'status':'PASS_EXACT_SCOPED_DELETE_AFTER_COMPLETE_RETURN','root':str(root),'export':str(export)}))
'''.replace('__ARCHIVE_SHA__', repr(proof['archive_sha256']))
    write(PUBLIC / 'scoped-delete-v1.json', ssh(code))
    absence = ssh('''
import json,time
from pathlib import Path
paths=[Path(__TASK_ROOT__),Path(__EXPORT_ROOT__)]
assert all(not p.exists() and not p.is_symlink() for p in paths)
print(json.dumps({'status':'PASS_FRESH_SCOPED_ABSENCE','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'absent_paths':[str(p) for p in paths]}))
'''.replace('__TASK_ROOT__', repr(REMOTE)).replace('__EXPORT_ROOT__', repr(EXPORT)))
    write(PUBLIC / 'fresh-absence-v1.json', absence)
    print(json.dumps(absence))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('action', choices=['preserve', 'cleanup']); args = p.parse_args()
    preserve() if args.action == 'preserve' else cleanup()
