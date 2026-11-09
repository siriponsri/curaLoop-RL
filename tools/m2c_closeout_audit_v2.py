"""Closeout evidence audit; retains old history and exact scoped cleanup proofs."""
import collections,hashlib,json,math,sys
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
        final_counter_jobs=[];lower_bound_jobs=[];reservation_only_jobs=[]
        for row in ledger['jobs']:
            if row['state']=='CHARGED_UTILITIES_ENVELOPE':
                reservation_only_jobs.append(row['job']);continue
            if row['job']=='closeout-audit-v1':continue
            assert row['state']in('PASS','FAIL','FAIL_RESOURCE_LIMIT','FAIL_ADMISSION')
            resource_path=TASK/'jobs'/row['job']/'resource.json'
            assert sha(resource_path)==row['resource_sha256'],'SETTLED_RESOURCE_RECEIPT_CHANGED'
            receipt=json.loads(resource_path.read_text())
            assert receipt['attempt']==row['job'] and receipt['status']==row['state']
            assert receipt['cpu_seconds']==row['reported_cpu_seconds']
            assert math.isfinite(receipt['cpu_seconds']) and 0<=receipt['cpu_seconds']<=row['reservation_seconds']
            if 'reservation_seconds'in receipt:assert receipt['reservation_seconds']==row['reservation_seconds']
            text=str(receipt.get('cpu_measurement_scope',''))+' '+str(receipt.get('measurement_scope',''))
            (lower_bound_jobs if 'LOWER_BOUND' in text else final_counter_jobs).append(row['job'])
        counts=collections.Counter(j['state'] for j in ledger['jobs']);execution=[j for j in ledger['jobs'] if j.get('execution_unit')]
        retained_failures=sum(j['state']=='FAIL' for j in execution)
        assert len(execution)==ledger['attempted_units']==4248+retained_failures and retained_failures==6
        assert sum(j['state']=='PASS' for j in execution)==4248
        calibration_retries=json.loads((TASK/'calibration-retry-overrides.json').read_text())
        retries={old:row['job'] for old,row in calibration_retries.items()}
        retries.update(json.loads((TASK/'execution-retry-resolution-v1.json').read_text())['mapping'])
        assert len(retries)==6 and set(retries)=={j['job'] for j in execution if j['state']=='FAIL'}
        probes=[]
        for name in('orchestration-recovery-probe.json','tuning-recovery-probe-v1.json'):
            rows=json.loads((TASK/name).read_text())['results']
            assert all(not r['job_exists'] and r['unit_state']['LoadState']=='not-found' and r['unit_state']['ActiveState']=='inactive' for r in rows)
            probes.extend(r['job'] for r in rows)
        assert set(probes)==set(retries)
        returned_manifest=json.loads((TASK/'remote-return/export/manifest.json').read_text())
        for old,replacement in retries.items():
            original=json.loads((TASK/'jobs'/old/'permit.json').read_text())
            retried=json.loads((TASK/'jobs'/replacement/'permit.json').read_text())
            for key in('arguments','cpu','handler','code_pins','code_directory'):
                assert original.get(key)==retried.get(key),'SCIENTIFIC_RETRY_CONTEXT_CHANGED'
            assert not any(r['path'].startswith('jobs/'+old+'/') for r in returned_manifest['files'])
            assert json.loads((TASK/'jobs'/replacement/'resource.json').read_text())['status']=='PASS'
        cpu={'status':'PASS_CUMULATIVE_RESERVATION_ACCOUNTING','prior_retained_seconds':ledger['prior_retained_seconds'],
          'fresh_charged_seconds':reserved,'cumulative_charged_seconds':reserved+ledger['prior_retained_seconds'],
          'cumulative_charged_cpu_hours':(reserved+ledger['prior_retained_seconds'])/3600,
          'cumulative_cap_seconds':172800,'unused_against_original_ceiling_seconds':172800-reserved-ledger['prior_retained_seconds'],
          'bucket_caps_seconds':ledger['bucket_caps_seconds'],'bucket_charged_seconds':ledger['bucket_reserved_seconds'],
          'attempted_units_this_release':len(execution),'successful_units_this_release':4248,
          'retained_not_dispatched_attempts':retained_failures,'unique_synthetic_contexts_including_previous_profile':96,
          'not_dispatched_absence_and_identical_retry_contexts_rechecked':len(retries),
          'biological_units':4164,'accounting_basis':'conservative reservations retained in full; not total-host measured consumption',
          'settled_resource_hashes_rechecked':len(final_counter_jobs)+len(lower_bound_jobs),
          'final_cpu_counter_unavailable_jobs':lower_bound_jobs,'reservation_only_utility_envelopes':reservation_only_jobs,
          'final_counter_scope':'Receipt values rechecked against reservations; unavailable final counters remain explicit lower bounds, not fabricated totals. Closeout-audit settles after this snapshot.',
          'deadline_utc':ledger['deadline_utc'],'final_outcomes_opened':False,'m3_released':False}
        new(PUBLIC/'cpu-accounting-v1.json',cpu)
        new(PUBLIC/'old-history-unchanged-v1.json',{'status':'PASS_PINNED_HISTORY_UNCHANGED','paths':pins,
          'previous_complete_preservation_audit_sha256':previous_audit_sha,
          'previous_complete_preservation_sources_rechecked':len(older['records']),
          'six_original_development_source_hashes_unchanged':True,'executed_scientific_code_matches_projection_03':True})
        transport=json.loads((TASK/'transport-constructed-checks-v1.json').read_text());assert transport['status']=='PASS_CONSTRUCTED_TRANSPORT_CHECKS'
        engine=json.loads((TASK/'jobs/engine-checks-03/result.json').read_text())
        analysis=json.loads((TASK/'jobs/analysis-constructed-checks/result.json').read_text())
        pairing=json.loads((TASK/'jobs/analysis-pairing-checks-v3/result.json').read_text())
        assert engine['status']=='PASS_CONSTRUCTED_ENGINE_CHECKS' and len(engine['checks'])==11
        assert all(c['status']=='PASS' for c in engine['checks']) and not engine['biological_records_read']
        assert analysis['status']=='PASS_CONSTRUCTED_ANALYSIS_CHECKS' and len(analysis['checks'])==3
        assert pairing['status']=='PASS_CONSTRUCTED_PAIRING_SUPPLEMENT' and all(c['status']=='PASS' for c in pairing['checks'])
        assert len(transport['checks'])==5 and all(c['status']=='PASS' for c in transport['checks'])
        for name in('engine-checks-03','analysis-constructed-checks','analysis-pairing-checks-v3'):
            assert json.loads((TASK/'jobs'/name/'resource.json').read_text())['status']=='PASS'
        new(PUBLIC/'constructed-checks-v1.json',{'engine':engine,'analysis':analysis,'pairing_supplement':pairing,'transport':transport})
        figures=json.loads((TASK/'figure-programmatic-qa-v1.json').read_text())
        manual=json.loads((TASK/'figure-manual-review-v1.json').read_text());assert manual['status']=='PASS_FINAL_SIZE_AND_GRAYSCALE_REVIEW'
        assert len(manual['reviewed_files'])==6
        assert all(sha(ROOT/r['path'])==r['sha256'] for r in manual['reviewed_files'])
        assert manual['source_values_sha256']==figures['source_values_sha256']
        assert all(r['passed'] for r in figures['preflight'])
        new(PUBLIC/'figure-qa-v1.json',{'status':'PASS_STRUCTURAL_AND_FINAL_RENDER_REVIEW','source_values_sha256':figures['source_values_sha256'],
          'figure_count':3,'export_count':len(figures['outputs']),'text_bounds':figures['text_bounds'],'manual_review':manual})
        new(job/'result.json',{'status':'PASS_COMPLETE_M2_CLOSEOUT_AUDIT','method_decision':results['method_decision'],
          'biological_units':4164,'all_scientific_sources_pinned':True,'final_outcomes_opened':False,'m3_released':False})
        guard.finish('PASS');print(json.dumps({'status':'PASS_COMPLETE_M2_CLOSEOUT_AUDIT','cumulative_charged_cpu_hours':cpu['cumulative_charged_cpu_hours']}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:300]});guard.finish('FAIL');raise


if __name__=='__main__':main()
