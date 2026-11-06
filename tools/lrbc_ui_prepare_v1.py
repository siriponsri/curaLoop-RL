"""Prepare and transport owned UI sources; heavy steps run in the quota envelope."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,ssh,write,run

SETUP='''
import hashlib,json,os,subprocess,tarfile,urllib.request
from pathlib import Path
root=Path(__ROOT__);software=root/'software';software.mkdir(exist_ok=False)
home=root/'home';home.mkdir(exist_ok=False);cache=root/'cache';cache.mkdir();tmp=root/'tmp';tmp.mkdir()
env=os.environ.copy();env.update(HOME=str(home),TMPDIR=str(tmp),npm_config_cache=str(cache/'npm'),HYPERFRAMES_SKIP_SKILLS='1',CI='1')
def download(url,path,limit):
 with urllib.request.urlopen(url,timeout=30) as response, path.open('xb') as out:
  count=0
  while True:
   chunk=response.read(1024*1024)
   if not chunk:break
   count+=len(chunk);assert count<=limit;out.write(chunk)
 return path
base='https://nodejs.org/dist/v24.19.0/'
checks=download(base+'SHASUMS256.txt',software/'node-SHASUMS256.txt',65536).read_text()
name='node-v24.19.0-linux-x64.tar.xz'
expected=dict((line.split()[1],line.split()[0]) for line in checks.splitlines())[name]
archive=download(base+name,software/name,80*1024**2)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
with tarfile.open(archive) as t:
 for member in t.getmembers():
  assert not member.name.startswith('/') and '..' not in Path(member.name).parts
 t.extractall(software,filter='data')
node=software/'node-v24.19.0-linux-x64/bin';env['PATH']=str(node)+':'+env['PATH']
frontend=root/'source/frontend'
commands=[['npm','install','--package-lock-only','--ignore-scripts','--no-audit','--no-fund'],['npm','ci','--no-audit','--no-fund'],['npm','run','typecheck'],['npm','run','lint'],['npm','run','test','--','--maxWorkers=1'],['npm','run','build']]
results=[]
for index,cmd in enumerate(commands):
 with (root/('setup-command-'+str(index)+'.txt')).open('x') as log:
  result=subprocess.run(cmd,cwd=frontend,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'argv':cmd,'exit_code':result.returncode})
 (root/'setup-results.json').write_text(json.dumps(results,indent=2))
 if result.returncode:raise SystemExit(result.returncode)
(root/'software-identity.json').write_text(json.dumps({'node_version':'24.19.0','node_archive_sha256':expected,'gsap':'3.15.1','new_scientific_requests':0},indent=2))
'''

def prepare():
    source=PRIVATE/'source-v1';source.mkdir(parents=True,exist_ok=False)
    paths=[]
    for p in (ROOT/'frontend').rglob('*'):
        if not p.is_file() or any(part in ['node_modules','dist','.vite'] for part in p.relative_to(ROOT/'frontend').parts):continue
        assert not p.is_symlink()
        rel=p.relative_to(ROOT);target=source/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());paths.append(target)
    setup=SETUP.replace('__ROOT__',repr(REMOTE));(source/'setup.py').write_text(setup,encoding='utf-8',newline='\n');paths.append(source/'setup.py')
    rows=[{'path':p.relative_to(source).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]
    write(source/'bundle.json',{'schema':'curaloop.ui.bundle.v1','files':rows})
    archive=PRIVATE/'source-v1.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(source.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(source).as_posix())
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    result=subprocess.run(['scp',*OPTIONS,str(archive),HOST+':'+REMOTE+'/source-v1.zip'],capture_output=True,timeout=60)
    if result.returncode:raise RuntimeError('Source transport failed')
    result=ssh('''
import json,hashlib,zipfile
from pathlib import Path,PurePosixPath
root=Path(__ROOT__);archive=root/'source-v1.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==__SHA__
target=root/'source';target.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())<500 and len(set(z.namelist()))==len(z.namelist())
 for info in z.infolist():
  name=PurePosixPath(info.filename);assert not name.is_absolute() and '..' not in name.parts and chr(92) not in info.filename and info.file_size<16*1024**2
  p=target/info.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
manifest=json.loads((target/'bundle.json').read_text())
assert all(hashlib.sha256((target/row['path']).read_bytes()).hexdigest()==row['sha256'] for row in manifest['files'])
print(json.dumps({'status':'PASS_TRANSPORT','source_files':len(manifest['files'])}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__SHA__',repr(digest)))
    write(PUBLIC/'source-v1-transport.json',{'archive_sha256':digest,**result})
    print(json.dumps(result))

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:run('ui-frontend-build-v1',['/usr/bin/python3','-B',REMOTE+'/source/setup.py'],REMOTE)
