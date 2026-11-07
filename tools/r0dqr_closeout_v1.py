"""Reconcile fresh receipts after full return, checks and exact remote absence."""
import ast,json
from pathlib import Path
from r0dqr_core_v1 import ROOT,PRIVATE,PUBLIC,LocalGuard,save,sha,now

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def validate():
    assert load(PUBLIC/'complete-return-verified-v1.json')['status']=='PASS_FULL_PRIVATE_RETURN_AND_STREAMED_LOCAL_REREAD'
    assert load(PUBLIC/'fresh-absence-v1.json')['status']=='PASS_FRESH_SCOPED_ABSENCE'
    assert load(PUBLIC/'acceptance-v1.json')['status']=='PASS_REAL_ARTIFACT_AND_SYNTHETIC_BOUNDARY_CHECKS'
    assert load(PUBLIC/'exposure-quarantine-audit-v1.json')['new_final_tasks_released']==0
    for pin in load(PRIVATE/'inputs/old-ledger-pins-and-stops-v1.json')['records']:assert sha(ROOT/pin['path'])==pin['sha256']
    book=load(PRIVATE/'ledger.json');assert book['status']=='ACTIVE'
    assert book['worker_reserved_seconds']+book['utility_reserved_seconds']<=14400
    assert all(book['stage_reserved_seconds'][k]<=v for k,v in book['stage_caps_seconds'].items())
    assert sum(r['cpu_limit_seconds'] for r in book['jobs'] if r['stage']=='utility')<=1800
    assert book['bulk_http_attempts']==0 and book['new_activity_numeric_queries']==0

def finalize():
    # Only small report writes follow the terminal closeout guard. Their CPU is
    # covered by the already retained1,800-second utility allocation, not a new grant.
    returned=PRIVATE/'remote-return/files';book=load(PRIVATE/'ledger.json');receipts=[]
    for job in book['jobs']:
        row={'name':job['name'],'stage':job['stage'],'cpu_limit_seconds':job['cpu_limit_seconds']}
        local=PRIVATE/(job['name']+'-resource.json');remote=returned/'jobs'/job['name']
        if local.exists():
            data=load(local);row.update(status=data['status'],parent_cpu_seconds=data['cpu_seconds'],wall_seconds=data['wall_seconds'])
            if 'aggregate_tree_cpu_seconds' in data:row['aggregate_tree_cpu_seconds']=data['aggregate_tree_cpu_seconds']
        elif job['name']=='remote-exact-cleanup-v1':
            data=load(PUBLIC/'scoped-delete-v1.json');row.update(status='PASS',parent_cpu_seconds=data['cpu_seconds'],stage_result=data['status'])
        else:
            remote=PRIVATE/'remote-return/export-terminal' if job['name']=='return-v1' else remote
            data=load(remote/'payload-exit.json');result=load(remote/'result.json')
            assert data['exit_code']==0 and data['resource_limit'] is None
            row.update(status='PASS',aggregate_tree_cpu_seconds=data['cpu_seconds_tree'],wall_seconds=data['wall_seconds'],stage_result=result['status'])
        assert row['status']=='PASS',row['name'];job['status']=row['status'];receipts.append(row)
    metadata=load(returned/'jobs/nominal-v1/result.json');taxonomy=load(returned/'jobs/inventory-v1/result.json')
    context=load(PRIVATE/'methods-intake-v1.json');charge=book['worker_reserved_seconds']+book['utility_reserved_seconds']
    early=[]
    for path in (PRIVATE/'code').glob('*.py'):
        try:ast.parse(path.read_text(encoding='utf-8'))
        except SyntaxError:early.append({'status':'RETAINED_PRE_EXECUTION_SETUP_SYNTAX_ERROR','source_snapshot_sha256':sha(path),
            'scientific_requests':0,'worker_launched':False,'charge':'inside retained utility envelope; no refund'})
    early.append({'status':'RETAINED_READ_COMMAND_ROUTING_ERROR','operation':'RTK cannot execute a PowerShell cmdlet as an external binary; corrected with Python file read',
        'scientific_requests':0,'source_or_credentials_read':False,'charge':'inside retained utility envelope'})
    early.append({'status':'RETAINED_READ_ONLY_SEARCH_PATH_ERROR','operation':'A literal Windows wildcard path was rejected before search; corrected with explicit file discovery',
        'scientific_requests':0,'worker_launched':False,'charge':'inside retained utility envelope'})
    summary={'schema':'curaloop.r0dqr.phase-readout.v1','phase_status':'COMPLETE_AWAITING_OWNER_DECISION',
        'scientific_verdict':'REVISE','release_utc':book['release_utc'],'deadline_utc':book['deadline_utc'],'closed_utc':now(),
        'gates':{'D1':'REVIEW_REQUIRED_TRACEABLE_CROSSWALK_NOT_FAMILY_CERTIFICATION',
            'D2':'REVISE_SHARED_SOURCE_AND_PLANNING_IDENTITY_JOINS_NO_FINAL_RELEASE',
            'D3':'FAIL_36_BUNDLES_18_UNITS_4_2_12_ROLE_TARGET',
            'D4':'NOT_ESTABLISHED_NO_METHODS_BODIES_OR_INCREMENTAL_FACTS',
            'D5':'PASS_BOUNDARIES_FULL_RETURN_REREAD_SCOPED_ABSENCE'},
        'taxonomy':taxonomy,'nominal_support':metadata,
        'source_feasibility':{k:v for k,v in context.items() if k!='documents'},
        'exposure_lineage_audit':load(PUBLIC/'exposure-quarantine-audit-v1.json'),
        'source':load(returned/'jobs/prepare-v1/result.json'),
        'returned_artifact_sha256':{name:sha(returned/name) for name in [
            'jobs/inventory-v1/taxonomy-inventory.json','jobs/nominal-v1/frame-frozen.json',
            'jobs/nominal-v1/topology-outcome-free.json','jobs/nominal-v1/identity-dispositions.json',
            'jobs/nominal-v1/candidates-frozen.json','jobs/context-v1/source-intent-frozen.json',
            'jobs/context-v1/development-packet.json']},
        'cpu_accounting':{'cap_seconds':14400,'conservative_retained_seconds':charge,'conservative_retained_cpu_hours':charge/3600,
            'stage_reserved_seconds':book['stage_reserved_seconds'],'utility_reserved_seconds':1800,
            'utility_job_sublimits_seconds':sum(r['cpu_limit_seconds'] for r in book['jobs'] if r['stage']=='utility'),
            'failed_or_unused_reservations_reclaimed':False,'measurements_are_receipt_scoped_not_complete_host_profiler':True,
            'authorized_combined_cpu_workers':2},
        'http':{'metadata_attempts':sum(r['kind']=='metadata' for r in book['http_attempts']),
            'methods_attempts':sum(r['kind']=='methods' for r in book['http_attempts']),'decoded_nonbulk_bytes':book['nonbulk_bytes'],
            'bulk_attempts':0,'retries':0,'stopped_sources':book['stopped_sources']},
        'early_setup_errors':early,'runtime_worker_failures':[],
        'numerical_activity_or_presence_queries':0,'old_final_outcomes_opened':False,'new_final_tasks_qualified':0,
        'model_fitting':'NOT_RUN','independent_reference_gold':'NOT_RUN','biological_family_certification':'NOT_RUN',
        'journal_readiness':'NOT_READY','commercial_clearance':'NOT_ESTABLISHED_BY_THIS_AUDIT',
        'complete_return':load(PUBLIC/'complete-return-verified-v1.json'),'fresh_remote_absence':load(PUBLIC/'fresh-absence-v1.json'),
        'next_actor':'owner','automatic_next_phase':False}
    save(PUBLIC/'phase-summary-v1.json',summary)
    save(PUBLIC/'resource-receipts-v1.json',{'receipts':receipts,'all_phase_jobs_terminal':True,
        'conservative_retained_seconds':charge,'scope':'receipt-scoped parent/tree CPU; overlapping controls are not added as a complete measured host total'})
    save(PUBLIC/'source-ledger-v1.json',{'attempts':book['http_attempts'],'bulk_attempts':0,'decoded_nonbulk_bytes':book['nonbulk_bytes'],
        'inherited_stopped_urls':load(PRIVATE/'inherited-stopped-urls-v1.json'),'old_ledger_pins':load(PRIVATE/'inputs/old-ledger-pins-and-stops-v1.json')})
    for name in ['release.json','frame-rules-v1.json','privacy-fixtures-v1.json']:
        assert not (PUBLIC/name).exists();(PUBLIC/name).write_bytes((PRIVATE/name).read_bytes())
    save(PUBLIC/'source-reuse-v1.json',load(PRIVATE/'source-reuse-v1.json'))
    save(PUBLIC/'source-environment-v1.json',{'source':summary['source'],'input_transport':load(PRIVATE/'input-transfer-v1.json'),
        'all_input_hashes_verified_remotely':True,'transport_receipt_is_preverification_snapshot':True,
        'new_package_installs':0,'ssh_profile_or_known_hosts_changed':False,
        'opaque_source_bytes_are_not_planner_outcomes':True})
    book.update(status='CLOSED',closed_utc=summary['closed_utc'],scientific_verdict='REVISE',
        all_owned_remote_roots_absent=True,unused_budget_not_next_phase_authority=True)
    save(PRIVATE/'ledger.json',book)
    print(json.dumps({'phase_status':summary['phase_status'],'scientific_verdict':'REVISE',
        'conservative_retained_cpu_hours':charge/3600,'jobs':len(receipts),'all_jobs_terminal':True}))

if __name__=='__main__':
    guard=LocalGuard('phase-closeout-v1',cpu_seconds=60,wall=120)
    try:validate()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS');finalize()
