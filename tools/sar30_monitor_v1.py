"""Read-only owned-worker snapshot; never replays dispatch or installation."""
import base64,json,subprocess
from datetime import datetime,timezone
from tools.sar30_control_v1 import ACCOUNT, authority, write_new
REMOTE=r'''
import json,os,resource,subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(10,10));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
t=Path.home()/'curaloop-tasks/lr-sar30-qual-20261114-v1';result={}
for name in ['environment-result.json','early-stop.json','resources-final.json','guard-probes.json']:
 p=t/'control'/name
 if p.exists():result[name]=json.loads(p.read_text())
p=subprocess.run(['docker','inspect','curaloop-sar30-env-20261114-v1','--format','{{json .State}}'],capture_output=True,text=True,timeout=10)
result['state']=json.loads(p.stdout) if p.returncode==0 else {'inspect_exit_code':p.returncode}
logs=sorted((t/'control').glob('install-*.log'),key=lambda p:p.stat().st_mtime)
if logs:
 p=logs[-1];result['latest_install']={'file':p.name,'tail':p.read_text(errors='replace')[-1800:]}
print(json.dumps(result))
'''
def main():
 authority()
 command='python3 -c "import base64;exec(base64.b64decode(\''+base64.b64encode(REMOTE.encode()).decode()+'\'))"'
 p=subprocess.run(['rtk','proxy','ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','100.77.149.83',command],capture_output=True,text=True,timeout=35)
 assert p.returncode==0,p.stderr
 value=json.loads(p.stdout)
 write_new(ACCOUNT/'monitor'/('snapshot-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.json'),value)
 print(json.dumps(value))
if __name__=='__main__':main()
