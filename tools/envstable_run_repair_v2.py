"""Continue authorized engineering cycle two without new research qualification."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,reserve,settle,save,write_new
from tools.envstable_transport_v1 import call
if __name__=='__main__':
 r,l=authority('build');assert len(l['attempts']['engineering_cycles'])==1
 first=json.loads((PUBLIC/'profile-build-cycle1.json').read_text());assert all(not x.get('install') or x['install']['result']['status']=='PASS_INSTALL' for x in first['rows'])
 l['attempts']['engineering_cycles'].append(dict(cycle=2,status='DISPATCHED',reason='Audit/complete native ELF dependency closure; preserve successful profile artifacts'));save(l)
 reserve('remote-engineering-cycle2','build',4500,remote=True,scope='Read ELF closure, ordinary missing system libraries, fresh complete profile import workers; no scientific reference')
 result=call(ROOT/'tools/envstable_repair_worker_v2.py',{},ACCOUNT/'cycle2-transport.json',timeout=4000)
 write_new(PUBLIC/'engineering-cycle2.json',result);settle('remote-engineering-cycle2',result['status'],measured_host_process_cpu_seconds=result['host_process_cpu_seconds'],dependency_receive_bytes_cumulative=result['dependency_receive_bytes'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['attempts']['engineering_cycles'][1]['status']=result['status'];l['all_imports_pass']=result['all_imports_pass'];save(l)
 print(json.dumps(dict(status=result['status'],all_imports_pass=result['all_imports_pass'],missing_before=result['missing_before'],profiles=[dict(name=x['name'],status=(x['result'] or {}).get('status')) for x in result['profiles']])))
