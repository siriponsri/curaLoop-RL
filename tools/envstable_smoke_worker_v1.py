"""Run substantive profile workloads in fresh read-only environment workers."""
import base64,hashlib,importlib.util,json,os,resource,sys
from pathlib import Path
def main():
 resource.setrlimit(resource.RLIMIT_CPU,(180,180));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1');assert hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
 code=base64.b64decode(p['workload_b64']);assert hashlib.sha256(code).hexdigest()==p['workload_sha256'];(t/'code/envstable_workloads_v1.py').write_bytes(code)
 s=importlib.util.spec_from_file_location('rt',t/'code/envstable_runtime_v1.py');rt=importlib.util.module_from_spec(s);s.loader.exec_module(rt)
 plan=json.loads((t/'build-plan-v1.json').read_text());out=[]
 for group in plan['groups']:
  name=group['name'];home=t/'workload-homes'/name;home.mkdir(parents=True);home.chmod(0o777)
  program='import runpy,sys\nsys.argv=["envstable_workloads_v1.py",'+repr(name)+']\nrunpy.run_path("/code/envstable_workloads_v1.py",run_name="__main__")'
  receipt=rt.run('workload-'+name+'-v1',program,cpu=90,wall=150,
   mounts=[(t/'env','/env',True),(t/'systemlibs-v2','/syslibs',True),(t/'code','/code',True),(home,'/home/worker',False)],
   env=['HOME=/home/worker','PYSTOW_HOME=/home/worker/.data','XDG_CACHE_HOME=/home/worker/.cache','MPLCONFIGDIR=/home/worker/.cache/matplotlib','TF_USE_LEGACY_KERAS=1','TF_CPP_MIN_LOG_LEVEL=2',
    'LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu','PYTHONPATH=/env/'+name+':/env/base'],tmp_disk=True,stage='build')
  path=t/'leases'/('workload-'+name+'-v1')/'workload-result.json';out.append(dict(profile=name,receipt=receipt,result=json.loads(path.read_text()) if path.exists() else None))
  (t/'workload-progress-v1.json').write_text(json.dumps(out,indent=2))
 result=dict(status='PROFILE_WORKLOADS_COMPLETED',profiles=out,all_pass=all(x['result'] and x['result']['status']=='PASS_WORKLOAD' for x in out),
  host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,native_references=0,actor_calls=0)
 (t/'workload-result-v1.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
