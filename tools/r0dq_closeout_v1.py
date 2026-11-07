"""Collect actual phase evidence after complete return and scoped absence."""
import hashlib,json
from pathlib import Path
from r0dq_core_v1 import PRIVATE,PUBLIC,ROOT,save,now,LocalGuard

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    returned=PRIVATE/'remote-return/files'
    full=load(PUBLIC/'complete-return-verified-v1.json');absence=load(PUBLIC/'fresh-absence-v1.json')
    assert full['status']=='PASS_FULL_PRIVATE_RETURN_AND_STREAMED_LOCAL_REREAD' and absence['status']=='PASS_FRESH_SCOPED_ABSENCE'
    assert load(PUBLIC/'qualification-acceptance-v1.json')['status']=='PASS_REAL_DERIVED_ARTIFACT_INVARIANTS'
    bulk=load(PRIVATE/'download-status-latest.json')['result.json'];assert bulk['status']=='PASS_ARCHIVE_DIGEST'
    unpack=load(returned/'jobs/unpack-v2/result.json');assert unpack['status']=='PASS_VERIFIED_EXTRACTION_AND_SCHEMA'
    frame=load(returned/'jobs/frame-v3/result.json');assert frame['status']=='PASS_METADATA_FRAME_FROZEN'
    support=load(returned/'jobs/support-v1/result.json');assert support['status']=='PASS_BOUNDED_SUPPORT_QUALIFICATION'
    context=load(PRIVATE/'methods-intake-v1.json')
    review=load(PRIVATE/'context-review-v1.json')
    assert review['independent_gold_established'] is False
    book=load(PRIVATE/'ledger.json');assert book['status']=='ACTIVE'
    charge=book['worker_reserved_seconds']+book['utility_reserved_seconds'];assert charge<=57600
    assert all(book['stage_reserved_seconds'][k]<=v for k,v in book['stage_caps_seconds'].items())
    assert sum(r['cpu_limit_seconds'] for r in book['jobs'] if r['stage']=='utility')<=3600
    for item in book['http_attempts']:
        if item['name']=='chembl37-bulk-archive':
            item.update(status=bulk['status'],decoded_bytes=bulk['bytes'],sha256=bulk['sha256'],http_status=200,reconciled_utc=now())
    book['bulk_decoded_bytes']=bulk['bytes']
    receipts=[];failures=[]
    for job in book['jobs']:
        local=PRIVATE/(job['name']+'-resource.json');remote=returned/'jobs'/job['name']
        row={'name':job['name'],'stage':job['stage'],'retained_cpu_limit_seconds':job['cpu_limit_seconds']}
        if local.exists():
            data=load(local);row.update(status=data['status'],wall_seconds=data['wall_seconds'],parent_cpu_seconds=data['cpu_seconds'])
            if 'aggregate_tree_cpu_seconds' in data:row['aggregate_tree_cpu_seconds']=data['aggregate_tree_cpu_seconds']
        elif (remote/'payload-exit.json').exists():
            data=load(remote/'payload-exit.json');row.update(status='PASS' if data['exit_code']==0 and data['resource_limit'] is None else 'FAIL',
                wall_seconds=data['wall_seconds'],aggregate_tree_cpu_seconds=data['cpu_seconds_tree'],exit_code=data['exit_code'],resource_limit=data['resource_limit'])
            if (remote/'result.json').exists():row['stage_result']=load(remote/'result.json')['status']
        elif job['name']=='remote-exact-cleanup-v1':
            data=load(PUBLIC/'scoped-delete-v1.json');row.update(status='PASS',parent_cpu_seconds=data['cpu_seconds'],stage_result=data['status'])
        elif job['name']=='return-v1':
            capsule=PRIVATE/'remote-return/export-terminal'
            data=load(capsule/'payload-exit.json');result=load(capsule/'result.json')
            row.update(status='PASS' if data['exit_code']==0 and data['resource_limit'] is None else 'FAIL',
                aggregate_tree_cpu_seconds=data['cpu_seconds_tree'],wall_seconds=data['wall_seconds'],stage_result=result['status'])
        elif (remote/'controller-stop.json').exists():
            data=load(remote/'controller-stop.json');row.update(status='FAIL_STOPPED_QUERY_PLAN',stage_result=data['status'],
                aggregate_tree_cpu_seconds=int(data['state_before_stop']['CPUUsageNSec'])/1000000000)
        else:row['status']='NOT_RECONCILED'
        if row['name']=='frame-v1':row['scientific_use']='REJECTED_EMPTY_SQLITE_ENUM_REPRESENTATION; superseded before values'
        job['status']=row['status'];receipts.append(row)
        if row['status'].startswith('FAIL'):failures.append(row)
    groups=support['reserved_group_roles']
    target_met=all(groups.get(k,0)>=n for k,n in [('development',4),('validation',2),('final',12)]) and support['reserved_bundles']>=36
    context_met=(review['candidate_decision_sensitive_groups']>=2 and review['clear_context_controls']>=2
        and context['development_bundles']==8 and context['development_groups']==4)
    verdict='PASS_FOR_REFERENCE_REVIEW' if target_met and context_met else 'PILOT_ONLY_REVISE'
    summary={'schema':'curaloop.r0dq.phase-readout.v1','phase_status':'COMPLETE_AWAITING_OWNER_DECISION','scientific_verdict':verdict,
        'release_utc':book['release_utc'],'deadline_utc':book['deadline_utc'],'closed_utc':now(),
        'source':{'release':'ChEMBL_37','archive_bytes':bulk['bytes'],'archive_sha256':bulk['sha256'],**unpack['database']},
        'gates':{
            'G1_source':'PASS_PINNED_ARCHIVE_SCHEMA_AND_ATTRIBUTION; commercial clearance not established',
            'G2_protection':'PASS_IMPLEMENTED_KNOWN_IDENTITY_GATES; family/source certification pending',
            'G3_structural':'PASS_CANDIDATE_SUPPORT_TARGET' if target_met else 'FAIL_FULL_SCALE_TARGET; thresholds unchanged',
            'G4_context':'CANDIDATE_FACTS_FOR_REFERENCE_REVIEW' if context_met else 'NOT_ESTABLISHED; see source/access/projection limits',
            'G5_integrity_return':'PASS_FULL_PRIVATE_RETURN_REREAD_AND_SCOPED_ABSENCE'},
        'frame':frame,'support':support,'context':{k:v for k,v in context.items() if k!='documents'},'context_review':review,
        'cpu_accounting':{'cap_seconds':57600,'conservative_retained_seconds':charge,'utility_reserved_seconds':3600,
            'stage_reserved_seconds':book['stage_reserved_seconds'],'authorized_max_combined_cpu_workers':2,
            'measured_times_are_receipt_scoped_not_a_complete_host_profiler':True,'failed_reservations_reclaimed':False},
        'http':{'attempts':len(book['http_attempts']),'cap':96,'bulk_attempts':1,'bulk_bytes':book['bulk_decoded_bytes'],
            'nonbulk_decoded_bytes':book['nonbulk_decoded_bytes'],'stopped_sources':book['stopped_sources'],'automatic_retries':0},
        'retained_worker_failures':failures,'rejected_empty_frame_retained':True,
        'old_final_outcomes_queried':False,'planner_numeric_outcomes_exposed':False,'utility_or_topk_computed':False,
        'model_fitting':'NOT_RUN','biological_family_certification':'NOT_RUN','independent_reference_gold':'NOT_RUN',
        'journal_readiness':'NOT_READY','automatic_next_phase':False,'next_actor':'owner',
        'complete_return':full,'fresh_remote_absence':absence}
    summary['frozen_frame_diagnostics']=load(PRIVATE/'frame-readout-v1.json')
    summary['scaffold_similarity_audit']='NOT_APPLICABLE_TO_EMPTY_VALIDATION_AND_FINAL_ROLES; no chemical-OOD claim'
    save(PUBLIC/'qualification-summary-v1.json',summary)
    save(PUBLIC/'resource-receipts-v1.json',{'receipts':receipts,'conservative_retained_seconds':charge,
        'early_receipts_without_tree_cpu_are_not_promoted_to_full_measured_cpu':True})
    save(PUBLIC/'source-ledger-v1.json',{'attempts':book['http_attempts'],'nonbulk_decoded_bytes':book['nonbulk_decoded_bytes'],
        'bulk_decoded_bytes':book['bulk_decoded_bytes'],'inherited_stops_unchanged':True})
    save(PUBLIC/'source-manifest-v1.json',{'archive':bulk,'database':unpack['database'],'archive_entries':unpack['archive_entries'],
        'environment':{k:unpack[k] for k in ['rdkit_version','numpy_version','sqlite_runtime']},
        'terms':load(PRIVATE/'archive-source-pin-v1.json'),'additional_exposure':load(PRIVATE/'additional-exposure-pin-v1.json'),
        'original_4723_identity_protection_unchanged':True,'raw_source_data_private':True})
    for name in ['projection-fixtures-v2.json','selection-fixtures-v1.json','selection-fixtures-v2.json','pipeline-fixtures-v5.json','context-fixtures-v1.json','release.json','frame-rules-v1.json']:
        save(PUBLIC/name,load(PRIVATE/name))
    # Verify old intake ledgers have not changed while this fresh phase ran.
    old=load(PRIVATE/'inherited-source-stops-v1.json')
    for pin in old['old_ledgers']:assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256']
    book.update(status='CLOSED',closed_utc=summary['closed_utc'],scientific_verdict=verdict,
        unused_budget_not_a_next_phase_grant=True,all_remote_owned_roots_absent=True)
    save(PRIVATE/'ledger.json',book)
    print(json.dumps({'phase_status':summary['phase_status'],'scientific_verdict':verdict,'reserved_bundles':support['reserved_bundles'],
        'group_roles':groups,'conservative_retained_cpu_hours':charge/3600,'http_attempts':len(book['http_attempts'])}))

if __name__=='__main__':
    guard=LocalGuard('phase-readout-v1',cpu_seconds=60,wall=120,memory_mib=256)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
    # Reconcile this collector's terminal receipt after it has been written.
    book=load(PRIVATE/'ledger.json');receipt=load(PRIVATE/'phase-readout-v1-resource.json')
    next(j for j in book['jobs'] if j['name']=='phase-readout-v1')['status']=receipt['status'];save(PRIVATE/'ledger.json',book)
    public=load(PUBLIC/'resource-receipts-v1.json');row=next(r for r in public['receipts'] if r['name']=='phase-readout-v1')
    row.update(status=receipt['status'],wall_seconds=receipt['wall_seconds'],parent_cpu_seconds=receipt['cpu_seconds'])
    save(PUBLIC/'resource-receipts-v1.json',public)
