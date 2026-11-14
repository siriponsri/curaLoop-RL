"""Restore complete artifacts, build missing profiles, and smoke-test fresh workers."""
import base64,hashlib,importlib.util,json,os,resource,shutil,sys,tarfile
from pathlib import Path

SETUP=r'''
import importlib.metadata,json,subprocess,sys,traceback
from pathlib import Path
plan=json.loads(Path('/control/plan.json').read_text());target=Path('/env')/plan['name'];out={}
try:
 target.mkdir(exist_ok=False)
 args=[sys.executable,'-m','pip','install','--disable-pip-version-check','--no-input','--cache-dir=/cache/pip',
  '--target='+str(target),'--constraint=/control/constraints.txt','--report=/control/pip-report.json',*plan['packages']]
 with Path('/control/pip.log').open('wb') as log:p=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,timeout=1700)
 out=dict(status='PASS_INSTALL' if p.returncode==0 else 'FAIL_INSTALL',exit_code=p.returncode,
  versions={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=[str(target)])})
except BaseException as e:out=dict(status='FAIL_INSTALL',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc())
finally:Path('/control/install-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''

IMPORTS=r'''
import importlib,importlib.metadata,json,os,sys,traceback
from pathlib import Path
plan=json.loads(Path('/control/plan.json').read_text());events=[];out={}
try:
 for name in plan['imports']:
  try:importlib.import_module(name);events.append(dict(module=name,pass_=True))
  except BaseException as e:events.append(dict(module=name,pass_=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc()))
 out=dict(status='PASS_IMPORTS' if all(x['pass_'] for x in events) else 'FAIL_IMPORTS',events=events,python=sys.version)
finally:Path('/control/import-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while True:
   b=f.read(1024**2)
   if not b:break
   h.update(b)
 return h.hexdigest()

def main():
 resource.setrlimit(resource.RLIMIT_CPU,(1200,1200));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1')
 assert sha(t/'release.json')==p['release_sha256'];spec=importlib.util.spec_from_file_location('rt',t/'code/envstable_runtime_v1.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
 # Count all writable mounts conservatively, leaving 16 GiB for staged/return artifacts.
 rt.SUPERVISOR=rt.SUPERVISOR.replace('while child.poll() is None:', '''last_disk_check=0
while child.poll() is None:
 if time.time()-last_disk_check>10:
  last_disk_check=time.time();total=0
  for root in ['/env','/cache','/home/worker','/tmp','/control','/syslibs']:
   for base,dirs,names in os.walk(root):
    for name in names:
     try:total+=os.lstat(os.path.join(base,name)).st_size
     except FileNotFoundError:pass
  if total>=64*1024**3:reason='DISK_CAP'
''')
 for name in ('env','cache','home','systemlibs'):
  (t/name).mkdir();(t/name).chmod(0o777)
 (t/'build-worker-v1.py').write_bytes(base64.b64decode(p['worker_b64']));(t/'build-plan-v1.json').write_text(json.dumps(p['plan'],indent=2))
 manifest=json.loads((t/'incoming/prior-manifest.json').read_text());bundle=t/'incoming/prior-return.tar.gz'
 assert sha(bundle)==p['prior_bundle_sha256']
 mapping={'env/base/':'base','env/lineage-06/':'profile-21','env/lineage-07/':'papyrus','env/lineage-08/':'prolif'};count=0;total=0;seen=set()
 with tarfile.open(bundle,'r|gz') as archive:
  for item in archive:
   if not item.isfile():continue
   assert item.name in manifest and item.size==manifest[item.name]['bytes']
   source=archive.extractfile(item);h=hashlib.sha256();target=None
   for prefix,name in mapping.items():
    if item.name.startswith(prefix):
     suffix=Path(item.name[len(prefix):]);assert not suffix.is_absolute() and '..' not in suffix.parts
     target=t/'env'/name/suffix;target.parent.mkdir(parents=True,exist_ok=True);break
   dst=target.open('xb') if target else None
   try:
    while True:
     block=source.read(1024**2)
     if not block:break
     h.update(block)
     if dst:dst.write(block)
   finally:
    source.close()
    if dst:dst.close()
   assert h.hexdigest()==manifest[item.name]['sha256'];seen.add(item.name)
   if target:target.chmod(0o755 if item.mode&0o111 else 0o644);count+=1;total+=item.size
 assert seen==set(manifest)
 # Preparation is complete before any fresh consumer process receives this search tree.
 sys.path.insert(0,str(t/'code'));from envstable_overlay_v1 import extract_deb
 packages=[extract_deb(path,t/'systemlibs') for path in sorted((t/'packages').glob('*.deb'))]
 (t/'system-library-manifest.json').write_text(json.dumps(packages,indent=2))
 mounts=[(t/'env','/env',False),(t/'cache','/cache',False),(t/'home','/home/worker',False),(t/'systemlibs','/syslibs',True)]
 env=['HOME=/home/worker','PYSTOW_HOME=/home/worker/.data','XDG_CACHE_HOME=/home/worker/.cache','MPLCONFIGDIR=/home/worker/.cache/matplotlib',
  'PIP_ROOT_USER_ACTION=ignore','TMPDIR=/tmp','TF_USE_LEGACY_KERAS=1','TF_CPP_MIN_LOG_LEVEL=2',
  'LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu','PYTHONPATH=/env/base','LOKY_MAX_CPU_COUNT=1']
 outcomes=[];rx=0;plan=p['plan']
 for group in plan['groups']:
  row=dict(name=group['name'],cases=group['cases'],reuse=group.get('reuse'),install=None,imports=None)
  if not group.get('reuse'):
   if shutil.disk_usage(t).free<5*1024**3:row['error']='LOW_DISK';outcomes.append(row);break
   program='from pathlib import Path\nPath("/control/plan.json").write_text('+repr(json.dumps(group))+')\nPath("/control/constraints.txt").write_text('+repr(plan['constraints'])+')\n'+SETUP
   install=rt.run('install-'+group['name']+'-v1',program,cpu=1200,wall=1800,network=True,mounts=mounts,env=env,network_bytes=max(1,20*1024**3-rx),tmp_disk=True,stage='build')
   rx+=install['resources']['network_receive_bytes'];path=t/'leases'/('install-'+group['name']+'-v1')/'install-result.json'
   row['install']=dict(receipt=install,result=json.loads(path.read_text()) if path.exists() else None)
   if install['state']['ExitCode'] or not row['install']['result'] or row['install']['result']['status']!='PASS_INSTALL':
    log=t/'leases'/('install-'+group['name']+'-v1')/'pip.log';row['pip_log_tail']=log.read_text(errors='replace')[-5000:] if log.exists() else 'NOT_EMITTED'
    outcomes.append(row);(t/'build-progress-v1.json').write_text(json.dumps(outcomes,indent=2));continue
  imports=sorted({name for case in group['cases'] for name in case['imports']});gp=dict(group,imports=imports)
  program='from pathlib import Path\nPath("/control/plan.json").write_text('+repr(json.dumps(gp))+')\n'+IMPORTS
  paths=['PYTHONPATH=/env/'+group['name']+':/env/base']
  imported=rt.run('imports-'+group['name']+'-v1',program,cpu=120,wall=180,mounts=mounts,env=[*env,*paths],tmp_disk=True,stage='build')
  path=t/'leases'/('imports-'+group['name']+'-v1')/'import-result.json'
  row['imports']=dict(receipt=imported,result=json.loads(path.read_text()) if path.exists() else None)
  outcomes.append(row);(t/'build-progress-v1.json').write_text(json.dumps(outcomes,indent=2))
 result=dict(status='PROFILE_BUILD_CYCLE_1_COMPLETED',rows=outcomes,restored_files=count,restored_bytes=total,
  source_manifest_full_reread=True,dependency_receive_bytes=rx,host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
  native_references=0,actor_calls=0)
 (t/'build-result-v1.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
