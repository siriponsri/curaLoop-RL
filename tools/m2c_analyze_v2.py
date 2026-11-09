"""Reconcile the complete fixed cohort and report conditional paired evidence."""
import collections,csv,hashlib,itertools,json,math,random,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.m2_costed_v2.guard import CostedGuard,new
TASK=ROOT/'.local/m2-costed-20261108-v2';PUBLIC=ROOT/'docs/evidence/m2-costed-20261108-v2'
SEEDS=[1009,2027,3041,4051,5059];ARMS=['R','G1','Gk','U','P','T','E','L']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def avg(values):return statistics.mean(list(values))
def quantile(values,p):
    v=sorted(values);a=(len(v)-1)*p;i=math.floor(a);return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(a-i)


def balanced(rows,field):
    groups=sorted({r['component'] for r in rows});result={}
    for g in groups:
        tasks=sorted({r['task_id'] for r in rows if r['component']==g})
        per_task=[[r[field] for r in rows if r['task_id']==t and r[field]is not None] for t in tasks]
        result[g]=avg(avg(v) for v in per_task) if all(per_task) else None
    return (avg(result.values()) if all(v is not None for v in result.values()) else None),result


def contrast(rows,left,right,seeds):
    lookup={(r['task_id'],r['spec']['n0'],r['spec']['seed'],r['arm']):r for r in rows}
    assert len(lookup)==len(rows),'DUPLICATE_PAIRED_CONTEXT'
    tasks=sorted({r['task_id'] for r in rows});groups=sorted({r['component'] for r in rows})
    components={t:next(r['component'] for r in rows if r['task_id']==t) for t in tasks}
    vectors=[];group_vectors={g:[] for g in groups}
    for seed in seeds:
        delta={t:avg(lookup[t,n0,seed,left]['new_positives']-lookup[t,n0,seed,right]['new_positives'] for n0 in(0,16)) for t in tasks}
        v={g:avg(delta[t] for t in tasks if components[t]==g) for g in groups}
        vectors.append(avg(v.values()))
        for g in groups:group_vectors[g].append(v[g])
    rng=random.Random(20261108);boot=[avg(vectors[rng.randrange(len(seeds))] for _ in seeds) for _ in range(10000)]
    effects={g:avg(v) for g,v in group_vectors.items()}
    return {'contrast':left+'-'+right,'mean_delta_new_positives':avg(vectors),'component_effects':effects,
      'positive_components':sum(v>0 for v in effects.values()),'component_range':[min(effects.values()),max(effects.values())],
      'conditional_seed_interval_95':[quantile(boot,.025),quantile(boot,.975)],'shared_seed_effect_vector':vectors,
      'interval_scope':'10,000 joint seed-index bootstrap resamples; conditional on this fixed four-component exposed cohort'}


def main():
    permit=json.loads(Path(sys.argv[1]).read_text());job=TASK/'jobs'/permit['attempt'];guard=CostedGuard(job/'resource.json',permit)
    try:
        for stage in('prefix','branch','tuning','main','ablation','transfer'):
            assert json.loads((TASK/(stage+'-summary.json')).read_text())['status']=='PASS_COMPLETE_STAGE'
        returned=json.loads((TASK/'remote-return/verified-v1.json').read_text());assert returned['status']=='PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD'
        matrix=json.loads((TASK/'execution-matrix-v1.json').read_text());projection=json.loads((TASK/'development-projection-manifest.json').read_text())
        frozen=json.loads((TASK/'main-execution-freeze.json').read_text())
        assert sha(TASK/'execution-matrix-v1.json')==frozen['matrix_sha256'],'EXECUTION_MATRIX_CHANGED_AFTER_FREEZE'
        assert sha(TASK/'code-stage-03.json')==frozen['code_stage']
        assert sha(TASK/'jobs/fit-gates/result.json')==frozen['gates_sha256']
        assert sha(TASK/'jobs/fit-controls/result.json')==frozen['controls_sha256']
        assert len({e['job'] for e in matrix['entries']})==len(matrix['entries'])==4164
        assert len(frozen['jobs'])==len(set(frozen['jobs']))==2100
        assert all(sha(TASK/'specs'/(name+'.json'))==expected for name,expected in frozen['spec_pins'].items())
        assert matrix['counts']=={'prefix':48,'branch':1152,'tuning':576,'main':1920,'ablation':180,'transfer':288}
        gate_artifacts=json.loads((TASK/'jobs/fit-gates/result.json').read_text())
        control_artifacts=json.loads((TASK/'jobs/fit-controls/result.json').read_text())['artifacts']
        resolution=json.loads((TASK/'execution-retry-resolution-v1.json').read_text())['mapping'] if (TASK/'execution-retry-resolution-v1.json').exists() else {}
        files=TASK/'remote-return/files';rows=[];counts=collections.Counter();audit=collections.Counter();overheads=[];branches=collections.defaultdict(dict)
        originals={}
        for f in projection['files']:
            path=TASK/f['path'];assert sha(path)==f['sha256']
            originals[f['task_id']]=json.loads(path.read_text())
        for e in matrix['entries']:
            actual_job=resolution.get(e['job'],e['job'])
            local=TASK/'jobs'/actual_job;r=json.loads((local/'result.json').read_text());resource=json.loads((local/'resource.json').read_text())
            assert r['status'].startswith('PASS') and resource['status']=='PASS'
            assert sha(local/'result.json')==sha(files/'jobs'/actual_job/'result.json')
            assert not r['cpu_violation'];counts[e['handler']]+=1
            args=r['spec'];source=originals[r['task_id']];records=source['records']
            assert args['training']==(e['handler']in('prefix','branch','tuning'))
            if args['policy']=='L':
                variant='no_history' if args.get('variant')=='no_history' else 'full'
                assert args['gate']==gate_artifacts['artifacts'][args['predictor']+':'+r['component']+':'+variant]
                assert args['gate']['heldout_component']==r['component']
            if args['policy']in('Gk','T') and e['handler']!='tuning':
                index=control_artifacts[args['predictor']+':'+r['component']][args['policy']]['selected_configuration']
                expected=([2,4,8] if args['policy']=='Gk' else [[2,.02],[4,.05],[8,.10]])[index]
                assert args['parameter']==expected
            if args['training']:records=[v for v in records if v['candidate_id'] in set(source['training_candidate_ids'])]
            assert all(args[k]==v for k,v in e['arguments'].items()),'FROZEN_UNIT_ARGUMENT_CHANGED'
            trace=json.loads((files/'jobs'/actual_job/'trace-private.json').read_text())
            assert len(trace)==r['new_deliveries']<=args['budget']
            assert r['new_positives']==sum(t['delivered_label'] for t in trace)
            assert len({t['candidate_index'] for t in trace})==len(trace)
            for t in trace:
                assert int(records[t['candidate_index']]['active'])==t['delivered_label']
                if r['status']!='PASS_INFEASIBLE_PREFIX':assert t['scientific_cpu_seconds']<=args['cap']
                assert t['requested_operation']not in args.get('restricted',[])
            if e['handler']!='branch' or r['branch_eligible']:assert r['scientific_cpu_seconds']<=args['cap']
            if e['handler']=='branch' and not r['branch_eligible']:
                assert r['status']=='PASS_INFEASIBLE_PREFIX' and r['continuation_invoked']is False;audit['infeasible_branches']+=1
            if e['handler']=='branch':branches[(args['prefix_job'],args['snapshot'],args['regime'])][args['forced']]=r
            assert resource['cpu_affinity']==[e['cpu']] and resource['memory_limit_bytes']==4294967296
            assert resource['cpu_seconds']<=resource['reservation_seconds'];audit['verified_units']+=1
            incremental=r['scientific_cpu_seconds']-r.get('prefix_cpu_seconds',0)
            overhead=resource['cpu_seconds']-max(0,incremental)
            assert 0<=overhead<=5.,'STARTUP_REPORTING_ALLOWANCE_EXCEEDED'
            overheads.append(overhead)
            if e['handler']in('main','ablation','transfer'):
                arm=args.get('variant',args['policy']);r['arm']=arm;r['handler']=e['handler']
                r['total_observed']=r['initial_observations']+r['new_deliveries']
                r['whole_process_cpu_seconds']=resource['cpu_seconds'];r['whole_process_wall_seconds']=resource['wall_seconds']
                cumulative=[0];h=0
                for t in trace:h+=t['delivered_label'];cumulative.append(h)
                cumulative.extend([h]*(args['budget']+1-len(cumulative)))
                r['discovery_curve']=cumulative
                r['auc_discovery_over_assigned_B']=sum(cumulative[1:])/args['budget']
                r['H_over_B']=r['new_positives']/args['budget']
                r['brier_delivered']=avg((t['prequential_prediction']-t['delivered_label'])**2 for t in trace) if trace else None
                r['logloss_delivered']=avg(-(t['delivered_label']*math.log(min(1-1e-6,max(1e-6,t['prequential_prediction'])))+
                  (1-t['delivered_label'])*math.log(1-min(1-1e-6,max(1e-6,t['prequential_prediction'])))) for t in trace) if trace else None
                rows.append(r)
        assert dict(counts)==matrix['counts']
        target_values=collections.defaultdict(list)
        for group in branches.values():
            assert set(group)=={'REUSE','UPDATE','PLAN'}
            base=group['REUSE']
            if all(r['branch_eligible'] for r in group.values()):
                for operation in('UPDATE','PLAN'):
                    target_values[(base['spec']['predictor'],base['spec']['regime'],operation)].append(group[operation]['new_positives']-base['new_positives'])
        target_summary=[{'predictor':key[0],'regime':key[1],'forced_operation':key[2],'states':len(v),
          'positive':sum(x>0 for x in v),'zero':sum(x==0 for x in v),'negative':sum(x<0 for x in v),
          'mean_terminal_hit_difference':avg(v),'range':[min(v),max(v)]} for key,v in sorted(target_values.items())]
        # Confirm all paired contexts have one physical initial CPU slot.
        cores=collections.defaultdict(set)
        for e in matrix['entries']:
            if e['handler']in('main','ablation','transfer'):
                a=e['arguments'];cores[(a['predictor'],a['task_id'],a['n0'],a['budget'],a['regime'],a['seed'])].add(e['cpu'])
        assert all(len(v)==1 for v in cores.values())
        artifacts=json.loads((TASK/'jobs/fit-gates/result.json').read_text())
        for artifact in artifacts['artifacts'].values():
            assert artifact['heldout_component']not in artifact['training_components'] and len(artifact['training_components'])==3
            heldout_tasks={f['task_id'] for f in projection['files'] if f['component']==artifact['heldout_component']}
            assert not heldout_tasks.intersection(artifact['training_tasks'])
        import numpy as np
        bootstrap_rng=random.Random(20261108)
        bootstrap_indices=np.asarray([[bootstrap_rng.randrange(5) for _ in SEEDS] for _ in range(10000)],dtype=int)
        summaries=[];contrasts=[];curves=[]
        for predictor,regime in itertools.product(('rf','neighbor'),('cheap','high')):
            sub=[r for r in rows if r['handler']=='main' and r['spec']['predictor']==predictor and r['spec']['regime']==regime]
            for arm in ARMS:
                selected=[r for r in sub if r['arm']==arm];stats={}
                for field in('new_positives','new_deliveries','total_observed','scientific_cpu_seconds','whole_process_cpu_seconds','whole_process_wall_seconds','H_over_B','auc_discovery_over_assigned_B','brier_delivered','logloss_delivered'):
                    stats[field]=balanced(selected,field)[0]
                stats.update(predictor=predictor,regime=regime,arm=arm,campaigns=len(selected),
                  interrupted_campaigns=sum(r['interruptions']>0 for r in selected),
                  full_B_campaigns=sum(r['new_deliveries']==r['assigned_B'] for r in selected),
                  operation_counts={op:sum(r['operations'][op] for r in selected) for op in('REUSE','UPDATE','PLAN')},
                  fallbacks=sum(r['feasibility_fallbacks'] for r in selected))
                summaries.append(stats)
                seed_curves=[]
                for seed in SEEDS:
                    seed_rows=[v for v in selected if v['spec']['seed']==seed]
                    seed_curves.append([balanced([dict(v,value=v['discovery_curve'][k]) for v in seed_rows],'value')[0] for k in range(33)])
                array=np.asarray(seed_curves,dtype=float);boot=array[bootstrap_indices].mean(axis=1)
                limits=np.quantile(boot,[.025,.975],axis=0,method='linear');mean=array.mean(axis=0)
                assert abs(mean[-1]-stats['new_positives'])<1e-12
                curves.append({'predictor':predictor,'regime':regime,'arm':arm,'assigned_B':32,
                  'query_budget':list(range(33)),'mean_new_positives':mean.tolist(),
                  'conditional_seed_lower_95':limits[0].tolist(),'conditional_seed_upper_95':limits[1].tolist(),
                  'shared_seed_vectors':array.tolist(),'uncertainty_scope':'same 10,000 joint seed-index bootstrap; fixed cohort'})
            for baseline in('G1','T','E'):contrasts.append(dict(contrast(sub,'L',baseline,SEEDS),predictor=predictor,regime=regime))
        frontier=[]
        for predictor in('rf','neighbor'):
            points=[r for r in summaries if r['predictor']==predictor]
            for point in points:
                dominated=any(other['scientific_cpu_seconds']<=point['scientific_cpu_seconds'] and other['new_positives']>=point['new_positives'] and
                  (other['scientific_cpu_seconds']<point['scientific_cpu_seconds'] or other['new_positives']>point['new_positives']) for other in points)
                frontier.append({'predictor':predictor,'regime':point['regime'],'arm':point['arm'],
                  'scientific_cpu_seconds':point['scientific_cpu_seconds'],'new_positives':point['new_positives'],'nondominated_mean_point':not dominated})
        primary=[r for r in rows if r['handler']=='main' and r['spec']['predictor']=='rf' and r['spec']['regime']=='cheap']
        ablations=[r for r in rows if r['handler']=='ablation'];ablation_contrasts=[contrast(primary+ablations,'L',arm,SEEDS) for arm in('no_history','no_UPDATE','no_PLAN')]
        transfer=[]
        for regime in('cheap','high'):
            sub=[r for r in rows if r['handler']=='transfer' and r['spec']['regime']==regime]
            for baseline in('G1','T','E'):transfer.append(dict(contrast(sub,'L',baseline,SEEDS[:3]),predictor='rf',regime=regime,B=16))
        p=[v for v in contrasts if v['predictor']=='rf' and v['regime']=='cheap'];history=ablation_contrasts[0]
        potential=all(v['mean_delta_new_positives']>0 for v in p) and p[0]['positive_components']>=3 and history['mean_delta_new_positives']>0
        # Do not invent a practical-effect or confirmatory significance threshold.
        decision='PROMISING_DEVELOPMENT_SIGNAL' if potential else 'INCONCLUSIVE'
        if all(v['mean_delta_new_positives']<=0 for v in contrasts) and history['mean_delta_new_positives']<=0:decision='NOT_SUPPORTED_IN_THIS_STUDY'
        paired={(r['task_id'],r['spec']['n0'],r['spec']['seed'],r['arm']):r for r in primary}
        contexts=sorted({k[:3] for k in paired})
        exact_equal=all(paired[c+('L',)]['new_positives']==paired[c+(arm,)]['new_positives'] for c in contexts for arm in('G1','T','E'))
        cheaper=all(balanced([r for r in primary if r['arm']=='L'],'scientific_cpu_seconds')[0]<
          balanced([r for r in primary if r['arm']==arm],'scientific_cpu_seconds')[0] for arm in('G1','T','E'))
        if not potential and exact_equal and cheaper:decision='EFFICIENCY_SIGNAL_ONLY'
        ledger=json.loads((TASK/'ledger.json').read_text())
        training_names={resolution.get(e['job'],e['job']) for e in matrix['entries'] if e['handler']in('prefix','branch','tuning')}|{'fit-gates','fit-controls'}
        training_cpu=sum(j.get('reported_cpu_seconds',0) for j in ledger['jobs'] if j['job']in training_names)
        retry_training_names={resolution[e['job']] for e in matrix['entries'] if e['handler']in('prefix','branch','tuning') and e['job']in resolution}
        retry_training_charge=sum(j['reservation_seconds'] for j in ledger['jobs'] if j['job']in retry_training_names)
        result={'schema':'curaloop.m2_costed.aggregate_results.v2','status':'COMPLETE_MATRIX_AWAITING_CLEANUP_AND_DELIVERY',
          'method_decision':decision,'technical_matrix_audit':'PASS','counts':dict(counts),'audit':dict(audit),
          'six_development_assays':6,'annotation_components':4,'task_rows':1285,'source_role':'exposed development',
          'primary_endpoint':'new FS-Mol assay-relative binary positives at assigned B32/Ccheap; initial positives excluded',
          'main_summaries':summaries,'discovery_curves':curves,'paired_contrasts':contrasts,'rf_ablation_contrasts':ablation_contrasts,'rf_B16_transfer_contrasts':transfer,
          'descriptive_compute_discovery_frontier':frontier,
          'secondary_metric_definitions':{'auc_discovery_over_assigned_B':'sum H(k) for k=1..B divided by assigned B; count units; carry last count after CPU stop',
            'prequential_errors':'campaign-mean errors on delivered labels, then same component balancing; selected observations, not pool calibration; probabilities clipped at 1e-6 for log loss',
            'whole_process_times':'process CPU/wall include startup/reporting; exclude pre-dispatch queue waiting; project elapsed separately recorded in release/close timestamps'},
          'frontier_scope':'descriptive nondominance of the 16 mean CPU/H operating points per predictor; not statistical dominance or a population frontier',
          'training_state_support':{'states':artifacts['states'],'eligible_states':artifacts['eligible_states'],'gate_artifacts':len(artifacts['artifacts'])},
          'descriptive_training_target_distribution':target_summary,
          'whole_process_minus_incremental_science_cpu_range_seconds':[min(overheads),max(overheads)],
          'offline_training_and_tuning_verified_worker_cpu_seconds':training_cpu,
          'offline_training_and_tuning_charged_stage_seconds':sum(ledger['bucket_reserved_seconds'][b] for b in('training_prefixes_branches_gate','control_tuning'))+retry_training_charge,
          'offline_training_and_tuning_retry_charge_seconds':retry_training_charge,
          'offline_worker_cpu_amortization_lower_bound_seconds_per_campaign':{str(n):training_cpu/n for n in(1,10,100)},
          'offline_cost_scope':'verified worker CPU includes startup; shared orchestration/setup/return overhead is additional and included in project reservation accounting',
          'final_outcomes_opened':False,'automatic_m3':False,'publication_ready':False,
          'limitations':['Four dependent annotation components; not biological-family population inference.',
            'Previously exposed development cohort; no independent final evidence.',
            'Balanced assay-relative labels do not represent HTS prevalence, clinical benefit or lab savings.',
            'CPU-specific calibrated regimes; selection-biased delivered-observation diagnostics.',
            'Correlated training branches and five seed vectors do not add independent biological replication.']}
        new(PUBLIC/'aggregate-results-v1.json',result)
        with (PUBLIC/'discovery-curves-v1.csv').open('x',encoding='utf-8',newline='') as f:
            writer=csv.writer(f,lineterminator='\n');writer.writerow(['predictor','regime','arm','assigned_query_budget','mean_new_positives','conditional_seed_lower_95','conditional_seed_upper_95'])
            for curve in curves:
                for k in range(33):writer.writerow([curve['predictor'],curve['regime'],curve['arm'],k,curve['mean_new_positives'][k],curve['conditional_seed_lower_95'][k],curve['conditional_seed_upper_95'][k]])
        with (PUBLIC/'main-summary-v1.csv').open('x',encoding='utf-8',newline='') as f:
            fields=['predictor','regime','arm','campaigns','new_positives','new_deliveries','total_observed','scientific_cpu_seconds','whole_process_cpu_seconds','whole_process_wall_seconds',
              'H_over_B','auc_discovery_over_assigned_B','brier_delivered','logloss_delivered','interrupted_campaigns','full_B_campaigns','fallbacks']
            writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');writer.writeheader();writer.writerows(summaries)
        new(job/'result.json',{'status':'PASS_COMPLETE_MATRIX_ANALYSIS','method_decision':decision,'verified_units':audit['verified_units'],'aggregate_curve_series':len(curves)})
        guard.finish('PASS');print(json.dumps({'status':'PASS_COMPLETE_MATRIX_ANALYSIS','decision':decision,'primary_contrasts':p,'history':history}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:300]});guard.finish('FAIL');raise


if __name__=='__main__':main()
