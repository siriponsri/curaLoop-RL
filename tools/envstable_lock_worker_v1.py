"""Lock complete installed artifact, offline byte reconstruction and two clean starts."""
import hashlib,importlib.util,json,os,resource,sys
from pathlib import Path
LOCK=r'''
import hashlib,importlib.metadata as md,json,os,shutil,stat
from pathlib import Path
root=Path('/source');out=Path('/rebuilt');manifest={};total=0
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024**2):h.update(b)
 return h.hexdigest()
for base,dirs,names in os.walk(root,followlinks=False):
 base=Path(base);rel=base.relative_to(root);(out/rel).mkdir(parents=True,exist_ok=True)
 for n in dirs[:]+names:
  p=base/n;r=p.relative_to(root).as_posix();dest=out/r;s=p.lstat()
  if p.is_symlink():
   target=os.readlink(p);assert not Path(target).is_absolute() and p.resolve().is_relative_to(root)
   dest.symlink_to(target);manifest[r]=dict(type='symlink',target=target)
   if n in dirs:dirs.remove(n)
  elif p.is_file():
   total+=s.st_size;assert total<32*1024**3
   h=sha(p);shutil.copyfile(p,dest);dest.chmod(stat.S_IMODE(s.st_mode));assert sha(dest)==h
   manifest[r]=dict(type='file',bytes=s.st_size,sha256=h,mode=stat.S_IMODE(s.st_mode))
lock=dict(schema='curaloop.installed-artifact-lock.v1',base_image='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d',python='3.10.22',files=manifest,regular_bytes=total)
Path('/control/environment-content-lock.json').write_text(json.dumps(lock,indent=2))
versions={}
for profile in sorted((root/'env').iterdir()):
 if profile.is_dir():versions[profile.name]=sorted([dict(name=d.metadata['Name'],version=d.version) for d in md.distributions(path=[str(profile)])],key=lambda d:d['name'].lower())
Path('/control/package-versions.json').write_text(json.dumps(versions,indent=2))
Path('/control/reconstruction-result.json').write_text(json.dumps(dict(status='PASS_OFFLINE_CONTENT_RECONSTRUCTION',files=len(manifest),regular_bytes=total,every_regular_file_rehashed=True,network=False,installer_executed=False,lock_sha256=sha(Path('/control/environment-content-lock.json')),versions_sha256=sha(Path('/control/package-versions.json')))))
'''
def main():
 resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1');assert hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
 s=importlib.util.spec_from_file_location('rt',t/'code/envstable_runtime_v1.py');rt=importlib.util.module_from_spec(s);s.loader.exec_module(rt)
 assert json.loads((t/'cycle3-result.json').read_text())['all_pass']
 source=t/'artifact';source.mkdir();(source/'env').symlink_to('../env');(source/'systemlibs').symlink_to('../systemlibs-v2')
 # Explicit mounts expose directory bytes rather than following an untrusted archive link.
 rebuilt=t/'reconstructed';rebuilt.mkdir();rebuilt.chmod(0o777)
 receipt=rt.run('offline-reconstruct-v1',LOCK,cpu=900,wall=1800,mounts=[(t/'env','/source/env',True),(t/'systemlibs-v2','/source/systemlibs',True),(rebuilt,'/rebuilt',False)],stage='validation',tmp_disk=True)
 path=t/'leases/offline-reconstruct-v1/reconstruction-result.json';result=json.loads(path.read_text()) if path.exists() else None;rows=[]
 if result:
  for cold in [1,2]:
   for group in json.loads((t/'build-plan-v1.json').read_text())['groups']:
    name=group['name'];home=t/('cold-home-'+str(cold))/name;home.mkdir(parents=True);home.chmod(0o777)
    paths=('/env/addons-profile12:' if name=='profile-12' else '')+'/env/'+name+':/env/base'
    program='import runpy,sys\nsys.argv=["envstable_workloads_v2.py",'+repr(name)+']\nrunpy.run_path("/code/envstable_workloads_v2.py",run_name="__main__")'
    ident='cold'+str(cold)+'-'+name
    v=rt.run(ident,program,cpu=30,wall=90,mounts=[(rebuilt/'env','/env',True),(rebuilt/'systemlibs','/syslibs',True),(t/'code','/code',True),(home,'/home/worker',False)],env=['HOME=/home/worker','PYSTOW_HOME=/home/worker/.data','XDG_CACHE_HOME=/home/worker/.cache','MPLCONFIGDIR=/home/worker/.cache/matplotlib','TF_USE_LEGACY_KERAS=1','TF_CPP_MIN_LOG_LEVEL=2','LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu','PYTHONPATH='+paths],tmp_disk=True,stage='validation')
    f=t/'leases'/ident/'workload-result.json';rows.append(dict(cold=cold,profile=name,receipt=v,result=json.loads(f.read_text()) if f.exists() else None));(t/'cold-progress.json').write_text(json.dumps(rows,indent=2))
 out=dict(status='OFFLINE_RECONSTRUCTION_AND_COLD_STARTS_COMPLETED',reconstruction=result,reconstruction_receipt=receipt,cold_starts=rows,all_pass=bool(result) and len(rows)==26 and all(x['result'] and x['result']['status']=='PASS_WORKLOAD' for x in rows),host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime)
 (t/'lock-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
if __name__=='__main__':main()
