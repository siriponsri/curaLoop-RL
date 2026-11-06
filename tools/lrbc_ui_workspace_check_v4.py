"""Pin the additive C UI and retained permitted metadata before bounded checks."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,ssh,write,run

def prepare():
    folder=PRIVATE/'workspace-studio-v4';folder.mkdir(exist_ok=False)
    returned=ROOT/'.local/lrbc-c-20261106-v1/remote-return/full-v1/files'
    manifest=json.loads((ROOT/'.local/lrbc-c-20261106-v1/remote-return-manifest.json').read_text())
    pins={row['path']:row for row in manifest['files']}
    for p in (ROOT/'src/curaloop_rd').rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        if p.suffix not in ['.py','.html','.css','.js','.png']:continue
        frozen=returned/'bundles/portfolio-v2'/p.relative_to(ROOT)
        if frozen.exists():
            assert p.read_bytes()==frozen.read_bytes(), 'Frozen core source changed'
        target=folder/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    for p in (returned/'bundles/portfolio-v2/inputs').rglob('*'):
        if not p.is_file():continue
        assert hashlib.sha256(p.read_bytes()).hexdigest()==pins[p.relative_to(returned).as_posix()]['sha256']
        target=folder/'inputs'/p.relative_to(returned/'bundles/portfolio-v2/inputs');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    (folder/'font').mkdir()
    for name in ['NotoSansThai.ttf','OFL.txt']:(folder/'font'/name).write_bytes((ROOT/'frontend/public/fonts'/name).read_bytes())
    (folder/'checks.py').write_bytes((ROOT/'research/ui_studio_v1/workspace_checks.py').read_bytes())
    rows=[{'path':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(folder.rglob('*')) if p.is_file()]
    write(folder/'bundle.json',{'schema':'curaloop.studio.c-ui-checks.v1','files':rows,'new_scientific_source_calls':0})
    archive=PRIVATE/'workspace-studio-v4.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(folder).as_posix())
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    result=subprocess.run(['scp',*OPTIONS,str(archive),HOST+':'+REMOTE+'/workspace-studio-v4.zip'],capture_output=True,timeout=60);assert result.returncode==0
    result=ssh('''
import json,zipfile,hashlib
from pathlib import Path,PurePosixPath
root=Path(__ROOT__);archive=root/'workspace-studio-v4.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==__SHA__
target=root/'workspace-studio-v4';target.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())<=100
 for info in z.infolist():
  name=PurePosixPath(info.filename);assert not name.is_absolute() and '..' not in name.parts and info.file_size<16*1024**2
  p=target/info.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
manifest=json.loads((target/'bundle.json').read_text());assert all(hashlib.sha256((target/row['path']).read_bytes()).hexdigest()==row['sha256'] for row in manifest['files'])
print(json.dumps({'status':'PASS_PINNED_TRANSPORT','files':len(manifest['files'])}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__SHA__',repr(digest)))
    write(PUBLIC/'workspace-studio-v4-transport.json',{'archive_sha256':digest,**result});print(json.dumps(result))

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:run('ui-c-workspace-checks-v4',['/usr/bin/python3','-B',REMOTE+'/workspace-studio-v4/checks.py',REMOTE+'/workspace-studio-v4',REMOTE+'/workspace-studio-checks-v4'],REMOTE)
