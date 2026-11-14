import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,reserve,settle,save,write_new
from tools.envstable_transport_v1 import call
if __name__=='__main__':
 r,l=authority('validation');assert l['all_workloads_pass']
 reserve('remote-offline-lock-cold-v1','validation',2100,remote=True,scope='Content lock, complete offline copied artifact with file reread, two cold worker sets')
 result=call(ROOT/'tools/envstable_lock_worker_v1.py',{},ACCOUNT/'lock-transport-v1.json',timeout=4500)
 write_new(PUBLIC/'offline-reconstruction-cold-starts-v1.json',result);settle('remote-offline-lock-cold-v1',result['status'],measured_host_process_cpu_seconds=result['host_process_cpu_seconds'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['cold_reconstruction_pass']=result['all_pass'];save(l);print(json.dumps(dict(all_pass=result['all_pass'],reconstruction=result['reconstruction'],cold=[dict(cold=x['cold'],profile=x['profile'],result=x['result']) for x in result['cold_starts']])))
