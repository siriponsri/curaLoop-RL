"""Close the M2 resource checkpoint only after complete return and exact absence."""
import ast
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from research.m2_v1.admission import M2Guard

LOCAL=ROOT/'.local/m2-selective-compute-20261108-v1'
PUBLIC=ROOT/'docs/evidence/m2-selective-compute-20261108-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def replace_json(path,value):
    temp=path.with_suffix('.next.json')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    os.replace(temp,path)


def main():
    permit=json.loads((LOCAL/'jobs/closeout-validation-v1/permit.json').read_text())
    guard=M2Guard(LOCAL/'jobs/closeout-validation-v1/resource.json',permit)
    try:
        PUBLIC.mkdir(parents=True,exist_ok=True)
        returned=json.loads((PUBLIC/'complete-return-verified-v1.json').read_text())
        absence=json.loads((PUBLIC/'fresh-absence-v1.json').read_text())
        assert returned['status']=='PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD'
        assert absence['status']=='PASS_FRESH_EXACT_ABSENCE'
        prior=json.loads((LOCAL/'previous-ledger-pins.json').read_text())['records']
        extra=json.loads((LOCAL/'additional-history-pins.json').read_text())
        rows=[]
        for record in prior+[{'path':p,'sha256':pin} for p,pin in extra.items()]:
            assert sha(ROOT/record['path'])==record['sha256']
            rows.append(dict(record,status='PASS_UNCHANGED'))
        freeze=json.loads((ROOT/'docs/evidence/lr-m12-20261108-v1/m1-freeze-v2.json').read_text())
        for path,pin in freeze['code_sha256'].items():
            assert sha(ROOT/path)==pin
            rows.append({'path':path,'sha256':pin,'status':'PASS_UNCHANGED'})
        new(PUBLIC/'old-history-unchanged-v1.json',{'status':'PASS_OLD_HISTORY_UNCHANGED','records':rows})
        snapshot=json.loads((LOCAL/'release-snapshot.json').read_text())
        plan=json.loads((ROOT/snapshot['plan_config']).read_text())
        assert sha(ROOT/snapshot['plan_config'])==snapshot['plan_sha256']
        assert sha(ROOT/snapshot['data_scope'])==snapshot['scope_sha256']
        assert sha(ROOT/plan['plan_document'])==snapshot['plan_document_sha256']
        admission=json.loads((LOCAL/'admission/summary.json').read_text())
        assert admission['status']=='PASS_OUTCOME_BLIND_ADMISSION' and not admission['labels_decoded']
        assert not admission['final_feature_label_presence_decoded']
        new(PUBLIC/'data-admission-v1.json',admission)
        checks=json.loads((LOCAL/'jobs/constructed-checks-v1/result.json').read_text())
        assert checks['count']==len(checks['checks'])==12 and not checks['biological_data_accessed']
        new(PUBLIC/'constructed-checks-v1.json',checks)
        first=json.loads((LOCAL/'jobs/calibration-000/result.json').read_text())
        invalidity=json.loads((LOCAL/'calibration-000-invalidity.json').read_text())
        final=json.loads((LOCAL/'jobs/calibration-000-r1/result.json').read_text())
        assert first['calibrated_cap_lower_bound']<30<final['calibrated_cap_lower_bound']
        assert final['spec']==first['spec'] and not final['biological_outcomes_accessed']
        order=json.loads((LOCAL/'synthetic-calibration-order.json').read_text())
        assert final['spec']==order['units'][0] and len(order['units'])==96
        transport=json.loads((LOCAL/'bundle-result.json').read_text())
        executed_pins={p:transport['code_pins'][p] for p in ('research/m2_v1/models.py','research/m2_v1/calibration.py')}
        executed_pins['research/m2_v1/checks.py']=json.loads((LOCAL/'jobs/constructed-checks-v1/permit.json').read_text())['arguments']['checks_sha256']
        executed_pins['research/m2_v1/calibration_v2.py']=json.loads((LOCAL/'jobs/timer-repair-install-v2/result.json').read_text())['source_sha256']
        assert all(sha(ROOT/p)==pin for p,pin in executed_pins.items())
        summary={'schema':'curaloop.m2.preflight_summary.v1','status':'INCOMPLETE_AT_RESOURCE_CHECKPOINT',
            'data_admission':'PASS','constructed_checks':12,'synthetic_unique_configurations_attempted':1,
            'synthetic_attempts':2,'synthetic_campaigns_completed':0,'remaining_unique_calibration_configs_not_run':95,
            'biological_label_payloads_decoded':0,'biological_campaigns':0,'gate_fits':0,
            'counterfactual_training_branches':0,'original_attempt':first,'original_inference_valid':False,
            'invalidity_annotation':invalidity,'verified_attempt':final,
            'required_cap_seconds':30,'full_baseline_cpu_seconds':None,
            'startup_assumption_seconds':1,'observed_whole_process_minus_scientific_lower_bound_seconds':
                json.loads((LOCAL/'jobs/calibration-000-r1/resource.json').read_text())['cpu_seconds']-final['scientific_cpu_seconds_lower_bound'],
            'startup_assumption_supported':False,'aggregate_attempt_reservation_seconds':31,
            'protected_final_opened':False,'m3_released':False,'method_efficacy':'NOT_RUN',
            'publication_readiness':'NOT_ESTABLISHED','scientific_order_sha256':sha(LOCAL/'synthetic-calibration-order.json'),
            'executed_scientific_code_sha256':executed_pins}
        new(PUBLIC/'synthetic-admission-summary-v1.json',summary)
        resources={}
        for job in sorted((LOCAL/'jobs').iterdir()):
            if job.name=='closeout-validation-v1':continue
            path=job/'resource.json'
            if path.exists():resources[job.name]=json.loads(path.read_text())
        new(PUBLIC/'worker-resources-v1.json',{'status':'RECORDED_GUARDED_WORKERS','resources':resources,
            'excludes_current_closeout_final_receipt':True,'utility_cpu_measured':False})
        # Inspect only newly authored source/metadata, without importing ML or executing tests.
        sources=list((ROOT/'research/m2_v1').glob('*.py'))+list((ROOT/'tools').glob('m2_*_v1.py'))
        pins={}
        for path in sources:
            ast.parse(path.read_text(encoding='utf-8'));pins[path.relative_to(ROOT).as_posix()]=sha(path)
        config_names=['research/manifests/m2_release_20261108_v1.json','research/manifests/m2_data_scope_20261108_v1.json',
                      'research/configs/m2_status_20261108_v1.json','research/configs/m2_experiment_plan_20261108_v1.json',
                      'research/configs/m2_profile_amendment_20261108_v1.json']
        for name in config_names:json.loads((ROOT/name).read_text())
        amendment=json.loads((ROOT/config_names[-1]).read_text())
        assert not amendment['execution_enabled'] and not amendment['owner_approval_received']
        assert not (ROOT/amendment['root_proposed']).exists()
        assert sum(amendment['cpu_reservations_seconds'].values())==amendment['profile_cpu_cap_seconds_including_utilities']==3600
        assert amendment['intended_units']==12 and amendment['max_attempts']==14
        assert sum(amendment['proposed_stage_cap_deltas_seconds'].values())==0
        docs=[ROOT/p for p in ('AGENTS.md','GOAL.md','PLAN.md','HANDOFF.md','README.md','START_HERE.md',
              'docs/00_project/CLAIM_LEDGER.md','docs/03_research/M2_PREFLIGHT_RESULTS_20261108.md',
              'docs/06_execution/M2_RESOURCE_OWNER_CHECKPOINT_20261108.md',
              'docs/evidence/m2-selective-compute-20261108-v1/README.md')]
        links=0
        for path in docs:
            body=path.read_text(encoding='utf-8')
            assert not re.search('[\u0e00-\u0e7f]',body),str(path)
            for target in re.findall(r'\]\(([^\n]+?)\)',body):
                target=target.strip('<>')
                if target.startswith('#') or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',target):continue
                assert (path.parent/target.split('#',1)[0]).resolve().exists(),(str(path),target)
                links+=1
        new(PUBLIC/'delivery-validation-v1.json',{'status':'PASS_STATIC_CHECKPOINT_DELIVERY',
            'source_files_parsed':len(sources),'source_sha256':pins,'english_documents':len(docs),
            'json_configurations_parsed':len(config_names),'pending_amendment_arithmetic_checked':True,
            'local_links_checked':links,'original_plan_scope_bytes_unchanged':True,
            'full_return_and_fresh_absence_required':True,'ml_fits_or_campaigns_in_validation':0})
        guard.finish('PASS')
        # Settle this final, already-finished process before closing the single-writer ledger.
        lock=LOCAL/'.ledger.lock'
        with lock.open('x') as f:f.write(str(os.getpid()))
        try:
            ledger=json.loads((LOCAL/'ledger.json').read_text())
            row=next(j for j in ledger['jobs'] if j['job']=='closeout-validation-v1')
            receipt=json.loads((LOCAL/'jobs/closeout-validation-v1/resource.json').read_text())
            row.update(state='PASS',reported_cpu_seconds=receipt['cpu_seconds'],resource_sha256=sha(LOCAL/'jobs/closeout-validation-v1/resource.json'))
            assert not any(j['state']=='RESERVED' for j in ledger['jobs'])
            for j in ledger['jobs']:
                if j['state']=='RESERVED_UTILITIES_ENVELOPE':j['state']='CHARGED_UTILITIES_ENVELOPE'
            assert ledger['scientific_units_attempted']==2 and not ledger['final_outcomes_opened']
            assert sum(ledger['bucket_reserved_seconds'].values())<=ledger['cpu_cap_seconds']==172800
            assert all(ledger['bucket_reserved_seconds'][k]<=v for k,v in ledger['bucket_caps_seconds'].items())
            ledger.update(status='CLOSED_OWNER_RESOURCE_CHECKPOINT',closed_utc=datetime.now(timezone.utc).isoformat(),
                next_actor='OWNER_AMENDMENT_REQUIRED',m2_scientific_status='INCOMPLETE_RESOURCE_FIT',
                scientific_release_open=False,biological_campaigns=0,
                guarded_worker_cpu_seconds=sum(j.get('reported_cpu_seconds',0) for j in ledger['jobs']),
                total_cpu_measured=False,resource_limit_attempts=2,invalid_timer_inferences=1)
            replace_json(LOCAL/'ledger.json',ledger)
            new(PUBLIC/'ledger-checkpoint-v1.json',ledger)
            status_path=ROOT/'research/configs/m2_status_20261108_v1.json'
            status=json.loads(status_path.read_text())
            status.update(status='OWNER_RESOURCE_CHECKPOINT',scientific_release_open=False,
                m2_status='INCOMPLETE_RESOURCE_FIT',m3_status='NOT_RELEASED',
                data_admission='PASS',constructed_checks=12,biological_labels_decoded=0,
                biological_campaigns=0,gate_fits=0,synthetic_attempts=2,
                owner_checkpoint='docs/06_execution/M2_RESOURCE_OWNER_CHECKPOINT_20261108.md')
            replace_json(status_path,status)
            print(json.dumps({'status':ledger['status'],'retained_seconds':sum(ledger['bucket_reserved_seconds'].values()),
                'guarded_worker_cpu_seconds':ledger['guarded_worker_cpu_seconds'],
                'total_cpu_measured':False,'returned_files':returned['file_count'],'sources_parsed':len(sources)}))
        finally:lock.unlink()
    except BaseException:
        if not guard.completed.is_set():guard.finish('FAIL')
        raise


if __name__=='__main__':main()
