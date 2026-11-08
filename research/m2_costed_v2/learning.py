"""Grouped, outcome-supervised operation regressors and training-only controls."""
import numpy as np
from research.m2_costed_v2.engine import FEATURE_NAMES,NO_HISTORY_KEEP


class Gate:
    def __init__(self,artifact):
        self.artifact=artifact;self.mean=np.asarray(artifact['mean']);self.scale=np.asarray(artifact['scale'])
        self.coef=np.asarray(artifact['coefficients']);self.intercept=np.asarray(artifact['intercepts'])
        self.keep=np.asarray(artifact['feature_indices'],dtype=int)

    def predict(self,features):
        value=(np.asarray(features)[self.keep]-self.mean)/self.scale
        return self.coef@value+self.intercept


def fit_gate(rows,heldout,kind,no_history=False):
    from sklearn.linear_model import Ridge
    selected=[r for r in rows if r['component']!=heldout and r['predictor']==kind and r['eligible']]
    if len(selected)<3:raise ValueError('INSUFFICIENT_TRAINING_STATE_SUPPORT')
    groups=sorted({r['component'] for r in selected});assert heldout not in groups and len(groups)==3
    keep=list(NO_HISTORY_KEEP) if no_history else list(range(len(FEATURE_NAMES)))
    x=np.asarray([r['features'] for r in selected],dtype=float)[:,keep]
    y=np.asarray([r['benefits'] for r in selected],dtype=float)
    counts={g:sum(r['component']==g for r in selected) for g in groups}
    weights=np.asarray([1/counts[r['component']] for r in selected]);weights*=len(weights)/weights.sum()
    mean=np.average(x,axis=0,weights=weights);variance=np.average((x-mean)**2,axis=0,weights=weights)
    scale=np.sqrt(variance);scale=np.where(scale<1e-12,1.0,scale);z=(x-mean)/scale
    coefficients=[];intercepts=[]
    for column in range(2):
        reg=Ridge(alpha=1.0,fit_intercept=True);reg.fit(z,y[:,column],sample_weight=weights)
        coefficients.append(reg.coef_.tolist());intercepts.append(float(reg.intercept_))
    return {'schema':'curaloop.m2_costed.gate.v2','predictor':kind,'heldout_component':heldout,
        'variant':'no_history' if no_history else 'full','alpha':1.0,'feature_names':list(FEATURE_NAMES),
        'feature_indices':keep,'mean':mean.tolist(),'scale':scale.tolist(),
        'coefficients':coefficients,'intercepts':intercepts,'training_components':groups,
        'training_tasks':sorted({r['task_id'] for r in selected}),'training_states':len(selected),
        'training_state_counts':counts,'training_weighting':'equal component totals; mean weight one',
        'target':'realized forced-operation terminal hits minus REUSE, with common G1 continuation',
        'scaler_and_targets_exclude_heldout':True}


def choose_controls(rows,heldout,kind):
    selected=[r for r in rows if r['component']!=heldout and r['predictor']==kind]
    groups=sorted({r['component'] for r in selected});assert len(groups)==3 and heldout not in groups
    result={}
    for family in('Gk','T'):
        configs=sorted({r['configuration'] for r in selected if r['family']==family})
        assert len(configs)==3
        values=[]
        for index in configs:
            candidates=[r for r in selected if r['family']==family and r['configuration']==index]
            group_scores=[];group_cpu=[]
            for group in groups:
                assays=sorted({r['task_id'] for r in candidates if r['component']==group})
                group_scores.append(np.mean([np.mean([r['new_positives']/32 for r in candidates if r['task_id']==task]) for task in assays]))
                group_cpu.append(np.mean([np.mean([r['scientific_cpu_seconds'] for r in candidates if r['task_id']==task]) for task in assays]))
            values.append({'configuration':index,'mean_H_over_B':float(np.mean(group_scores)),
                           'mean_scientific_cpu_seconds':float(np.mean(group_cpu))})
        best=max(v['mean_H_over_B'] for v in values)
        tied=[v for v in values if abs(v['mean_H_over_B']-best)<1e-12]
        chosen=min(tied,key=lambda v:(v['mean_scientific_cpu_seconds'],v['configuration']))
        result[family]={'selected_configuration':chosen['configuration'],'training_comparisons':values,
                        'training_components':groups,'heldout_component':heldout,'predictor':kind}
    return result
