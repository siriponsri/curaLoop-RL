"""One engineering candidate in the real retained image; no native or model run."""
import base64,hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path

def main():
 resource.setrlimit(resource.RLIMIT_CPU,(180,180));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/lr-sara-lr1-20261114-v1')
 assert t.parent.resolve()==t.parent and not t.exists();assert shutil.disk_usage(t.parent).free>=80*1024**3
 release=base64.b64decode(p['release_b64']);assert hashlib.sha256(release).hexdigest()==p['release_sha256']
 t.mkdir();(t/'release.json').write_bytes(release)
 for name in ('code','packages','overlay'):
  (t/name).mkdir();(t/name).chmod(0o777 if name=='overlay' else 0o755)
 for row in p['files']:
  path=t/row['path'];assert path.parent in (t/'code',t/'packages') and '/' not in path.name
  content=base64.b64decode(row['bytes_b64']);assert hashlib.sha256(content).hexdigest()==row['sha256'];path.write_bytes(content)
 matrix=p['matrix'];(t/'engineering-matrix.json').write_text(json.dumps(matrix,indent=2))
 assert hashlib.sha256((t/'code/saralr1_overlay_v1.py').read_bytes()).hexdigest()==matrix['patch_source_sha256']
 (t/'engineering-worker.py').write_bytes(base64.b64decode(p['worker_b64']))
 spec=importlib.util.spec_from_file_location('runtime',t/'code/saralr1_runtime_v1.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
 # Probe actual stop mechanisms before the acceptance program. These are non-scientific tests.
 wall=rt.run('wall-probe-v1','import time\ntime.sleep(30)',cpu=30,wall=2,memory=1024**3)
 cpu=rt.run('cpu-probe-v1','while True: pass',cpu=7,wall=30,memory=1024**3)
 assert wall['resources']['stop_reason']=='WALL_DEADLINE' and cpu['resources']['stop_reason']=='CPU_CAP'
 program='from pathlib import Path\nPath("/control/matrix.json").write_text('+repr(json.dumps(matrix))+')\n'+(t/'code/saralr1_acceptance_program_v1.py').read_text()
 try:
  receipt=rt.run('engineering-acceptance-v1',program,cpu=180,wall=300,memory=2*1024**3,
   mounts=[(t/'code','/code',True),(t/'packages','/packages',True),(t/'overlay','/overlay',False)],
   env=['LD_LIBRARY_PATH=/overlay/payload/usr/lib/x86_64-linux-gnu:/overlay/payload/lib/x86_64-linux-gnu'])
  path=t/'leases/engineering-acceptance-v1/acceptance-result.json'
  result=json.loads(path.read_text()) if path.exists() else None
  value=dict(status='PASS_ENGINEERING_ACCEPTANCE' if receipt['state']['ExitCode']==0 and result and result['status']=='PASS_FROZEN_ENGINEERING_MATRIX' else 'NO_GO_ENGINEERING_ACCEPTANCE',
   receipt=receipt,result=result,log=(t/'leases/engineering-acceptance-v1/container.log').read_text(errors='replace'),guard_probes=dict(wall=wall,cpu=cpu))
 except BaseException as error:
  value=dict(status='NO_GO_ENGINEERING_WORKER',error_type=type(error).__name__,error=str(error),guard_probes=dict(wall=wall,cpu=cpu))
 value.update(remote_host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
  free_disk_bytes=shutil.disk_usage(t).free,native_references=0,provider_calls=0,gpu_allocated_seconds=0)
 (t/'engineering-outcome.json').write_text(json.dumps(value,indent=2));print(json.dumps(value))
if __name__=='__main__':main()
