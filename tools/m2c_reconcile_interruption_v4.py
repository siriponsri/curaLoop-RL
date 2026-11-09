"""Recover only after the recorded v3 controller exhausted its local utility guard."""
import json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,collect,save_collected
from tools.m2c_live_readback_v4 import alive,shared_json,pin_local_reader
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2'


def main():
    pin_local_reader()
    assert not (TASK/'durable-pipeline-pid-v4.json').exists()
    old=shared_json(TASK/'durable-pipeline-pid-v3.json')
    child=shared_json(TASK/'main-resume-v3-orchestration-resource.json')
    assert not alive(old['pid']) and not alive(child['pid']),'PREVIOUS_CONTROLLER_STILL_ALIVE'
    assert child['status']=='FAIL_ORCHESTRATION_RESOURCE_LIMIT' and child['aggregate_cpu_seconds']>=499
    ledger=shared_json(TASK/'ledger.json')
    parent=next(j for j in ledger['jobs'] if j['job']=='orchestration-recovery-v3')
    assert parent['state']=='FAIL','PREVIOUS_CONTROLLER_NOT_SETTLED'
    active=[j['job'] for j in ledger['jobs'] if j['state']=='RESERVED']
    assert len(active)<=3 and all(n.startswith(('main-','ablation-')) for n in active)
    rows=collect(active)['results'] if active else []
    successful=[r for r in rows if r.get('resource',{}).get('status')=='PASS' and r.get('result',{}).get('status')=='PASS_CAMPAIGN'
      and r['unit_state']['ActiveState']=='inactive']
    undispatched=[r for r in rows if not r['job_exists'] and r['unit_state']['LoadState']=='not-found'
      and r['unit_state']['ActiveState']=='inactive']
    if len(successful)+len(undispatched)!=len(rows):
        print(json.dumps({'status':'WAIT_OR_INSPECT_REMOTE_UNITS','jobs':[
          {'job':r['job'],'resource_status':r.get('resource',{}).get('status'),'unit':r['unit_state']} for r in rows]}));return
    for row in successful:
        save_collected(row);admin_call('settle',row['job'])
    new(TASK/'local-controller-absence-v4.json',{'status':'PASS_FRESH_NO_RECORDED_V3_CONTROLLERS',
      'utc':datetime.now(timezone.utc).isoformat(),'parent_pid':old['pid'],'child_pid':child['pid'],
      'absence_check':'Windows OpenProcess ERROR_INVALID_PARAMETER; access errors are not absence',
      'recovered_successful_remote_jobs':[r['job'] for r in successful],
      'reserved_not_dispatched_jobs':[r['job'] for r in undispatched],
      'fresh_not_dispatched_proofs':undispatched,
      'old_controller_and_scientific_reservations_retained':True})
    new(TASK/'pipeline-status-interrupted-v3.json',shared_json(TASK/'pipeline-status.json'))
    path=TASK/'specs/orchestration-recovery-v4.json'
    new(path,{'job':'orchestration-recovery-v4','host':'local','handler':'orchestration_recovery','bucket':'engineering_guards',
      'reservation_seconds':2000,'guard_cpu_seconds':1999.5,'wall_seconds':25000,'memory_bytes':536870912,
      'arguments':{'scope':'metadata-only controller continuation of the unchanged frozen main/ablation/transfer matrix',
      'main_child_cpu_envelope_seconds':1000,'scientific_retries':0}})
    admin_call('reserve',path)
    print(json.dumps({'status':'PASS_V3_LOCAL_LIMIT_RECOVERY_BOOKED','recovered_remote_successes':len(successful),
      'retained_bookings_awaiting_first_dispatch':len(undispatched),
      'new_orchestration_envelope_seconds':2000,'final_outcomes_opened':False}))


if __name__=='__main__':main()
