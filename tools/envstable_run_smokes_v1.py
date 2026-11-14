"""Substantive workload acceptance, separate from benchmark/reference claims."""
import base64,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,reserve,settle,save,write_new
from tools.envstable_transport_v1 import call
if __name__=='__main__':
 r,l=authority('build');assert l['all_imports_pass'];workload=ROOT/'tools/envstable_workloads_v1.py'
 reserve('remote-substantive-workloads-v1','build',1500,remote=True,scope='Thirteen fresh CPU workloads on explicit engineering fixtures; no native/agent outcomes')
 result=call(ROOT/'tools/envstable_smoke_worker_v1.py',dict(workload_b64=base64.b64encode(workload.read_bytes()).decode(),workload_sha256=digest(workload)),ACCOUNT/'workloads-transport-v1.json',timeout=2600)
 write_new(PUBLIC/'profile-workloads-v1.json',result);settle('remote-substantive-workloads-v1',result['status'],measured_host_process_cpu_seconds=result['host_process_cpu_seconds'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['all_workloads_pass']=result['all_pass'];save(l)
 print(json.dumps(dict(all_pass=result['all_pass'],profiles=[dict(name=x['profile'],result=x['result']) for x in result['profiles']])))
