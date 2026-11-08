"""Constructed checks of the exact admitted predictor and planner implementation."""
import json
import sys
from pathlib import Path

from research.m2_v1.admission import M2Guard, new


def run():
    import numpy as np
    from threadpoolctl import threadpool_info
    from research.m2_v1.models import Predictor, ranked, seeded_order, synthetic_pool
    checks=[]
    def check(name,value):
        if not value:raise AssertionError(name)
        checks.append(name)
    check('numerical libraries single-threaded',all(p['num_threads']==1 for p in threadpool_info()))
    x=np.array([[1,0,0],[1,1,0],[0,0,1],[0,1,1]],dtype=np.uint8)
    m=Predictor('neighbor',x,1)
    check('neighbor prior is one half',np.all(m.probabilities({})==0.5))
    p=m.probabilities({0:1})
    check('neighbor Beta smoothing analytic example',abs(p[1]-1.5/2.5)<1e-12 and p[2]==0.5)
    check('neighbor graph excludes own index',all(i not in row for i,row in enumerate(m.neighbors)))
    m.update({0:1});before=m.p.copy();obs={0:1}
    tie=np.array([0,1,2,3])
    chosen=m.plan(obs,2,tie)
    manual={}
    for i in (1,2,3):
        tail=[]
        for y in (0,1):
            history=dict(obs);history[i]=y
            q=m.probabilities(history)
            other=[j for j in (1,2,3) if j!=i]
            tail.append(y+max(q[j] for j in other))
        manual[i]=(1-before[i])*tail[0]+before[i]*tail[1]
    expected=min(manual,key=lambda i:(-manual[i],int(tie[i])))
    check('neighbor planner matches independent two-query enumeration',chosen==expected)
    check('planning leaves observed state and cached means unchanged',obs=={0:1} and np.array_equal(before,m.p))
    check('one remaining query reduces to greedy',m.plan(obs,1,tie)==ranked(m.p,[1,2,3],tie)[0])
    rf=Predictor('rf',x,17)
    check('RF empty and one-class states have neutral prior',np.all(rf.probabilities({})==0.5) and np.all(rf.probabilities({0:1})==0.5))
    rf.update({0:1,2:0})
    check('RF delivered-only update has finite probabilities',np.all(np.isfinite(rf.p)) and np.all((rf.p>=0)&(rf.p<=1)))
    rf_observed={0:1,2:0};state=dict(rf_observed)
    rf.plan(rf_observed,2,tie)
    check('RF hypothetical planning does not mutate caller labels',state==rf_observed)
    a,b,ids=synthetic_pool(128,0);c,d,_=synthetic_pool(128,0)
    check('synthetic generator deterministic and nonconstant',np.array_equal(a,c) and np.array_equal(b,d) and len(set(b.tolist()))==2)
    order=seeded_order(ids,101)
    check('seed ordering is a complete reproducible permutation',len(set(order.tolist()))==128 and np.array_equal(order,seeded_order(ids,101)))
    return {'status':'PASS_CONSTRUCTED_CHECKS','count':len(checks),'checks':checks,'biological_data_accessed':False}


def main():
    permit=json.loads(Path(sys.argv[1]).read_text())
    assert permit['schema']=='curaloop.m2.permit.v1' and permit['host']=='dr-train'
    task=Path(permit['task_root']);job=task/'jobs'/permit['attempt']
    guard=M2Guard(job/'resource.json',permit)
    try:
        result=run();new(job/'result.json',result);guard.finish('PASS')
        print(json.dumps(result))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]});guard.finish('FAIL');raise


if __name__=='__main__':main()
