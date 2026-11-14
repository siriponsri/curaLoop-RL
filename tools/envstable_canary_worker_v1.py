"""One immutable native attempt per exposed development canary, isolated grading."""
import base64,hashlib,importlib.util,json,os,resource,sys,tarfile
from pathlib import Path,PurePosixPath
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024**2):h.update(b)
 return h.hexdigest()
def main():
 resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1');assert sha(t/'release.json')==p['release_sha256']
 plan=json.loads(base64.b64decode(p['protocol_b64']));assert [x['instance_id'] for x in plan['cases']]==[12,13,71,72]
 (t/'canary-protocol-private-v1.json').write_text(json.dumps(plan,indent=2));assert json.loads((t/'lock-result.json').read_text())['all_pass']
 tarpath=t/'incoming/development-assets-v1.tar';assert sha(tarpath)==plan['asset_bundle_sha256'];assets=t/'development-assets';assets.mkdir();seen=set()
 with tarfile.open(tarpath,'r|') as tar:
  for item in tar:
   n=item.name;assert n in plan['members'] and n not in seen and item.isfile() and '..' not in PurePosixPath(n).parts and not PurePosixPath(n).is_absolute()
   out=assets/n;out.parent.mkdir(parents=True,exist_ok=True)
   with tar.extractfile(item) as f,out.open('xb') as w:
    while b:=f.read(1024**2):w.write(b)
   assert sha(out)==plan['members'][n]['sha256'];seen.add(n)
 assert seen==set(plan['members'])
 s=importlib.util.spec_from_file_location('rt',t/'code/envstable_runtime_v1.py');rt=importlib.util.module_from_spec(s);s.loader.exec_module(rt);rows=[]
 for case in plan['cases']:
  i=case['instance_id'];name=case['profile'];work=t/'canaries'/str(i)/'reference';work.mkdir(parents=True);work.chmod(0o777);(work/'pred_results').mkdir();(work/'pred_results').chmod(0o777)
  home=t/'canaries'/str(i)/'home';home.mkdir();home.chmod(0o777)
  env=['HOME=/home/worker','PYSTOW_HOME=/home/worker/.data','XDG_CACHE_HOME=/home/worker/.cache','MPLCONFIGDIR=/home/worker/.cache/matplotlib','LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu','PYTHONPATH='+('/env/addons-profile12:' if name=='profile-12' else '')+'/env/'+name+':/env/base','TF_USE_LEGACY_KERAS=1','LOKY_MAX_CPU_COUNT=1','PYTHONUNBUFFERED=1']
  shared=[(t/'reconstructed/env','/env',True),(t/'reconstructed/systemlibs','/syslibs',True),(home,'/home/worker',False)]
  start=dict(case_id=i,status='REFERENCE_DISPATCHED',reference_attempt=1,reference_sha256=sha(assets/case['gold_program']),evaluator_sha256=sha(assets/case['eval_program']))
  (t/('canary-attempt-'+str(i)+'.json')).write_text(json.dumps(start,indent=2))
  program='import os,runpy\nos.chdir("/work")\nrunpy.run_path("/reference.py",run_name="__main__")'
  ref=rt.run('native-dev'+str(i)+'-v1',program,cpu=plan['reference_cpu_seconds'],wall=plan['reference_wall_seconds'],mounts=[*shared,(work,'/work',False),(assets/'benchmark/datasets','/work/benchmark/datasets',True),(assets/case['gold_program'],'/reference.py',True)],env=env,tmp_disk=True,stage='validation')
  row=dict(start,reference=ref,output_exists=(work/case['output']).is_file(),grader=None,score=None,status='FAIL_REFERENCE_RUNTIME')
  if ref['state']['ExitCode']==0 and row['output_exists']:
   grade=t/'canaries'/str(i)/'grader';grade.mkdir();grade.chmod(0o777)
   program='''import json,os,runpy,traceback
from pathlib import Path
os.chdir('/work');out={}
try:
 d=runpy.run_path('/evaluator.py',run_name='native_grader');v=d['eval']();assert isinstance(v,tuple) and len(v)==2 and type(v[0]) is int and v[0] in [0,1]
 out=dict(status='PASS_GRADER_EXECUTION',score=v[0],detail=str(v[1]),raw_result=list(v))
except BaseException as e:out=dict(status='FAIL_GRADER_RUNTIME',error=str(e),traceback=traceback.format_exc())
finally:Path('/control/grader-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''
   mounts=[*shared,(grade,'/work',False),(work/'pred_results','/work/pred_results',True),(assets/'benchmark/datasets','/work/benchmark/datasets',True),(assets/case['eval_program'],'/evaluator.py',True)]
   gold=assets/'benchmark/eval_programs/gold_results'
   if case['gold_members']:mounts.append((gold,'/work/benchmark/eval_programs/gold_results',True))
   g=rt.run('grade-dev'+str(i)+'-v1',program,cpu=90,wall=150,mounts=mounts,env=env,tmp_disk=True,stage='validation');f=t/'leases'/('grade-dev'+str(i)+'-v1')/'grader-result.json'
   gr=json.loads(f.read_text()) if f.exists() else None;row.update(grader=dict(receipt=g,result=gr),score=gr.get('score') if gr else None,status='PASS_NATIVE_CANARY' if gr and gr.get('score')==1 else 'FAIL_NATIVE_PREDICATE_OR_GRADER')
  rows.append(row);(t/'canary-progress.json').write_text(json.dumps(rows,indent=2))
 result=dict(status='FOUR_NATIVE_DEVELOPMENT_ATTEMPTS_COMPLETED',cases=rows,all_pass=len(rows)==4 and all(x['status']=='PASS_NATIVE_CANARY' for x in rows),host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,actor_calls=0,locked_references=0,allocated_gpu_seconds=0)
 (t/'canary-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
