"""Retain an interrupted local controller after recovering completed remote units."""
import json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2'


def main():
    rows=json.loads((TASK/'owner-status-remote-readback-20261109.json').read_text())['results']
    assert len(rows)==3 and all(r['resource']['status']=='PASS' and r['unit_state']['ActiveState']=='inactive' for r in rows)
    ledger=json.loads((TASK/'ledger.json').read_text());active=[j for j in ledger['jobs'] if j['state']=='RESERVED']
    assert len(active)==1 and active[0]['job']=='orchestration-recovery-v2'
    # The owner-status check independently observed no matching local processes.
    new(TASK/'local-controller-absence-v3.json',{'status':'PASS_FRESH_NO_LOCAL_M2_CONTROLLER',
      'processes':[],'observed_by':'status-processes-20261109.ps1 / Get-CimInstance exact Python controller filter',
      'utc':datetime.now(timezone.utc).isoformat(),'remote_completed_jobs':[r['job'] for r in rows]})
    previous=json.loads((TASK/'recovery-pipeline-resource-v2.json').read_text())
    new(TASK/'jobs/orchestration-recovery-v2/resource.json',{'schema':'curaloop.m2_costed.resources.v2',
      'attempt':'orchestration-recovery-v2','host':'local','status':'FAIL','cpu_seconds':previous['aggregate_cpu_seconds'],
      'reservation_seconds':2000,'cpu_measurement_scope':'INITIAL_COUNTER_LOWER_BOUND_ONLY; final counter unavailable after process exit; full 2000-second reservation retained',
      'failure':'CONTROLLER_ABSENT_WITH_UNCLOSED_INITIAL_RUNNING_RECEIPT','remote_worker_failures':0})
    admin_call('settle','orchestration-recovery-v2')
    new(TASK/'pipeline-status-interrupted-v2.json',json.loads((TASK/'pipeline-status.json').read_text()))
    path=TASK/'specs/orchestration-recovery-v3.json'
    new(path,{'job':'orchestration-recovery-v3','host':'local','handler':'orchestration_recovery','bucket':'engineering_guards',
      'reservation_seconds':2000,'guard_cpu_seconds':1999.5,'wall_seconds':25000,'memory_bytes':536870912,
      'arguments':{'scope':'resume only frozen remaining main/ablation/transfer units; retain all completed outcomes'}})
    admin_call('reserve',path)
    print(json.dumps({'status':'PASS_COMPLETED_REMOTE_UNITS_RECONCILED','retained_main_and_ablation':210,'new_orchestration_envelope_seconds':2000,
      'final_outcomes_opened':False}))


if __name__=='__main__':main()
