"""Recover a provably undispatched preparation error; retain original bookings."""
import base64,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,settle,save,write_new
from tools.envstable_transport_v1 import call
if __name__=='__main__':
 r,l=authority('build');assert len(l['attempts']['engineering_cycles'])==3
 assert 'remote-engineering-cycle3' in l['active_jobs'] and not (ACCOUNT/'cycle3-transport.json').exists()
 assert json.loads((ACCOUNT/'jobs/engineering-cycle3-v1/resources.json').read_text())
 write_new(PUBLIC/'cycle3-preflight-recovery.json',dict(status='RECOVERED_BEFORE_REMOTE_DISPATCH',cause='PowerShell quoting failed creating workload source; controller did not preflight source before reserving',remote_dispatches_before_recovery=0,retained_local_booking_seconds=300,remote_booking_reused_seconds=2400,scientific_attempts=0))
 w=ROOT/'tools/envstable_workloads_v2.py';assert w.exists()
 result=call(ROOT/'tools/envstable_repair_worker_v3.py',dict(workload_b64=base64.b64encode(w.read_bytes()).decode(),workload_sha256=digest(w)),ACCOUNT/'cycle3-transport.json',timeout=3000)
 write_new(PUBLIC/'engineering-cycle3.json',result);settle('remote-engineering-cycle3',result['status'],measured_host_process_cpu_seconds=result['host_process_cpu_seconds'],dependency_receive_bytes_cumulative=result['dependency_receive_bytes'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['attempts']['engineering_cycles'][2]['status']=result['status'];l['all_workloads_pass']=result['all_pass'];l['status']='ACTIVE_VALIDATION' if result['all_pass'] else 'ACTIVE_BUILD';save(l)
 print(json.dumps(dict(status=result['status'],all_pass=result['all_pass'],profiles=[dict(name=x['profile'],result=x['result']) for x in result['profiles']])))
