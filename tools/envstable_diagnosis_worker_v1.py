"""Matched actual-image loader controls; each always writes its observed outcome."""
import base64,hashlib,importlib.util,json,os,resource,shutil,subprocess,sys
from pathlib import Path

EXTRACT=r'''
import json,sys
from pathlib import Path
sys.path.insert(0,'/code')
from envstable_overlay_v1 import extract_deb,file_sha
root=Path('/work/payload');root.mkdir(exist_ok=True)
records=[]
for path in sorted(Path('/packages').glob('*.deb')):records.append(extract_deb(path,root))
Path('/control/extraction.json').write_text(json.dumps(records,indent=2))
'''
LOAD=r'''
import ctypes,json,os,sys,traceback
from pathlib import Path
libc=ctypes.CDLL(None);libc.gnu_get_libc_version.restype=ctypes.c_char_p
libc.getauxval.argtypes=[ctypes.c_ulong];libc.getauxval.restype=ctypes.c_ulong
out=dict(python=sys.version,glibc=libc.gnu_get_libc_version().decode(),at_secure=libc.getauxval(23),ld_library_path=os.environ['LD_LIBRARY_PATH'],loads=[])
for name in ('libgomp.so.1','libXrender.so.1'):
 try:ctypes.CDLL('/work/payload/usr/lib/x86_64-linux-gnu/'+name);out['loads'].append(dict(library=name,pass_=True))
 except Exception as e:out['loads'].append(dict(library=name,pass_=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc()))
out['success']=all(x['pass_'] for x in out['loads']);Path('/control/loader-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''

def main():
 resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1')
 assert not t.exists() and t.parent.resolve()==t.parent and shutil.disk_usage(t.parent).free>4*1024**3
 t.mkdir();(t/'leases').mkdir()
 release=base64.b64decode(p['release_b64']);assert hashlib.sha256(release).hexdigest()==p['release_sha256'];(t/'release.json').write_bytes(release)
 for name in ('code','packages','cases','incoming'):(t/name).mkdir()
 for row in p['files']:
  target=t/row['path'];assert target.parent in (t/'code',t/'packages');content=base64.b64decode(row['bytes_b64']);assert hashlib.sha256(content).hexdigest()==row['sha256'];target.write_bytes(content)
 (t/'diagnosis-worker.py').write_bytes(base64.b64decode(p['worker_b64']))
 spec=importlib.util.spec_from_file_location('rt',t/'code/envstable_runtime_v1.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
 probes={}
 for key,program,cpu,wall in [('wall','import time\ntime.sleep(30)',30,2),('cpu','while True:pass',7,30)]:
  probes[key]=rt.run('guard-'+key+'-v1',program,cpu=cpu,wall=wall,memory=1024**3)
 assert probes['wall']['resources']['stop_reason']=='WALL_DEADLINE' and probes['cpu']['resources']['stop_reason']=='CPU_CAP'
 results={}
 for label in ('A','B','C'):
  case=t/'cases'/label;case.mkdir();case.chmod(0o777)
  if label=='C':
   for path in [case/'payload',case/'payload/usr',case/'payload/usr/lib',case/'payload/usr/lib/x86_64-linux-gnu']:
    path.mkdir(exist_ok=True);path.chmod(0o777)
  mounts=[(t/'code','/code',True),(t/'packages','/packages',True),(case,'/work',False)]
  if label=='B':
   built=rt.run('prepare-b-v1',EXTRACT,cpu=90,wall=150,mounts=mounts);assert built['state']['ExitCode']==0
  program=LOAD if label=='B' else EXTRACT+'\n'+LOAD
  receipt=rt.run('loader-'+label.lower()+'-v1',program,cpu=90,wall=150,mounts=mounts,
   env=['LD_LIBRARY_PATH=/work/payload/usr/lib/x86_64-linux-gnu','LD_DEBUG=libs,files'],memory=2*1024**3)
  result_path=t/'leases'/('loader-'+label.lower()+'-v1')/'loader-result.json'
  results[label]=dict(receipt=receipt,result=json.loads(result_path.read_text()) if result_path.exists() else None)
 out=dict(status='MATCHED_LOADER_CONTROLS_COMPLETED',controls=results,guard_probes=probes,
  mechanism_supported=bool(results['A']['result'] and not results['A']['result']['success'] and results['B']['result'] and results['B']['result']['success'] and results['C']['result'] and results['C']['result']['success']),
  base_image=rt.IMAGE,host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
  native_references=0,actor_calls=0,gpu_allocated_seconds=0)
 (t/'diagnosis-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
if __name__=='__main__':main()
