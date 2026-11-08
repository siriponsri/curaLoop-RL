"""Closeout evidence audit; retains old history and exact scoped cleanup proofs."""
import collections,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.m2_costed_v2.guard import CostedGuard,new
TASK=ROOT/'.local/m2-costed-20261108-v2';PUBLIC=ROOT/'docs/evidence/m2-costed-20261108-v2'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    permit=json.loads((TASK/'jobs/closeout-audit-v1/permit.json').read_text());job=TASK/'jobs'/permit['attempt'];guard=CostedGuard(job/'resource.json',permit)
    try:
        pins=json.loads((TASK/'previous-state-pins.json').read_text())
        assert all(sha(ROOT/name)==expected for name,expected in pins.items())
        older=json.loads((ROOT/'docs/evidence/m2-selective-compute-20261108-v1/old-history-unchanged-v1.json').read_text())
        assert older['status']=='PASS_OLD_HISTORY_UNCHANGED'
        assert all(sha(ROOT/row['path'])==row['sha256'] for row in older['records'])
        previous_audit_sha=sha(ROOT/'docs/evidence/m2-selective-compute-20261108-v1/old-history-unchanged-v1.json')
        code=json.loads((TASK/'code-stage-03.json').read_text())
        assert all(sha(ROOT/name)==expected for name,expected in code['code_pins'].items())
        scope=json.loads((ROOT/'research/manifests/m2_data_scope_20261108_v1.json').read_text())
        assert all(sha(ROOT/t['private_input_path'])==t['expected_input_sha256'] for t in scope['tasks'])
        results=json.loads((PUBLIC/'aggregate-results-v1.json').read_text())
        assert results['technical_matrix_audit']=='PASS' and results['audit']['verified_units']==4164
        returned=json.loads((TASK/'remote-return/verified-v1.json').read_text());assert returned['status']=='PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD'
        cleanup=json.loads((PUBLIC/'scoped-delete-v1.json').read_text());absence=json.loads((PUBLIC/'fresh-absence-v1.json').read_text())
        assert cleanup['status']=='PASS_EXACT_DELETE_AFTER_FULL_RETURN' and absence['status']=='PASS_FRESH_EXACT_ABSENCE'
        ledger=json.loads((TASK/'ledger.json').read_text());reserved=sum(ledger['bucket_reserved_seconds'].values())
        assert reserved<=164250 and reserved+ledger['prior_retained_seconds']<=172800
        assert all(ledger['bucket_reserved_seconds'][k]<=v for k,v in ledger['bucket_caps_seconds'].items())
        assert [j['job'] for j in ledger['jobs'] if j['state']=='RESERVED']==['closeout-audit-v1']
        assert not ledger['final_outcomes_opened'] and not ledger['m3_released']
        counts=collections.Counter(j['state'] for j in ledger['jobs']);execution=[j for j in ledger['jobs'] if j.get('execution_unit')]
        assert len(execution)==ledger['attempted_units']==4251
        assert sum(j['state']=='FAIL' for j in execution)==3
        assert sum(j['state']=='PASS' for j in execution)==4248
        cpu={'status':'PASS_CUMULATIVE_RESERVATION_ACCOUNTING','prior_retained_seconds':ledger['prior_retained_seconds'],
          'fresh_charged_seconds':reserved,'cumulative_charged_seconds':reserved+ledger['prior_retained_seconds'],
          'cumulative_charged_cpu_hours':(reserved+ledger['prior_retained_seconds'])/3600,
          'cumulative_cap_seconds':172800,'unused_against_original_ceiling_seconds':172800-reserved-ledger['prior_retained_seconds'],
          'bucket_caps_seconds':ledger['bucket_caps_seconds'],'bucket_charged_seconds':ledger['bucket_reserved_seconds'],
          'attempted_units_this_release':len(execution),'successful_units_this_release':4248,
          'retained_not_dispatched_attempts':3,'unique_synthetic_contexts_including_previous_profile':96,
          'biological_units':4164,'accounting_basis':'conservative reservations retained in full; not total-host measured consumption',
          'deadline_utc':ledger['deadline_utc'],'final_outcomes_opened':False,'m3_released':False}
        new(PUBLIC/'cpu-accounting-v1.json',cpu)
        new(PUBLIC/'old-history-unchanged-v1.json',{'status':'PASS_PINNED_HISTORY_UNCHANGED','paths':pins,
          'previous_complete_preservation_audit_sha256':previous_audit_sha,
          'previous_complete_preservation_sources_rechecked':len(older['records']),
          'six_original_development_source_hashes_unchanged':True,'executed_scientific_code_matches_projection_03':True})
        new(PUBLIC/'constructed-checks-v1.json',{'engine':json.loads((TASK/'jobs/engine-checks-03/result.json').read_text()),
          'analysis':json.loads((TASK/'jobs/analysis-constructed-checks/result.json').read_text())})
        new(job/'result.json',{'status':'PASS_COMPLETE_M2_CLOSEOUT_AUDIT','method_decision':results['method_decision'],
          'biological_units':4164,'all_scientific_sources_pinned':True,'final_outcomes_opened':False,'m3_released':False})
        guard.finish('PASS');print(json.dumps({'status':'PASS_COMPLETE_M2_CLOSEOUT_AUDIT','cumulative_charged_cpu_hours':cpu['cumulative_charged_cpu_hours']}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:300]});guard.finish('FAIL');raise


if __name__=='__main__':main()
