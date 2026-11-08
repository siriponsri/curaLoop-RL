"""Check that timing wrappers preserve deterministic RF behavior and restore methods."""
import json
import sys
from pathlib import Path
from research.m2_profile_v1.guard import ProfileGuard,new


def main():
    permit=json.loads(Path(sys.argv[1]).read_text());job=Path(permit['task_root'])/'jobs'/permit['attempt']
    guard=ProfileGuard(job/'resource.json',permit)
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from threadpoolctl import threadpool_info
        from research.m2_profile_v1.worker import FitClock
        checks=[]
        def check(name,value):
            if not value:raise AssertionError(name)
            checks.append(name)
        check('numeric pools single threaded',all(p['num_threads']==1 for p in threadpool_info()))
        x=np.array([[1,0],[0,1],[1,1],[0,0],[1,0],[0,1],[1,1],[0,0]],dtype=np.uint8)
        y=np.array([1,0,1,0,0,1,1,0])
        kwargs=dict(n_estimators=64,max_depth=6,min_samples_leaf=2,max_features='sqrt',bootstrap=True,
                    class_weight=None,n_jobs=1,random_state=7300)
        plain=RandomForestClassifier(**kwargs).fit(x,y).predict_proba(x)
        original_fit=RandomForestClassifier.fit;original_predict=RandomForestClassifier.predict_proba
        with FitClock(RandomForestClassifier) as clock:
            clock.stage='check';model=RandomForestClassifier(**kwargs);returned=model.fit(x,y);timed=model.predict_proba(x)
            check('instrumented fit returns the original instance',returned is model)
            check('instrumented RF predictions exactly match original',np.array_equal(plain,timed))
            check('nested counters record each real call once',clock.rows['check:fit']['calls']==1 and clock.rows['check:predict_proba']['calls']==1)
        check('instrumentation restores original methods',RandomForestClassifier.fit is original_fit and RandomForestClassifier.predict_proba is original_predict)
        new(job/'kernel-proof.json',guard.kernel_proof())
        result={'status':'PASS_PROFILE_INSTRUMENTATION_CHECKS','count':len(checks),'checks':checks,
                'biological_data_accessed':False,'full_profile_campaigns':0}
        new(job/'result.json',result);guard.finish('PASS');print(json.dumps(result))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]});guard.finish('FAIL');raise


if __name__=='__main__':main()
