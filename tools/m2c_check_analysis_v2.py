"""Constructed checks of dependence weighting, pairing and conditional intervals."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call
from tools.m2c_analyze_v2 import balanced,contrast,SEEDS
from research.m2_costed_v2.guard import CostedGuard,new
TASK=ROOT/'.local/m2-costed-20261108-v2';job=TASK/'jobs/analysis-constructed-checks'
if len(sys.argv)==1:
    path=TASK/'specs/analysis-constructed-checks.json'
    new(path,dict(job=job.name,host='local',handler='constructed_analysis_checks',bucket='engineering_guards',
      reservation_seconds=60,wall_seconds=120,memory_bytes=536870912,arguments={}))
    print(json.dumps(admin_call('reserve',path)))
else:
    permit=json.loads((job/'permit.json').read_text());guard=CostedGuard(job/'resource.json',permit)
    try:
        rows=[]
        for g,count in enumerate((1,2,1,2)):
            for task in range(count):
                for n0 in(0,16):
                    for seed in SEEDS:
                        for arm in('L','G1'):rows.append({'task_id':f'g{g}-t{task}','component':f'g{g}',
                          'arm':arm,'new_positives':g+1 if arm=='L' else 0,'spec':{'n0':n0,'seed':seed}})
        selected=[r for r in rows if r['arm']=='L'];mean,components=balanced(selected,'new_positives')
        assert mean==2.5 and components=={'g0':1,'g1':2,'g2':3,'g3':4}
        result=contrast(rows,'L','G1',SEEDS)
        assert result['mean_delta_new_positives']==2.5 and result['conditional_seed_interval_95']==[2.5,2.5]
        assert result['positive_components']==4 and result['shared_seed_effect_vector']==[2.5]*5
        reverse=contrast(rows,'G1','L',SEEDS);assert reverse['mean_delta_new_positives']==-2.5
        new(job/'result.json',{'status':'PASS_CONSTRUCTED_ANALYSIS_CHECKS','checks':[
          'equal component weights despite unequal assay counts','paired signs and initial-count/seed matching',
          'joint seed-vector conditional bootstrap on constructed constant effects'],
          'biological_outcomes_read':False,'final_outcomes_opened':False})
        guard.finish('PASS');print('PASS: constructed dependence-weighting and paired-interval checks')
    except BaseException:guard.finish('FAIL');raise
