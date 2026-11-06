"""Partial immediate evidence return; never authorizes remote cleanup."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,REMOTE,HOST,OPTIONS,ssh,write

def fetch(name,paths):
    assert name.replace('-','').isalnum() and paths
    metadata=ssh('''
import json,zipfile,hashlib
from pathlib import Path,PurePosixPath
root=Path(__ROOT__);chosen=[]
for rel in __PATHS__:
 name=PurePosixPath(rel);assert not name.is_absolute() and '..' not in name.parts
 p=root/rel;assert p.exists() and not p.is_symlink()
 chosen.extend(x for x in p.rglob('*') if x.is_file() and not x.is_symlink()) if p.is_dir() else chosen.append(p)
chosen=sorted(set(chosen));assert len(chosen)<=1000 and sum(p.stat().st_size for p in chosen)<64*1024**2
rows=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in chosen]
archive=root/(__NAME__+'.zip')
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
 for p in chosen:z.write(p,p.relative_to(root).as_posix())
print(json.dumps({'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':rows}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__PATHS__',repr(paths)).replace('__NAME__',repr(name)))
    archive=PRIVATE/(name+'.zip')
    if archive.exists():raise ValueError('New return identity required')
    r=subprocess.run(['scp',*OPTIONS,HOST+':'+REMOTE+'/'+name+'.zip',str(archive)],capture_output=True,timeout=120);assert r.returncode==0
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==metadata['archive_sha256']
    target=PRIVATE/name;target.mkdir(exist_ok=False)
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())=={row['path'] for row in metadata['files']}
        for row in metadata['files']:
            path=PurePosixPath(row['path']);assert not path.is_absolute() and '..' not in path.parts
            data=z.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
            p=target/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    for row in metadata['files']:
        p=target/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    write(PRIVATE/(name+'-manifest.json'),dict(metadata,status='PASS_PARTIAL_RETURN_ONLY',cleanup_released=False))
    print(json.dumps({'status':'PASS_PARTIAL_RETURN_ONLY','files':len(metadata['files']),'cleanup_released':False}))

if __name__=='__main__':fetch(sys.argv[1],sys.argv[2:])
