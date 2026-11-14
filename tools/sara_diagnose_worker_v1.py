"""Restore retained dependencies and capture one import trace per affected lineage."""
import base64,hashlib,importlib.util,json,os,resource,signal,sys,tarfile
from pathlib import Path,PurePosixPath

TASK=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1')
PROGRAM=r'''
import importlib,json,os,subprocess,sys,traceback
from pathlib import Path
mounts={}
for path in ['/','/tmp','/control','/retained-env']:
 v=os.statvfs(path);mounts[path]={'free_bytes':v.f_bavail*v.f_frsize,'total_bytes':v.f_blocks*v.f_frsize,'free_inodes':v.f_favail}
result={'mounts':mounts,'home':str(Path.home()),'pwd':os.getcwd(),'network':'none; differs from original setup bridge, avoids scientific-input downloads','cases':[]}
for identity,module,group in [(22,'papyrus_scripts','lineage-07'),(26,'prolif','lineage-08')]:
 code='import importlib,json,traceback\ntry:\n importlib.import_module('+repr(module)+'); print(json.dumps({"status":"PASS_IMPORT"}))\nexcept Exception as e:\n print(json.dumps({"status":"FAIL_IMPORT","error_type":type(e).__name__,"error_message":str(e),"traceback":traceback.format_exc()}))'
 env={**os.environ,'PYTHONPATH':'/retained-env/'+group+':/retained-env/base'}
 try:
  p=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=60)
  Path('/control/diagnostic-'+str(identity)+'-stdout.log').write_text(p.stdout);Path('/control/diagnostic-'+str(identity)+'-stderr.log').write_text(p.stderr)
  value=json.loads(p.stdout) if p.returncode==0 else {'status':'PROCESS_FAILURE','exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 except Exception as e:value={'status':'CAPTURE_FAILURE','error_type':type(e).__name__,'message':str(e)}
 result['cases'].append({'instance_id':identity,'module':module,'result':value})
Path('/control/diagnosis.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
 resource.setrlimit(resource.RLIMIT_CPU,(1200,1200));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));signal.alarm(1800)
 os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);assert sha(TASK/'release.json')==p['release_sha256']
 worker=base64.b64decode(p['worker_b64']);assert hashlib.sha256(worker).hexdigest()==p['worker_sha256']
 (TASK/'diagnose-worker.py').write_bytes(worker)
 util=base64.b64decode(p['runtime_b64']);assert hashlib.sha256(util).hexdigest()==p['runtime_sha256']
 (TASK/'docker-runtime-v1.py').write_bytes(util)
 spec=importlib.util.spec_from_file_location('owned_runtime',TASK/'docker-runtime-v1.py');runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
 bundle=TASK/'incoming/prior-owned-return.tar.gz';manifest=TASK/'incoming/prior-owned-manifest.json'
 assert sha(bundle)=='4351f5c2675fc5580f163d9a5c19fb4e1dd49ae0f512aedb511ef919c00e8ca3'
 assert sha(manifest)=='c0f5581070a131d83cc30ebee55d7618791b1a498da13fcd1ffd145150cf7eb5'
 expected=json.loads(manifest.read_text());seen={};restored={}
 target=TASK/'retained-env';target.mkdir()
 with tarfile.open(bundle,'r|gz') as tar:
  for member in tar:
   path=PurePosixPath(member.name)
   assert member.isfile() and not path.is_absolute() and '..' not in path.parts and member.name in expected
   want=any(member.name.startswith('env/'+group+'/') for group in ['base','lineage-07','lineage-08'])
   h=hashlib.sha256();dst=None
   if want:
    dest=target.joinpath(*path.parts[1:]);assert dest.resolve().is_relative_to(target)
    dest.parent.mkdir(parents=True,exist_ok=True);dst=dest.open('xb')
   with tar.extractfile(member) as f:
    while block:=f.read(1024**2):
     h.update(block)
     if dst:dst.write(block)
   if dst:dst.close()
   seen[member.name]={'bytes':member.size,'sha256':h.hexdigest()}
   if want:restored[member.name]=seen[member.name]
 assert seen==expected
 runtime.write(TASK/'restoration-v1.json',dict(status='PASS_ALL_PRIOR_MEMBERS_REREAD_SELECTED_ENVS_RESTORED',prior_files=len(seen),restored_files=len(restored),restored_bytes=sum(x['bytes'] for x in restored.values())))
 probes=[]
 for kind,cpu,wall in [('wall',30,3),('cpu',7,30)]:
  result=runtime.run('probe-'+kind,'while True: pass\n',cpu=cpu,wall=wall)
  assert result['state']['ExitCode']==124 and result['resources']['stop_reason']==('WALL_DEADLINE' if kind=='wall' else 'CPU_CAP')
  probes.append(result)
 runtime.write(TASK/'guard-probes-v1.json',dict(status='PASS_ACTUAL_CPU_WALL_TERMINATION',probes=probes))
 result=runtime.run('diagnosis-v1',PROGRAM,cpu=180,wall=200,mounts=[(target,'/retained-env',True)])
 diagnostic=json.loads((TASK/'leases/diagnosis-v1/diagnosis.json').read_text())
 runtime.write(TASK/'diagnosis-receipt-v1.json',dict(container=result,diagnosis=diagnostic))
 print(json.dumps({'status':'DIAGNOSTIC_CAPTURE_COMPLETE_NOT_CORRECTION','container':result,'diagnosis':diagnostic,
  'remote_host_process_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime}))

if __name__=='__main__':main()
