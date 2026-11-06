"""Repair acceptance selectors without changing product or old evidence."""
import base64,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,REMOTE,ssh,run
if sys.argv[1]=='prepare':
 body=(PRIVATE/'browser-app-v4-inputs/capture-v5.py').read_text()
 body=body.replace('browser-evidence-v5','browser-evidence-v6').replace("  page.get_by_label('Resume JSON file'","  page.goto(base+'/evidence');page.get_by_label('Resume JSON file'")
 body=body.replace("  page.get_by_role('button',name='Advance +1 step',exact=True).click();page.get_by_role", "  page.goto(base+'/lab');page.get_by_role('button',name='Advance +1 step',exact=True).click();page.get_by_role")
 body=body.replace("name='Campaign complete'","name='Completed'")
 path=PRIVATE/'browser-scripts/capture-v6.py';path.write_text(body,encoding='utf-8',newline='\n')
 print(ssh("import base64,json;from pathlib import Path;p=Path("+repr(REMOTE+'/browser-app-v4/capture-v6.py')+");assert not p.exists();p.write_bytes(base64.b64decode("+repr(base64.b64encode(body.encode()).decode())+"));print(json.dumps({'status':'PREPARED'}))"))
else:
 run('ui-studio-browser-capture-v6',[REMOTE+'/qa-env/bin/python','-B',REMOTE+'/browser-app-v4/capture-v6.py'],REMOTE,{'HOME':REMOTE+'/home','TMPDIR':REMOTE+'/tmp','PLAYWRIGHT_BROWSERS_PATH':REMOTE+'/software/playwright','LD_LIBRARY_PATH':REMOTE+'/software/browser-libraries-v1/root/usr/lib/x86_64-linux-gnu'})
