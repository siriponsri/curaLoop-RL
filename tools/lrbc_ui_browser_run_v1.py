"""Owned loopback browser session and versioned bilingual acceptance capture."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,ssh,write,run

SERVER=r'''
import json,os,subprocess,time,socket
from pathlib import Path
root=Path(__ROOT__);app=root/'browser-app';state=root/'browser-state';state.mkdir(exist_ok=False)
with socket.socket() as s:s.bind(('127.0.0.1',18770))
env=os.environ.copy();env.update(HOME=str(root/'home'),TMPDIR=str(root/'tmp'),CURALOOP_STORAGE_PATH=str(state/'isolated.sqlite3'),GIT_CEILING_DIRECTORIES=str(root),PYTHONPATH=str(app/'src'))
code="from pathlib import Path;from api.main import app;from starlette.routing import Mount;from starlette.staticfiles import StaticFiles;import uvicorn;app.router.routes.insert(0,Mount('/workspace',StaticFiles(directory='workspace',html=True)));uvicorn.run(app,host='127.0.0.1',port=18770,log_level='warning')"
with (state/'server-private.txt').open('x') as log:
 process=subprocess.Popen([str(root/'qa-env/bin/python'),'-B','-c',code],cwd=app,env=env,stdout=log,stderr=subprocess.STDOUT)
 deadline=time.monotonic()+780
 try:
  while not (state/'stop.json').exists() and time.monotonic()<deadline:
   if process.poll() is not None:raise RuntimeError('Owned API exited early')
   time.sleep(.25)
 finally:
  if process.poll() is None:process.terminate()
  try:process.wait(timeout=8)
  except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
 (state/'server-exit.json').write_text(json.dumps({'owned_pid':process.pid,'exit_code':process.returncode,'stop_requested':(state/'stop.json').exists()}))
 if not (state/'stop.json').exists():raise SystemExit(124)
'''

CAPTURE=r'''
import json,hashlib,time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright,expect
root=Path(__ROOT__);app=root/'browser-app';out=root/'browser-evidence-v1';out.mkdir(exist_ok=False)
base='http://127.0.0.1:18770';errors=[];external=[];audits=[];captures=[];overflows=[];checks=[]
expect.set_options(timeout=30000)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-gpu'])
 context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',accept_downloads=True)
 context.route('**/*',lambda route:route.continue_() if urlparse(route.request.url).hostname in ('127.0.0.1','localhost',None) else (external.append(route.request.url),route.abort()))
 page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 def capture(name,audit=True):
  page.evaluate('document.fonts.ready');page.screenshot(path=str(out/(name+'.png')),full_page=True);captures.append(name+'.png')
  overflow=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
  if overflow['scroll']>overflow['width']+1:overflows.append({'name':name,**overflow})
  if audit:
   page.add_script_tag(path=str(app/'axe.min.js'))
   result=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}})")
   audits.append({'capture':name,'violations':[{'id':v['id'],'impact':v['impact'],'nodes':[n['target'] for n in v['nodes']]} for v in result['violations']]})
 def switch(lang):
  page.get_by_role('button',name='ไทย' if lang=='th' else 'EN',exact=True).click()
  expect(page.locator('html')).to_have_attribute('lang',lang)
 def current():
  sid=page.evaluate("localStorage.getItem('curaloop-session')")
  response=page.request.get(base+'/api/v1/runs/'+sid);assert response.ok
  return response.json()
 page.goto(base);expect(page.get_by_role('heading',name='Current campaign',exact=True)).to_be_visible()
 before=current();capture('01-overview-en');switch('th');assert current()==before;checks.append('locale_preserves_campaign_public_state');capture('01-overview-th')
 page.set_viewport_size({'width':390,'height':844});capture('01-overview-mobile-th',False);page.set_viewport_size({'width':1440,'height':1000});switch('en')
 page.goto(base+'/scenario');expect(page.get_by_role('heading',name='Scenario builder',exact=True)).to_be_visible();capture('02-scenario-en')
 page.get_by_label('Screening budget',exact=True).fill('6');page.get_by_label('Concurrent assay capacity',exact=True).fill('2');page.get_by_label('Feedback delay · steps',exact=True).fill('2')
 switch('th');expect(page.get_by_label('งบคัดกรองจำลอง',exact=True)).to_have_value('6');capture('02-scenario-th');switch('en')
 page.get_by_role('button',name='Create campaign',exact=True).click();expect(page.get_by_role('heading',name='Simulation lab',exact=True)).to_be_visible();capture('03-lab-ready-en',False)
 page.get_by_role('button',name='Select batch',exact=True).click();expect(page.get_by_text('Awaiting feedback',exact=True).first).to_be_visible()
 pending=current();assert pending['pending'] and pending['report']['metrics']['confirmed_hits']==0
 response=page.request.get(base+'/api/v1/runs/'+pending['session_id']+'/candidates?status=pending');assert response.ok
 for row in response.json()['items']:assert row['revealed_active'] is None
 assert not pending['report']['delivered_results'];checks.append('pending_outcomes_hidden_in_public_api')
 (out/'pending-run.json').write_text(json.dumps(pending['report'],indent=2))
 capture('03-lab-pending-en');switch('th');assert current()==pending;capture('03-lab-pending-th')
 page.set_viewport_size({'width':390,'height':844});capture('03-lab-mobile-th',False);page.set_viewport_size({'width':1440,'height':1000});switch('en')
 page.get_by_role('button',name='Advance time',exact=True).click();page.get_by_role('button',name='Advance time',exact=True).click()
 expect(page.get_by_text('Ready to select',exact=True).first).to_be_visible();assert current()['report']['metrics']['delivered_assays']==2;checks.append('explicit_time_advance_delivers_results');capture('03-lab-delivered-en',False)
 page.goto(base+'/compounds');expect(page.get_by_role('heading',name='Compound explorer',exact=True)).to_be_visible();expect(page.locator('.compound-item').first).to_be_visible();capture('04-compounds-en');switch('th');capture('04-compounds-th');switch('en')
 first=page.locator('.compound-item').first;first.click();expect(page.get_by_role('dialog')).to_be_visible();capture('04-compound-details-en',False);page.keyboard.press('Escape');expect(first).to_be_focused();checks.append('compound_dialog_keyboard_focus_restored')
 page.goto(base+'/benchmarks');expect(page.get_by_role('heading',name='Benchmark arena',exact=True)).to_be_visible();capture('05-benchmarks-en');switch('th');capture('05-benchmarks-th');switch('en')
 page.goto(base+'/evidence');expect(page.get_by_role('heading',name='Research evidence',exact=True)).to_be_visible();capture('06-evidence-en');switch('th');capture('06-evidence-th');switch('en')
 page.goto(base+'/presentation');expect(page.get_by_role('heading',name='Guided presentation',exact=True)).to_be_visible();capture('07-guide-en');switch('th');capture('07-guide-th');switch('en')
 page.goto(base+'/workspace/workspace.html');expect(page.get_by_role('heading',name='Evidence workspace',exact=True)).to_be_visible();capture('08-workspace-en');page.locator('summary').first.focus();page.keyboard.press('Enter');expect(page.locator('details').first).to_have_attribute('open','');checks.append('workspace_citation_keyboard_disclosure')
 report=page.request.get(base+'/workspace/report.json').json();assert report['report_sha256']=='706eb54e7417a31d161f333ef88b7ca752b1c1c20c6bae146fd48f071e16e50f'
 switch('th');capture('08-workspace-th');assert page.request.get(base+'/workspace/report.json').json()==report;checks.append('workspace_locale_preserves_original_report')
 for name in ['report.json','report.md','readiness-plan.json','preview.json','handoff-manifest.json']:assert page.request.get(base+'/workspace/'+name).ok
 page.set_viewport_size({'width':390,'height':844});capture('08-workspace-mobile-th',False);page.set_viewport_size({'width':720,'height':1000});capture('08-workspace-reflow-720-th',False)
 browser.close()
result={'schema':'curaloop.bilingual-browser.v1','status':'PASS' if not errors and not external and not overflows and len(audits)==16 and all(not a['violations'] for a in audits) else 'FAIL',
 'actual_production_build':True,'anonymous_isolated_storage':True,'viewport_desktop':[1440,1000],'viewport_mobile':[390,844],'reflow_width':720,
 'native_browser_zoom_200_percent':'NOT_RUN','checks':checks,'captures':captures,'axe_routes':len(audits),'expected_axe_routes':16,'axe':audits,'page_errors':errors,'external_requests':external,'horizontal_overflows':overflows,'live_agent_evaluation':'NOT_RUN'}
(out/'browser-result.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['status','axe_routes','page_errors','external_requests','horizontal_overflows']}))
raise SystemExit(0 if result['status']=='PASS' else 1)
'''

def prepare():
    files={'serve-v1.py':SERVER.replace('__ROOT__',repr(REMOTE)),'capture-v1.py':CAPTURE.replace('__ROOT__',repr(REMOTE))}
    import base64
    result=ssh('''
import json,base64
from pathlib import Path
root=Path(__ROOT__)/'browser-app'
for name,encoded in __FILES__.items():
 p=root/name
 with p.open('xb') as f:f.write(base64.b64decode(encoded))
print(json.dumps({'status':'PREPARED_NOT_EXECUTED','files':list(__FILES__)}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__FILES__',repr({k:base64.b64encode(v.encode()).decode() for k,v in files.items()})))
    for name,body in files.items():
        target=PRIVATE/'browser-scripts'/name;target.parent.mkdir(exist_ok=True);target.write_text(body,encoding='utf-8',newline='\n')
    print(json.dumps(result))

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='server':run('ui-browser-server-v1',['/usr/bin/python3','-B',REMOTE+'/browser-app/serve-v1.py'],REMOTE)
    else:run('ui-browser-capture-v1',[REMOTE+'/qa-env/bin/python','-B',REMOTE+'/browser-app/capture-v1.py'],REMOTE,{'HOME':REMOTE+'/home','TMPDIR':REMOTE+'/tmp','PLAYWRIGHT_BROWSERS_PATH':REMOTE+'/software/playwright'})
