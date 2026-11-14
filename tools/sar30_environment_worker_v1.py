"""Isolated one-batch source-bounded import qualification; no benchmark execution."""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

TASK=Path.home()/'curaloop-tasks/lr-sar30-qual-20261114-v1'
IMAGE='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d'
NAME='curaloop-sar30-env-20261114-v1'

SUPERVISOR=r'''
import json,os,signal,subprocess,sys,time
from pathlib import Path
p=json.loads(Path('/control/limits.json').read_text())
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
child=subprocess.Popen([sys.executable,'/control/setup.py'],start_new_session=True)
reason=None
while child.poll() is None:
 cpu=int(dict(x.split() for x in Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines())['usage_usec'])/1e6
 rx=int(Path('/sys/class/net/eth0/statistics/rx_bytes').read_text())
 if time.time()>=p['deadline_epoch']:reason='WALL_DEADLINE'
 if cpu>=p['cpu_cap_seconds']-5:reason='CPU_CAP'
 if rx>=p['network_receive_cap_bytes']-1024**2:reason='DOWNLOAD_CAP'
 if reason:
  os.killpg(child.pid,signal.SIGKILL);child.wait();break
 time.sleep(.5)
cpu=int(dict(x.split() for x in Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines())['usage_usec'])/1e6
Path('/control/resources-final.json').write_text(json.dumps({'aggregate_cpu_seconds':cpu,'exit_code':child.returncode,
 'stop_reason':reason,'network_receive_bytes':int(Path('/sys/class/net/eth0/statistics/rx_bytes').read_text()),
 'initial_affinity_core':max(os.sched_getaffinity(0)),'python_version':sys.version}))
sys.exit(124 if reason else child.returncode)
'''

SETUP=r'''
import importlib.metadata,json,os,subprocess,sys,time
from pathlib import Path
plan=json.loads(Path('/control/environment-plan.json').read_text()); result=[]
def save():Path('/control/environment-result.json').write_text(json.dumps(result,indent=2))
for group in plan['groups']:
 target=Path('/env')/group['name'];target.mkdir()
 began=time.time()
 with open('/control/install-'+group['name']+'.log','wb') as log:
  try:
   p=subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','--no-input',
    '--cache-dir=/wheels','--target='+str(target),'--constraint=/control/constraints.txt',
    '--report=/control/pip-'+group['name']+'.json',*group['packages']],stdout=log,stderr=subprocess.STDOUT,timeout=900)
   exit_code=p.returncode
  except subprocess.TimeoutExpired:exit_code=124
 row={'name':group['name'],'ids':group['ids'],'install_exit_code':exit_code,'elapsed_seconds':time.time()-began,'imports':[]}
 if exit_code==0:
  for case in group['cases']:
   code='import importlib,json\nresult=[]\n'
   code+='\nfor name in '+repr(case['imports'])+':\n try: importlib.import_module(name);result.append({"module":name,"pass":True})\n except Exception as e:result.append({"module":name,"pass":False,"error_type":type(e).__name__})\nprint(json.dumps(result))'
   env={**os.environ,'PYTHONPATH':str(target)+':/env/base'}
   try:
    p=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,timeout=90)
    parsed=json.loads(p.stdout) if p.returncode==0 else None
    row['imports'].append({'instance_id':case['instance_id'],'exit_code':p.returncode,'results':parsed})
    Path('/control/import-private-'+str(case['instance_id'])+'.log').write_text(p.stderr)
   except (subprocess.TimeoutExpired,json.JSONDecodeError) as e:
    row['imports'].append({'instance_id':case['instance_id'],'error_type':type(e).__name__})
 row['versions']={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=[str(target)])}
 result.append(row);save()
 if group['name']=='base' and exit_code!=0:
  Path('/control/early-stop.json').write_text(json.dumps({'status':'FAIL_BASE_ENVIRONMENT','optimistic_locked_upper_bound':0,'minimum':24}))
  break
 # Optimistic full coverage counts unprocessed tasks as possible successes.
 invalid=set()
 for old in result:
  if old['install_exit_code']!=0:invalid.update(old['ids'])
  else:
   for case in old['imports']:
    if case.get('exit_code')!=0 or not case.get('results') or not all(x['pass'] for x in case['results']):invalid.add(case['instance_id'])
 locked=set(plan['locked_ids']); upper=len(locked-invalid)
 if upper<24:
  Path('/control/early-stop.json').write_text(json.dumps({'status':'FAIL_ENVIRONMENT_UPPER_BOUND','invalid_locked_ids':sorted(locked&invalid),'optimistic_locked_upper_bound':upper,'minimum':24}))
  break
'''

def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2)

def main():
    p=json.load(sys.stdin)
    assert os.environ.get('USER')=='chaw' and not TASK.exists()
    TASK.mkdir(parents=True);(TASK/'control').mkdir();(TASK/'env').mkdir();(TASK/'wheels').mkdir()
    import base64
    source=base64.b64decode(p['worker_b64'],validate=True)
    assert hashlib.sha256(source).hexdigest()==p['worker_sha256']
    (TASK/'environment-worker.py').write_bytes(source)
    for d in ('control','env','wheels'): (TASK/d).chmod(0o777)
    write(TASK/'release.json',p['release']);write(TASK/'control/environment-plan.json',p['plan'])
    (TASK/'control/constraints.txt').write_text(p['plan']['constraints'])
    (TASK/'control/setup.py').write_text(SETUP);(TASK/'control/supervisor.py').write_text(SUPERVISOR)
    limits=dict(cpu_cap_seconds=8880,deadline_epoch=min(time.time()+10800,p['deadline_epoch']),network_receive_cap_bytes=30*1024**3)
    write(TASK/'control/limits.json',limits)
    command=['docker','create','--name',NAME,'--label','curaloop.task=lr-sar30-qual-20261114-v1',
        '--cpus=1','--memory=8g','--memory-swap=8g','--pids-limit=256','--read-only','--cap-drop=ALL',
        '--security-opt=no-new-privileges','--network=bridge','--tmpfs','/tmp:rw,size=4g',
        '--env','OMP_NUM_THREADS=1','--env','OPENBLAS_NUM_THREADS=1','--env','MKL_NUM_THREADS=1',
        '--env','NUMEXPR_NUM_THREADS=1','--env','MPLBACKEND=Agg','--env','PYTHONDONTWRITEBYTECODE=1',
        '--env','NVIDIA_VISIBLE_DEVICES=void','--env','PIP_ROOT_USER_ACTION=ignore']
    for key in ('control','env','wheels'):command+=['--mount',f'type=bind,source={TASK/key},target=/{key}']
    command += [IMAGE,'python','/control/supervisor.py']
    probes=[]
    for kind in ('wall','cpu'):
        folder=TASK/('probe-'+kind);folder.mkdir();folder.chmod(0o777)
        (folder/'supervisor.py').write_text(SUPERVISOR)
        (folder/'setup.py').write_text('while True: pass\n')
        write(folder/'limits.json',dict(cpu_cap_seconds=30 if kind=='wall' else 8,
            deadline_epoch=time.time()+(3 if kind=='wall' else 30),network_receive_cap_bytes=30*1024**3))
        probe_name=NAME+'-probe-'+kind
        probe=command.copy();probe[probe.index(NAME)]=probe_name
        probe[probe.index(f'type=bind,source={TASK/"control"},target=/control')]=f'type=bind,source={folder},target=/control'
        x=subprocess.run(probe,capture_output=True,text=True,timeout=30);assert x.returncode==0,x.stderr
        subprocess.run(['docker','start',probe_name],check=True,capture_output=True,timeout=20)
        try:wait=subprocess.run(['docker','wait',probe_name],capture_output=True,text=True,timeout=40)
        except subprocess.TimeoutExpired:
            subprocess.run(['docker','kill',probe_name],capture_output=True,timeout=15)
            raise RuntimeError('Guard probe failed to terminate; no setup authorized')
        usage=json.loads((folder/'resources-final.json').read_text())
        assert wait.stdout.strip()=='124' and usage['stop_reason']==('WALL_DEADLINE' if kind=='wall' else 'CPU_CAP')
        probes.append(dict(kind=kind,resources=usage,actual_container_exit=124))
    write(TASK/'control/guard-probes.json',{'status':'PASS_ACTUAL_WALL_AND_CPU_TERMINATION','probes':probes})
    created=subprocess.run(command,capture_output=True,text=True,timeout=30)
    write(TASK/'control/create-receipt.json',{'exit_code':created.returncode,'stdout':created.stdout,'stderr':created.stderr})
    assert created.returncode==0,'Owned container creation failed'
    ins=json.loads(subprocess.check_output(['docker','inspect',NAME],text=True))[0];h=ins['HostConfig']
    assert ins['Image']==IMAGE and h['NanoCpus']==1000000000 and h['Memory']==8*1024**3 and h['MemorySwap']==8*1024**3
    assert not h['DeviceRequests'] and h['ReadonlyRootfs'] and h['NetworkMode']=='bridge'
    write(TASK/'control/container-admission.json',{'id':ins['Id'],'image':ins['Image'],'host_config':h})
    subprocess.run(['docker','start',NAME],check=True,capture_output=True,timeout=20)
    print(json.dumps({'status':'STARTED_GUARDED_ENVIRONMENT_ONLY','root':str(TASK),'name':NAME,'cpu_reserved_seconds':9000,'gpu_allocated_seconds':0}),flush=True)

if __name__=='__main__':main()
