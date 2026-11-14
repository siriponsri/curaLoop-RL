"""Existing noninteractive SSH profile; no config/key changes or blind replay."""
import base64,json,subprocess
from tools.envstable_control_v1 import RELEASE,digest,write_new
def invoke(source,payload,timeout=180):
 if isinstance(source,str):source=source.encode()
 cmd='python3 -c "import base64;exec(base64.b64decode(\''+base64.b64encode(source).decode()+'\'))"'
 p=subprocess.run(['rtk','proxy','ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','100.77.149.83',cmd],input=json.dumps(payload),capture_output=True,text=True,timeout=timeout)
 return dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)
def call(worker,payload,receipt,timeout=180):
 source=worker.read_bytes();value=invoke(source,dict(payload,release_b64=base64.b64encode(RELEASE.read_bytes()).decode(),release_sha256=digest(RELEASE),worker_b64=base64.b64encode(source).decode(),worker_sha256=digest(worker)),timeout)
 write_new(receipt,value);assert value['exit_code']==0,'Inspect exact owned attempt; never replay blindly';return json.loads(value['stdout'])
