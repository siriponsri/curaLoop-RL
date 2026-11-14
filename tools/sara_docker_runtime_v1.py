"""Owned CPU-limited containers with real cgroup/wall watchdogs and receipts."""
import json,os,subprocess,time
from datetime import datetime
from pathlib import Path

TASK=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1')
IMAGE='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d'
SUPERVISOR=r'''
import json,os,signal,subprocess,sys,time
from pathlib import Path
limits=json.loads(Path('/control/limits.json').read_text());os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
child=subprocess.Popen([sys.executable,'/control/program.py'],start_new_session=True)
reason=None
def cpu():return int(dict(x.split() for x in Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines())['usage_usec'])/1e6
def rx():
 p=Path('/sys/class/net/eth0/statistics/rx_bytes');return int(p.read_text()) if p.exists() else 0
while child.poll() is None:
 if time.time()>=limits['deadline_epoch']:reason='WALL_DEADLINE'
 if cpu()>=limits['cpu_cap_seconds']-3:reason='CPU_CAP'
 if limits['network_receive_cap_bytes'] and rx()>=limits['network_receive_cap_bytes']-1024**2:reason='DOWNLOAD_CAP'
 if reason:
  os.killpg(child.pid,signal.SIGKILL);child.wait();break
 time.sleep(.25)
Path('/control/resources-final.json').write_text(json.dumps({'aggregate_cpu_seconds':cpu(),'exit_code':child.returncode,'stop_reason':reason,
 'network_receive_bytes':rx(),'python_version':sys.version,'initial_affinity_core':max(os.sched_getaffinity(0))}))
sys.exit(124 if reason else child.returncode)
'''

def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,indent=2)

def run(identity,program,*,cpu=180,wall=240,network=False,mounts=(),env=(),memory=8*1024**3,network_bytes=0,tmp_disk=False):
    assert identity.replace('-','').isalnum() and TASK.resolve()==TASK
    release=json.loads((TASK/'release.json').read_text());deadline=datetime.fromisoformat(release['technical_deadline_utc']).timestamp()
    assert time.time()<deadline
    control=TASK/'leases'/identity;control.mkdir(exist_ok=False);control.chmod(0o777)
    (control/'supervisor.py').write_text(SUPERVISOR);(control/'program.py').write_text(program)
    write(control/'limits.json',dict(cpu_cap_seconds=cpu,deadline_epoch=min(time.time()+wall,deadline),network_receive_cap_bytes=network_bytes))
    name='curaloop-sara-'+identity
    command=['docker','create','--name',name,'--label','curaloop.task=lr-sara-20261114-v1','--cpus=1',
      '--memory='+str(memory),'--memory-swap='+str(memory),'--pids-limit=256','--read-only','--cap-drop=ALL',
      '--security-opt=no-new-privileges','--network='+('bridge' if network else 'none'),
      '--mount',f'type=bind,source={control},target=/control']
    if tmp_disk:
        tmp=control/'temporary';tmp.mkdir();tmp.chmod(0o777);command+=['--mount',f'type=bind,source={tmp},target=/tmp']
    else:command+=['--tmpfs','/tmp:rw,size=4g']
    for source,target,readonly in mounts:
        source=Path(source);assert source.resolve().is_relative_to(TASK)
        command+=['--mount',f'type=bind,source={source},target={target}'+(',readonly' if readonly else '')]
    for value in ['OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','NUMEXPR_NUM_THREADS=1','MPLBACKEND=Agg','PYTHONDONTWRITEBYTECODE=1','NVIDIA_VISIBLE_DEVICES=void',*env]:
        command+=['--env',value]
    command += [IMAGE,'python','/control/supervisor.py']
    p=subprocess.run(command,capture_output=True,text=True,timeout=30)
    write(control/'create.json',dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
    ins=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0];h=ins['HostConfig']
    assert ins['Image']==IMAGE and h['NanoCpus']==1000000000 and h['Memory']==h['MemorySwap']==memory
    assert not h['DeviceRequests'] and h['ReadonlyRootfs'] and not h['Privileged']
    write(control/'container-admission.json',dict(id=ins['Id'],image=ins['Image'],host_config=h))
    subprocess.run(['docker','start',name],check=True,capture_output=True,timeout=15)
    try:p=subprocess.run(['docker','wait',name],capture_output=True,text=True,timeout=wall+30)
    except subprocess.TimeoutExpired:
        subprocess.run(['docker','kill',name],capture_output=True,timeout=15)
        raise RuntimeError('Watchdog failed; no automatic repeated attempt')
    (control/'container.log').write_bytes(subprocess.check_output(['docker','logs',name],stderr=subprocess.STDOUT,timeout=20))
    state=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]['State'];assert not state['Running']
    result=dict(container_name=name,state=state,resources=json.loads((control/'resources-final.json').read_text()))
    write(control/'receipt.json',result);return result
