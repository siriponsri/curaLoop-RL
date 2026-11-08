"""Technical repair: verify process-CPU lower bound before declaring a cap failure.

ITIMER_PROF delivery and process_time have different accounting granularity.
The original synthetic attempt is preserved as an invalid admission inference.
Predictors, planner, synthetic data, objective and proposed 30-second cap are unchanged.
"""
import json
import signal
import sys
import time
from pathlib import Path

from research.m2_v1.admission import M2Guard, new
from research.m2_v1.calibration import ScientificCPUStop, run_campaign


def main():
    permit=json.loads(Path(sys.argv[1]).read_text())
    assert permit['schema']=='curaloop.m2.permit.v1' and permit['host']=='dr-train'
    assert permit['reservation_seconds']==31 and permit['guard_cpu_seconds']==30.5
    task=Path(permit['task_root']).resolve()
    assert task==Path('/home/chaw/curaloop-tasks/m2-selective-compute-20261108-v1')
    job=task/'jobs'/permit['attempt']
    guard=M2Guard(job/'resource.json',permit)
    cg=Path('/sys/fs/cgroup'+next(s.split('::',1)[1] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')))
    proof={k:(cg/k).read_text().strip() for k in ('cpu.max','memory.max','memory.swap.max')}
    assert proof=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
    new(job/'kernel-proof.json',proof)
    began=None
    def stop(signum,frame):
        elapsed=time.process_time()-began
        if elapsed <= 24.05:
            signal.setitimer(signal.ITIMER_PROF,max(0.1,24.1-elapsed))
            return
        raise ScientificCPUStop('CALIBRATED_CAP_LOWER_BOUND_EXCEEDS_30')
    try:
        import numpy
        from sklearn.ensemble import RandomForestClassifier
        from threadpoolctl import threadpool_info
        assert all(p['num_threads']==1 for p in threadpool_info())
        began=time.process_time()
        signal.signal(signal.SIGPROF,stop)
        signal.setitimer(signal.ITIMER_PROF,24.1)
        result=run_campaign(permit['arguments'])
        signal.setitimer(signal.ITIMER_PROF,0)
        result['whole_process_cpu_seconds']=time.process_time()
        result['timer_revision']='v2_verified_process_time_lower_bound'
        new(job/'result.json',result);guard.finish('PASS')
        print(json.dumps({'status':result['status'],'scientific_cpu_seconds':result['scientific_cpu_seconds']}))
    except ScientificCPUStop:
        signal.setitimer(signal.ITIMER_PROF,0)
        elapsed=time.process_time()-began
        assert elapsed > 24 and 1.25*elapsed > 30
        result={'status':'STOP_RESOURCE_FIT','spec':permit['arguments'],
            'scientific_cpu_seconds_lower_bound':elapsed,'calibrated_cap_lower_bound':1.25*elapsed,
            'proposed_cap_seconds':30,'exact_completed_campaign_time':None,
            'timer_revision':'v2_verified_process_time_lower_bound','biological_outcomes_accessed':False}
        new(job/'result.json',result);guard.finish('FAIL_RESOURCE_LIMIT')
        print(json.dumps(result))
    except BaseException as e:
        signal.setitimer(signal.ITIMER_PROF,0)
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]})
        guard.finish('FAIL');raise


if __name__=='__main__':main()
