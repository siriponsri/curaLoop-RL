"""Version UI source bundles; reuse installed dependencies without rewriting old sources."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,ssh,write,run

def prepare(version):
    assert version.startswith('source-v') and version[8:].isdigit()
    folder=PRIVATE/version;folder.mkdir(exist_ok=False)
    paths=[]
    for p in (ROOT/'frontend').rglob('*'):
        rel=p.relative_to(ROOT/'frontend')
        if not p.is_file() or any(x in ['node_modules','dist','.vite'] for x in rel.parts):continue
        target=folder/'frontend'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());paths.append(target)
    script='''
import json,os,subprocess
from pathlib import Path
root=Path(__ROOT__);folder=root/__VERSION__;frontend=folder/'frontend'
env=os.environ.copy();env.update(HOME=str(root/'home'),TMPDIR=str(root/'tmp'),npm_config_cache=str(root/'cache/npm'),HYPERFRAMES_SKIP_SKILLS='1',CI='1',PATH=str(root/'software/node-v24.19.0-linux-x64/bin')+':'+env['PATH'])
commands=[['npm','run','typecheck'],['npm','run','lint'],['npm','run','test','--','--maxWorkers=1'],['npm','run','build']]
results=[]
for i,cmd in enumerate(commands):
 with (folder/('command-'+str(i)+'.txt')).open('x') as log:
  result=subprocess.run(cmd,cwd=frontend,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'argv':cmd,'exit_code':result.returncode});(folder/'results.json').write_text(json.dumps(results,indent=2))
 if result.returncode:raise SystemExit(result.returncode)
'''.replace('__ROOT__',repr(REMOTE)).replace('__VERSION__',repr(version))
    (folder/'check.py').write_text(script,encoding='utf-8',newline='\n');paths.append(folder/'check.py')
    rows=[{'path':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]
    write(folder/'bundle.json',{'schema':'curaloop.ui.bundle.v1','files':rows})
    archive=PRIVATE/(version+'.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(folder).as_posix())
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    result=subprocess.run(['scp',*OPTIONS,str(archive),HOST+':'+REMOTE+'/'+version+'.zip'],capture_output=True,timeout=60)
    assert result.returncode==0
    result=ssh('''
import json,hashlib,zipfile,shutil,os
from pathlib import Path,PurePosixPath
root=Path(__ROOT__);archive=root/(__VERSION__+'.zip');assert hashlib.sha256(archive.read_bytes()).hexdigest()==__SHA__
target=root/__VERSION__;target.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())<500 and len(set(z.namelist()))==len(z.namelist())
 for info in z.infolist():
  name=PurePosixPath(info.filename);assert not name.is_absolute() and '..' not in name.parts and chr(92) not in info.filename and info.file_size<16*1024**2
  p=target/info.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
manifest=json.loads((target/'bundle.json').read_text());assert all(hashlib.sha256((target/row['path']).read_bytes()).hexdigest()==row['sha256'] for row in manifest['files'])
shutil.copyfile(root/'source/frontend/package-lock.json',target/'frontend/package-lock.json')
os.symlink('../../source/frontend/node_modules',target/'frontend/node_modules',target_is_directory=True)
effective=[]
for p in sorted((target/'frontend').rglob('*')):
 if 'node_modules' in p.relative_to(target).parts or not p.is_file():continue
 effective.append({'path':p.relative_to(target).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(target/'effective-build-inputs.json').write_text(json.dumps({'schema':'curaloop.ui.effective-inputs.v1','generated_lock_source':'source/frontend/package-lock.json','files':effective},indent=2))
print(json.dumps({'status':'PASS_TRANSPORT','source_files':len(manifest['files'])}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__VERSION__',repr(version)).replace('__SHA__',repr(digest)))
    write(PUBLIC/(version+'-transport.json'),{'archive_sha256':digest,**result});print(json.dumps(result))

if __name__=='__main__':
    version=sys.argv[2]
    if sys.argv[1]=='prepare':prepare(version)
    else:run('ui-frontend-'+version,['/usr/bin/python3','-B',REMOTE+'/'+version+'/check.py'],REMOTE)
