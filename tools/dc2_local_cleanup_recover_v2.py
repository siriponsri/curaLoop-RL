"""Recover partial owned cleanup using the same authorized Docker boundary, no chmod."""
import base64
import json
import subprocess
from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write

PROGRAM = r'''
import hashlib,http.client,json,os,resource,socket,sys,threading,time
from pathlib import Path
root=Path('/home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1')
resource.setrlimit(resource.RLIMIT_CPU,(180,180));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
watch=threading.Timer(500,lambda:os._exit(124));watch.daemon=True;watch.start()
p=json.load(sys.stdin)
assert root.resolve()==root and root.parent.resolve()==Path('/home/chaw/curaloop-tasks') and not root.is_symlink()
manifest_path=root.parent/(root.name+'-return-v1.manifest.json')
receipt_path=root.parent/(root.name+'-return-v1.receipt.json')
archive_path=root.parent/(root.name+'-return-v1.tar.gz')
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(manifest_path)==p['manifest_sha256']
assert json.loads(receipt_path.read_text())['archive_sha256']==p['archive_sha256'] and p['local_all_files_reread'] is True
manifest=json.loads(manifest_path.read_text());remaining=0
for here,dirs,files in os.walk(root,followlinks=False):
 for name in [*dirs,*files]:
  path=Path(here)/name;rel=path.relative_to(root).as_posix()
  if path.is_symlink():
   assert manifest['symlink_metadata'].get(rel)==os.readlink(path)
   if name in dirs:dirs.remove(name)
  elif path.is_file():
   assert rel in manifest['files'] and sha(path)==manifest['files'][rel]['sha256'];remaining+=1
class Unix(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect('/var/run/docker.sock')
def api(method,path,body=None):
 c=Unix('localhost',timeout=30);data=None if body is None else json.dumps(body).encode()
 c.request(method,path,body=data,headers={'Content-Type':'application/json'});r=c.getresponse();raw=r.read();status=r.status;c.close()
 assert status<300,(status,raw[:500]);return json.loads(raw) if raw else {}
assert not any(c.get('Labels',{}).get('curaloop.task')==root.name for c in api('GET','/containers/json?all=1'))
name='curaloop-dc2-local-cleanup-20261113-v2'
body="""import json,os,resource,shutil,threading,time
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(120,120))
watch=threading.Timer(300,lambda:os._exit(124));watch.daemon=True;watch.start()
root=Path('/owned')
assert root.is_dir() and not root.is_symlink()
for path in root.iterdir():
 if path.is_dir() and not path.is_symlink():shutil.rmtree(path)
 else:path.unlink()
assert not list(root.iterdir())
print(json.dumps({'status':'PASS_OWNED_BIND_CONTENTS_CLEARED'}),flush=True)
os._exit(0)
"""
config={'Image':'sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d','Cmd':['python','-c',body],'User':'0:0','Labels':{'curaloop.task':root.name,'curaloop.operation':'exact-cleanup-v2'},'HostConfig':{'NetworkMode':'none','NanoCpus':1000000000,'CpusetCpus':str(max(os.sched_getaffinity(0))),'Memory':512*1024**2,'MemorySwap':512*1024**2,'ReadonlyRootfs':True,'PidsLimit':32,'Privileged':False,'Mounts':[{'Type':'bind','Source':str(root),'Target':'/owned','ReadOnly':False}]}}
api('POST','/containers/create?name='+name,config)
info=api('GET','/containers/'+name+'/json');h=info['HostConfig']
assert h['NetworkMode']=='none' and h['ReadonlyRootfs'] and not h['Privileged'] and h['NanoCpus']==1000000000 and h['Memory']==h['MemorySwap']==512*1024**2
assert len(h['Mounts'])==1 and h['Mounts'][0]['Source']==str(root)
api('POST','/containers/'+name+'/start')
began=time.monotonic()
while True:
 info=api('GET','/containers/'+name+'/json')
 if not info['State']['Running']:break
 assert time.monotonic()-began<340
 time.sleep(.5)
assert info['State']['ExitCode']==0,info['State']
assert not list(root.iterdir())
api('DELETE','/containers/'+name)
root.rmdir()
for path in (archive_path,manifest_path,receipt_path):
 assert path.parent.resolve()==Path('/home/chaw/curaloop-tasks') and path.name.startswith(root.name+'-return-v1.')
 path.unlink()
assert not root.exists() and not any(path.exists() for path in (archive_path,manifest_path,receipt_path))
result={'status':'PASS_EXACT_OWNED_CONTAINER_ASSISTED_CLEANUP','remaining_files_verified_before_cleanup':remaining,'remote_root_absent':True,'export_files_absent':True,'cleanup_container_removed':True,'permissions_changed':False,'shared_models_images_other_projects_untouched':True,'host_config':h,'final_container_state':info['State'],'retained_cpu_cap_seconds':300,'host_observed_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime}
print(json.dumps(result),flush=True);os._exit(0)
'''

def main():
    _, ledger = authority()
    proof = read(PUBLIC / "full-remote-return-v1.json")
    assert proof["local_all_files_reread"]
    assert sha(TASK / "remote-return-v1/owned-persistent-files.tar.gz") == proof["archive_sha256"]
    old = read(TASK / "remote-persistent-cleanup-v1-transport.json")
    write(PUBLIC / "owned-cleanup-v1.json", {"status":"FAIL_PARTIAL_OWNED_CLEANUP_RETAINED", "error":"PermissionError on root-owned native environment file; complete returned originals remain local", "transport_returncode":old["returncode"], "system_permissions_changed":False})
    name = "remote-exact-cleanup-recovery-v2"
    assert name not in ledger["bookings"]
    ledger["retained_cpu_seconds"]["return_delivery"] += 300
    assert ledger["retained_cpu_seconds"]["return_delivery"] <= ledger["stage_cpu_caps_seconds"]["return_delivery"]
    ledger["bookings"][name] = {"status":"RESERVED","host":"dr-train-cleanup","bucket":"return_delivery","cpu_cap":300,"gpu_cap":0}
    save(ledger)
    encoded=base64.b64encode(PROGRAM.encode()).decode()
    command="python3 -c \"import base64;exec(compile(base64.b64decode('"+encoded+"'),'<exact-owned-cleanup-v2>','exec'))\""
    ssh=["rtk","proxy","ssh","-T","-o","BatchMode=yes","-o","StrictHostKeyChecking=yes","-o","ConnectTimeout=15","100.77.149.83"]
    result=subprocess.run([*ssh,command],input=json.dumps({"archive_sha256":proof["archive_sha256"],"manifest_sha256":proof["manifest_sha256"],"local_all_files_reread":True}),text=True,encoding="utf-8",capture_output=True,timeout=550)
    write(TASK / "cleanup-recovery-v2-transport.json",{"returncode":result.returncode,"stdout":result.stdout,"stderr":result.stderr})
    ledger=read(TASK / "ledger.json");ledger["bookings"][name]["status"]="PASS" if result.returncode==0 else "FAIL";save(ledger)
    assert result.returncode==0,result.stderr[-1600:]
    fresh=subprocess.run([*ssh,"test ! -e /home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1 && test ! -e /home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1-return-v1.tar.gz && printf 'PASS_FRESH_OWNED_ABSENCE'"],capture_output=True,text=True,timeout=30)
    assert fresh.returncode==0 and fresh.stdout=="PASS_FRESH_OWNED_ABSENCE"
    receipt={**json.loads(result.stdout),"fresh_ssh_absence":fresh.stdout,"full_return_receipt_sha256":sha(PUBLIC/"full-remote-return-v1.json")}
    write(PUBLIC / "owned-cleanup-v2.json",receipt)
    print(json.dumps(receipt))

if __name__ == "__main__":
    main()
