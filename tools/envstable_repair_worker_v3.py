"""Final bounded engineering cycle: missing declared dependency and fixture repairs."""
import base64,hashlib,importlib.util,json,os,resource,sys
from pathlib import Path

INSTALL=r'''
import hashlib,importlib.metadata as md,json,subprocess,traceback
from pathlib import Path
out={}
try:
 for name in ['pandas-flavor','rdkit','scipy','numpy']:assert md.version(name)
 cache=Path('/control/private-cache');cache.mkdir(mode=0o700)
 args=['python','-m','pip','install','--no-deps','--only-binary=:all:','--cache-dir',str(cache),'--target','/addon','--report','/control/pip-report.json','descriptastorus==2.8.0']
 with Path('/control/install.log').open('wb') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=300)
 assert p.returncode==0
 report=json.loads(Path('/control/pip-report.json').read_text());item=report['install'];assert len(item)==1
 assert item[0]['download_info']['archive_info']['hashes']['sha256']=='cc0c8201d6d9d8534dc8a45ce629aeaf4cf1e62ba848b9b1e392b2600ca834dc'
 out=dict(status='PASS_ADDON',report=report)
except BaseException as e:out=dict(status='FAIL_ADDON',error=str(e),traceback=traceback.format_exc())
finally:Path('/control/addon-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''

def main():
 resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1');assert hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
 code=base64.b64decode(p['workload_b64']);assert hashlib.sha256(code).hexdigest()==p['workload_sha256'];(t/'code/envstable_workloads_v2.py').write_bytes(code)
 s=importlib.util.spec_from_file_location('rt',t/'code/envstable_runtime_v1.py');rt=importlib.util.module_from_spec(s);s.loader.exec_module(rt)
 addon=t/'env/addons-profile12';addon.mkdir();addon.chmod(0o777)
 prior=json.loads((t/'repair-result-v2.json').read_text());remaining=20*1024**3-prior['dependency_receive_bytes'];assert remaining>0
 common=['HOME=/home/worker','PYSTOW_HOME=/home/worker/.data','XDG_CACHE_HOME=/home/worker/.cache','MPLCONFIGDIR=/home/worker/.cache/matplotlib','TF_USE_LEGACY_KERAS=1','TF_CPP_MIN_LOG_LEVEL=2','LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu','LOKY_MAX_CPU_COUNT=1']
 prep=rt.run('addon-builder-v3',INSTALL,cpu=300,wall=450,network=True,network_bytes=remaining,mounts=[(t/'env/profile-12','/profile',True),(t/'env/base','/base',True),(addon,'/addon',False)],env=['PYTHONPATH=/profile:/base'],tmp_disk=True,stage='build')
 prepared=json.loads((t/'leases/addon-builder-v3/addon-result.json').read_text());rows=[]
 if prepared['status']=='PASS_ADDON':
  for group in json.loads((t/'build-plan-v1.json').read_text())['groups']:
   name=group['name'];home=t/'workload-homes-v2'/name;home.mkdir(parents=True);home.chmod(0o777)
   paths=('/env/addons-profile12:' if name=='profile-12' else '')+'/env/'+name+':/env/base'
   program='import runpy,sys\nsys.argv=["envstable_workloads_v2.py",'+repr(name)+']\nrunpy.run_path("/code/envstable_workloads_v2.py",run_name="__main__")'
   receipt=rt.run('workload-'+name+'-v2',program,cpu=90,wall=150,mounts=[(t/'env','/env',True),(t/'systemlibs-v2','/syslibs',True),(t/'code','/code',True),(home,'/home/worker',False)],env=[*common,'PYTHONPATH='+paths],tmp_disk=True,stage='build')
   path=t/'leases'/('workload-'+name+'-v2')/'workload-result.json';rows.append(dict(profile=name,receipt=receipt,result=json.loads(path.read_text()) if path.exists() else None));(t/'cycle3-progress.json').write_text(json.dumps(rows,indent=2))
 result=dict(status='ENGINEERING_CYCLE_3_COMPLETED',addon=prepared,addon_receipt=prep,profiles=rows,all_pass=len(rows)==13 and all(x['result'] and x['result']['status']=='PASS_WORKLOAD' for x in rows),dependency_receive_bytes=prior['dependency_receive_bytes']+prep['resources']['network_receive_bytes'],host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,native_references=0,actor_calls=0)
 (t/'cycle3-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
