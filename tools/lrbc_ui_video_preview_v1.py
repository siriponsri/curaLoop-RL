"""Owned loopback-only preview; explicit stop before final complete return."""
import base64,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,REMOTE,ssh,run
SOURCE=r'''
from pathlib import Path
from http.server import HTTPServer,SimpleHTTPRequestHandler
from functools import partial
import time,json
root=Path(__ROOT__);folder=root/'motion-walkthrough-v4';stop=folder/'preview-stop.json'
(folder/'review.html').write_text('<!doctype html><html lang="en"><title>CuraLoop-RL walkthrough review</title><body style="margin:0;background:#28282B"><video controls muted playsinline preload="auto" style="width:100vw;height:100vh" src="molecular-studio.mp4"></video></body></html>')
server=HTTPServer(('127.0.0.1',5173),partial(SimpleHTTPRequestHandler,directory=str(folder)));server.timeout=.25;deadline=time.monotonic()+150
while not stop.exists() and time.monotonic()<deadline:server.handle_request()
server.server_close();(folder/'preview-terminal.json').write_text(json.dumps({'stopped_explicitly':stop.exists()}))
if not stop.exists():raise SystemExit(124)
'''
if __name__=='__main__':
 if sys.argv[1]=='prepare':
  body=SOURCE.replace('__ROOT__',repr(REMOTE));(PRIVATE/'video-preview-v1.py').write_text(body,encoding='utf-8',newline='\n')
  print(ssh("import base64,json;from pathlib import Path;p=Path("+repr(REMOTE+'/video-preview-v1.py')+");assert not p.exists();p.write_bytes(base64.b64decode("+repr(base64.b64encode(body.encode()).decode())+"));print(json.dumps({'status':'PREPARED'}))"))
 elif sys.argv[1]=='stop':print(ssh("import json;from pathlib import Path;p=Path("+repr(REMOTE+'/motion-walkthrough-v4/preview-stop.json')+");p.write_text('{}');print(json.dumps({'status':'STOP_REQUESTED'}))"))
 else:run('ui-video-preview-v1',['/usr/bin/python3','-B',REMOTE+'/video-preview-v1.py'],REMOTE)
