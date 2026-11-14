"""Inspect the existing failed-to-start owned guard; never starts it."""
import json
from tools.sara_control_v1 import ACCOUNT,authority,write_new
from tools.sara_transport_v1 import invoke

REMOTE=r'''
import json,subprocess
from pathlib import Path
t=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1');result={}
for name in ['curaloop-sara-probe-wall']:
 p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=15)
 if p.returncode==0:
  v=json.loads(p.stdout)[0];assert v['Config']['Labels']['curaloop.task']=='lr-sara-20261114-v1'
  result[name]={'state':v['State'],'host_config':v['HostConfig'],'path':v['Path'],'args':v['Args']}
 else:result[name]={'exit_code':p.returncode,'stderr':p.stderr}
result['restoration_receipt']=json.loads((t/'restoration-v1.json').read_text())
result['diagnosis_program_exists']=(t/'leases/diagnosis-v1/program.py').exists()
print(json.dumps(result))
'''

def main():
 authority('technical');v=invoke(REMOTE,{},timeout=35);write_new(ACCOUNT/'guard-start-inspection-transport-v1.json',v)
 assert v['exit_code']==0
 result=json.loads(v['stdout']);write_new(ACCOUNT/'guard-start-inspection-v1.json',result);print(json.dumps(result))

if __name__=='__main__':main()
