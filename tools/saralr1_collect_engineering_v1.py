"""Read existing completed matrix artifacts after a result-serialization error."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.saralr1_control_v1 import ACCOUNT,PUBLIC,authority,save,settle,stop,write_new
from tools.saralr1_transport_v1 import invoke
REMOTE=r'''
import json,subprocess
from pathlib import Path
t=Path('/home/chaw/curaloop-tasks/lr-sara-lr1-20261114-v1');d=t/'leases/engineering-acceptance-v1'
receipt=json.loads((d/'receipt.json').read_text());assert not receipt['state']['Running']
ids=subprocess.check_output(['docker','ps','-q','--filter','label=curaloop.task=lr-sara-lr1-20261114-v1'],text=True).split();assert not ids
path=d/'acceptance-result.json';result=json.loads(path.read_text()) if path.exists() else None
proof=json.loads((t/'first-start-proof.json').read_text())
status='PASS_ENGINEERING_ACCEPTANCE' if receipt['state']['ExitCode']==0 and result and result['status']=='PASS_FROZEN_ENGINEERING_MATRIX' else 'NO_GO_ENGINEERING_ACCEPTANCE'
print(json.dumps(dict(status=status,receipt=receipt,result=result,log=(d/'container.log').read_text(errors='replace'),first_start_proof=proof,
 guard_probes={k:json.loads((t/'leases'/v/'receipt.json').read_text()) for k,v in [('wall','wall-probe-v1'),('cpu','cpu-probe-v1')]},
 native_references=0,provider_calls=0,gpu_allocated_seconds=0,collection_only=True)))
'''
def main():
 r,l=authority('engineering');value=invoke(REMOTE,{},timeout=45);write_new(ACCOUNT/'collect-engineering-transport-v1.json',value);assert value['exit_code']==0,value
 result=json.loads(value['stdout']);write_new(PUBLIC/'engineering-acceptance-v1.json',result)
 incidents=dict(status='RETAINED_BOOTSTRAP_AND_RESULT_COLLECTION_ERRORS',actual_matrix_executions=1,patch_and_matrix_changed=False,
  before_first_start=json.loads((ACCOUNT/'engineering-transport-v1.json').read_text()),
  after_completed_matrix=json.loads((ACCOUNT/'first-matrix-start-transport-v1.json').read_text()),
  interpretation='Lease parent was missing before any container existed. First actual execution completed; wrapper then lacked shutil for disk-report serialization. Existing artifacts were read without replay.')
 write_new(PUBLIC/'engineering-administration-incidents-v1.json',incidents)
 settle('remote-engineering-v1',result['status'],remote_host_cpu_seconds='NOT_ESTABLISHED',measured_acceptance_container_cpu_seconds=result['receipt']['resources']['aggregate_cpu_seconds'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['attempts']['engineering'].update(status=result['status'],actual_matrix_executions=1,administration_failures_retained=True);save(l)
 if result['status']!='PASS_ENGINEERING_ACCEPTANCE':stop('NO_GO_ENGINEERING_ACCEPTANCE','The first and sole frozen acceptance failed; no patch change or second matrix')
 else:l['status']='ACTIVE_PREPARATION';save(l)
 print(json.dumps(dict(status=result['status'],tests=len((result.get('result') or {}).get('tests',[])),log=result['log'][-2400:])))
if __name__=='__main__':main()
