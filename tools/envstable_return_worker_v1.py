"""Root-owned/readable owned-file export inside an isolated read-only container."""
import base64,hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path

TASK=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1')
EXPORT=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1-export')
IMAGE='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d'
PROGRAM=r'''
import hashlib,json,os,resource,signal,stat,tarfile,time
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(2100,2100));signal.alarm(3600)
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
root=Path('/source');out=Path('/return');files={};directories={}
def meta(p):
 s=p.lstat();return {'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid,'mtime':int(s.st_mtime)}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while True:
   b=f.read(1024**2)
   if not b:break
   h.update(b)
 return h.hexdigest()
for base,dirs,names in os.walk(root,followlinks=False,onerror=lambda e:(_ for _ in ()).throw(e)):
 base=Path(base);directories[base.relative_to(root).as_posix()]=meta(base)
 for name in list(dirs):
  p=base/name
  if p.is_symlink():
   files[p.relative_to(root).as_posix()]={'type':'symlink','target':os.readlink(p),**meta(p)};dirs.remove(name)
 for name in names:
  p=base/name;relative=p.relative_to(root).as_posix()
  if p.is_symlink():files[relative]={'type':'symlink','target':os.readlink(p),**meta(p)}
  else:
   assert p.is_file(),'Unsupported special node'
   files[relative]={'type':'file','bytes':p.stat().st_size,'sha256':sha(p),**meta(p)}
assert sum(v.get('bytes',0) for v in files.values())<80*1024**3
manifest={'files':files,'directories':directories}
(out/'owned-manifest.json').write_text(json.dumps(manifest,indent=2))
bundle=out/'owned-return.tar.gz';assert not bundle.exists()
content_seen={}
with tarfile.open(bundle,'w:gz',compresslevel=1) as tar:
 for name,entry in sorted(directories.items()):
  item=tarfile.TarInfo(name);item.type=tarfile.DIRTYPE
  for key in ('mode','uid','gid','mtime'):setattr(item,key,entry[key])
  tar.addfile(item)
 for name,entry in sorted(files.items()):
  item=tarfile.TarInfo(name)
  for key in ('mode','uid','gid','mtime'):setattr(item,key,entry[key])
  if entry['type']=='symlink':
   item.type=tarfile.SYMTYPE;item.linkname=entry['target'];tar.addfile(item)
  else:
   key=(entry['sha256'],entry['bytes'])
   if key in content_seen:
    item.type=tarfile.LNKTYPE;item.linkname=content_seen[key];tar.addfile(item)
   else:
    item.size=entry['bytes']
    with (root/name).open('rb') as f:tar.addfile(item,f)
    content_seen[key]=name
cpu=int(dict(x.split() for x in Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines())['usage_usec'])/1e6
result={'status':'PASS_FULL_OWNED_WORKSPACE_EXPORTED','regular_files':sum(v['type']=='file' for v in files.values()),
 'symlinks':sum(v['type']=='symlink' for v in files.values()),'directories':len(directories),
 'regular_bytes':sum(v.get('bytes',0) for v in files.values()),'bundle_bytes':bundle.stat().st_size,
 'bundle_sha256':sha(bundle),'manifest_sha256':sha(out/'owned-manifest.json'),'export_container_cpu_seconds':cpu}
(out/'export-result.json').write_text(json.dumps(result,indent=2))
'''

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
    os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
    p=json.load(sys.stdin);assert hashlib.sha256((TASK/'release.json').read_bytes()).hexdigest()==p['release_sha256']
    assert TASK.resolve()==TASK and EXPORT.parent.resolve()==TASK.parent and not EXPORT.exists()
    source=base64.b64decode(p['worker_b64']);assert hashlib.sha256(source).hexdigest()==p['worker_sha256']
    (TASK/'return-worker.py').write_bytes(source)
    state={}
    names=subprocess.check_output(['docker','ps','-a','--filter','label=curaloop.task=env-stable-lr-20261114-v1','--format','{{.Names}}'],text=True).splitlines()
    for name in names:
        value=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
        assert not value['State']['Running'];state[name]=value
    (TASK/'pre-export-docker-state.json').write_text(json.dumps(state,indent=2))
    EXPORT.mkdir();EXPORT.chmod(0o777);(EXPORT/'export.py').write_text(PROGRAM)
    name='curaloop-envstable-owned-export-v1'
    command=['docker','create','--name',name,'--label','curaloop.task=env-stable-lr-20261114-v1','--network=none','--cpus=1',
       '--memory=2g','--memory-swap=2g','--pids-limit=32','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',
       '--mount',f'type=bind,source={TASK},target=/source,readonly','--mount',f'type=bind,source={EXPORT},target=/return',
       IMAGE,'python','/return/export.py']
    v=subprocess.run(command,capture_output=True,text=True,timeout=30)
    (EXPORT/'create-receipt.json').write_text(json.dumps({'exit_code':v.returncode,'stdout':v.stdout,'stderr':v.stderr}));assert v.returncode==0
    inspect=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
    h=inspect['HostConfig'];assert h['NanoCpus']==1000000000 and h['Memory']==2*1024**3 and h['ReadonlyRootfs'] and not h['DeviceRequests']
    (EXPORT/'container-admission.json').write_text(json.dumps({'id':inspect['Id'],'image':inspect['Image'],'host_config':h},indent=2))
    subprocess.run(['docker','start',name],check=True,capture_output=True,timeout=15)
    try:wait=subprocess.run(['docker','wait',name],capture_output=True,text=True,timeout=3700)
    except subprocess.TimeoutExpired:
        subprocess.run(['docker','kill',name],capture_output=True,timeout=15);raise
    log=subprocess.run(['docker','logs',name],capture_output=True,timeout=15)
    (EXPORT/'container-stdout.log').write_bytes(log.stdout);(EXPORT/'container-stderr.log').write_bytes(log.stderr)
    assert wait.stdout.strip()=='0',log.stderr.decode(errors='replace')[-1000:]
    result=json.loads((EXPORT/'export-result.json').read_text())
    result.update(export_root=str(EXPORT),source_root=str(TASK),container_name=name,
        remote_host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime)
    print(json.dumps(result))

if __name__=='__main__':main()
