"""Frozen predictor adapters and matched full-budget one-step planning."""
from dataclasses import dataclass
import hashlib
import time

import numpy as np


def seeded_order(ids, seed):
    return np.array(sorted(range(len(ids)), key=lambda i: hashlib.sha256(
        (str(seed)+':'+ids[i]).encode()).digest()), dtype=int)


def ranked(scores, eligible, order):
    return sorted(eligible, key=lambda i: (-float(scores[i]), int(order[i])))


def dense_bits(records):
    x = np.zeros((len(records),1024), dtype=np.uint8)
    for i,r in enumerate(records):
        x[i,r['morgan_on_bits']] = 1
    return x


@dataclass
class Predictor:
    kind: str
    x: np.ndarray
    seed: int

    def __post_init__(self):
        assert self.kind in ('rf','neighbor') and self.x.ndim == 2
        self.p = np.full(len(self.x),0.5)
        self.fitted_observations = -1
        self.last_fit_cpu = 0.0
        if self.kind == 'neighbor':
            dense = self.x.astype(np.float32)
            intersection = dense @ dense.T
            counts = dense.sum(axis=1)
            union = counts[:,None]+counts[None,:]-intersection
            self.similarity = np.divide(intersection,union,out=np.zeros_like(union),where=union>0)
            np.fill_diagonal(self.similarity,0)
            # Stable input-order tie break is public and shared by every policy.
            graph_scores=self.similarity.copy()
            np.fill_diagonal(graph_scores,-1)
            self.neighbors = np.argsort(-graph_scores,axis=1,kind='stable')[:,:min(16,len(self.x)-1)]

    def probabilities(self, observed):
        if not observed:
            return np.full(len(self.x),0.5)
        if self.kind == 'rf':
            labels = [observed[i] for i in sorted(observed)]
            if len(set(labels)) < 2:
                return np.full(len(self.x),0.5)
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=64,max_depth=6,min_samples_leaf=2,
                max_features='sqrt',bootstrap=True,class_weight=None,n_jobs=1,random_state=self.seed)
            model.fit(self.x[sorted(observed)], labels)
            return model.predict_proba(self.x)[:,list(model.classes_).index(1)]
        labels = np.zeros(len(self.x),dtype=float)
        known = np.zeros(len(self.x),dtype=float)
        for i,y in observed.items(): labels[i]=y; known[i]=1
        weights = np.take_along_axis(self.similarity,self.neighbors,axis=1)
        return (1+(weights*labels[self.neighbors]).sum(axis=1))/(2+(weights*known[self.neighbors]).sum(axis=1))

    def update(self, observed):
        start=time.process_time()
        self.p=self.probabilities(observed)
        self.fitted_observations=len(observed)
        self.last_fit_cpu=time.process_time()-start

    def plan(self, observed, remaining, tie_order):
        eligible=[i for i in range(len(self.x)) if i not in observed]
        assert remaining > 0 and eligible
        cheap=ranked(self.p,eligible,tie_order)
        if remaining == 1: return cheap[0]
        if self.kind == 'rf':
            uncertain=ranked(self.p*(1-self.p),eligible,tie_order)
            shortlist=list(dict.fromkeys(cheap[:4]+uncertain[:4]))
            for i in cheap:
                if len(shortlist)>=min(8,len(eligible)): break
                if i not in shortlist:shortlist.append(i)
        else:
            shortlist=cheap
        scores={}
        for i in shortlist:
            other=[j for j in eligible if j != i]
            count=min(remaining-1,len(other))
            branch=[]
            for outcome in (0,1):
                hypothetical=dict(observed); hypothetical[i]=outcome
                p=self.probabilities(hypothetical)[other]
                tail=float(np.partition(p,len(p)-count)[-count:].sum()) if count else 0.0
                branch.append(tail+outcome)
            scores[i]=(1-self.p[i])*branch[0]+self.p[i]*branch[1]
        return min(shortlist,key=lambda i:(-scores[i],int(tie_order[i])))


def synthetic_pool(n, repeat):
    """Constructed bit features and labels; no biological records or outcomes."""
    rng=np.random.default_rng(910000+n*13+repeat)
    x=np.zeros((n,1024),dtype=np.uint8)
    for row in x: row[rng.choice(1024,48,replace=False)]=1
    # A declared synthetic nonconstant objective, never molecular supervision.
    y=((x[:,:32].sum(axis=1)+rng.integers(0,4,size=n))>=3).astype(int)
    return x,y,[f'synthetic-{n}-{repeat}-{i}' for i in range(n)]
