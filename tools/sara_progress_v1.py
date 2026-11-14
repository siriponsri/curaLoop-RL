"""Read only this release's existing job state; never starts or restarts a job."""
import json
from datetime import datetime,timezone
from tools.sara_control_v1 import ACCOUNT,authority,write_new
from tools.sara_transport_v1 import invoke

REMOTE=r'''
import json,os,resource,subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(10,10));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
t=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1')
result={'root_exists':t.exists(),'incoming_files':{p.name:p.stat().st_size for p in (t/'incoming').glob('*') if p.is_file()},'leases':{}}
for folder in sorted((t/'leases').glob('*')):
 item={}
 for name in ['resources-final.json','receipt.json','diagnosis.json','setup-summary.json','qualification.json']:
  p=folder/name
  if p.exists():item[name]=json.loads(p.read_text())
 result['leases'][folder.name]=item
p=subprocess.run(['docker','ps','-a','--filter','label=curaloop.task=lr-sara-20261114-v1','--format','{{.Names}}: {{.Status}}'],capture_output=True,text=True,timeout=15)
result['owned_containers']=p.stdout.splitlines()
print(json.dumps(result))
'''

def main():
 authority();value=invoke(REMOTE,{},timeout=40)
 assert value['exit_code']==0,value['stderr']
 state=json.loads(value['stdout']);write_new(ACCOUNT/'progress'/('snapshot-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.json'),state)
 print(json.dumps(state))

if __name__=='__main__':main()
