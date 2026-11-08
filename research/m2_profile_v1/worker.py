"""Twelve fixed synthetic profiles, with additive and nested timing categories."""
import hashlib
import json
import signal
import sys
import time
from pathlib import Path

from research.m2_profile_v1.guard import ProfileGuard,new


class ProfileStop(RuntimeError):pass


class FitClock:
    """Time original sklearn calls without changing arguments or returned values."""
    def __init__(self,cls):
        self.cls=cls;self.stage='other';self.rows={};self.originals={}

    def __enter__(self):
        for method in ('fit','predict_proba'):
            original=getattr(self.cls,method);self.originals[method]=original
            def wrap(instance,*args,_method=method,_original=original,**kwargs):
                started=time.process_time();key=self.stage+':'+_method
                try:return _original(instance,*args,**kwargs)
                finally:
                    row=self.rows.setdefault(key,{'calls':0,'cpu_seconds':0.0})
                    row['calls']+=1;row['cpu_seconds']+=time.process_time()-started
            setattr(self.cls,method,wrap)
        return self

    def __exit__(self,*_):
        for method,original in self.originals.items():setattr(self.cls,method,original)


def campaign(spec,job,start,clock,progress):
    import numpy as np
    from research.m2_v1.models import Predictor,ranked,seeded_order,synthetic_pool
    categories={'preparation':0.0,'update':0.0,'planning':0.0,'cheap_selection':0.0,'delivery_and_record':0.0}
    t=time.process_time()
    x,y,ids=synthetic_pool(spec['n'],spec['repeat'])
    order=seeded_order(ids,5000+spec['repeat']);tie=np.empty(len(ids),dtype=int);tie[order]=np.arange(len(ids))
    observed={int(i):int(y[i]) for i in order[:spec['n0']]}
    model=Predictor('rf',x,7300+spec['repeat'])
    categories['preparation']+=time.process_time()-t
    logs=[];hits=0
    for step in range(32):
        eligible=[i for i in range(len(x)) if i not in observed]
        cold=len(set(observed.values()))<2
        if cold:
            t=time.process_time();chosen=min(eligible,key=lambda i:int(tie[i]));categories['cheap_selection']+=time.process_time()-t
        else:
            clock.stage='update';t=time.process_time();model.update(observed);categories['update']+=time.process_time()-t
            if spec['policy']=='P':
                clock.stage='plan';t=time.process_time();chosen=model.plan(observed,32-step,tie);categories['planning']+=time.process_time()-t
            else:
                t=time.process_time();chosen=ranked(model.p,eligible,tie)[0];categories['cheap_selection']+=time.process_time()-t
        clock.stage='other';t=time.process_time()
        value=int(y[chosen]);observed[chosen]=value;hits+=value
        logs.append({'query':step+1,'chosen_index':int(chosen),'cold_start':cold,'synthetic_label':value,
                     'elapsed_scientific_cpu_seconds':time.process_time()-start})
        categories['delivery_and_record']+=time.process_time()-t
        progress.update(completed_queries=len(logs),steps=logs,categories=categories,nested_calls=clock.rows)
        temp=job/'progress.next.json';temp.write_text(json.dumps(progress,indent=2)+'\n')
        temp.replace(job/'progress.json')
    total=time.process_time()-start
    return {'status':'PASS_COMPLETE_SYNTHETIC_PROFILE','spec':spec,'new_queries':32,
            'scientific_cpu_seconds':total,'exclusive_cpu_seconds':categories,
            'other_and_instrumentation_cpu_seconds':total-sum(categories.values()),
            'nested_fit_and_predict':clock.rows,'nested_times_are_not_additive':True,
            'trajectory_sha256':hashlib.sha256(json.dumps([(r['chosen_index'],r['synthetic_label']) for r in logs]).encode()).hexdigest(),
            'synthetic_positives_not_molecular_evidence':hits,'steps':logs,
            'biological_data_accessed':False}


def main():
    permit=json.loads(Path(sys.argv[1]).read_text())
    assert permit['schema']=='curaloop.m2_profile.permit.v1' and permit['host']=='dr-train'
    assert permit['reservation_seconds']==185 and permit['wall_seconds']==240
    task=Path(permit['task_root']).resolve()
    assert task==Path('/home/chaw/curaloop-tasks/m2-cpu-profile-20261108-v1')
    job=task/'jobs'/permit['attempt'];code_root=task/'code'
    for name,pin in permit['code_pins'].items():assert hashlib.sha256((code_root/name).read_bytes()).hexdigest()==pin
    guard=ProfileGuard(job/'resource.json',permit)
    new(job/'kernel-proof.json',guard.kernel_proof())
    started=None;progress={'status':'RUNNING_SYNTHETIC_ONLY','spec':permit['arguments'],'completed_queries':0}
    def stop(signum,frame):raise ProfileStop('SCIENTIFIC_CPU_GUARD')
    try:
        from sklearn.ensemble import RandomForestClassifier
        from threadpoolctl import threadpool_info
        from research.m2_v1 import models
        assert all(p['num_threads']==1 for p in threadpool_info())
        assert permit['arguments']['predictor']=='rf' and permit['arguments']['n0']in(0,16) and permit['arguments']['repeat']in(0,1,2)
        startup=time.process_time();started=time.process_time()
        signal.signal(signal.SIGPROF,stop)
        # Leave a small, declared interrupt/recording margin inside the 180s scientific cap.
        signal.setitimer(signal.ITIMER_PROF,179.9)
        with FitClock(RandomForestClassifier) as clock:
            result=campaign(permit['arguments'],job,started,clock,progress)
        signal.setitimer(signal.ITIMER_PROF,0)
        result.update(startup_cpu_seconds=startup,whole_process_cpu_seconds_before_result_write=time.process_time(),
            guard_interrupt_margin_seconds=0.1,instrumentation_overhead_charged=True)
        new(job/'result.json',result);guard.finish('PASS')
        print(json.dumps({'status':result['status'],'scientific_cpu_seconds':result['scientific_cpu_seconds'],
                          'startup_cpu_seconds':startup,'new_queries':32}))
    except ProfileStop:
        signal.setitimer(signal.ITIMER_PROF,0)
        new(job/'result.json',{'status':'CENSORED_SCIENTIFIC_CPU_GUARD','spec':permit['arguments'],
            'scientific_cpu_seconds_lower_bound':time.process_time()-started,
            'completed_queries':progress['completed_queries'],'full_campaign_cpu_seconds':None,
            'guard_interrupt_margin_seconds':0.1,'biological_data_accessed':False})
        guard.finish('FAIL_RESOURCE_LIMIT')
        print(json.dumps({'status':'CENSORED_SCIENTIFIC_CPU_GUARD'}))
    except BaseException as e:
        signal.setitimer(signal.ITIMER_PROF,0)
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]});guard.finish('FAIL');raise


if __name__=='__main__':main()
