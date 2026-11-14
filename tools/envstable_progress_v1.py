"""Small read-only owned-job observation; never starts or replays a worker."""
import json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_transport_v1 import invoke
from tools.envstable_control_v1 import ACCOUNT,write_new
REMOTE=r'''
import json,os,resource,subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(15,15));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
t=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1');p=t/'build-progress-v1.json'
rows=json.loads(p.read_text()) if p.exists() else []
states=subprocess.check_output(['docker','ps','-a','--filter','label=curaloop.task=env-stable-lr-20261114-v1','--format','{{.Names}} {{.Status}}'],text=True).splitlines()
live=[]
if (t/'leases').exists():
 for path in (t/'leases').glob('install-*'):
  if not (path/'receipt.json').exists():
   log=path/'pip.log';live.append(dict(name=path.name,log_tail=log.read_text(errors='replace')[-1800:] if log.exists() else 'NOT_YET_EMITTED'))
print(json.dumps(dict(incoming={x.name:x.stat().st_size for x in (t/'incoming').glob('*') if x.is_file()},states=states,
 profiles=[dict(name=x['name'],install=((x.get('install') or {}).get('result') or {}).get('status','REUSED'),imports=((x.get('imports') or {}).get('result') or {}).get('status'),errors=x.get('pip_log_tail')) for x in rows],live=live)))
'''
if __name__=='__main__':
 value=invoke(REMOTE,{},timeout=40);write_new(ACCOUNT/('progress-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.json'),value);assert value['exit_code']==0,value
 print(value['stdout'])
