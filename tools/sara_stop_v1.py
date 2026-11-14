"""Record the terminal correction failure and inspect its existing log only."""
import json
from tools.sara_control_v1 import ACCOUNT,PUBLIC,authority,save,write_new
from tools.sara_transport_v1 import invoke

REMOTE=r'''
import json,subprocess
from pathlib import Path
t=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1');p=t/'leases/final-correction-setup-v1'
summary=json.loads((p/'setup-summary.json').read_text());assert summary['status']=='FAIL_SINGLE_INSTALLATION_BATCH'
state=json.loads(subprocess.check_output(['docker','inspect','curaloop-sara-final-correction-setup-v1'],text=True))[0]['State']
assert not state['Running']
print(json.dumps({'summary':summary,'state':state,'failed_operation_log':(p/'extract-libgomp1.log').read_text(errors='replace'),
 'native_case_root_exists':(t/'native-cases').exists(),'import_regression_exists':(t/'leases/offline-import-regression-v1').exists()}))
'''

def main():
 r,l=authority();value=invoke(REMOTE,{},timeout=40);write_new(ACCOUNT/'terminal-correction-inspection-transport-v1.json',value)
 assert value['exit_code']==0
 result=json.loads(value['stdout']);assert result['summary']['operations'][-1]['exit_code']==2
 write_new(PUBLIC/'terminal-technical-stop-v1.json',dict(status='NO_GO_FINAL_CORRECTION_OPERATION_FAILED',
    evidence=result,correction_batches=1,further_corrections=False,native_reference_attempts=0,
    native_scorer_calls=0,agent_calls=0,gpu_allocated_seconds=0,core_bench_migration=False,
    failure_scope='Our preparer failed before offline import regression or native admission; benchmark scientific validity and agent effects remain unmeasured'))
 l['status']='ACTIVE_CLOSEOUT_FAILED_FINAL_CORRECTION';l['terminal_gate']='NO_GO_FINAL_CORRECTION_OPERATION_FAILED';save(l)
 print(json.dumps(result))

if __name__=='__main__':main()
