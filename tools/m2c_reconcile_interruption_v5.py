"""Fresh proof before first dispatch of three original, already prepared bookings."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,collect
from tools.m2c_remote_v2 import render_dispatch
from tools.m2c_live_readback_v4 import alive,shared_json,pin_local_reader
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pin_local_reader();assert not (TASK/'durable-pipeline-pid-v5.json').exists()
    parent=shared_json(TASK/'durable-pipeline-pid-v4.json')
    child=shared_json(TASK/'main-resume-v4-orchestration-resource.json')
    assert not alive(parent['pid']) and not alive(child['pid'])
    assert child['status']=='FAIL_ORCHESTRATION_OR_UNIT'
    ledger=shared_json(TASK/'ledger.json')
    assert next(j for j in ledger['jobs'] if j['job']=='orchestration-recovery-v4')['state']=='FAIL'
    active=[j['job'] for j in ledger['jobs'] if j['state']=='RESERVED']
    previous=shared_json(TASK/'local-controller-absence-v4.json')
    assert len(active)==3 and set(active)==set(previous['reserved_not_dispatched_jobs'])
    rows=collect(active)['results']
    assert all(not r['job_exists'] and r['unit_state']['LoadState']=='not-found' and r['unit_state']['ActiveState']=='inactive' for r in rows)
    pins={}
    for name in active:
        path=TASK/'jobs'/name/'remote-command.py'
        source,permit=render_dispatch('worker',name)
        assert path.read_text()==source,'PREPARED_COMMAND_DIFFERS_FROM_FROZEN_PERMIT'
        pins[name]={'permit_sha256':sha(path.parent/'permit.json'),'command_sha256':sha(path)}
    new(TASK/'local-controller-absence-v5.json',{'status':'PASS_FRESH_V5_LOCAL_ABSENCE_AND_NOT_DISPATCHED',
      'utc':datetime.now(timezone.utc).isoformat(),'previous_parent_pid':parent['pid'],'previous_child_pid':child['pid'],
      'reserved_not_dispatched_jobs':active,'fresh_not_dispatched_proofs':rows,'local_prepared_pins':pins,
      'golden_prepared_commands_equal_fresh_rendering':True,'scientific_units_repeated':0,'old_charges_retained':True})
    new(TASK/'pipeline-status-interrupted-v4.json',shared_json(TASK/'pipeline-status.json'))
    path=TASK/'specs/orchestration-recovery-v5.json'
    new(path,{'job':'orchestration-recovery-v5','host':'local','handler':'orchestration_recovery','bucket':'engineering_guards',
      'reservation_seconds':1500,'guard_cpu_seconds':1499.5,'wall_seconds':25000,'memory_bytes':536870912,
      'arguments':{'scope':'first dispatch of three original permits, then unchanged frozen remaining units',
      'main_child_cpu_envelope_seconds':700,'scientific_retries':0}})
    admin_call('reserve',path)
    print(json.dumps({'status':'PASS_V5_PREPARED_COMMAND_RECOVERY_BOOKED','retained_successful_main_ablation':1494,
      'same_bookings_awaiting_first_dispatch':len(active),'new_engineering_envelope_seconds':1500,'final_outcomes_opened':False}))


if __name__=='__main__':main()
