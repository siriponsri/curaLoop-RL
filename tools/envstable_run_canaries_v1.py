import base64,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,reserve,settle,save,write_new
from tools.envstable_transport_v1 import call
if __name__=='__main__':
 r,l=authority('validation');assert l['cold_reconstruction_pass'];assert not l['attempts']['canaries']
 plan=ACCOUNT/'canary-protocol-private-v1.json';assert plan.is_file()
 # Persist one-attempt slots before transfer; an uncertain dispatch is inspected, never replayed.
 l['attempts']['canaries']={str(i):dict(status='PREPARED',max_reference_attempts=1) for i in [12,13,71,72]};save(l)
 reserve('remote-native-canaries-v1','validation',9900,remote=True,scope='Four unchanged development reference attempts and isolated native grading, CPU only')
 p=subprocess.run(['rtk','proxy','scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',str(ACCOUNT/'development-assets-v1.tar'),'100.77.149.83:/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1/incoming/development-assets-v1.tar'],capture_output=True,text=True,timeout=1800)
 write_new(ACCOUNT/'development-assets-transfer.json',dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0
 result=call(ROOT/'tools/envstable_canary_worker_v1.py',dict(protocol_b64=base64.b64encode(plan.read_bytes()).decode()),ACCOUNT/'canaries-transport-v1.json',timeout=10800)
 write_new(PUBLIC/'native-development-canaries-v1.json',result);settle('remote-native-canaries-v1',result['status'],measured_host_process_cpu_seconds=result['host_process_cpu_seconds'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['native_canaries_pass']=result['all_pass'];l['attempts']['canaries']={str(x['case_id']):dict(status=x['status'],reference_attempts=1,score=x['score']) for x in result['cases']};l['status']='ACTIVE_CLOSEOUT_READY' if result['all_pass'] else 'ACTIVE_CLOSEOUT_NATIVE_FAILED';save(l)
 print(json.dumps(dict(all_pass=result['all_pass'],cases=[dict(case_id=x['case_id'],status=x['status'],score=x['score'],reference_exit=x['reference']['state']['ExitCode']) for x in result['cases']])))
