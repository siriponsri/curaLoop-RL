"""Reconcile the complete fixed cohort and report conditional paired evidence."""
import collections,hashlib,itertools,json,math,random,statistics,sys
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
        files=TASK/'remote-return/files';rows=[];counts=collections.Counter();audit=collections.Counter();trace_metrics={}
        originals={}
        for f in projection['files']:
            path=TASK/f['path'];assert sha(path)==f['sha256']
            originals[f['task_id']]=json.loads(path.read_text())
        for e in matrix['entries']:
            local=TASK/'jobs'/e['job'];r=json.loads((local/'result.json').read_text());resource=json.loads((local/'resource.json').read_text())
            assert r['status'].startswith('PASS') and resource['status']=='PASS'
            assert sha(local/'result.json')==sha(files/'jobs'/e['job']/'result.json')
            assert not r['cpu_violation'];counts[e['handler']]+=1
            args=r['spec'];source=originals[r['task_id']];records=source['records']
            if args['training']:records=[v for v in records if v['candidate_id'] in set(source['training_candidate_ids'])]
            trace=json.loads((files/'jobs'/e['job']/'trace-private.json').read_text())
            assert len(trace)==r['new_deliveries']<=args['budget']
            assert r['new_positives']==sum(t['delivered_label'] for t in trace)
            assert len({t['candidate_index'] for t in trace})==len(trace)
            for t in trace:
                assert int(records[t['candidate_index']]['active'])==t['delivered_label']
                if r['status']!='PASS_INFEASIBLE_PREFIX':assert t['scientific_cpu_seconds']<=args['cap']
            if e['handler']!='branch' or r['branch_eligible']:assert r['scientific_cpu_seconds']<=args['cap']
            if e['handler']=='branch' and not r['branch_eligible']:
                assert r['status']=='PASS_INFEASIBLE_PREFIX' and r['continuation_invoked']is False;audit['infeasible_branches']+=1
            assert resource['cpu_affinity']==[e['cpu']] and resource['memory_limit_bytes']==4294967296
            assert resource['cpu_seconds']<=resource['reservation_seconds'];audit['verified_units']+=1
            if e['handler']in('main','ablation','transfer'):
                arm=args.get('variant',args['policy']);r['arm']=arm;r['handler']=e['handler']
                cumulative=[0];h=0
                for t in trace:h+=t['delivered_label'];cumulative.append(h)
                cumulative.extend([h]*(args['budget']+1-len(cumulative)))
                r['auc_discovery_over_assigned_B']=sum(cumulative[1:])/args['budget']
                r['H_over_B']=r['new_positives']/args['budget']
                r['brier_delivered']=avg((t['prequential_prediction']-t['delivered_label'])**2 for t in trace) if trace else None
                rows.append(r)
        assert dict(counts)==matrix['counts']
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
        summaries=[];contrasts=[]
        for predictor,regime in itertools.product(('rf','neighbor'),('cheap','high')):
            sub=[r for r in rows if r['handler']=='main' and r['spec']['predictor']==predictor and r['spec']['regime']==regime]
            for arm in ARMS:
                selected=[r for r in sub if r['arm']==arm];stats={}
                for field in('new_positives','new_deliveries','scientific_cpu_seconds','H_over_B','auc_discovery_over_assigned_B','brier_delivered'):
                    stats[field]=balanced(selected,field)[0]
                stats.update(predictor=predictor,regime=regime,arm=arm,campaigns=len(selected),
                  interrupted_campaigns=sum(r['interruptions']>0 for r in selected),
                  full_B_campaigns=sum(r['new_deliveries']==r['assigned_B'] for r in selected),
                  operation_counts={op:sum(r['operations'][op] for r in selected) for op in('REUSE','UPDATE','PLAN')},
                  fallbacks=sum(r['feasibility_fallbacks'] for r in selected))
                summaries.append(stats)
            for baseline in('G1','T','E'):contrasts.append(dict(contrast(sub,'L',baseline,SEEDS),predictor=predictor,regime=regime))
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
        ledger=json.loads((TASK/'ledger.json').read_text())
        training_cpu=sum(j.get('reported_cpu_seconds',0) for j in ledger['jobs'] if j.get('bucket')in('training_prefixes_branches_gate','control_tuning'))
        result={'schema':'curaloop.m2_costed.aggregate_results.v2','status':'COMPLETE_MATRIX_AWAITING_CLEANUP_AND_DELIVERY',
          'method_decision':decision,'technical_matrix_audit':'PASS','counts':dict(counts),'audit':dict(audit),
          'six_development_assays':6,'annotation_components':4,'task_rows':1285,'source_role':'exposed development',
          'primary_endpoint':'new FS-Mol assay-relative binary positives at assigned B32/Ccheap; initial positives excluded',
          'main_summaries':summaries,'paired_contrasts':contrasts,'rf_ablation_contrasts':ablation_contrasts,'rf_B16_transfer_contrasts':transfer,
          'training_state_support':{'states':artifacts['states'],'eligible_states':artifacts['eligible_states'],'gate_artifacts':len(artifacts['artifacts'])},
          'offline_training_and_tuning_actual_cpu_seconds':training_cpu,
          'offline_amortized_cpu_seconds_per_campaign':{str(n):training_cpu/n for n in(1,10,100)},
          'final_outcomes_opened':False,'automatic_m3':False,'publication_ready':False,
          'limitations':['Four dependent annotation components; not biological-family population inference.',
            'Previously exposed development cohort; no independent final evidence.',
            'Balanced assay-relative labels do not represent HTS prevalence, clinical benefit or lab savings.',
            'CPU-specific calibrated regimes; selection-biased delivered-observation diagnostics.',
            'Correlated training branches and five seed vectors do not add independent biological replication.']}
        new(PUBLIC/'aggregate-results-v1.json',result);new(job/'result.json',{'status':'PASS_COMPLETE_MATRIX_ANALYSIS','method_decision':decision,'verified_units':audit['verified_units']})
        guard.finish('PASS');print(json.dumps({'status':'PASS_COMPLETE_MATRIX_ANALYSIS','decision':decision,'primary_contrasts':p,'history':history}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:300]});guard.finish('FAIL');raise


if __name__=='__main__':main()
