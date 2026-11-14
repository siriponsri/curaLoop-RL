"""Read-only dr-train identity, owned-path absence, Docker cache and capacity."""
import base64
import json
import subprocess
from tools.sar30_control_v1 import PUBLIC, authority, write_new

REMOTE = r'''
import json,os,shutil,socket,subprocess
from pathlib import Path
assert os.environ.get('USER')=='chaw'
result={'host':socket.gethostname(),'user':os.environ.get('USER'),'affinity_cpus':len(os.sched_getaffinity(0)),
'free_disk_bytes':shutil.disk_usage(Path.home()).free,
'owned_root_exists':(Path.home()/'curaloop-tasks/lr-sar30-qual-20261114-v1').exists()}
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
result['initial_affinity']=list(os.sched_getaffinity(0))
for label,cmd in [('images',['docker','image','ls','--no-trunc','--format','{{json .}}']),
                  ('docker_version',['docker','version','--format','{{json .Server}}']),
                  ('gpu',['nvidia-smi','--query-gpu=name,uuid,memory.total,memory.used,utilization.gpu','--format=csv,noheader'])]:
 try:
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
  result[label]={'exit_code':p.returncode,'stdout':p.stdout[:25000],'stderr':p.stderr[:1000]}
 except (OSError,subprocess.TimeoutExpired) as e:result[label]={'error_type':type(e).__name__}
print(json.dumps(result))
'''

def main():
    authority()
    command='python3 -c "import base64;exec(base64.b64decode(\''+base64.b64encode(REMOTE.encode()).decode()+'\'))"'
    p=subprocess.run(['rtk','proxy','ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
                      '-o','ConnectTimeout=15','100.77.149.83',command],capture_output=True,text=True,timeout=80)
    result=dict(status='PASS_READ_ONLY_INVENTORY' if p.returncode==0 else 'FAIL_SSH_INVENTORY',exit_code=p.returncode,
                transport_stderr=p.stderr,inventory=json.loads(p.stdout) if p.returncode==0 else p.stdout)
    write_new(PUBLIC/'remote-read-only-inventory-v1.json',result)
    print(json.dumps(result))

if __name__=='__main__':main()
