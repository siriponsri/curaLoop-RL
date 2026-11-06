"""Capture the actual owner-approved studio build in a fresh isolated app copy."""
import base64,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,ssh,write,run
from tools.lrbc_ui_browser_run_v1 import SERVER,CAPTURE

CRITICAL = '\n # Repeat the asynchronous state/persistence/recovery path in three fresh contexts.\n for repeat in range(1,4):\n  cx=browser.new_context(viewport={\'width\':1440,\'height\':1000},reduced_motion=\'reduce\');page=cx.new_page();page.on(\'pageerror\',lambda e:errors.append(str(e)))\n  page.goto(base+\'/scenario\');expect(page.get_by_role(\'heading\',name=\'Scenario builder\',exact=True)).to_be_visible()\n  page.get_by_label(\'Screening budget\',exact=True).fill(\'2\');page.get_by_label(\'Concurrent assay capacity\',exact=True).fill(\'2\');page.get_by_label(\'Feedback delay · steps\',exact=True).fill(\'2\')\n  page.get_by_role(\'button\',name=\'Create campaign\',exact=True).click();expect(page.get_by_role(\'heading\',name=\'Simulation lab\',exact=True)).to_be_visible()\n  page.get_by_role(\'button\',name=\'Select next batch\',exact=True).click();expect(page.get_by_text(\'Awaiting feedback\',exact=True).first).to_be_visible();saved=current()\n  assert len(saved[\'pending\'])==2 and saved[\'report\'][\'metrics\'][\'confirmed_hits\']==0\n  page.reload();expect(page.get_by_text(\'Awaiting feedback\',exact=True).first).to_be_visible();assert current()==saved\n  # A rejected action must not spend again or replace the campaign.\n  page.route(\'**/api/v1/runs/*/advance\',lambda route:route.fulfill(status=409,content_type=\'application/json\',body=\'{"detail":"Injected acceptance check: action rejected."}\'))\n  page.get_by_role(\'button\',name=\'Advance +1 step\',exact=True).click();expect(page.get_by_role(\'alert\').first).to_be_visible();assert current()==saved;page.unroute(\'**/api/v1/runs/*/advance\')\n  payload=page.request.get(base+\'/api/v1/runs/\'+saved[\'session_id\']+\'/export?format=json\').json();(out/(\'recovery-\'+str(repeat)+\'.json\')).write_text(json.dumps(payload))\n  page.get_by_label(\'Resume JSON file\',exact=True).set_input_files(str(out/(\'recovery-\'+str(repeat)+\'.json\')));page.get_by_role(\'button\',name=\'Validate & resume\',exact=True).click()\n  page.wait_for_function(\'(old)=>localStorage.getItem("curaloop-session")!==old\',arg=saved[\'session_id\']);restored=current();assert restored[\'report\']==saved[\'report\'] and restored[\'session_id\']!=saved[\'session_id\']\n  page.get_by_role(\'button\',name=\'Advance +1 step\',exact=True).click();page.get_by_role(\'button\',name=\'Advance +1 step\',exact=True).click();expect(page.get_by_text(\'Campaign complete\',exact=True).first).to_be_visible();assert current()[\'report\'][\'metrics\'][\'delivered_assays\']==2\n  page.goto(base+\'/benchmarks\');page.get_by_role(\'button\',name=\'Compare selected policies\',exact=True).click()\n  page.wait_for_function(\'!!localStorage.getItem("curaloop-comparison")\');jid=page.evaluate(\'localStorage.getItem("curaloop-comparison")\')\n  deadline=time.monotonic()+75\n  while True:\n   job=page.request.get(base+\'/api/v1/comparisons/\'+jid).json()\n   if job[\'status\'] in (\'completed\',\'failed\',\'interrupted\'):break\n   assert time.monotonic()<deadline;page.wait_for_timeout(150)\n  assert job[\'status\']==\'completed\' and len(job[\'reports\'])==3\n  page.reload();expect(page.get_by_role(\'heading\',name=\'Benchmark arena\',exact=True)).to_be_visible();assert page.evaluate(\'localStorage.getItem("curaloop-comparison")\')==jid\n  assert page.request.get(base+\'/api/v1/comparisons/\'+jid+\'/export?format=json\').ok\n  checks.append(\'fresh_async_persistence_failure_recovery_comparison_\'+str(repeat));cx.close()\n'

def prepare():
    folder=PRIVATE/'browser-app-v4-inputs';folder.mkdir(exist_ok=False)
    for p in (ROOT/'docs/05_product/metadata-workspace-v2').iterdir():
        (folder/p.name).write_bytes(p.read_bytes())
    server=SERVER.replace('18770','5173').replace("'browser-state'","'browser-state-v4'").replace("'browser-app'","'browser-app-v4'").replace('__ROOT__',repr(REMOTE))
    capture=CAPTURE.replace('18770','5173').replace("'browser-evidence-v1'","'browser-evidence-v5'")
    capture=capture.replace("name='Current campaign'","name='HIV screening'").replace("name='Select batch'","name='Select next batch'").replace("name='Advance time'","name='Advance +1 step'")
    capture=capture.replace("page.get_by_role('button',name='Advance +1 step',exact=True).click();page.get_by_role('button',name='Advance +1 step',exact=True).click()", "page.get_by_role('button',name='Advance +1 step',exact=True).click();page.get_by_role('button',name='Advance +1 step',exact=True).click()")
    capture=capture.replace("checks.append('workspace_citation_keyboard_disclosure')", "checks.append('workspace_citation_keyboard_disclosure');page.locator('.claim-select').nth(3).click();assert page.locator('#selected-field-value').inner_text()=='5';assert page.locator('#selected-locator').inner_text().endswith('/unit');checks.append('workspace_selection_tracks_original_source_locator')")
    capture=capture.replace("switch('th');capture('08-workspace-th');", "switch('th');assert page.locator('#selected-field-value').inner_text()=='5';capture('08-workspace-th');")

    capture=capture.replace("before=current();capture('01-overview-en');", "before=current();expect(page.locator('.studio-molecule')).to_be_visible();original=page.locator('.studio-molecule').get_attribute('src');page.get_by_role('button',name='Zoom in structure',exact=True).click();expect(page.locator('.studio-molecule')).to_have_attribute('style','transform: scale(1.2);');page.get_by_role('button',name='Reset structure view',exact=True).click();page.get_by_role('button',name='Next compound',exact=True).click();expect(page.locator('.studio-molecule')).not_to_have_attribute('src',original);page.get_by_role('button',name='Previous compound',exact=True).click();expect(page.locator('.studio-molecule')).to_have_attribute('src',original);assert current()==before;checks.append('structure_paging_zoom_read_only');capture('01-overview-en');")
    capture=capture.replace(" browser.close()", CRITICAL + "\n browser.close()")

    capture=capture.replace('__ROOT__',repr(REMOTE))
    for name,body in [('serve-v4.py',server),('capture-v5.py',capture)]:
        (folder/name).write_text(body,encoding='utf-8',newline='\n')
    archive=PRIVATE/'browser-app-v4-inputs.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in folder.iterdir():z.write(p,p.name)
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    r=subprocess.run(['scp',*OPTIONS,str(archive),HOST+':'+REMOTE+'/browser-app-v4-inputs.zip'],capture_output=True,timeout=60);assert r.returncode==0
    result=ssh('''
import json,zipfile,hashlib,shutil
from pathlib import Path
root=Path(__ROOT__);archive=root/'browser-app-v4-inputs.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==__SHA__
base=root/'browser-app';target=root/'browser-app-v4';target.mkdir(exist_ok=False)
manifest=json.loads((base/'bundle.json').read_text())
for row in manifest['files']:
 if row['path'].startswith('workspace/'):continue
 p=base/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 out=target/row['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
shutil.copytree(root/'source-v8/frontend/dist',target/'frontend/dist');shutil.copyfile(base/'axe.min.js',target/'axe.min.js')
workspace=target/'workspace';workspace.mkdir()
with zipfile.ZipFile(archive) as z:
 for info in z.infolist():
  assert '/' not in info.filename and chr(92) not in info.filename and info.file_size<4*1024**2
  out=(target if info.filename.endswith('.py') else workspace)/info.filename;out.write_bytes(z.read(info))
print(json.dumps({'status':'PASS_STUDIO_APP_TRANSPORT','built_source':'source-v8','new_state':'browser-state-v4'}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__SHA__',repr(digest)))
    write(PUBLIC/'browser-app-v4-transport.json',{'archive_sha256':digest,**result});print(json.dumps(result))

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='stop':print(ssh("import json;from pathlib import Path;p=Path("+repr(REMOTE+'/browser-state-v4/stop.json')+");p.write_text(json.dumps({'reason':'Frontend session complete'}));print(json.dumps({'status':'STOP_REQUESTED'}))"))
    else:
        name='serve-v4.py' if mode=='server' else 'capture-v5.py'
        run('ui-studio-browser-'+mode+('-v4' if mode=='server' else '-v5'),[REMOTE+'/qa-env/bin/python','-B',REMOTE+'/browser-app-v4/'+name],REMOTE,
            {'HOME':REMOTE+'/home','TMPDIR':REMOTE+'/tmp','PLAYWRIGHT_BROWSERS_PATH':REMOTE+'/software/playwright','LD_LIBRARY_PATH':REMOTE+'/software/browser-libraries-v1/root/usr/lib/x86_64-linux-gnu'})
