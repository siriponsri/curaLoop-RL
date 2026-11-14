"""Verify the complete returned workspace before removing exact owned resources."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,digest,reserve,settle,write_new
from tools.sara_transport_v1 import invoke

VERIFY=r'''
import hashlib,json,os,resource,signal,stat
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(2400,2400));signal.alarm(2600)
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
t=Path('/owned');m=json.loads(Path('/exports/owned-manifest.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while True:
   block=f.read(1024**2)
   if not block:break
   h.update(block)
 return h.hexdigest()
files={};dirs={}
def meta(s):return dict(mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,mtime=int(s.st_mtime))
def error(e):raise e
for base,children,names in os.walk(t,followlinks=False,onerror=error):
 p=Path(base);rel=p.relative_to(t).as_posix();dirs[rel]=meta(p.lstat())
 for name in children[:]+names:
  q=p/name;s=q.lstat();r=q.relative_to(t).as_posix()
  if stat.S_ISLNK(s.st_mode):
   files[r]=dict(type='symlink',target=os.readlink(q),**meta(s))
   if name in children:children.remove(name)
  elif stat.S_ISREG(s.st_mode):files[r]=dict(type='file',bytes=s.st_size,sha256=sha(q),**meta(s))
  else:assert stat.S_ISDIR(s.st_mode),'Unexpected special file'
assert files==m['files'] and dirs==m['directories'],'Remote tree changed after export'
changed=0
for name,entry in dirs.items():
 if entry['uid']==0:
  p=t/name;assert p.is_dir() and not p.is_symlink();p.chmod(0o777);changed+=1
receipt=dict(status='PASS_REMOTE_FULL_REREAD_BEFORE_CLEANUP',files=len(files),directories=len(dirs),
 root_owned_directories_prepared=changed,content_and_metadata_match=True,
 cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime)
Path('/exports/cleanup-verified.json').write_text(json.dumps(receipt));print(json.dumps(receipt))
'''

DELETE=r'''
import json,os,resource,shutil,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(300,300));signal.alarm(600)
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
t=Path('/owned');assert t.is_mount() and t.is_dir() and not t.is_symlink()
r=json.loads(Path('/exports/cleanup-verified.json').read_text());assert r['status']=='PASS_REMOTE_FULL_REREAD_BEFORE_CLEANUP'
removed=0
for p in t.iterdir():
 if p.is_symlink() or not p.is_dir():p.unlink()
 else:shutil.rmtree(p)
 removed+=1
assert not list(t.iterdir());print(json.dumps(dict(status='PASS_OWNED_CONTENTS_REMOVED',top_level_entries=removed)))
'''

REMOTE=r'''
import hashlib,json,os,resource,subprocess,sys
from pathlib import Path,PurePosixPath
resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
p=json.load(sys.stdin);parent=Path('/home/chaw/curaloop-tasks');t=parent/'lr-sara-20261114-v1';out=parent/'lr-sara-20261114-v1-export'
assert parent.resolve()==parent and t.resolve()==t and out.resolve()==out and not t.is_symlink() and not out.is_symlink()
assert t.parent==parent and out.parent==parent and hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
assert hashlib.sha256((out/'owned-manifest.json').read_bytes()).hexdigest()==p['manifest_sha256']
label='curaloop.task=lr-sara-20261114-v1';image='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d'
existing=subprocess.check_output(['docker','ps','-aq','--filter','label='+label],text=True).split()
for ident in existing:
 i=json.loads(subprocess.check_output(['docker','inspect',ident],text=True))[0]
 assert i['Config']['Labels'].get('curaloop.task')=='lr-sara-20261114-v1' and not i['State']['Running']
receipts=[]
def run(name,program,wall):
 cmd=['docker','create','--name',name,'--label',label,'--network=none','--cpus=1','--memory=2g','--memory-swap=2g','--pids-limit=32',
  '--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',
  '--mount',f'type=bind,source={t},target=/owned','--mount',f'type=bind,source={out},target=/exports',image,'python','-c',program]
 c=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert c.returncode==0,c.stderr
 i=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
 assert i['HostConfig']['NanoCpus']==1000000000 and i['HostConfig']['Memory']==2*1024**3 and not i['HostConfig']['DeviceRequests']
 assert i['HostConfig']['CapDrop']==['ALL'] and i['HostConfig']['ReadonlyRootfs']
 subprocess.run(['docker','start',name],check=True,capture_output=True,timeout=15)
 try:w=subprocess.run(['docker','wait',name],capture_output=True,text=True,timeout=wall)
 except subprocess.TimeoutExpired:
  subprocess.run(['docker','kill',name],capture_output=True,timeout=15);raise
 logs=subprocess.run(['docker','logs',name],capture_output=True,text=True,timeout=15)
 receipt=dict(name=name,id=i['Id'],exit_code=w.stdout.strip(),stdout=logs.stdout,stderr=logs.stderr,
  program_sha256=hashlib.sha256(program.encode()).hexdigest(),host_config=i['HostConfig'])
 receipts.append(receipt);assert w.stdout.strip()=='0',receipt
 return json.loads(logs.stdout)
verification=run('curaloop-sara-cleanup-verify-v1',p['verify_program'],2700)
m=json.loads((out/'owned-manifest.json').read_text());own_count=0
for name,entry in m['directories'].items():
 rel=PurePosixPath(name);assert not rel.is_absolute() and '..' not in rel.parts
 path=t.joinpath(*rel.parts);assert path.resolve()==path and path.is_relative_to(t) and not path.is_symlink()
 if entry['uid']==os.getuid():path.chmod(0o777);own_count+=1
deleted=run('curaloop-sara-cleanup-delete-v1',p['delete_program'],650)
assert not list(t.iterdir()) and t.resolve()==parent/'lr-sara-20261114-v1';t.rmdir()
removed=[]
for ident in subprocess.check_output(['docker','ps','-aq','--filter','label='+label],text=True).split():
 i=json.loads(subprocess.check_output(['docker','inspect',ident],text=True))[0]
 assert i['Config']['Labels'].get('curaloop.task')=='lr-sara-20261114-v1' and i['Name'].startswith('/curaloop-sara-') and not i['State']['Running']
 subprocess.run(['docker','rm',ident],check=True,capture_output=True,timeout=30);removed.append(dict(id=ident,name=i['Name']))
assert out.resolve()==parent/'lr-sara-20261114-v1-export' and not out.is_symlink()
for path in out.iterdir():
 assert not path.is_dir();path.unlink()
out.rmdir()
remaining=subprocess.check_output(['docker','ps','-aq','--filter','label='+label],text=True).split()
assert not t.exists() and not out.exists() and not remaining
print(json.dumps(dict(status='PASS_EXACT_OWNED_CLEANUP',verification=verification,deleted=deleted,
 owner_directories_prepared=own_count,removed_containers=removed,helper_receipts=receipts,
 source_root_absent=True,export_root_absent=True,owned_containers_remaining=remaining,
 shared_images_models_services_modified=False,remote_host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime)))
'''

ABSENCE=r'''
import json,subprocess
from pathlib import Path
t=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1');out=t.parent/(t.name+'-export')
ids=subprocess.check_output(['docker','ps','-aq','--filter','label=curaloop.task=lr-sara-20261114-v1'],text=True).split()
assert not t.exists() and not t.is_symlink() and not out.exists() and not out.is_symlink() and not ids
print(json.dumps(dict(status='PASS_FRESH_SSH_ABSENCE',source_root_absent=True,export_root_absent=True,owned_containers=[])))
'''

def main():
 authority('analysis_return');r=json.loads((PUBLIC/'owned-return-verification-v1.json').read_text())
 assert r['every_file_content_and_link_metadata_verified'] and not r['returned_links_extracted_or_followed']
 reserve('remote-exact-cleanup-v1','analysis_return',3600,remote=True,scope='Complete independent remote reread then exact owned-root/export/container cleanup only')
 value=invoke(REMOTE,dict(release_sha256=digest(RELEASE),manifest_sha256=r['manifest_sha256'],verify_program=VERIFY,delete_program=DELETE),timeout=3500)
 write_new(ACCOUNT/'cleanup-transport-v1.json',value);assert value['exit_code']==0,value
 result=json.loads(value['stdout']);write_new(PUBLIC/'owned-cleanup-v1.json',result)
 settle('remote-exact-cleanup-v1','PASS_EXACT_OWNED_CLEANUP',measured_verification_container_cpu_seconds=result['verification']['cpu_seconds'],measured_remote_host_process_cpu_seconds=result['remote_host_process_cpu_seconds'])
 fresh=invoke(ABSENCE,{},timeout=45);write_new(ACCOUNT/'cleanup-fresh-absence-transport-v1.json',fresh);assert fresh['exit_code']==0
 write_new(PUBLIC/'owned-cleanup-fresh-absence-v1.json',json.loads(fresh['stdout']));print(result['status'])

if __name__=='__main__':main()
