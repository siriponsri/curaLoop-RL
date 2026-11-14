"""The single evidence-supported correction batch and offline import regression."""
import base64,hashlib,importlib.util,json,os,resource,shutil,sys,traceback
from pathlib import Path

TASK=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1')
SETUP=r'''
import importlib.metadata,json,os,subprocess,sys,time,traceback
from pathlib import Path
plan=json.loads(Path('/control/plan.json').read_text());results=[]
def write(name,value):Path('/control/'+name).write_text(json.dumps(value,indent=2))
def command(name,args,timeout):
 with open('/control/'+name+'.log','wb') as f:
  p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 results.append({'operation':name,'exit_code':p.returncode});write('setup-summary.json',{'status':'IN_PROGRESS','operations':results})
 if p.returncode:raise RuntimeError(name+' failed; no retry permitted')
try:
 for folder in ['/control/apt/lists/partial','/control/apt/cache','/control/apt/log','/control/apt/state','/control/debs','/workspace-home/.cache/pip']:
  Path(folder).mkdir(parents=True,exist_ok=True)
 opts=['-o','APT::Sandbox::User=root','-o','Debug::NoLocking=true',
       '-o','Dir::State=/control/apt/state','-o','Dir::State::status=/var/lib/dpkg/status','-o','Dir::State::extended_states=/control/apt/extended_states',
       '-o','Dir::State::lists=/control/apt/lists','-o','Dir::Cache=/control/apt/cache',
       '-o','Dir::Cache::archives=/control/debs','-o','Dir::Log=/control/apt/log']
 command('apt-update',['apt-get',*opts,'update'],300)
 command('apt-download-system-libraries',['apt-get',*opts,'-y','--download-only','--no-install-recommends','install',*plan['system_packages']],300)
 debs=[]
 for path in sorted(Path('/control/debs').glob('*.deb')):
  name=subprocess.check_output(['dpkg-deb','-f',str(path),'Package'],text=True).strip()
  if name in {'libc6','libc-bin','base-files'}:raise RuntimeError('Unexpected base ABI package; no overlay')
  command('extract-'+name,['dpkg-deb','-x',str(path),'/syslibs'],60)
  import hashlib
  with path.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
  debs.append({'package':name,'bytes':path.stat().st_size,'sha256':h})
 write('system-library-manifest.json',debs)
 for group in plan['groups']:
  target=Path('/env')/group['name']
  if group.get('reuse'):
   results.append({'operation':'reuse-'+group['name'],'exit_code':0,'install_attempts':0});continue
  target.mkdir()
  command('pip-'+group['name'],[sys.executable,'-m','pip','install','--disable-pip-version-check','--no-input',
    '--cache-dir=/workspace-home/.cache/pip','--target='+str(target),'--constraint=/control/constraints.txt',
    '--report=/control/pip-'+group['name']+'.json',*group['packages']],600)
 versions={g['name']:{d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=['/env/'+g['name']])} for g in plan['groups']}
 write('setup-summary.json',{'status':'PASS_SINGLE_INSTALLATION_BATCH','operations':results,'versions':versions})
except BaseException as e:
 write('setup-summary.json',{'status':'FAIL_SINGLE_INSTALLATION_BATCH','operations':results,'error_type':type(e).__name__,'error_message':str(e),'traceback':traceback.format_exc()})
 raise
'''

IMPORTS=r'''
import json,os,subprocess,sys,traceback
from pathlib import Path
plan=json.loads(Path('/control/plan.json').read_text());results=[]
for group in plan['groups']:
 for case in group['cases']:
  code='import importlib,json,traceback\nr=[]\nfor name in '+repr(case['imports'])+':\n try:importlib.import_module(name);r.append({"module":name,"pass":True})\n except Exception as e:r.append({"module":name,"pass":False,"error_type":type(e).__name__,"error_message":str(e),"traceback":traceback.format_exc()})\nprint(json.dumps(r))'
  env={**os.environ,'PYTHONPATH':'/env/'+group['name']+':/env/base'}
  try:
   p=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=90)
   Path('/control/import-'+str(case['instance_id'])+'-stderr.log').write_text(p.stderr)
   value=json.loads(p.stdout) if p.returncode==0 else None
   row={'instance_id':case['instance_id'],'group':group['name'],'process_exit_code':p.returncode,'results':value,
        'pass':p.returncode==0 and bool(value) and all(x['pass'] for x in value)}
  except BaseException as e:row={'instance_id':case['instance_id'],'group':group['name'],'pass':False,'error_type':type(e).__name__,'error_message':str(e)}
  results.append(row);Path('/control/import-regression.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'cases':len(results),'passed':sum(x['pass'] for x in results)}))
'''

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(1200,1200));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
    os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
    p=json.load(sys.stdin)
    assert hashlib.sha256((TASK/'release.json').read_bytes()).hexdigest()==p['release_sha256']
    source=base64.b64decode(p['worker_b64']);assert hashlib.sha256(source).hexdigest()==p['worker_sha256']
    (TASK/'correction-worker.py').write_bytes(source)
    plan=p['plan'];assert plan['correction_batch_number']==1 and not (TASK/'correction-plan.json').exists()
    (TASK/'correction-plan.json').write_text(json.dumps(plan,indent=2))
    for directory in ['env','syslibs','workspace-home']:(TASK/directory).mkdir();(TASK/directory).chmod(0o777)
    for group in plan['groups']:
        if group.get('reuse'):
            shutil.copytree(TASK/'retained-env'/group['reuse'],TASK/'env'/group['name'],copy_function=os.link)
    spec=importlib.util.spec_from_file_location('owned_runtime',TASK/'docker-runtime-v1.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
    # Limit writable workspace to 64 GiB, leaving 16 GiB for retained inputs and
    # staged authorized assets under the release's 80 GiB peak ceiling.
    rt.SUPERVISOR=rt.SUPERVISOR.replace("while child.poll() is None:","""last_disk_check=0
while child.poll() is None:
 if time.time()-last_disk_check>10:
  last_disk_check=time.time();total=0
  for root in ['/env','/syslibs','/workspace-home','/tmp','/control']:
   for base,dirs,files in os.walk(root):
    for name in files:
     try:total+=os.lstat(os.path.join(base,name)).st_size
     except FileNotFoundError:pass
  if total>=64*1024**3:reason='DISK_CAP'
""")
    setup_id='final-correction-setup-v1'
    expected=TASK/'leases'/setup_id;expected.mkdir();expected.rmdir()
    # The runtime creates the directory; stage its plan through a private program
    # prefix so no concurrent writer or precreated lease can be mistaken for a run.
    setup='from pathlib import Path\nPath("/control/plan.json").write_text('+repr(json.dumps(plan))+')\nPath("/control/constraints.txt").write_text('+repr(plan['constraints'])+')\n'+SETUP
    mounts=[(TASK/'env','/env',False),(TASK/'syslibs','/syslibs',False),(TASK/'workspace-home','/workspace-home',False)]
    env=['HOME=/workspace-home','XDG_CACHE_HOME=/workspace-home/.cache','MPLCONFIGDIR=/workspace-home/.cache/matplotlib',
         'PYSTOW_HOME=/workspace-home/.data','PIP_ROOT_USER_ACTION=ignore','TMPDIR=/tmp',
         'LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu:/syslibs/lib/x86_64-linux-gnu',
         'TF_USE_LEGACY_KERAS=1','TF_CPP_MIN_LOG_LEVEL=2','LOKY_MAX_CPU_COUNT=1']
    try:
        install=rt.run(setup_id,setup,cpu=5400,wall=6600,network=True,mounts=mounts,env=env,network_bytes=20*1024**3,tmp_disk=True)
        summary=json.loads((TASK/'leases'/setup_id/'setup-summary.json').read_text())
        if install['state']['ExitCode']!=0 or summary['status']!='PASS_SINGLE_INSTALLATION_BATCH':
            result={'status':'FAIL_FINAL_CORRECTION_INSTALLATION','install':install,'summary':summary,'further_correction_batches':False}
        else:
            program='from pathlib import Path\nPath("/control/plan.json").write_text('+repr(json.dumps(plan))+')\n'+IMPORTS
            offline_mounts=[(TASK/'env','/env',True),(TASK/'syslibs','/syslibs',True),(TASK/'workspace-home','/workspace-home',False)]
            imports=rt.run('offline-import-regression-v1',program,cpu=600,wall=1500,mounts=offline_mounts,env=env,tmp_disk=True)
            cases=json.loads((TASK/'leases/offline-import-regression-v1/import-regression.json').read_text())
            result={'status':'FINAL_CORRECTION_AND_IMPORTS_COMPLETE','install':install,'summary':summary,'offline_imports':imports,'cases':cases,'further_correction_batches':False}
        result['remote_host_process_cpu_seconds']=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime
        (TASK/'correction-result-v1.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
    except BaseException as e:
        (TASK/'correction-worker-error.json').write_text(json.dumps({'error_type':type(e).__name__,'error_message':str(e),'traceback':traceback.format_exc()}));raise

if __name__=='__main__':main()
