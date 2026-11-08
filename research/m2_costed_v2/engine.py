"""Delivered-information screening with common computation guards and operation controls.

The state never owns an oracle or a future-label array. Oracle queries happen only
after a public action is committed inside the joint assay/CPU limits.
"""
import copy
import math
import signal
import time
from dataclasses import dataclass

import numpy as np
from research.m2_v1.models import Predictor,ranked,seeded_order

OPS=('REUSE','UPDATE','PLAN')
FEATURE_NAMES=('remaining_over_32','remaining_fraction','cpu_fraction','observed_fraction',
 'positive_count_fraction','negative_count_fraction','positive_fraction','staleness_fraction',
 'cached_margin','cached_std','cached_top_mean','observed_neighbor_support',
 'recent_brier','recent_logloss','prequential_fraction','error_available','model_available',
 'reuse_cost_fraction','update_cost_fraction','plan_cost_fraction')
NO_HISTORY_KEEP=(0,1,2,8,9,10)


class ComputeInterrupt(RuntimeError):pass


class Clock:
    def __init__(self,cap,prefix=0.0):
        self.cap=float(cap);self.prefix=float(prefix);self.start=time.process_time()
        self.margin=min(.05,max(.002,.01*self.cap))

    def spent(self):return self.prefix+time.process_time()-self.start
    def remaining(self):return self.cap-self.spent()
    def enough(self,cost=0.0):return self.remaining()>max(0.0,float(cost))+self.margin

    def arm(self):
        remaining=self.remaining()-self.margin
        if remaining<=0:raise ComputeInterrupt('NO_COMPUTE_RESERVE')
        signal.setitimer(signal.ITIMER_PROF,max(.001,remaining))

    @staticmethod
    def disarm():signal.setitimer(signal.ITIMER_PROF,0)


@dataclass
class PublicPool:
    task_id:str
    component:str
    ids:tuple
    x:np.ndarray


class Oracle:
    def __init__(self,labels,budget):
        self.__labels=np.asarray(labels,dtype=np.int8);self.budget=int(budget);self.queried=set()
        assert np.isin(self.__labels,[0,1]).all()

    def initial(self,indices):return {int(i):int(self.__labels[i]) for i in indices}

    def query(self,index):
        assert index not in self.queried and len(self.queried)<self.budget
        self.queried.add(index);return int(self.__labels[index])


def public_graph(x):
    dense=x.astype(np.float32);intersection=dense@dense.T;counts=dense.sum(axis=1)
    union=counts[:,None]+counts[None,:]-intersection
    sim=np.divide(intersection,union,out=np.zeros_like(union),where=union>0);np.fill_diagonal(sim,0)
    scores=sim.copy();np.fill_diagonal(scores,-1)
    neighbors=np.argsort(-scores,axis=1,kind='stable')[:,:min(16,len(x)-1)]
    return sim,neighbors


class State:
    def __init__(self,pool,kind,seed,n0,budget,cost_priors):
        self.pool=pool;self.kind=kind;self.seed=int(seed);self.n0=int(n0);self.budget=int(budget)
        self.order=seeded_order(pool.ids,seed);self.tie=np.empty(len(pool.ids),dtype=int);self.tie[self.order]=np.arange(len(pool.ids))
        self.model=Predictor(kind,pool.x,seed)
        if kind=='neighbor':self.similarity,self.neighbors=self.model.similarity,self.model.neighbors
        else:self.similarity,self.neighbors=public_graph(pool.x)
        self.observed={};self.deliveries=0;self.hits=0;self.errors=[];self.logloss=[];self.trace=[]
        self.costs={op:max(.00001,float(cost_priors[op])) for op in OPS}
        self.operation_counts={op:0 for op in OPS};self.interruptions=0;self.feasibility_fallbacks=0
        self.initial_fit_count=0;self.weights=np.zeros(3);self.rng=np.random.default_rng(seed+7919)

    def initial_indices(self):return self.order[:self.n0]
    def eligible(self):return [i for i in range(len(self.pool.ids)) if i not in self.observed]
    def cold(self):return self.kind=='rf' and len(set(self.observed.values()))<2
    def ready(self):return self.model.fitted_observations>=0
    def stale(self):return max(0,len(self.observed)-max(0,self.model.fitted_observations))

    def estimated_cost(self,op):
        if op=='UPDATE' and self.stale()==0:return self.costs['REUSE']
        if op=='PLAN' and self.budget-self.deliveries==1:return self.estimated_cost('UPDATE')
        return max(self.costs['REUSE'],self.costs[op])

    def initialize_model(self,clock):
        if self.ready() or self.cold():return True
        if not clock.enough(self.costs['UPDATE']):return False
        before=self.model.p.copy();fitted=self.model.fitted_observations
        try:
            clock.arm();t=time.process_time();self.model.update(self.observed);elapsed=time.process_time()-t
            self.costs['UPDATE']=.5*self.costs['UPDATE']+.5*max(.00001,elapsed);self.initial_fit_count+=1
            return True
        except ComputeInterrupt:
            self.model.p=before;self.model.fitted_observations=fitted;self.interruptions+=1;return False
        finally:clock.disarm()

    def features(self,clock):
        eligible=self.eligible();r=self.budget-self.deliveries;n=len(self.observed)
        scores=self.model.p[eligible] if eligible else np.array([.5])
        top=sorted(eligible,key=lambda i:(-float(self.model.p[i]),int(self.tie[i])))[:2]
        margin=float(self.model.p[top[0]]-self.model.p[top[1]]) if len(top)>1 else 0.0
        support=sum(int(j) in self.observed for j in self.neighbors[top[0]])/max(1,len(self.neighbors[top[0]])) if top else 0.0
        pos=sum(self.observed.values());scale=max(1,self.n0+self.budget)
        return np.array([r/32,r/max(1,self.budget),max(0,clock.remaining())/max(clock.cap,1e-9),n/len(self.pool.ids),
            pos/scale,(n-pos)/scale,pos/n if n else .5,self.stale()/scale,margin,float(np.std(scores)),float(np.mean(scores)),
            support,float(np.mean(self.errors[-8:])) if self.errors else .25,
            float(np.mean(self.logloss[-8:])) if self.logloss else math.log(2),len(self.errors)/max(1,self.budget),
            float(bool(self.errors)),float(self.ready()),*(self.costs[op]/max(clock.cap,1e-9) for op in OPS)],dtype=float)

    def choose_operation(self,policy,clock,parameter=None,gate=None,restricted=()):
        feasible=[op for op in OPS if op not in restricted and clock.enough(self.estimated_cost(op))]
        if not feasible:return None,None
        requested='REUSE';credit=None
        if policy in('G1','U'):requested='UPDATE'
        elif policy=='P':requested='PLAN'
        elif policy=='Gk':requested='UPDATE' if self.stale()>=int(parameter) else 'REUSE'
        elif policy=='T':
            k,tau=parameter
            if self.stale()>=k:requested='UPDATE'
            else:
                eligible=self.eligible();top=ranked(self.model.p,eligible,self.tie)[:2]
                margin=float(self.model.p[top[0]]-self.model.p[top[1]]) if len(top)>1 else 0
                if margin<=tau and self.budget-self.deliveries>=8:requested='PLAN'
        elif policy=='E':
            indices=[OPS.index(op) for op in feasible];w=np.exp(self.weights[indices]-np.max(self.weights[indices]))
            probabilities=.9*w/w.sum()+.1/len(indices)
            chosen=int(self.rng.choice(len(indices),p=probabilities));index=indices[chosen]
            requested=OPS[index];credit=(index,float(probabilities[chosen]))
        elif policy=='L':
            assert gate is not None
            gain=gate.predict(self.features(clock));values={'REUSE':0.0,'UPDATE':float(gain[0]),'PLAN':float(gain[1])}
            feasible=[op for op in feasible if clock.enough(self.estimated_cost(op))]
            if not feasible:return None,None
            chosen=min(feasible,key=lambda op:(-values[op],self.estimated_cost(op),OPS.index(op)))
            requested=chosen if values[chosen]>0 else 'REUSE'
        elif policy=='R':requested='REUSE'
        elif policy in OPS:requested=policy
        else:raise ValueError('UNKNOWN_FROZEN_POLICY')
        if requested not in feasible:
            self.feasibility_fallbacks+=1;requested='REUSE' if 'REUSE'in feasible else None
        return requested,credit

    def execute(self,op,policy,clock):
        if not clock.enough(self.estimated_cost(op)):return None,'NO_CPU'
        before=(self.model.p.copy(),self.model.fitted_observations,self.model.last_fit_cpu)
        start=time.process_time();actual=op
        try:
            clock.arm()
            if policy=='R':chosen=min(self.eligible(),key=lambda i:int(self.tie[i]))
            else:
                if op in('UPDATE','PLAN') and self.stale()>0:self.model.update(self.observed)
                eligible=self.eligible()
                if op=='PLAN':chosen=self.model.plan(self.observed,self.budget-self.deliveries,self.tie)
                else:
                    score=self.model.p*(1-self.model.p) if policy=='U' else self.model.p
                    chosen=ranked(score,eligible,self.tie)[0]
        except ComputeInterrupt:
            self.model.p,self.model.fitted_observations,self.model.last_fit_cpu=before
            self.interruptions+=1;actual='INTERRUPTED_'+op
            clock.disarm()
            if not clock.enough(self.costs['REUSE']):chosen=None
            else:chosen=ranked(self.model.p,self.eligible(),self.tie)[0]
        finally:clock.disarm()
        elapsed=time.process_time()-start;self.costs[op]=.5*self.costs[op]+.5*max(.00001,elapsed)
        self.operation_counts[op]+=1
        return chosen,actual

    def accept(self,index,label,prediction,requested,actual,clock,credit=None):
        assert index not in self.observed and self.deliveries<self.budget
        self.observed[index]=int(label);self.deliveries+=1;self.hits+=int(label)
        self.errors.append((float(prediction)-label)**2);p=min(1-1e-6,max(1e-6,float(prediction)))
        self.logloss.append(-(label*math.log(p)+(1-label)*math.log(1-p)))
        if credit is not None:
            arm,probability=credit;self.weights[arm]+=(.1/3)*(label/max(probability,1e-9))
        self.trace.append({'query':self.deliveries,'candidate_index':int(index),'delivered_label':int(label),
            'prequential_prediction':float(prediction),'requested_operation':requested,'actual_operation':actual,
            'new_positives':self.hits,'scientific_cpu_seconds':clock.spent()})

    def snapshot(self,clock):
        return {'observed':dict(self.observed),'deliveries':self.deliveries,'hits':self.hits,
            'cached_p':self.model.p.tolist(),'fitted_observations':self.model.fitted_observations,
            'last_fit_cpu':self.model.last_fit_cpu,'errors':list(self.errors),'logloss':list(self.logloss),
            'costs':dict(self.costs),'operation_counts':dict(self.operation_counts),
            'initial_fit_count':self.initial_fit_count,'prefix_cpu_seconds':clock.spent(),
            'rng_state':copy.deepcopy(self.rng.bit_generator.state),'trace':copy.deepcopy(self.trace)}

    @classmethod
    def restore(cls,pool,kind,seed,n0,budget,snapshot,similarity,neighbors):
        value=cls.__new__(cls);value.pool=pool;value.kind=kind;value.seed=int(seed);value.n0=int(n0);value.budget=int(budget)
        value.order=seeded_order(pool.ids,seed);value.tie=np.empty(len(pool.ids),dtype=int);value.tie[value.order]=np.arange(len(pool.ids))
        model=Predictor.__new__(Predictor);model.kind=kind;model.x=pool.x;model.seed=int(seed)
        model.p=np.asarray(snapshot['cached_p'],dtype=float);model.fitted_observations=snapshot['fitted_observations'];model.last_fit_cpu=snapshot['last_fit_cpu']
        if kind=='neighbor':model.similarity=similarity;model.neighbors=neighbors
        value.model=model;value.similarity=similarity;value.neighbors=neighbors
        value.observed={int(k):int(v) for k,v in snapshot['observed'].items()}
        value.deliveries=int(snapshot['deliveries']);value.hits=int(snapshot['hits'])
        value.errors=list(snapshot['errors']);value.logloss=list(snapshot['logloss']);value.trace=copy.deepcopy(snapshot['trace'])
        value.costs=dict(snapshot['costs']);value.operation_counts=dict(snapshot['operation_counts'])
        value.interruptions=0;value.feasibility_fallbacks=0;value.initial_fit_count=snapshot['initial_fit_count'];value.weights=np.zeros(3)
        value.rng=np.random.default_rng();value.rng.bit_generator.state=copy.deepcopy(snapshot['rng_state'])
        return value


def run(state,oracle,clock,policy,parameter=None,gate=None,forced=None,restricted=(),snapshots=False):
    saved={}
    previous_handler=signal.getsignal(signal.SIGPROF)
    def interrupt(signum,frame):raise ComputeInterrupt('SCIENTIFIC_CPU_LIMIT')
    signal.signal(signal.SIGPROF,interrupt)
    try:
        if not state.observed:state.observed=oracle.initial(state.initial_indices())
        if state.deliveries==0:state.initialize_model(clock)
        if snapshots:saved[0]=state.snapshot(clock)
        while state.deliveries<state.budget and state.eligible() and clock.enough():
            credit=None
            step_policy=('R' if state.rng.random()<.5 else 'G1') if policy=='MIX' else policy
            if state.cold():
                forced=None
                requested=actual='COLD_UNIFORM';chosen=min(state.eligible(),key=lambda i:int(state.tie[i]))
            else:
                if not state.initialize_model(clock):
                    if not clock.enough(state.costs['REUSE']):break
                    forced=None
                    requested=actual='NO_MODEL_UNIFORM';chosen=min(state.eligible(),key=lambda i:int(state.tie[i]))
                else:
                    chosen_policy=forced if forced is not None else step_policy
                    requested,credit=state.choose_operation(chosen_policy,clock,parameter,gate,restricted)
                    forced=None
                    if requested is None:break
                    chosen,actual=state.execute(requested,step_policy,clock)
                    if chosen is None:break
            if not clock.enough():break
            prediction=float(state.model.p[chosen]);label=oracle.query(chosen)
            state.accept(chosen,label,prediction,requested,actual,clock,credit)
            if snapshots and state.deliveries in(8,16,24):saved[state.deliveries]=state.snapshot(clock)
        return {'new_positives':state.hits,'new_deliveries':state.deliveries,'assigned_B':state.budget,
            'assigned_C':clock.cap,'scientific_cpu_seconds':clock.spent(),'cpu_guard_reserve_seconds':clock.margin,
            'cpu_violation':clock.spent()>clock.cap,'initial_observations':state.n0,
            'operations':state.operation_counts,'interruptions':state.interruptions,
            'feasibility_fallbacks':state.feasibility_fallbacks,'trace':state.trace},saved
    finally:clock.disarm();signal.signal(signal.SIGPROF,previous_handler)
