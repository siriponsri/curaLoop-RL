"""Blind staged coordinator: paired CPU slots, serial ledger, complete retained units."""
import hashlib,json,math,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,batch
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2';REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'
BUCKET={'prefix':'training_prefixes_branches_gate','branch':'training_prefixes_branches_gate','tuning':'control_tuning',
        'main':'main_comparison','ablation':'ablation_transfer','transfer':'ablation_transfer'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    stage=sys.argv[1];guard=OrchestrationGuard(TASK/(stage+'-orchestration-resource.json'),500,'2026-11-12T08:17:29Z')
    try:
        if stage=='main':
            from tools.m2c_transport_checks_v2 import checks
            checks(TASK)
        matrix=json.loads((TASK/'execution-matrix-v1.json').read_text());code=json.loads((TASK/'code-stage-03.json').read_text())
        predecessor={'branch':'prefix','tuning':'branch','main':'tuning','ablation':'main','transfer':'ablation'}.get(stage)
        if predecessor:assert json.loads((TASK/(predecessor+'-summary.json')).read_text())['status']=='PASS_COMPLETE_STAGE'
        selected=[e for e in matrix['entries'] if e['handler']in(('main','ablation') if stage=='main' else (stage,))]
        if stage=='ablation' and (TASK/'ablation-summary.json').exists():
            assert json.loads((TASK/'ablation-summary.json').read_text())['interleaved_with_main']is True
            assert all(json.loads((TASK/'jobs'/e['job']/'resource.json').read_text())['status']=='PASS' for e in selected)
            guard.finish('PASS');print(json.dumps({'stage':'ablation','status':'ALREADY_COMPLETED_INTERLEAVED_WITH_MAIN','units':len(selected)}));return
        if stage=='main':selected.sort(key=lambda e:hashlib.sha256(('interleaved-order:'+e['job']).encode()).digest())
        gates=json.loads((TASK/'jobs/fit-gates/result.json').read_text())['artifacts'] if stage in('main','ablation','transfer') else None
        controls=json.loads((TASK/'jobs/fit-controls/result.json').read_text())['artifacts'] if gates else None
        queues={cpu:[] for cpu in(69,70,71)}
        for entry in selected:
            assert not (TASK/'jobs'/entry['job']).exists(),'RESUME_REQUIRES_EXPLICIT_RECOVERY'
            args=entry['arguments'];component=next(f['component'] for f in json.loads((TASK/'development-projection-manifest.json').read_text())['files'] if f['task_id']==args['task_id'])
            if gates:
                key=args['predictor']+':'+component
                if args['policy']=='L':args['gate']=gates[key+(':'+args['variant'] if args.get('variant')=='no_history' else ':full')]
                if args.get('variant')in('no_UPDATE','no_PLAN'):args['restricted']=[args['variant'][3:]]
                if args['policy']in('Gk','T'):
                    index=controls[key][args['policy']]['selected_configuration']
                    args['parameter']=([2,4,8] if args['policy']=='Gk' else [[2,.02],[4,.05],[8,.10]])[index]
            reservation=20 if stage=='prefix' else math.ceil(args['cap'])+5
            spec=dict(job=entry['job'],host='dr-train',cpu=entry['cpu'],handler=entry['handler'],bucket=BUCKET[entry['handler']],
                reservation_seconds=reservation,wall_seconds=max(60,3*reservation),memory_bytes=4294967296,task_root=REMOTE,
                code_directory=code['code_directory'],code_pins=code['code_pins'],arguments=args,execution_unit=True,
                development_admission='PASS',final_outcomes_opened=False)
            path=TASK/'specs'/(entry['job']+'.json');new(path,spec);queues[entry['cpu']].append((entry,path))
        # Derived gates/configurations are fixed before any held-out evaluation unit.
        new(TASK/(stage+'-execution-freeze.json'),{'stage':stage,'jobs':[e['job'] for e in selected],
          'spec_pins':{e['job']:sha(TASK/'specs'/(e['job']+'.json')) for e in selected},
          'code_stage':sha(TASK/'code-stage-03.json'),'matrix_sha256':sha(TASK/'execution-matrix-v1.json'),
          'gates_sha256':sha(TASK/'jobs/fit-gates/result.json') if gates else None,
          'controls_sha256':sha(TASK/'jobs/fit-controls/result.json') if controls else None})
        completed=0;started=time.monotonic()
        while any(queues.values()):
            group=[queues[cpu].pop(0) for cpu in(69,70,71) if queues[cpu]]
            for e,path in group:admin_call('reserve',path)
            output=batch([e['job'] for e,path in group],action='worker')
            failures=[]
            for e,path in group:
                admin_call('settle',e['job']);r=json.loads((TASK/'jobs'/e['job']/'resource.json').read_text())
                result_path=TASK/'jobs'/e['job']/'result.json'
                result=json.loads(result_path.read_text()) if result_path.exists() else {}
                if r['status']!='PASS' or not result.get('status','').startswith('PASS'):failures.append(e['job'])
                completed+=1
            print(json.dumps({'stage':stage,'complete':completed,'total':len(selected),'elapsed_seconds':round(time.monotonic()-started,1),'failures':failures}),flush=True)
            if failures:raise RuntimeError('RETAINED_UNIT_FAILURE:'+','.join(failures))
        new(TASK/(stage+'-summary.json'),{'status':'PASS_COMPLETE_STAGE','stage':stage,'units':1920 if stage=='main' else completed,'outcome_inspection_for_selection':False})
        if stage=='main':new(TASK/'ablation-summary.json',{'status':'PASS_COMPLETE_STAGE','stage':'ablation','units':180,
          'interleaved_with_main':True,'outcome_inspection_for_selection':False})
        guard.finish('PASS')
    except BaseException:
        guard.finish('FAIL_ORCHESTRATION_OR_UNIT');raise


if __name__=='__main__':main()
