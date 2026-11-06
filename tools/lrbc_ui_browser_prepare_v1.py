"""Package the existing app oracle and isolated browser tooling, not research cohorts."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,ssh,write,run

SETUP='''
import json,os,subprocess,sys
from pathlib import Path
root=Path(__ROOT__);app=root/'browser-app';env=os.environ.copy()
env.update(HOME=str(root/'home'),TMPDIR=str(root/'tmp'),PIP_CACHE_DIR=str(root/'cache/pip'),PLAYWRIGHT_BROWSERS_PATH=str(root/'software/playwright'))
venv=root/'qa-env';subprocess.run([sys.executable,'-m','venv',str(venv)],check=True,env=env)
python=str(venv/'bin/python');wheels=root/'software/python-wheels';wheels.mkdir(exist_ok=False)
constraints=[]
for file in ['requirements-lock.txt','requirements-web-lock.txt']:
 constraints.extend(line for line in (app/file).read_text().splitlines() if line and not line.startswith(('#','-r')))
(app/'qa-constraints.txt').write_text('\\n'.join(constraints)+'\\n')
packages=['fastapi==0.162.0','uvicorn==0.54.0','httpx==0.28.1','gymnasium==1.4.0','numpy==2.3.5','scikit-learn==1.8.0','scipy==1.17.0','rdkit==2026.9.1','playwright==1.64.1','reportlab==4.4.9','pypdf==6.10.0']
commands=[[python,'-m','pip','download','--only-binary=:all:','--dest',str(wheels),'-c',str(app/'qa-constraints.txt'),*packages],
 [python,'-m','pip','install','--no-index','--find-links',str(wheels),'-c',str(app/'qa-constraints.txt'),*packages],
 [python,'-m','playwright','install','chromium']]
results=[]
for i,cmd in enumerate(commands):
 with (app/('dependency-'+str(i)+'.txt')).open('x') as log:r=subprocess.run(cmd,cwd=app,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'argv':cmd,'exit_code':r.returncode});(app/'dependency-results.json').write_text(json.dumps(results,indent=2))
 if r.returncode:raise SystemExit(r.returncode)
with (app/'python-freeze.txt').open('x') as f:subprocess.run([python,'-m','pip','freeze'],env=env,stdout=f,check=True)
'''

def prepare():
    folder=PRIVATE/'browser-app';folder.mkdir(exist_ok=False)
    paths=[*list((ROOT/'api').glob('*.py')),*list((ROOT/'src/curaloop').glob('*.py'))]
    paths += [ROOT/'src/curaloop/resources'/name for name in ['hiv_replay_v1.json.gz','hiv_manifest.json','q_learning.json','contextual_bandit.json']]
    paths += [ROOT/name for name in ['requirements-lock.txt','requirements-web-lock.txt','requirements-qa.txt','pyproject.toml','docs/evidence/hiv-benchmark/summary.json']]
    for p in paths:
        target=folder/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    for p in (ROOT/'docs/05_product/metadata-workspace-v2').iterdir():
        target=folder/'workspace'/p.name;target.parent.mkdir(exist_ok=True);target.write_bytes(p.read_bytes())
    (folder/'setup.py').write_text(SETUP.replace('__ROOT__',repr(REMOTE)),encoding='utf-8',newline='\n')
    rows=[{'path':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(folder.rglob('*')) if p.is_file()]
    write(folder/'bundle.json',{'schema':'curaloop.ui.app-bundle.v1','source_base_commit':'3fbba89','dirty_working_sources':True,'scientific_source_requests':0,'files':rows})
    archive=PRIVATE/'browser-app.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(folder).as_posix())
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    result=subprocess.run(['scp',*OPTIONS,str(archive),HOST+':'+REMOTE+'/browser-app.zip'],capture_output=True,timeout=60);assert result.returncode==0
    result=ssh('''
import json,hashlib,zipfile,shutil
from pathlib import Path,PurePosixPath
root=Path(__ROOT__);archive=root/'browser-app.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==__SHA__
target=root/'browser-app';target.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())<100 and len(set(z.namelist()))==len(z.namelist())
 for info in z.infolist():
  name=PurePosixPath(info.filename);assert not name.is_absolute() and '..' not in name.parts and info.file_size<20*1024**2
  p=target/info.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
manifest=json.loads((target/'bundle.json').read_text());assert all(hashlib.sha256((target/row['path']).read_bytes()).hexdigest()==row['sha256'] for row in manifest['files'])
shutil.copytree(root/'source-v3/frontend/dist',target/'frontend/dist')
shutil.copyfile(root/'source/frontend/node_modules/axe-core/axe.min.js',target/'axe.min.js')
print(json.dumps({'status':'PASS_TRANSPORT','source_files':len(manifest['files'])}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__SHA__',repr(digest)))
    write(PUBLIC/'browser-app-transport.json',{'archive_sha256':digest,**result});print(json.dumps(result))

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:run('ui-browser-dependencies-v1',['/usr/bin/python3','-B',REMOTE+'/browser-app/setup.py'],REMOTE)
