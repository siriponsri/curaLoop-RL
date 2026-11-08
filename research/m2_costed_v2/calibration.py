"""Remaining original calibration contexts; no biological data handlers."""
import hashlib
import json
import signal
import sys
import time
from pathlib import Path
from research.m2_costed_v2.guard import CostedGuard,new


class CPUStop(RuntimeError):pass


def campaign(spec,start):
    import numpy as np
    from research.m2_v1.models import Predictor,ranked,seeded_order,synthetic_pool
    from research.m2_profile_v1.worker import FitClock
    from sklearn.ensemble import RandomForestClassifier
    x,y,ids=synthetic_pool(spec['n'],spec['repeat']);order=seeded_order(ids,5000+spec['repeat'])
    tie=np.empty(len(ids),dtype=int);tie[order]=np.arange(len(ids))
    observed={int(i):int(y[i]) for i in order[:spec['n0']]};model=Predictor(spec['predictor'],x,7300+spec['repeat'])
    trace=[]
    with FitClock(RandomForestClassifier) as clock:
        for step in range(spec['budget']):
            eligible=[i for i in range(len(x)) if i not in observed]
            cold=spec['predictor']=='rf' and len(set(observed.values()))<2
            if cold:chosen=min(eligible,key=lambda i:int(tie[i]))
            else:
                clock.stage='update';model.update(observed)
                if spec['policy']=='P':clock.stage='plan';chosen=model.plan(observed,spec['budget']-step,tie)
                else:chosen=ranked(model.p,eligible,tie)[0]
            clock.stage='other';value=int(y[chosen]);observed[chosen]=value
            trace.append((int(chosen),value))
    return {'spec':spec,'new_queries':len(trace),'scientific_cpu_seconds':time.process_time()-start,
            'trajectory_sha256':hashlib.sha256(json.dumps(trace).encode()).hexdigest(),
            'nested_fit_predict':clock.rows,'biological_labels_decoded':False}


def main():
    permit=json.loads(Path(sys.argv[1]).read_text());task=Path(permit['task_root']).resolve()
    assert permit['schema']=='curaloop.m2_costed.permit.v2' and permit['handler']=='calibration'
    assert task==Path('/home/chaw/curaloop-tasks/m2-costed-20261108-v2')
    job=task/'jobs'/permit['attempt']
    for name,pin in permit['code_pins'].items():assert hashlib.sha256((task/'code'/name).read_bytes()).hexdigest()==pin
    guard=CostedGuard(job/'resource.json',permit);new(job/'kernel-proof.json',guard.kernel_proof())
    started=None
    def interrupt(signum,frame):raise CPUStop('TECHNICAL_CPU_ENVELOPE')
    try:
        import numpy
        from sklearn.ensemble import RandomForestClassifier
        from threadpoolctl import threadpool_info
        from research.m2_v1 import models
        from research.m2_profile_v1.worker import FitClock
        assert all(p['num_threads']==1 for p in threadpool_info())
        spec=permit['arguments'];science_limit=permit['science_limit_seconds']
        assert spec['predictor']in('rf','neighbor') and spec['policy']in('G1','P')
        assert spec['n']in(128,303) and spec['n0']in(0,16) and spec['budget']in(16,32) and spec['repeat']in(0,1,2)
        startup=time.process_time();started=time.process_time()
        signal.signal(signal.SIGPROF,interrupt);signal.setitimer(signal.ITIMER_PROF,max(0.1,science_limit-0.1))
        result=campaign(spec,started);signal.setitimer(signal.ITIMER_PROF,0)
        envelope=5 if spec['policy']=='G1' else 65 if spec['predictor']=='rf' else 25
        result.update(startup_cpu_seconds=startup,derived_cap_seconds=1.25*result['scientific_cpu_seconds'],
                      admission_envelope_seconds=envelope)
        passed=result['derived_cap_seconds']<=envelope
        result['status']='PASS_SYNTHETIC_CONTEXT' if passed else 'FAIL_DERIVED_CPU_ENVELOPE'
        new(job/'result.json',result);guard.finish('PASS' if passed else 'FAIL_ADMISSION')
        print(json.dumps({k:result[k] for k in('status','scientific_cpu_seconds','derived_cap_seconds','admission_envelope_seconds')}))
    except CPUStop:
        signal.setitimer(signal.ITIMER_PROF,0)
        new(job/'result.json',{'status':'CENSORED_TECHNICAL_CPU_LIMIT','spec':permit['arguments'],
             'scientific_cpu_seconds_lower_bound':time.process_time()-started,'full_campaign_time':None,
             'biological_labels_decoded':False})
        guard.finish('FAIL_RESOURCE_LIMIT');print(json.dumps({'status':'CENSORED_TECHNICAL_CPU_LIMIT'}))
    except BaseException as e:
        signal.setitimer(signal.ITIMER_PROF,0)
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]});guard.finish('FAIL');raise


if __name__=='__main__':main()
