"""One resource-permitted costed M2 unit; private evaluator separated from policy state."""
import hashlib,json,sys,time
from pathlib import Path
from research.m2_costed_v2.guard import CostedGuard,new


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def seed_for(task,seed):return int.from_bytes(hashlib.sha256(f'm2:{task}:{seed}'.encode()).digest()[:4],'big')%2147483647


def fit_artifacts(root,a):
    from research.m2_costed_v2.learning import fit_gate,choose_controls
    manifest=root/a['matrix_path'];assert digest(manifest)==a['matrix_sha256']
    entries=json.loads(manifest.read_text())['entries'];components=a['components'];rows=[]
    if a['kind']=='gates':
        grouped={}
        for e in entries:
            if e['handler']!='branch':continue
            r=json.loads((root/'jobs'/e['job']/'result.json').read_text());assert r['status']in('PASS_CAMPAIGN','PASS_INFEASIBLE_PREFIX')
            key=(r['spec']['prefix_job'],r['spec']['snapshot'],r['spec']['regime'])
            grouped.setdefault(key,{})[r['spec']['forced']]=r
        for group in grouped.values():
            assert set(group)=={'REUSE','UPDATE','PLAN'}
            base=group['REUSE'];assert all(r['branch_features']==base['branch_features'] for r in group.values())
            rows.append({'component':base['component'],'task_id':base['task_id'],'predictor':base['spec']['predictor'],
              'eligible':all(r['branch_eligible'] for r in group.values()),'features':base['branch_features'],
              'benefits':[group[op]['new_positives']-base['new_positives'] for op in('UPDATE','PLAN')]})
        result={}
        for predictor in('rf','neighbor'):
            for heldout in components:
                result[predictor+':'+heldout+':full']=fit_gate(rows,heldout,predictor)
                if predictor=='rf':result[predictor+':'+heldout+':no_history']=fit_gate(rows,heldout,predictor,True)
        return {'status':'PASS_FROZEN_GATES','artifacts':result,'states':len(rows),
                'eligible_states':sum(r['eligible'] for r in rows),'heldout_outcomes_excluded':True}
    for e in entries:
        if e['handler']!='tuning':continue
        r=json.loads((root/'jobs'/e['job']/'result.json').read_text());assert r['status']=='PASS_CAMPAIGN'
        rows.append(dict(r,predictor=r['spec']['predictor'],family=r['spec']['policy'],configuration=r['spec']['configuration']))
    result={p+':'+g:choose_controls(rows,g,p) for p in('rf','neighbor') for g in components}
    return {'status':'PASS_FROZEN_CONTROLS','artifacts':result,'campaigns':len(rows),'heldout_outcomes_excluded':True}


def campaign(root,a):
    import numpy as np
    from research.m2_v1.models import dense_bits
    from research.m2_costed_v2.engine import Clock,State,Oracle,PublicPool,run
    from research.m2_costed_v2.learning import Gate
    # Libraries, authenticated file parsing and model deserialization are startup;
    # dense fingerprints, public graph, surrogate work and gate inference are charged C.
    source=root/a['input_path'];assert digest(source)==a['input_sha256']
    data=json.loads(source.read_text());assert data['task_id']==a['task_id'] and data['role']=='development'
    records=data['records']
    if a.get('training',False):
        keep=set(data['training_candidate_ids']);records=[r for r in records if r['candidate_id'] in keep]
    labels=np.asarray([int(r['active']) for r in records],dtype=np.int8)
    gate=Gate(a['gate']) if a.get('gate') else None
    seed=seed_for(a['task_id'],a['seed']);kind=a['predictor'];n0=a['n0'];b=a.get('budget',32)
    if a.get('prefix_job'):
        prefix=root/'jobs'/a['prefix_job'];snap=json.loads((prefix/'snapshots.json').read_text())[str(a['snapshot'])]
        with np.load(prefix/'public-cache.npz',allow_pickle=False) as archive:
            x=archive['x'];similarity=archive['similarity'];neighbors=archive['neighbors']
        pool=PublicPool(data['task_id'],data['component'],tuple(r['candidate_id'] for r in records),x)
        clock=Clock(a['cap'],snap['prefix_cpu_seconds'])
        state=State.restore(pool,kind,seed,n0,b,snap,similarity,neighbors)
        class FrozenClock:
            cap=float(a['cap'])
            def remaining(self):return max(0,self.cap-snap['prefix_cpu_seconds'])
        branch_features=state.features(FrozenClock()).tolist()
    else:
        clock=Clock(a['cap']);x=dense_bits(records)
        pool=PublicPool(data['task_id'],data['component'],tuple(r['candidate_id'] for r in records),x)
        state=State(pool,kind,seed,n0,b,a['cost_priors']);branch_features=None
    oracle=Oracle(labels,b)
    ineligible=a.get('prefix_job') and snap['prefix_cpu_seconds']>=a['cap']-clock.margin
    if ineligible:
        result={'new_positives':state.hits,'new_deliveries':state.deliveries,'assigned_B':b,'assigned_C':clock.cap,
          'scientific_cpu_seconds':snap['prefix_cpu_seconds'],'cpu_guard_reserve_seconds':clock.margin,
          'cpu_violation':False,'initial_observations':n0,'operations':state.operation_counts,
          'interruptions':0,'feasibility_fallbacks':0,'trace':state.trace,'continuation_invoked':False}
        snapshots={}
    else:
        result,snapshots=run(state,oracle,clock,a['policy'],parameter=a.get('parameter'),gate=gate,
            forced=a.get('forced'),restricted=tuple(a.get('restricted',[])),snapshots=a.get('save_snapshots',False))
    result.update(status='PASS_CAMPAIGN' if not result['cpu_violation'] else 'FAIL_SCIENTIFIC_CPU',spec=a,
                  component=data['component'],task_id=data['task_id'],branch_features=branch_features,
                  prefix_cpu_seconds=snap['prefix_cpu_seconds'] if a.get('prefix_job') else 0.)
    if ineligible:result['status']='PASS_INFEASIBLE_PREFIX'
    if a.get('prefix_job'):
        result['branch_eligible']=result['prefix_cpu_seconds']<a['cap']-clock.margin and a['snapshot']<b
        result['ineligible_reason']=None if result['branch_eligible'] else 'PREFIX_CPU_ALREADY_EXHAUSTED'
    return result,snapshots,state


def main():
    permit=json.loads(Path(sys.argv[1]).read_text());root=Path(permit['task_root']);job=root/'jobs'/permit['attempt']
    assert root==Path.home()/'curaloop-tasks/m2-costed-20261108-v2'
    guard=CostedGuard(job/'resource.json',permit)
    try:
        new(job/'kernel-proof.json',guard.kernel_proof())
        code=root/permit['code_directory']
        for name,expected in permit['code_pins'].items():assert digest(code/name)==expected
        # Eager imports are charged to whole-process startup, never hidden in an arm.
        import numpy as np
        import sklearn.ensemble,sklearn.linear_model
        from threadpoolctl import threadpool_limits,threadpool_info
        threadpool_limits(limits=1);assert all(p['num_threads']==1 for p in threadpool_info())
        handler=permit['handler']
        if handler=='synthetic_checks':
            from research.m2_costed_v2.checks import checks
            result=checks()
        elif handler=='gate_fit':
            assert permit['development_admission']=='PASS' and permit['final_outcomes_opened'] is False
            result=fit_artifacts(root,permit['arguments'])
        elif handler in('prefix','branch','tuning','main','ablation','transfer'):
            assert permit['development_admission']=='PASS' and permit['final_outcomes_opened'] is False
            result,snapshots,state=campaign(root,permit['arguments'])
            if handler=='prefix':
                assert set(snapshots)=={0,8,16,24},'INCOMPLETE_PREFIX_SUPPORT'
                new(job/'snapshots.json',snapshots)
                np.savez_compressed(job/'public-cache.npz',x=state.pool.x,similarity=state.similarity,neighbors=state.neighbors)
            new(job/'trace-private.json',result.pop('trace'))
        else:raise ValueError('UNKNOWN_HANDLER')
        new(job/'result.json',result)
        guard.finish('PASS' if result['status'].startswith('PASS') else 'FAIL_ADMISSION')
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:500]});guard.finish('FAIL');raise


if __name__=='__main__':main()
