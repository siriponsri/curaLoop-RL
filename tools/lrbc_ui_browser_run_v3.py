"""Capture the actual owner-approved studio build in a fresh isolated app copy."""
import base64,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,ssh,write,run
from tools.lrbc_ui_browser_run_v1 import SERVER,CAPTURE

def prepare():
    folder=PRIVATE/'browser-app-v3-inputs';folder.mkdir(exist_ok=False)
    for p in (ROOT/'docs/05_product/metadata-workspace-v2').iterdir():
        (folder/p.name).write_bytes(p.read_bytes())
    server=SERVER.replace('18770','5173').replace("'browser-state'","'browser-state-v3'").replace("'browser-app'","'browser-app-v3'").replace('__ROOT__',repr(REMOTE))
    capture=CAPTURE.replace('18770','5173').replace("'browser-evidence-v1'","'browser-evidence-v3'")
    capture=capture.replace("name='Current campaign'","name='HIV screening'").replace("name='Select batch'","name='Select next batch'").replace("name='Advance time'","name='Advance +1 step'")
    capture=capture.replace("page.get_by_role('button',name='Advance +1 step',exact=True).click();page.get_by_role('button',name='Advance +1 step',exact=True).click()", "page.get_by_role('button',name='Advance +1 step',exact=True).click();page.get_by_role('button',name='Advance +1 step',exact=True).click()")
    capture=capture.replace("checks.append('workspace_citation_keyboard_disclosure')", "checks.append('workspace_citation_keyboard_disclosure');page.locator('[data-select-index=3]').click();assert page.locator('#selected-field-value').inner_text()=='5';assert page.locator('#selected-locator').inner_text().endswith('/unit');checks.append('workspace_selection_tracks_original_source_locator')")
    capture=capture.replace("switch('th');capture('08-workspace-th');", "switch('th');assert page.locator('#selected-field-value').inner_text()=='5';capture('08-workspace-th');")
    capture=capture.replace('__ROOT__',repr(REMOTE))
    for name,body in [('serve-v3.py',server),('capture-v3.py',capture)]:
        (folder/name).write_text(body,encoding='utf-8',newline='\n')
    archive=PRIVATE/'browser-app-v3-inputs.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in folder.iterdir():z.write(p,p.name)
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    r=subprocess.run(['scp',*OPTIONS,str(archive),HOST+':'+REMOTE+'/browser-app-v3-inputs.zip'],capture_output=True,timeout=60);assert r.returncode==0
    result=ssh('''
import json,zipfile,hashlib,shutil
from pathlib import Path
root=Path(__ROOT__);archive=root/'browser-app-v3-inputs.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==__SHA__
base=root/'browser-app';target=root/'browser-app-v3';target.mkdir(exist_ok=False)
manifest=json.loads((base/'bundle.json').read_text())
for row in manifest['files']:
 if row['path'].startswith('workspace/'):continue
 p=base/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 out=target/row['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
shutil.copytree(root/'source-v5/frontend/dist',target/'frontend/dist');shutil.copyfile(base/'axe.min.js',target/'axe.min.js')
workspace=target/'workspace';workspace.mkdir()
with zipfile.ZipFile(archive) as z:
 for info in z.infolist():
  assert '/' not in info.filename and chr(92) not in info.filename and info.file_size<4*1024**2
  out=(target if info.filename.endswith('.py') else workspace)/info.filename;out.write_bytes(z.read(info))
print(json.dumps({'status':'PASS_STUDIO_APP_TRANSPORT','built_source':'source-v5','new_state':'browser-state-v3'}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__SHA__',repr(digest)))
    write(PUBLIC/'browser-app-v3-transport.json',{'archive_sha256':digest,**result});print(json.dumps(result))

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='stop':print(ssh("import json;from pathlib import Path;p=Path("+repr(REMOTE+'/browser-state-v3/stop.json')+");p.write_text(json.dumps({'reason':'Frontend session complete'}));print(json.dumps({'status':'STOP_REQUESTED'}))"))
    else:
        name='serve-v3.py' if mode=='server' else 'capture-v3.py'
        run('ui-studio-browser-'+mode+'-v3',[REMOTE+'/qa-env/bin/python','-B',REMOTE+'/browser-app-v3/'+name],REMOTE,
            {'HOME':REMOTE+'/home','TMPDIR':REMOTE+'/tmp','PLAYWRIGHT_BROWSERS_PATH':REMOTE+'/software/playwright','LD_LIBRARY_PATH':REMOTE+'/software/browser-libraries-v1/root/usr/lib/x86_64-linux-gnu'})
