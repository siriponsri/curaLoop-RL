"""Freeze 96 complete synthetic contexts and conditionally release development access."""
import hashlib,json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.m2_costed_v2.guard import CostedGuard,new
TASK=ROOT/'.local/m2-costed-20261108-v2'


def main():
    permit=json.loads((TASK/'jobs/finish-technical-admission/permit.json').read_text())
    guard=CostedGuard(TASK/'jobs/finish-technical-admission/resource.json',permit)
    try:
        assert json.loads((TASK/'technical-run-summary.json').read_text())['status']=='PASS_84_REMAINING_CONTEXTS'
        frozen=json.loads((TASK/'technical-freeze-v1.json').read_text());over=json.loads((TASK/'calibration-retry-overrides.json').read_text())
        rows=[]
        previous=json.loads((ROOT/'docs/evidence/m2-cpu-profile-20261108-v1/timing-summary-v1.json').read_text())
        for r in previous['rows']:
            rows.append({'spec':{k:r[k] for k in('predictor','n','n0','budget','policy','repeat')},
                'scientific_cpu_seconds':r['scientific_cpu_seconds'],
                'fit_predict_cpu_seconds':r['nested_fit_cpu_seconds']+r['nested_predict_cpu_seconds'],
                'source':'previous-complete-profile','source_result_sha256':r['result_sha256']})
        for entry in frozen['contexts']:
            job=over.get(entry['job'],{}).get('job',entry['job']);path=TASK/'jobs'/job/'result.json';r=json.loads(path.read_text())
            assert r['status']=='PASS_SYNTHETIC_CONTEXT' and r['spec']==entry['arguments']
            rows.append({'spec':r['spec'],'scientific_cpu_seconds':r['scientific_cpu_seconds'],
                'fit_predict_cpu_seconds':sum(v['cpu_seconds'] for v in r['nested_fit_predict'].values()),
                'source':job,'source_result_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        keys=[tuple(r['spec'][k] for k in('predictor','n','n0','budget','policy','repeat')) for r in rows]
        assert len(keys)==len(set(keys))==96
        caps={}
        for predictor in('rf','neighbor'):
            for n0 in(0,16):
                for b in(16,32):
                    group=[r for r in rows if r['spec']['predictor']==predictor and r['spec']['n0']==n0 and r['spec']['budget']==b]
                    g=[r for r in group if r['spec']['policy']=='G1'];p=[r for r in group if r['spec']['policy']=='P']
                    assert len(g)==len(p)==6
                    cheap=1.25*max(r['scientific_cpu_seconds'] for r in g);high=max(cheap,1.25*max(r['scientific_cpu_seconds'] for r in p))
                    assert cheap<=5 and high<=(65 if predictor=='rf' else 25)
                    reuse=statistics.median(max(.0001,(r['scientific_cpu_seconds']-r['fit_predict_cpu_seconds'])/b) for r in g)
                    caps[f'{predictor}:{n0}:{b}']={'cheap':cheap,'high':high,'collapse_high':high/cheap<1.5,
                        'operation_cost_priors':{'REUSE':reuse,'UPDATE':statistics.median(r['scientific_cpu_seconds']/b for r in g),
                                                'PLAN':statistics.median(r['scientific_cpu_seconds']/b for r in p)}}
        result={'schema':'curaloop.m2_costed.technical_admission.v2','status':'PASS_COMPLETE_SYNTHETIC_ADMISSION',
            'unique_contexts':96,'previous_completed_contexts':12,'remaining_completed_contexts':84,
            'retained_not_dispatched_attempts':3,'same_context_retries':3,'biological_labels_decoded':False,
            'caps':caps,'contexts':rows,'orchestration_repair':'in-process booking and three-unit SSH batches; no scientific parameter change'}
        new(TASK/'technical-admission-result.json',result)
        public=ROOT/'docs/evidence/m2-costed-20261108-v2';public.mkdir(parents=True,exist_ok=True)
        new(public/'technical-admission-v1.json',result)
        new(TASK/'jobs/finish-technical-admission/result.json',{'status':result['status'],'unique_contexts':96,'caps':caps})
        guard.finish('PASS');print(json.dumps({'status':result['status'],'caps':caps}))
    except BaseException:
        guard.finish('FAIL');raise


if __name__=='__main__':main()
