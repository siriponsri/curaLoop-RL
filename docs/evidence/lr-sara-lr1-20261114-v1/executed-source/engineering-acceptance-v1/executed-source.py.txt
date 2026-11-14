"""Freeze one attempt identity and dispatch the approved engineering matrix once."""
import base64,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.saralr1_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,reserve,settle,save,stop,write_new
from tools.saralr1_transport_v1 import call
def main():
 r,l=authority('engineering');assert l['attempts']['engineering'] is None
 matrix=json.loads((PUBLIC/'frozen-engineering-matrix-v1.json').read_text());files=[]
 for name in ('saralr1_overlay_v1.py','saralr1_acceptance_program_v1.py','saralr1_runtime_v1.py'):
  path=ROOT/'tools'/name;files.append(dict(path='code/'+name,sha256=digest(path),bytes_b64=base64.b64encode(path.read_bytes()).decode()))
 for row in matrix['debian_packages']:
  path=ACCOUNT/'engineering-input-v1/debs'/row['name'];assert digest(path)==row['sha256'];files.append(dict(path='packages/'+path.name,sha256=digest(path),bytes_b64=base64.b64encode(path.read_bytes()).decode()))
 l['attempts']['engineering']=dict(candidate=1,matrix_runs=1,status='DISPATCH_RESERVED',matrix_sha256=digest(PUBLIC/'frozen-engineering-matrix-v1.json'));save(l)
 reserve('remote-engineering-v1','engineering',600,remote=True,scope='New owned namespace; real wall/CPU probes plus one frozen actual-image engineering matrix; no science')
 result=call(ROOT/'tools/saralr1_engineering_worker_v1.py',dict(matrix=matrix,files=files),ACCOUNT/'engineering-transport-v1.json',timeout=500)
 write_new(PUBLIC/'engineering-acceptance-v1.json',result)
 settle('remote-engineering-v1',result['status'],measured_remote_host_cpu_seconds=result['remote_host_process_cpu_seconds'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['attempts']['engineering']['status']=result['status'];save(l)
 if result['status']!='PASS_ENGINEERING_ACCEPTANCE':stop('NO_GO_ENGINEERING_ACCEPTANCE','The one frozen patch acceptance failed; no repeat or broad patch authorized')
 else:
  l['status']='ACTIVE_PREPARATION';save(l)
 print(json.dumps(dict(status=result['status'],native_references=0,provider_calls=0)))
if __name__=='__main__':main()
