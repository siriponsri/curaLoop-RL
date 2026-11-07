"""One strict, noninteractive SSH admission. Remote code reads metadata only."""
import base64
import json
import shlex
import subprocess
from r0dq_core_v1 import ROOT,PRIVATE,REMOTE,HOST,SSH_OPTIONS,save,archive_code
from r0dq_transport_guard_v1 import TransportGuard

SCRIPT=r'''
import os,sys,json,shutil,signal,resource,time,platform,subprocess,importlib.util
from pathlib import Path
os.nice(19)
allowed=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{allowed[-1]})
resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
resource.setrlimit(resource.RLIMIT_CPU,(5,6));signal.alarm(25)
home=Path.home();root=home/'curaloop-runs/chembl-taskfirst-dq-20261107-v1'
memory={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.split(':')[0] in ['MemTotal','MemAvailable']}
def sample():
    return {line.split()[0]:list(map(int,line.split()[1:])) for line in Path('/proc/stat').read_text().splitlines() if line.startswith('cpu') and line.split()[0]!='cpu'}
a=sample();time.sleep(.2);b=sample();loads={}
for cpu,values in b.items():
    delta=[x-y for x,y in zip(values,a[cpu])];total=sum(delta)
    loads[int(cpu[3:])]=round(1-(delta[3]+delta[4])/total,4) if total else 0
manager=subprocess.run(['systemctl','--user','is-system-running'],capture_output=True,text=True,timeout=5)
processes=subprocess.run(['ps','-u',str(os.getuid()),'-o','pid,psr,pcpu,pmem,comm','--no-headers'],capture_output=True,text=True,timeout=5)
result={'hostname':platform.node(),'uid':os.getuid(),'home':str(home),'python':sys.version,
        'disk_free_bytes':shutil.disk_usage(home).free,'memory':memory,'allowed_cpus':allowed,
        'least_busy_cpu':min((cpu for cpu in allowed),key=lambda cpu:loads.get(cpu,1)),
        'cpu_load_sample':loads,'systemd_user_state':manager.stdout.strip(),'systemd_user_returncode':manager.returncode,
        'tools':{name:shutil.which(name) for name in ['python3','systemd-run','systemctl','tar','gzip','zstd']},
        'modules':{name:bool(importlib.util.find_spec(name)) for name in ['rdkit','psutil','pymupdf','fitz']},
        'owned_root_exists':root.exists(),'user_process_metadata':processes.stdout,
        'configuration_changed':False,'scientific_data_read':False}
print(json.dumps(result))
'''


def main():
    payload=base64.b64encode(SCRIPT.encode()).decode()
    command='python3 -c '+shlex.quote('import base64;exec(base64.b64decode('+repr(payload)+'))')
    result=subprocess.run(['ssh',*SSH_OPTIONS,HOST,command],capture_output=True,timeout=35)
    if result.returncode:
        save(PRIVATE/'ssh-admission-v1.json',{'status':'FAIL_CONNECTION_OR_METADATA','exit_code':result.returncode,
            'stderr':result.stderr.decode(errors='replace')[:1500],'automatic_retry':False})
        raise RuntimeError('Strict SSH admission failed; see retained error')
    data=json.loads(result.stdout.decode())
    data['status']='PASS_READ_ONLY_HOST_METADATA'
    data['storage_pass']=data['disk_free_bytes']>=80*1024**3
    data['memory_pass']=data['memory'].get('MemAvailable',0)>=5*1024**3
    data['new_root_pass']=not data['owned_root_exists']
    data['manager_pass']=data['systemd_user_state'] in ['running','degraded']
    save(PRIVATE/'ssh-admission-v1.json',data)
    archive_code(ROOT/'tools/r0dq_transport_guard_v1.py')
    print(json.dumps({k:data[k] for k in ['status','hostname','storage_pass','memory_pass','new_root_pass','manager_pass','least_busy_cpu','modules','disk_free_bytes']}))
    assert all(data[k] for k in ['storage_pass','memory_pass','new_root_pass','manager_pass'])


if __name__=='__main__':
    guard=TransportGuard('ssh-admission-v1',cpu_seconds=60,wall=50,memory_mib=256)
    try:main()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
