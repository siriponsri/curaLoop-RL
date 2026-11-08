"""Outcome-blind G1/P calibration; biological inputs are unavailable to this module."""
import json
import os
import signal
import sys
import time
from pathlib import Path

from research.m2_v1.admission import M2Guard, new


class ScientificCPUStop(RuntimeError):
    pass


def run_campaign(spec):
    import numpy as np
    from research.m2_v1.models import Predictor, ranked, seeded_order, synthetic_pool
    start=time.process_time()
    x,y,ids=synthetic_pool(spec['n'],spec['repeat'])
    order=seeded_order(ids,5000+spec['repeat'])
    tie=np.empty(len(ids),dtype=int);tie[order]=np.arange(len(ids))
    observed={int(i):int(y[i]) for i in order[:spec['n0']]}
    model=Predictor(spec['predictor'],x,7300+spec['repeat'])
    logs=[]; hits=0
    for step in range(spec['budget']):
        eligible=[i for i in range(len(x)) if i not in observed]
        operation='UPDATE' if spec['policy']=='G1' else 'PLAN'
        before=time.process_time()
        cold=spec['predictor']=='rf' and len(set(observed.values()))<2
        if cold:
            chosen=min(eligible,key=lambda i:int(tie[i]))
        else:
            model.update(observed)
            chosen=(ranked(model.p,eligible,tie)[0] if operation=='UPDATE'
                    else model.plan(observed,spec['budget']-step,tie))
        cpu=time.process_time()-before
        prediction=float(model.p[chosen])
        value=int(y[chosen]);observed[chosen]=value;hits+=value
        logs.append({'step':step,'operation':operation,'cold_start':cold,
                     'cpu_seconds':cpu,'fit_cpu_seconds':model.last_fit_cpu if not cold else 0,
                     'delivered':True,'prequential_prediction':prediction})
    return {'status':'PASS_SYNTHETIC_CAMPAIGN','spec':spec,'scientific_cpu_seconds':time.process_time()-start,
            'new_deliveries':len(logs),'synthetic_positives':hits,'steps':logs,
            'biological_outcomes_accessed':False}


def main():
    permit=json.loads(Path(sys.argv[1]).read_text())
    assert permit['schema']=='curaloop.m2.permit.v1' and permit['host']=='dr-train'
    assert permit['reservation_seconds']==31 and permit['guard_cpu_seconds']==30.5
    task=Path(permit['task_root']).resolve()
    assert task==Path('/home/chaw/curaloop-tasks/m2-selective-compute-20261108-v1')
    job=task/'jobs'/permit['attempt']
    guard=M2Guard(job/'resource.json',permit)
    # The systemd unit independently enforces aggregate quota, RAM, swap and wall timeout.
    cgroup=Path('/sys/fs/cgroup'+next(s.split('::',1)[1] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')))
    proof={k:(cgroup/k).read_text().strip() for k in ('cpu.max','memory.max','memory.swap.max')}
    assert proof=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
    new(job/'kernel-proof.json',proof)
    began=None
    def stop(signum,frame):
        raise ScientificCPUStop('30_CPU_SECOND_ADMISSION_LIMIT')
    try:
        # Import once before the scientific timer; this startup is still charged by the whole-process guard.
        import numpy
        from sklearn.ensemble import RandomForestClassifier
        from threadpoolctl import threadpool_info
        assert all(p['num_threads']==1 for p in threadpool_info())
        began=time.process_time()
        signal.signal(signal.SIGPROF,stop)
        # A complete time exceeding 24 seconds implies 1.25 * time > 30.
        # Stop the profile as soon as that lower bound proves admission failure.
        signal.setitimer(signal.ITIMER_PROF,24.01)
        result=run_campaign(permit['arguments'])
        signal.setitimer(signal.ITIMER_PROF,0)
        result['whole_process_cpu_seconds']=time.process_time()
        new(job/'result.json',result)
        guard.finish('PASS')
        print(json.dumps({'status':result['status'],'scientific_cpu_seconds':result['scientific_cpu_seconds']}))
    except ScientificCPUStop:
        signal.setitimer(signal.ITIMER_PROF,0)
        new(job/'result.json',{'status':'STOP_RESOURCE_FIT','spec':permit['arguments'],
            'scientific_cpu_seconds_lower_bound':time.process_time()-began,
            'calibrated_cap_lower_bound':1.25*(time.process_time()-began),'proposed_cap_seconds':30,
            'biological_outcomes_accessed':False})
        guard.finish('FAIL_RESOURCE_LIMIT')
        print(json.dumps({'status':'STOP_RESOURCE_FIT'}))
    except BaseException as e:
        signal.setitimer(signal.ITIMER_PROF,0)
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]})
        guard.finish('FAIL')
        raise


if __name__=='__main__':
    main()
