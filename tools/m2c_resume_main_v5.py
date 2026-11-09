"""Continue the original hash-frozen order; never repeat a completed campaign."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,batch
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2'


def main():
    permit=json.loads((TASK/'jobs/orchestration-recovery-v5/permit.json').read_text())
    guard=OrchestrationGuard(TASK/'main-resume-v5-orchestration-resource.json',700,permit['deadline_utc'])
    try:
        recovery=json.loads((TASK/'local-controller-absence-v5.json').read_text())
        assert recovery['status']=='PASS_FRESH_V5_LOCAL_ABSENCE_AND_NOT_DISPATCHED'
        already_booked=set(recovery.get('reserved_not_dispatched_jobs',[]))
        ledger=json.loads((TASK/'ledger.json').read_text())
        assert already_booked=={j['job'] for j in ledger['jobs'] if j['state']=='RESERVED' and j['host']=='dr-train'}
        frozen=json.loads((TASK/'main-execution-freeze.json').read_text());queues={cpu:[] for cpu in(69,70,71)};retained=[]
        for name in frozen['jobs']:
            path=TASK/'specs'/(name+'.json');assert hashlib.sha256(path.read_bytes()).hexdigest()==frozen['spec_pins'][name]
            spec=json.loads(path.read_text());assert spec['handler']in('main','ablation')
            resource=TASK/'jobs'/name/'resource.json'
            if resource.exists():
                assert json.loads(resource.read_text())['status']=='PASS'
                result=json.loads((resource.parent/'result.json').read_text());assert result['status']=='PASS_CAMPAIGN' and result['spec']==spec['arguments']
                retained.append(name)
            else:
                if name in already_booked:
                    permit=json.loads((TASK/'jobs'/name/'permit.json').read_text())
                    assert all(permit.get(k)==v for k,v in spec.items()),'RETAINED_PERMIT_DIFFERS_FROM_FROZEN_SPEC'
                else:assert not (TASK/'jobs'/name).exists(),'AMBIGUOUS_PREVIOUS_DISPATCH'
                queues[spec['cpu']].append((name,path))
        completed=len(retained);assert 210<=completed<=2100 and sum(len(v) for v in queues.values())+completed==2100
        new(TASK/'main-resume-v5-freeze.json',{'retained_successful_units':completed,'retained_jobs':retained,
          'source_freeze_sha256':hashlib.sha256((TASK/'main-execution-freeze.json').read_bytes()).hexdigest(),
          'retained_original_bookings_for_first_dispatch':sorted(already_booked),
          'pending_by_cpu':{str(k):[n for n,p in v] for k,v in queues.items()},'scientific_arguments_unchanged':True})
        start=time.monotonic()
        while any(queues.values()):
            group=[queues[cpu].pop(0) for cpu in(69,70,71) if queues[cpu]]
            reuse_prepared=any(name in already_booked for name,path in group)
            for name,path in group:
                if name in already_booked:already_booked.remove(name)
                else:admin_call('reserve',path)
            batch([name for name,path in group],action='worker',retained_proof=TASK/'local-controller-absence-v5.json' if reuse_prepared else None);failures=[]
            for name,path in group:
                admin_call('settle',name);resource=json.loads((TASK/'jobs'/name/'resource.json').read_text())
                result_path=TASK/'jobs'/name/'result.json';result=json.loads(result_path.read_text()) if result_path.exists() else {}
                if resource['status']!='PASS' or result.get('status')!='PASS_CAMPAIGN':failures.append(name)
                completed+=1
            print(json.dumps({'stage':'main-resume','complete':completed,'total':2100,'elapsed_seconds':round(time.monotonic()-start,1),'failures':failures}),flush=True)
            if failures:raise RuntimeError('RETAINED_UNIT_FAILURE:'+','.join(failures))
        assert not already_booked
        new(TASK/'main-summary.json',{'status':'PASS_COMPLETE_STAGE','stage':'main','units':1920,
          'retained_before_controller_v5':len(retained),'outcome_inspection_for_selection':False})
        new(TASK/'ablation-summary.json',{'status':'PASS_COMPLETE_STAGE','stage':'ablation','units':180,
          'interleaved_with_main':True,'outcome_inspection_for_selection':False})
        guard.finish('PASS')
    except BaseException:guard.finish('FAIL_ORCHESTRATION_OR_UNIT');raise


if __name__=='__main__':main()
