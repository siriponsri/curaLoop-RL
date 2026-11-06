"""Selected Molecular Studio composition, with a new non-teal palette."""
import base64,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,ssh,write,run

MAP={'#16333b':'#28282B','#f7f9f8':'#F6F4EF','#60716c':'#6A6661','#087f72':'#A6492D','#cbd9d3':'#D9D5CF','#dce5e1':'#D9D5CF','#e7f3ed':'#F4E5DC','#dbe7e2':'#E5DFD8','#b7ccc6':'#C2BCB6','#285057':'#414041','#315158':'#4B4744','#f2f6f3':'#F6F4EF','#d6e1db':'#D9D5CF','#d2ded7':'#D9D5CF','#e3eae5':'#E6E1DB','#fbfcfa':'#FCFBF8','#b66914':'#95611E'}

def prepare():
    source=PRIVATE/'direction-study-v1';folder=PRIVATE/'studio-copper-preview-v1';folder.mkdir(exist_ok=False)
    text=(source/'a-studio.html').read_text(encoding='utf-8')
    start=text.index('<style>')+7;end=text.index('</style>')
    css=text[start:end]
    import re
    css=re.sub(r'#[0-9a-fA-F]{6}',lambda m:MAP.get(m.group().lower(),m.group()),css)
    css+=' .brand{filter:grayscale(1)}'
    text=text[:start]+css+text[end:]
    (folder/'index.html').write_text(text,encoding='utf-8',newline='\n')
    for name in ['CuraThai.ttf','OFL.txt','molecule.svg','snapshot.json']:(folder/name).write_bytes((source/name).read_bytes())
    (folder/'brand').mkdir();(folder/'brand/logo-v2.png').write_bytes((ROOT/'frontend/public/brand/logo-v2.png').read_bytes())
    serve=r'''
import json,os,subprocess,time,socket
from pathlib import Path
root=Path(__ROOT__);state=root/'studio-preview-state-v1';state.mkdir(exist_ok=False)
with socket.socket() as s:s.bind(('127.0.0.1',5173))
env=os.environ.copy();env.update(HOME=str(root/'home'),TMPDIR=str(root/'tmp'))
with (state/'server-private.txt').open('x') as log:
 p=subprocess.Popen(['/usr/bin/python3','-B','-m','http.server','5173','--bind','127.0.0.1','--directory',str(root/'studio-copper-preview-v1')],env=env,stdout=log,stderr=subprocess.STDOUT)
 deadline=time.monotonic()+780
 try:
  while not (state/'stop.json').exists() and time.monotonic()<deadline:
   if p.poll() is not None:raise RuntimeError('Preview server exited')
   time.sleep(.25)
 finally:
  if p.poll() is None:p.terminate()
  p.wait(timeout=8)
 (state/'server-exit.json').write_text(json.dumps({'pid':p.pid,'exit_code':p.returncode,'stop_requested':(state/'stop.json').exists()}))
 if not (state/'stop.json').exists():raise SystemExit(124)
'''.replace('__ROOT__',repr(REMOTE))
    (folder/'serve.py').write_text(serve,encoding='utf-8',newline='\n')
    rows=[{'path':p.relative_to(folder).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(folder.rglob('*')) if p.is_file()]
    write(folder/'manifest.json',{'schema':'curaloop.studio-color-preview.v1','official_gpo_palette':False,'selected_layout':'A_MOLECULAR_STUDIO','status':'STATIC_COMPOSITION_NOT_INTERACTIVE','files':rows})
    archive=PRIVATE/'studio-copper-preview-v1.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(folder).as_posix())
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    r=subprocess.run(['scp',*OPTIONS,str(archive),HOST+':'+REMOTE+'/studio-copper-preview-v1.zip'],capture_output=True,timeout=60);assert r.returncode==0
    result=ssh('''
import json,zipfile,hashlib
from pathlib import Path,PurePosixPath
root=Path(__ROOT__);archive=root/'studio-copper-preview-v1.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==__SHA__
target=root/'studio-copper-preview-v1';target.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 for info in z.infolist():
  name=PurePosixPath(info.filename);assert not name.is_absolute() and '..' not in name.parts and chr(92) not in info.filename and info.file_size<4*1024**2
  p=target/info.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
print(json.dumps({'status':'PASS_TRANSPORT','files':len(z.namelist())}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__SHA__',repr(digest)))
    write(PUBLIC/'studio-copper-preview-v1-transport.json',{'archive_sha256':digest,**result});print(json.dumps(result))

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:run('ui-studio-preview-server-v1',['/usr/bin/python3','-B',REMOTE+'/studio-copper-preview-v1/serve.py'],REMOTE)
