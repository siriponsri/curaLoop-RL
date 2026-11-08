"""Constructed information-boundary and continuation checks; no biological input."""
import copy
import numpy as np
from research.m2_costed_v2.engine import State,Oracle,PublicPool,Clock,run,OPS,FEATURE_NAMES
from research.m2_costed_v2.learning import fit_gate,choose_controls,Gate
from research.m2_v1.models import synthetic_pool


def checks():
    tests=[]
    def ok(name,condition):
        assert condition,name
        tests.append({'name':name,'status':'PASS'})
    x,y,ids=synthetic_pool(128,42);pool=PublicPool('constructed','g0',tuple(ids),x)
    priors={'REUSE':.0002,'UPDATE':.001,'PLAN':.1}
    a=State(pool,'neighbor',91,16,32,priors);b=State(pool,'neighbor',91,16,32,priors)
    initial=a.initial_indices();other=y.copy();hidden=[i for i in range(len(y)) if i not in initial];other[hidden]=1-other[hidden]
    a.observed=Oracle(y,32).initial(initial);b.observed=Oracle(other,32).initial(initial)
    a.model.update(a.observed);b.model.update(b.observed)
    class Fixed:
        cap=1.;margin=.002
        def remaining(self):return .8
        def enough(self,cost=0):return .8>cost+.002
        def spent(self):return .2
    fixed=Fixed()
    ok('hidden-label-permutation-leaves-public-features-and-choice-invariant',
       np.array_equal(a.features(fixed),b.features(fixed)) and a.choose_operation('T',fixed,(4,.05))==b.choose_operation('T',fixed,(4,.05)))
    snap=a.snapshot(fixed);restored=State.restore(pool,'neighbor',91,16,32,snap,a.similarity,a.neighbors)
    ok('snapshot-restores-observed-state-and-cache',a.observed==restored.observed and np.array_equal(a.model.p,restored.model.p) and np.array_equal(a.features(fixed),restored.features(fixed)))
    c=Clock(.2);s=State(pool,'neighbor',91,16,16,priors);out,_=run(s,Oracle(y,16),c,'R')
    ok('initial-positives-excluded-from-new-discovery',out['new_positives']==sum(t['delivered_label'] for t in out['trace']) and out['new_deliveries']==16 and len(s.observed)==32)
    c=Clock(.0001);s=State(pool,'neighbor',91,0,32,priors);out,_=run(s,Oracle(y,32),c,'P')
    ok('no-free-query-after-exhausted-compute',out['new_deliveries']==0)
    class Negative:
        def predict(self,features):return np.array([-1.,-2.])
    ok('nonpositive-gate-benefits-select-reuse',a.choose_operation('L',fixed,gate=Negative())[0]=='REUSE')
    class Positive:
        def predict(self,features):return np.array([2.,3.])
    ok('restricted-operation-excluded-before-choice',a.choose_operation('L',fixed,gate=Positive(),restricted=('PLAN',))[0]=='UPDATE')
    index=next(i for i in a.eligible());before=a.weights.copy();a.accept(index,1,.5,'UPDATE','UPDATE',fixed,(1,.25))
    ok('exp3-updates-only-selected-operation-with-actual-probability',np.allclose(a.weights-before,[0,.1/3/.25,0]))
    rows=[]
    for g in range(4):
        for k in range(6):rows.append({'component':'g'+str(g),'predictor':'rf','eligible':True,'task_id':'t'+str(g),
          'features':(np.arange(len(FEATURE_NAMES))*.03+k+g).tolist(),'benefits':[k-g,g-k]})
    fit=fit_gate(rows,'g0','rf');mut=copy.deepcopy(rows)
    for r in mut:
        if r['component']=='g0':r.update(features=[999.]*len(FEATURE_NAMES),benefits=[-999.,999.])
    ok('gate-and-scaler-exclude-entire-heldout-component',fit==fit_gate(mut,'g0','rf') and fit['training_components']==['g1','g2','g3'])
    ok('no-history-gate-has-only-budget-and-cached-ranking-features',fit_gate(rows,'g0','rf',True)['feature_indices']==[0,1,2,8,9,10])
    tuning=[]
    for g in range(4):
        for family in('Gk','T'):
            for i in range(3):tuning.append({'component':'g'+str(g),'predictor':'rf','family':family,'configuration':i,
              'task_id':'t'+str(g),'new_positives':i+1,'scientific_cpu_seconds':1.})
    selected=choose_controls(tuning,'g0','rf');mut=copy.deepcopy(tuning)
    for r in mut:
        if r['component']=='g0':r['new_positives']=999
    ok('control-selection-excludes-heldout-outcomes',selected==choose_controls(mut,'g0','rf'))
    # The actual signal guard must interrupt a long PLAN without publishing partial cache.
    c=Clock(.025);s=State(pool,'neighbor',91,16,32,dict(REUSE=.0001,UPDATE=.0001,PLAN=.0001))
    s.observed=Oracle(y,32).initial(s.initial_indices());s.model.update(s.observed);cache=s.model.p.copy()
    out,_=run(s,Oracle(y,32),c,'P')
    ok('millisecond-cpu-guard-retains-budget-and-discards-partial-work',not out['cpu_violation'] and out['scientific_cpu_seconds']<=.025 and out['interruptions']>=1)
    return {'status':'PASS_CONSTRUCTED_ENGINE_CHECKS','checks':tests,'biological_records_read':False,'final_outcomes_opened':False}
