"""Create only the new owned root and upload the previously verified return."""
import base64,json,subprocess
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,digest,write_new
from tools.sara_transport_v1 import invoke

REMOTE=r'''
import base64,hashlib,json,os,resource,shutil,socket,subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(30,30));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
p=json.load(__import__('sys').stdin);r=base64.b64decode(p['release_b64']);assert hashlib.sha256(r).hexdigest()==p['release_sha256']
t=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1')
assert os.environ.get('USER')=='chaw' and socket.gethostname()=='dr-train' and not t.exists()
assert t.parent.resolve()==Path('/home/chaw/curaloop-tasks') and shutil.disk_usage(t.parent).free>40*1024**3
image='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d'
v=json.loads(subprocess.check_output(['docker','image','inspect',image],text=True,timeout=15))[0]
assert v['Id']==image
t.mkdir();(t/'incoming').mkdir();(t/'leases').mkdir();(t/'release.json').write_bytes(r)
info={'status':'PASS_NEW_OWNED_ROOT_ONLY','host':socket.gethostname(),'user':os.environ.get('USER'),
      'free_disk_bytes':shutil.disk_usage(t).free,'base_image_id':v['Id'],'root':str(t),
      'gpu_inventory':subprocess.run(['nvidia-smi','--query-gpu=name,uuid,memory.total,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,timeout=15).stdout}
(t/'bootstrap-receipt.json').write_text(json.dumps(info,indent=2));print(json.dumps(info))
'''

def main():
    r,l=authority('technical')
    bundle=ROOT/r['prior_return_bundle'];assert digest(bundle)==r['prior_return_bundle_sha256']
    manifest=bundle.parent/'owned-manifest.json'
    value=invoke(REMOTE,dict(release_b64=base64.b64encode(RELEASE.read_bytes()).decode(),release_sha256=digest(RELEASE)))
    write_new(ACCOUNT/'bootstrap-transport-v1.json',value);assert value['exit_code']==0
    write_new(PUBLIC/'bootstrap-v1.json',json.loads(value['stdout']))
    for path,name in [(bundle,'prior-owned-return.tar.gz'),(manifest,'prior-owned-manifest.json')]:
        remote='100.77.149.83:'+r['remote_root']+'/incoming/'+name
        p=subprocess.run(['rtk','proxy','scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',str(path),remote],capture_output=True,text=True,timeout=1800)
        write_new(ACCOUNT/(name+'.upload-v1.json'),dict(exit_code=p.returncode,stderr=p.stderr,bytes=path.stat().st_size,sha256=digest(path)))
        assert p.returncode==0,'Preserve upload state and inspect rather than replay scientific work'
    print(json.dumps({'status':'PASS_PRIOR_RETURN_UPLOADED_NOT_RESTORED','bytes':bundle.stat().st_size,'reference_execution':'NOT_RUN','gpu_allocated_seconds':0}))

if __name__=='__main__':main()
