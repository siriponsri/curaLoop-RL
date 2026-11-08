"""Close the one-hour profile grant after verified full return and exact absence."""
import ast
import hashlib
import json
import os
import re
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.m2_profile_v1.guard import ProfileGuard,new
TASK=ROOT/'.local/m2-cpu-profile-20261108-v1'
PUBLIC=ROOT/'docs/evidence/m2-cpu-profile-20261108-v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    permit=json.loads((TASK/'jobs/closeout-v1/permit.json').read_text())
    guard=ProfileGuard(TASK/'jobs/closeout-v1/resource.json',permit)
    try:
        returned=json.loads((PUBLIC/'complete-return-verified-v1.json').read_text())
        assert returned['status']=='PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD'
        assert json.loads((PUBLIC/'fresh-absence-v1.json').read_text())['status']=='PASS_FRESH_EXACT_ABSENCE'
        assert returned['file_count']==1955 and returned['export_file_count']==7
        snapshot=json.loads((TASK/'release-snapshot.json').read_text())
        assert sha(ROOT/snapshot['specification'])==snapshot['specification_sha256']
        pins=json.loads((TASK/'previous-state-pins.json').read_text())
        for row in json.loads((ROOT/'docs/evidence/m2-selective-compute-20261108-v1/old-history-unchanged-v1.json').read_text())['records']:
            pins[row['path']]=row['sha256']
        assert all(sha(ROOT/name)==pin for name,pin in pins.items())
        new(PUBLIC/'previous-state-unchanged-v1.json',{'status':'PASS_PREVIOUS_STATE_UNCHANGED','sha256':pins})
        frozen=json.loads((TASK/'profile-freeze-v1.json').read_text())
        assert len(frozen['order'])==12 and all(sha(ROOT/name)==pin for name,pin in frozen['code_pins'].items())
        new(PUBLIC/'profile-freeze-v1.json',frozen)
        checks=json.loads((TASK/'jobs/checks-v1/result.json').read_text())
        assert checks['status']=='PASS_PROFILE_INSTRUMENTATION_CHECKS' and checks['count']==5
        new(PUBLIC/'instrumentation-checks-v1.json',checks)
        timing=json.loads((PUBLIC/'timing-summary-v1.json').read_text())
        assert timing['profiles_completed']==12 and timing['technical_retries']==0 and not timing['biological_data_accessed']
        assert json.loads((TASK/'matrix-run-summary.json').read_text())['status']=='PASS_COMPLETE_12_PROFILES'
        for entry in frozen['order']:
            result=TASK/'jobs'/entry['job']/'result.json'
            record=next(r for r in timing['rows'] if r['job']==entry['job'])
            assert sha(result)==record['result_sha256']
            assert json.loads(result.read_text())['spec']==entry['arguments']
        proposal_path=ROOT/'research/configs/m2_costed_continuation_20261108_v2.json'
        p=json.loads(proposal_path.read_text())
        assert not p['execution_enabled'] and not p['owner_approval_received'] and not p['final_outcomes_open']
        assert all(sum(c['units'] for c in w['cells'])==w['units'] and
                   sum(c['units']*c['cpu_per_unit'] for c in w['cells'])==w['cpu_seconds'] for w in p['workload'])
        assert sum(w['units'] for w in p['workload'])==p['intended_units_remaining']==4248
        assert sum(p['remaining_stage_cpu_seconds'].values())==p['remaining_grant_upper_seconds']==164250
        assert 4112+3600+164250==p['cumulative_upper_seconds']==171962<=172800
        assert 172800-171962==p['headroom_against_48_hours_seconds']==838
        assert p['attempts_remaining_max']==4386 and p['technical_retry_allowance_remaining']==138
        assert p['retry_reserve_cpu_seconds']==138*70 and p['retry_reserve_included_in_analysis']
        new(PUBLIC/'costed-continuation-validation-v1.json',{
            'status':'PASS_CONDITIONAL_BUDGET_ARITHMETIC','specification_sha256':sha(proposal_path),
            'remaining_intended_units':4248,'remaining_cpu_upper_seconds':164250,
            'cumulative_upper_seconds':171962,'cumulative_cap_seconds':172800,'headroom_seconds':838,
            'neighbor_runtime_gate':'NOT_RUN','molecular_release':'NOT_RELEASED',
            'conditions':'remaining synthetic contexts must establish cheap<=5 / RF-high<=65 / neighbor-high<=25 seconds'})
        code=list((ROOT/'research/m2_profile_v1').glob('*.py'))+list((ROOT/'tools').glob('m2p_*_v1.py'))
        for path in code:ast.parse(path.read_text(encoding='utf-8'))
        docs=[ROOT/name for name in('AGENTS.md','GOAL.md','PLAN.md','HANDOFF.md','README.md','START_HERE.md',
            'docs/00_project/CLAIM_LEDGER.md','docs/03_research/M2_CPU_PROFILE_RESULTS_20261108.md',
            'docs/06_execution/M2_COSTED_CONTINUATION_PROPOSAL_20261108.md',
            'docs/evidence/m2-cpu-profile-20261108-v1/README.md')]
        links=0
        for path in docs:
            text=path.read_text(encoding='utf-8');assert not re.search('[\u0e00-\u0e7f]',text),path
            for link in re.findall(r'\]\(([^\n]+?)\)',text):
                link=link.strip('<>')
                if link.startswith('#') or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',link):continue
                assert (path.parent/link.split('#',1)[0]).resolve().exists(),(path,link)
                links+=1
        new(PUBLIC/'delivery-validation-v1.json',{'status':'PASS_STATIC_PROFILE_DELIVERY',
            'source_files_parsed':len(code),'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in code},
            'english_documents_checked':len(docs),'links_checked':links,'costed_matrix_arithmetic':'PASS_CONDITIONAL',
            'old_state_and_frozen_scientific_code':'PASS_UNCHANGED','molecular_data_or_model_work_in_validation':False,
            'full_return_and_fresh_absence':'PASS'})
        guard.finish('PASS')
        lock=TASK/'.ledger.lock'
        with lock.open('x') as f:f.write(str(os.getpid()))
        try:
            ledger=json.loads((TASK/'ledger.json').read_text());row=next(j for j in ledger['jobs'] if j['job']=='closeout-v1')
            r=json.loads((TASK/'jobs/closeout-v1/resource.json').read_text())
            row.update(state='PASS',reported_cpu_seconds=r['cpu_seconds'],resource_sha256=sha(TASK/'jobs/closeout-v1/resource.json'))
            assert ledger['attempted_profiles']==12 and not any(j['state']=='RESERVED' for j in ledger['jobs'])
            assert all(j['state']in('PASS','CHARGED_UTILITIES_ENVELOPE') for j in ledger['jobs'])
            total=sum(ledger['bucket_reserved_seconds'].values());assert total<=3600
            assert all(ledger['bucket_reserved_seconds'][k]<=cap for k,cap in ledger['bucket_caps_seconds'].items())
            ledger.update(status='CLOSED_COMPLETE_FOR_OWNER_REVIEW',closed_utc=datetime.now(timezone.utc).isoformat(),
                profiles_complete=12,profiles_censored=0,technical_retries=0,biological_campaigns=0,
                scientific_release_open=False,next_actor='OWNER_REVIEW_COSTED_M2_CONTINUATION',
                measured_guarded_worker_cpu_seconds=sum(j.get('reported_cpu_seconds',0) for j in ledger['jobs']),
                total_cpu_measured=False,cumulative_retained_seconds=4112+total)
            temp=TASK/'ledger.next.json';temp.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8');os.replace(temp,TASK/'ledger.json')
            new(PUBLIC/'ledger-closeout-v1.json',ledger)
            new(ROOT/'research/configs/m2_profile_status_20261108_v1.json',{
                'schema':'curaloop.m2.profile_status.v1','status':'COMPLETE_FOR_OWNER_REVIEW',
                'scientific_release_open':False,'profiles_completed':12,'technical_retries':0,
                'biological_data_opened':False,'final_outcomes_opened':False,'gate_fits':0,'molecular_campaigns':0,
                'm3_status':'NOT_RELEASED','retained_seconds':total,'cumulative_retained_seconds':4112+total,
                'cpu_cap_seconds':3600,'next_plan':p['revised_plan'],'continuation_execution_enabled':False})
            print(json.dumps({'status':ledger['status'],'retained_seconds':total,'measured_guarded_worker_cpu_seconds':ledger['measured_guarded_worker_cpu_seconds'],
                              'total_cpu_measured':False,'cumulative_retained_seconds':4112+total,'remaining_plan_execution_enabled':False}))
        finally:lock.unlink()
    except BaseException:
        if not guard.completed.is_set():guard.finish('FAIL')
        raise


if __name__=='__main__':main()
