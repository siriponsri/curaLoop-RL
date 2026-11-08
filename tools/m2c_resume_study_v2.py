"""Resume the fixed tuning matrix after fresh proof that a batch was not sent."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,batch
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2'


def main():
    guard=OrchestrationGuard(TASK/'tuning-resume-01-orchestration-resource.json',500,'2026-11-12T08:17:29Z')
    try:
        matrix=json.loads((TASK/'execution-matrix-v1.json').read_text());over=json.loads((TASK/'execution-retry-resolution-v1.json').read_text())['mapping']
        selected=[e for e in matrix['entries'] if e['handler']=='tuning'];queues={cpu:[] for cpu in(69,70,71)};completed=0
        for e in selected:
            actual=over.get(e['job'],e['job']);path=TASK/'jobs'/actual/'result.json'
            if path.exists():
                assert json.loads(path.read_text())['status']=='PASS_CAMPAIGN';assert json.loads((path.parent/'resource.json').read_text())['status']=='PASS';completed+=1
            else:queues[e['cpu']].append((e,actual))
        assert completed==174
        new(TASK/'tuning-resume-01-freeze.json',{'retained_successful_units':completed,'pending_by_cpu':{str(k):[a for e,a in v] for k,v in queues.items()},
          'original_freeze_sha256':hashlib.sha256((TASK/'tuning-execution-freeze.json').read_bytes()).hexdigest(),
          'retry_mapping':over,'parameters_unchanged':True,'outer_outcomes_opened':False})
        started=time.monotonic()
        while any(queues.values()):
            group=[queues[cpu].pop(0) for cpu in(69,70,71) if queues[cpu]]
            for e,actual in group:admin_call('reserve',TASK/'specs'/(actual+'.json'))
            out=batch([actual for e,actual in group],action='worker');failures=[]
            for e,actual in group:
                admin_call('settle',actual);r=json.loads((TASK/'jobs'/actual/'resource.json').read_text())
                p=TASK/'jobs'/actual/'result.json';result=json.loads(p.read_text()) if p.exists() else {}
                if r['status']!='PASS' or not result.get('status','').startswith('PASS'):failures.append(actual)
                # Every original argument is preserved, including the paired core.
                assert result.get('spec')==e['arguments']
                completed+=1
            print(json.dumps({'stage':'tuning-resume','complete':completed,'total':576,'elapsed_seconds':round(time.monotonic()-started,1),'failures':failures}),flush=True)
            if failures:raise RuntimeError('RETAINED_UNIT_FAILURE:'+','.join(failures))
        new(TASK/'tuning-summary.json',{'status':'PASS_COMPLETE_STAGE','stage':'tuning','units':completed,
          'retained_completed_before_transport_failure':174,'retained_not_dispatched_failures':3,'same_context_retries':3,
          'retry_resolution':'execution-retry-resolution-v1.json','outcome_inspection_for_selection':False})
        guard.finish('PASS')
    except BaseException:guard.finish('FAIL_ORCHESTRATION_OR_UNIT');raise


if __name__=='__main__':main()
