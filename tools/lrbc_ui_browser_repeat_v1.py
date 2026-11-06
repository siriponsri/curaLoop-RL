"""Version capture scripts for corrected selectors and required fresh repetitions."""
import base64,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,REMOTE,ssh,run

def prepare(version):
    assert version in ['v4','v5','v6']
    body=(PRIVATE/'browser-app-v3-inputs/capture-v3.py').read_text(encoding='utf-8')
    assert body.count('[data-select-index=3]')==1
    body=body.replace('[data-select-index=3]','[data-select-index="3"]').replace('browser-evidence-v3','browser-evidence-'+version)
    local=PRIVATE/'browser-scripts'/('capture-'+version+'.py');local.write_text(body,encoding='utf-8',newline='\n')
    result=ssh('''
import json,base64
from pathlib import Path
p=Path(__ROOT__)/'browser-app-v3'/__NAME__
with p.open('xb') as f:f.write(base64.b64decode(__DATA__))
print(json.dumps({'status':'PREPARED_NOT_EXECUTED','script':p.name}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__NAME__',repr(local.name)).replace('__DATA__',repr(base64.b64encode(body.encode()).decode())))
    print(json.dumps(result))

if __name__=='__main__':
    mode,version=sys.argv[1:3]
    if mode=='prepare':prepare(version)
    else:run('ui-studio-browser-capture-'+version,[REMOTE+'/qa-env/bin/python','-B',REMOTE+'/browser-app-v3/capture-'+version+'.py'],REMOTE,
             {'HOME':REMOTE+'/home','TMPDIR':REMOTE+'/tmp','PLAYWRIGHT_BROWSERS_PATH':REMOTE+'/software/playwright','LD_LIBRARY_PATH':REMOTE+'/software/browser-libraries-v1/root/usr/lib/x86_64-linux-gnu'})
