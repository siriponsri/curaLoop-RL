"""Describe timing metadata only; no molecular or synthetic discovery comparison."""
import hashlib
import json
import statistics as stats
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'.local/m2-cpu-profile-20261108-v1'
PUBLIC=ROOT/'docs/evidence/m2-cpu-profile-20261108-v1'


def main():
    frozen=json.loads((TASK/'profile-freeze-v1.json').read_text());rows=[]
    for entry in frozen['order']:
        job=TASK/'jobs'/entry['job'];r=json.loads((job/'result.json').read_text())
        resource=json.loads((job/'resource.json').read_text())
        assert r['status']=='PASS_COMPLETE_SYNTHETIC_PROFILE' and r['new_queries']==32
        assert r['spec']==entry['arguments'] and resource['status']=='PASS'
        assert r['scientific_cpu_seconds']<180 and resource['cpu_seconds']<185
        nested=r['nested_fit_and_predict']
        fit=sum(v['cpu_seconds'] for k,v in nested.items() if k.endswith(':fit'))
        predict=sum(v['cpu_seconds'] for k,v in nested.items() if k.endswith(':predict_proba'))
        row={'job':entry['job'],**entry['arguments'],'scientific_cpu_seconds':r['scientific_cpu_seconds'],
            'startup_cpu_seconds':r['startup_cpu_seconds'],'whole_process_cpu_seconds':resource['cpu_seconds'],
            'wall_seconds':resource['wall_seconds'],'exclusive_cpu_seconds':r['exclusive_cpu_seconds'],
            'nested_fit_cpu_seconds':fit,'nested_predict_cpu_seconds':predict,
            'nested_fit_fraction_of_scientific':fit/r['scientific_cpu_seconds'],
            'trajectory_sha256':r['trajectory_sha256'],
            'result_sha256':hashlib.sha256((job/'result.json').read_bytes()).hexdigest()}
        rows.append(row)
    assert len(rows)==12
    policy={}
    for name in('G1','P'):
        group=[r for r in rows if r['policy']==name];values=[r['scientific_cpu_seconds'] for r in group]
        policy[name]={'n':len(values),'min':min(values),'median':stats.median(values),'max':max(values),
                      'mean':stats.fmean(values),'mean_nested_fit_fraction':stats.fmean(r['nested_fit_fraction_of_scientific'] for r in group)}
    pairs=[];caps={}
    for n0 in(0,16):
        g=[r['scientific_cpu_seconds'] for r in rows if r['n0']==n0 and r['policy']=='G1']
        p=[r['scientific_cpu_seconds'] for r in rows if r['n0']==n0 and r['policy']=='P']
        caps[str(n0)]={'provisional_Ccheap':1.25*max(g),'provisional_Cplan':1.25*max(p),
                      'pool_size':303,'new_queries':32,'calibration_complete_over_N128_and_B16':False}
        for repeat in range(3):
            pair={r['policy']:r['scientific_cpu_seconds'] for r in rows if r['n0']==n0 and r['repeat']==repeat}
            pairs.append({'n0':n0,'repeat':repeat,'plan_to_greedy_ratio':pair['P']/pair['G1']})
    result={'schema':'curaloop.m2_profile.timings.v1','status':'PASS_COMPLETE_12_SYNTHETIC_CPU_PROFILES',
        'profiles_completed':12,'new_queries_per_profile':32,'technical_retries':0,
        'policy_scientific_cpu_seconds':policy,'provisional_caps':caps,'paired_ratios':pairs,
        'median_paired_plan_to_greedy_ratio':stats.median(p['plan_to_greedy_ratio'] for p in pairs),
        'startup_cpu_seconds':{'min':min(r['startup_cpu_seconds'] for r in rows),
            'median':stats.median(r['startup_cpu_seconds'] for r in rows),'max':max(r['startup_cpu_seconds'] for r in rows)},
        'rows':rows,'remaining_original_synthetic_calibration_configs':84,
        'neighbor_predictor_profiled':False,'biological_data_accessed':False,'molecular_utility':'NOT_RUN',
        'limitations':['synthetic CPU measurements, not molecular discovery evidence','N303 and B32 only',
                      'three repeats per policy/initialization, no statistical runtime-coverage guarantee',
                      'fit/predict times are nested, not additional costs','instrumentation overhead included, not subtracted']}
    PUBLIC.mkdir(parents=True,exist_ok=True)
    with (PUBLIC/'timing-summary-v1.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'policy_seconds':policy,'caps':caps,'startup':result['startup_cpu_seconds'],
                      'median_paired_ratio':result['median_paired_plan_to_greedy_ratio']}))


if __name__=='__main__':main()
