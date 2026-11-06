"""Resolve optional host gaps with owned binaries and managed CPU Chrome only."""
import base64,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,REMOTE,ssh,run

SOURCE=r'''
import json,os,re,subprocess,urllib.request
from pathlib import Path
root=Path(__ROOT__);folder=root/'motion-environment-v2';folder.mkdir(exist_ok=False)
env=os.environ.copy();env.update(HOME=str(root/'home'),TMPDIR=str(root/'tmp'),XDG_CACHE_HOME=str(root/'cache'),XDG_CONFIG_HOME=str(root/'config'),npm_config_cache=str(root/'cache/npm'),PUPPETEER_CACHE_DIR=str(root/'cache/puppeteer'),HYPERFRAMES_SKIP_SKILLS='1',DO_NOT_TRACK='1',CI='1',LD_LIBRARY_PATH=str(root/'software/browser-libraries-v1/root/usr/lib/x86_64-linux-gnu'),PATH=str(root/'software/media-bin')+':'+str(root/'software/node-v24.19.0-linux-x64/bin')+':'+env['PATH'])
def command(name,argv,required=True):
 with (folder/(name+'.txt')).open('x') as log:r=subprocess.run(argv,cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT)
 if required and r.returncode:raise SystemExit(r.returncode)
 return {'name':name,'argv':argv,'exit_code':r.returncode}
results=[]
results.append(command('download-unzip',['apt-get','download','unzip']))
debs=list(folder.glob('*.deb'));assert len(debs)==1
results.append(command('extract-unzip',['dpkg-deb','--extract',str(debs[0]),str(folder/'root')]))
os.symlink(str(folder/'root/usr/bin/unzip'),root/'software/media-bin/unzip')
with urllib.request.urlopen('https://registry.npmjs.org/@ffprobe-installer/linux-x64/latest',timeout=20) as response:raw=response.read(1024*1024+1)
assert len(raw)<=1024*1024;(folder/'ffprobe-package-metadata.json').write_bytes(raw)
metadata=json.loads(raw);version=metadata['version'];assert re.fullmatch(r'\d+\.\d+\.\d+',version)
results.append(command('install-ffprobe',['npm','install','--prefix',str(root/'motion-tools'),'--save-exact','--no-audit','--no-fund','@ffprobe-installer/linux-x64@'+version]))
probe=root/'motion-tools/node_modules/@ffprobe-installer/linux-x64/ffprobe';assert probe.is_file()
os.symlink(str(probe),root/'software/media-bin/ffprobe')
cli=str(root/'motion-tools/node_modules/.bin/hyperframes')
results.append(command('disable-task-telemetry',[cli,'telemetry','disable']))
results.append(command('managed-chrome',[cli,'browser','ensure']))
results.append(command('doctor',[cli,'doctor']))
(folder/'results.json').write_text(json.dumps(results,indent=2))
'''

if __name__=='__main__':
    if sys.argv[1]=='prepare':
        body=SOURCE.replace('__ROOT__',repr(REMOTE));(PRIVATE/'motion-environment-v2.py').write_text(body,encoding='utf-8',newline='\n')
        print(ssh("import json,base64;from pathlib import Path;p=Path("+repr(REMOTE+'/motion-environment-v2.py')+");p.write_bytes(base64.b64decode("+repr(base64.b64encode(body.encode()).decode())+"));print(json.dumps({'status':'PREPARED_NOT_EXECUTED'}))"))
    else:run('ui-motion-environment-v2',['/usr/bin/python3','-B',REMOTE+'/motion-environment-v2.py'],REMOTE)
