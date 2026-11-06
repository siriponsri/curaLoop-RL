"""Use an existing approved loopback origin and task-local browser libraries."""
import base64,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,REMOTE,ssh,run
from tools.lrbc_ui_browser_run_v1 import SERVER,CAPTURE

LIBRARIES=r'''
import json,os,subprocess
from pathlib import Path
root=Path(__ROOT__);folder=root/'software/browser-libraries-v1';folder.mkdir(exist_ok=False)
environment=os.environ.copy();environment.update(HOME=str(root/'home'),TMPDIR=str(root/'tmp'))
browser=root/'software/playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'
before=subprocess.run(['ldd',str(browser)],capture_output=True,text=True,check=True).stdout
(folder/'ldd-before.txt').write_text(before)
missing=[line.split()[0] for line in before.splitlines() if 'not found' in line]
assert missing==['libasound.so.2'], missing
with (folder/'download.txt').open('x') as log:
 result=subprocess.run(['apt-get','download','libasound2t64'],cwd=folder,env=environment,stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0
debs=list(folder.glob('*.deb'));assert len(debs)==1
subprocess.run(['dpkg-deb','--extract',str(debs[0]),str(folder/'root')],check=True,env=environment)
environment['LD_LIBRARY_PATH']=str(folder/'root/usr/lib/x86_64-linux-gnu')
after=subprocess.run(['ldd',str(browser)],capture_output=True,text=True,check=True,env=environment).stdout
(folder/'ldd-after.txt').write_text(after);assert 'not found' not in after
print(json.dumps({'status':'PASS_TASK_LOCAL_LIBRARY','global_installation':False,'package':debs[0].name}))
'''

def prepare():
    files={'serve-v2.py':SERVER.replace('18770','5173').replace("'browser-state'","'browser-state-v2'").replace('__ROOT__',repr(REMOTE)),
           'capture-v2.py':CAPTURE.replace('18770','5173').replace("'browser-evidence-v1'","'browser-evidence-v2'").replace('__ROOT__',repr(REMOTE)),
           'libraries-v1.py':LIBRARIES.replace('__ROOT__',repr(REMOTE))}
    result=ssh('''
import json,base64
from pathlib import Path
root=Path(__ROOT__)/'browser-app'
for name,value in __FILES__.items():
 with (root/name).open('xb') as f:f.write(base64.b64decode(value))
print(json.dumps({'status':'PREPARED_NOT_EXECUTED','files':list(__FILES__)}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__FILES__',repr({k:base64.b64encode(v.encode()).decode() for k,v in files.items()})))
    for name,body in files.items():
        target=PRIVATE/'browser-scripts'/name;target.write_text(body,encoding='utf-8',newline='\n')
    print(json.dumps(result))

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':prepare()
    elif mode=='stop-v1':print(ssh("import json;from pathlib import Path;p=Path("+repr(REMOTE+'/browser-state/stop.json')+");p.write_text(json.dumps({'reason':'QA origin corrected to existing approved5173'}));print(json.dumps({'status':'STOP_REQUESTED'}))"))
    else:
        file={'libraries':'libraries-v1.py','server':'serve-v2.py','capture':'capture-v2.py'}[mode]
        run('ui-browser-'+mode+'-v2',[REMOTE+'/qa-env/bin/python','-B',REMOTE+'/browser-app/'+file],REMOTE,
            {'HOME':REMOTE+'/home','TMPDIR':REMOTE+'/tmp','PLAYWRIGHT_BROWSERS_PATH':REMOTE+'/software/playwright','LD_LIBRARY_PATH':REMOTE+'/software/browser-libraries-v1/root/usr/lib/x86_64-linux-gnu'})
