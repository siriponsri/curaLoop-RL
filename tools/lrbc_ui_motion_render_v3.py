"""Render the approved, offline, capture-derived HyperFrames walkthrough on CPU."""
import base64,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,REMOTE,ssh,run
SOURCE=r'''
import json,os,subprocess,shutil,time
from pathlib import Path
root=Path(__ROOT__);project=root/'motion-walkthrough-v4';assets=project/'assets';assets.mkdir(parents=True,exist_ok=False)
for name,source in __SCREENS__.items():shutil.copyfile(root/'browser-evidence-v5'/source,assets/name)
shutil.copyfile(root/'source-v8/frontend/public/fonts/NotoSansThai.ttf',assets/'NotoSansThai.ttf');shutil.copyfile(root/'source-v8/frontend/public/fonts/OFL.txt',assets/'OFL.txt')
gsap=root/'source/frontend/node_modules/gsap';shutil.copyfile(gsap/'dist/gsap.min.js',assets/'gsap.min.js')
for p in gsap.glob('*LICENSE*'):shutil.copyfile(p,assets/p.name)
import base64
for name,raw in __FILES__.items():(project/name).write_bytes(base64.b64decode(raw))
env=os.environ.copy();env.update(HOME=str(root/'home'),TMPDIR=str(root/'tmp'),XDG_CACHE_HOME=str(root/'cache'),XDG_CONFIG_HOME=str(root/'config'),HYPERFRAMES_SKIP_SKILLS='1',DO_NOT_TRACK='1',CI='1',PRODUCER_BROWSER_GPU_MODE='software',CUDA_VISIBLE_DEVICES='',LD_LIBRARY_PATH=str(root/'software/browser-libraries-v1/root/usr/lib/x86_64-linux-gnu'),PATH=str(root/'software/media-bin')+':'+str(root/'software/node-v24.19.0-linux-x64/bin')+':'+env['PATH'])
wrapper=project/'cpu-chrome.py'
wrapper.write_text("#!/usr/bin/python3\nimport os,sys\nargs=[a for a in sys.argv[1:] if not a.startswith(('--use-gl=','--use-angle=','--enable-features='))]\nargs+=['--disable-gpu','--disable-gpu-compositing','--disable-accelerated-2d-canvas','--disable-webgl','--disable-webgl2','--disable-vulkan','--disable-features=Vulkan,WebGPU','--use-gl=disabled']\nos.execv("+repr(str(root/'home/.cache/hyperframes/chrome/chrome-headless-shell/linux-152.0.7977.30/chrome-headless-shell-linux64/chrome-headless-shell'))+",['chrome-headless-shell',*args])\n")
wrapper.chmod(0o700)
env.update(HYPERFRAMES_BROWSER_PATH=str(wrapper),LIBGL_ALWAYS_SOFTWARE='1',__EGL_VENDOR_LIBRARY_FILENAMES=str(project/'no-egl-vendors.json'),VK_ICD_FILENAMES=str(project/'no-vulkan-drivers.json'))
cli=str(root/'motion-tools/node_modules/.bin/hyperframes');results=[]
for name,args in [('lint',['lint','--json']),('validate',['validate','--json']),('inspect',['inspect','--json','--at','2.5,5.3,7.5,10.3,12.5,15.3,17.5']),('render',['render','--output',str(project/'molecular-studio.mp4'),'--no-browser-gpu','--fps','24','--quality','standard','--workers','1','--low-memory-mode','--experimental-fast-capture=false','--no-page-side-compositing'])]:
 with (project/(name+'.txt')).open('x') as log:
  process=subprocess.Popen([cli,*args],cwd=project,env=env,stdout=log,stderr=subprocess.STDOUT)
  seen={};device_checks=0
  while process.poll() is None:
   owned={process.pid};procrows=[]
   for entry in Path('/proc').iterdir():
    if not entry.name.isdigit():continue
    try:procrows.append((int(entry.name),int((entry/'stat').read_text().rsplit(')',1)[1].split()[1])))
    except (OSError,ValueError):pass
   for _ in range(8):owned.update(pid for pid,ppid in procrows if ppid in owned)
   for pid in owned:
    try:
     entry=Path('/proc')/str(pid);cmd=(entry/'cmdline').read_bytes().replace(bytes([0]),b' ').decode(errors='replace');seen[pid]=cmd
     for fd in (entry/'fd').iterdir():
      try:target=os.readlink(fd)
      except OSError:continue
      if target.startswith('/dev/nvidia'):
       (project/'gpu-device-rejection.json').write_text(json.dumps({'pid':pid,'cmd':cmd,'target':target}))
       raise RuntimeError('Unexpected GPU device opened')
     device_checks+=1
    except (FileNotFoundError,ProcessLookupError):pass
   time.sleep(.2)
  r=process
 (project/(name+'-processes.json')).write_text(json.dumps({'forced_browser_mode':env['PRODUCER_BROWSER_GPU_MODE'],'nvidia_fd_checks':device_checks,'observed_descendants':seen},indent=2))
 results.append({'check':name,'argv':args,'exit_code':r.returncode});(project/'results.json').write_text(json.dumps(results,indent=2))
 if r.returncode:raise SystemExit(r.returncode)
probe=subprocess.check_output([str(root/'software/media-bin/ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(project/'molecular-studio.mp4')],env=env);(project/'ffprobe.json').write_bytes(probe)
# Deterministic layout/motion map and representative decoded frames.
for second in [2,7,12,17]:subprocess.run([str(root/'software/media-bin/ffmpeg'),'-hide_banner','-loglevel','error','-threads','1','-ss',str(second),'-i',str(project/'molecular-studio.mp4'),'-frames:v','1',str(project/('frame-'+str(second)+'.png'))],env=env,check=True)
(project/'animation-map.json').write_text(json.dumps({'duration_seconds':20,'fps':24,'scenes':[{'start':i*5,'hero':i*5+2.5,'transition_seconds':.45,'caption_entrance_seconds':.55} for i in range(4)],'numeric_interpolation':False,'source':'separate actual browser captures; not continuous recording'},indent=2))
print(json.dumps({'status':'PASS_RENDERED','project':project.name}))
'''
if __name__=='__main__':
 if sys.argv[1]=='prepare':
  files={p.name:base64.b64encode(p.read_bytes()).decode() for p in (ROOT/'docs/media/molecular-studio').iterdir() if p.name in ['DESIGN.md','index.html']}
  body=SOURCE.replace('__ROOT__',repr(REMOTE)).replace('__FILES__',repr(files)).replace('__SCREENS__',repr({'overview-en.png':'01-overview-en.png','overview-th.png':'01-overview-th.png','pending-en.png':'03-lab-pending-en.png','workspace-en.png':'08-workspace-en.png'}))
  (PRIVATE/'motion-render-v3.py').write_text(body,encoding='utf-8',newline='\n')
  print(ssh("import base64,json;from pathlib import Path;p=Path("+repr(REMOTE+'/motion-render-v3.py')+");assert not p.exists();p.write_bytes(base64.b64decode("+repr(base64.b64encode(body.encode()).decode())+"));print(json.dumps({'status':'PREPARED'}))"))
 else:run('ui-motion-render-v3',[REMOTE+'/qa-env/bin/python','-B',REMOTE+'/motion-render-v3.py'],REMOTE)
