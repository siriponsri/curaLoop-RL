"""Supplement paired-analysis checks with heterogeneous constructed seed effects."""
import itertools,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call
from tools.m2c_analyze_v2 import contrast,SEEDS
from research.m2_costed_v2.guard import CostedGuard,new
TASK=ROOT/'.local/m2-costed-20261108-v2';job=TASK/'jobs/analysis-pairing-checks-v3'


def main():
    if len(sys.argv)==1:
        assert json.loads((TASK/'pipeline-status.json').read_text())['status']=='PASS_COMPLETE_FIXED_M2_MATRIX'
        path=TASK/'specs/analysis-pairing-checks-v3.json'
        new(path,dict(job=job.name,host='local',handler='constructed_pairing_checks',bucket='engineering_guards',
          reservation_seconds=60,wall_seconds=120,memory_bytes=536870912,arguments={}))
        print(json.dumps(admin_call('reserve',path)));return
    permit=json.loads((job/'permit.json').read_text());guard=CostedGuard(job/'resource.json',permit)
    try:
        rows=[];seed_effects=[0,4,-1,2,-5]
        for group,count in enumerate((1,2,1,2)):
            for task in range(count):
                for n0 in(0,16):
                    for seed_index,seed in enumerate(SEEDS):
                        base=100*group+17*task+13*seed_index+7*(n0//16)
                        delta=group-2+task+.5*(n0//16)+seed_effects[seed_index]
                        for arm in('L','G1'):
                            rows.append({'task_id':f'g{group}-t{task}','component':f'g{group}','arm':arm,
                              'new_positives':base+(delta if arm=='L' else 0),'spec':{'n0':n0,'seed':seed}})
        result=contrast(rows,'L','G1',SEEDS)
        assert result['mean_delta_new_positives']==0
        assert result['shared_seed_effect_vector']==seed_effects
        assert result['component_effects']=={'g0':-1.75,'g1':-.25,'g2':.25,'g3':1.75}
        assert result['positive_components']==2
        # Exhaustive distribution of all3125 equally likely seed-vector draws is
        # independent of the Monte Carlo sampler used by the production analysis.
        exact=sorted(sum(draw)/5 for draw in itertools.product(seed_effects,repeat=5))
        limits=[exact[math.floor((len(exact)-1)*p)] for p in(.025,.975)]
        assert all(abs(a-b)<=.2+1e-12 for a,b in zip(result['conditional_seed_interval_95'],limits))
        try:contrast(rows+[dict(rows[0])],'L','G1',SEEDS)
        except AssertionError as exc:assert str(exc)=='DUPLICATE_PAIRED_CONTEXT'
        else:raise AssertionError('DUPLICATE_PAIR_NOT_REJECTED')
        try:contrast(rows[1:],'L','G1',SEEDS)
        except KeyError:pass
        else:raise AssertionError('MISSING_PAIR_NOT_REJECTED')
        new(job/'result.json',{'status':'PASS_CONSTRUCTED_PAIRING_SUPPLEMENT','checks':[
          {'name':'heterogeneous-assay-n0-seed-offsets-retain-paired-effects-and-equal-component-weight','status':'PASS'},
          {'name':'joint-seed-bootstrap-agrees-with-exhaustive-finite-distribution','status':'PASS'},
          {'name':'duplicate-and-missing-paired-contexts-rejected','status':'PASS'}],
          'scope':'constructed nonbiological fixture; no new efficacy criterion or analytical estimator',
          'biological_outcomes_read':False,'final_outcomes_opened':False})
        guard.finish('PASS');print('PASS: heterogeneous pairing, joint uncertainty and malformed-pair rejection')
    except BaseException:guard.finish('FAIL');raise


if __name__=='__main__':main()
