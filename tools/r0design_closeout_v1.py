"""Close the authorized review; preserve unresolved scientific/owner decisions."""
import json
from r0design_core_v1 import ROOT,PRIVATE,PUBLIC,Guard,save,sha,now

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def validate_close():
    cfg=ROOT/'research/configs/r0_design_review_protocol_20261107_v1.json'
    checks=load(PUBLIC/'protocol-validation-v1.json')
    assert checks['status']=='PASS_PROTOCOL_AUTHORITY_AND_SYNTHETIC_CONSTRAINT_CHECKS'
    assert checks['protocol_sha256']==sha(cfg) and (PUBLIC/'protocol-proposed-v1.json').read_bytes()==cfg.read_bytes()
    for pin in load(PRIVATE/'input-pins-v1.json')['inputs']+load(PRIVATE/'input-pins-v1.json')['old_ledgers']:
        assert sha(ROOT/pin['path'])==pin['sha256']
    book=load(PRIVATE/'ledger.json');assert book['status']=='ACTIVE'
    assert book['worker_reserved_seconds']+900<=3600
    assert all(book['stage_reserved_seconds'][k]<=v for k,v in book['stage_caps_seconds'].items())
    assert book['source_http_requests']==book['ssh_connections']==book['new_records_or_source_queries']==0

def finalize():
    # Small final report writes remain inside the already retained utility envelope.
    book=load(PRIVATE/'ledger.json');receipts=[]
    for job in book['jobs']:
        receipt=load(PRIVATE/(job['name']+'-resource.json'));assert receipt['status']=='PASS'
        job['status']='PASS';receipts.append({'name':job['name'],'stage':job['stage'],**receipt})
    charge=book['worker_reserved_seconds']+900;cfg=load(ROOT/'research/configs/r0_design_review_protocol_20261107_v1.json')
    docs=['docs/03_research/R0_DESIGN_REVIEW_PROTOCOL_20261107.md','docs/06_execution/R0_DESIGN_REVIEW_DECISIONS_20261107.md',
        'docs/06_execution/R0_SUPPORT_CENSUS_PROPOSAL_20261107.md','docs/06_execution/R0_DESIGN_REVIEW_CONTRACT_20261107.md']
    result={'schema':'curaloop.r0-design-review.readout.v1','phase_status':'COMPLETE_AWAITING_OWNER_DECISION',
        'design_status':'READY_FOR_OWNER_AND_DOMAIN_REVIEW','scientific_status':'REVISE',
        'release_utc':book['release_utc'],'deadline_utc':book['deadline_utc'],'closed_utc':now(),
        'base_commit':load(PRIVATE/'release.json')['base_commit'],'documents_sha256':{p:sha(ROOT/p) for p in docs},
        'protocol_sha256':sha(ROOT/'research/configs/r0_design_review_protocol_20261107_v1.json'),
        'design_diagnostic':load(PUBLIC/'design-diagnostic-v1.json'),
        'acceptance':{'protocol_specified':'PASS','known_failures_assigned':'PASS','artifact_and_synthetic_constraints':'PASS',
            'independent_domain_review':'NOT_RUN','method_novelty':'NOT_ESTABLISHED','qualified_benchmark':'NOT_RUN',
            'journal_readiness':'NOT_READY'},
        'remaining_decisions':cfg['remaining_decisions'],
        'next_proposal':cfg['next_census_proposal'],
        'cpu_accounting':{'cap_seconds':3600,'retained_seconds':charge,'retained_cpu_hours':charge/3600,
            'utility_reserved_seconds':900,'stage_reserved_seconds':book['stage_reserved_seconds'],
            'unused_or_failed_reservations_reclaimed':False,'receipt_scoped_cpu_not_complete_host_profiler':True},
        'activity_or_final_outcomes_opened':False,'new_source_records':0,'source_http_requests':0,'ssh_connections':0,
        'new_split_or_real_cohort_constructed':False,'model_fitting':'NOT_RUN','remote_root_created':False,
        'literature_freshness':'CACHED_REVIEW_ONLY_NO_NEW_VERIFICATION',
        'independent_review_claim':False,'next_actor':'owner','automatic_next_phase':False}
    save(PUBLIC/'phase-readout-v1.json',result)
    save(PUBLIC/'resource-receipts-v1.json',{'receipts':receipts,'all_jobs_terminal':True,
        'conservative_retained_seconds':charge,'normal_delivery_within_original_utility_reserve':True})
    (PUBLIC/'release.json').write_bytes((PRIVATE/'release.json').read_bytes())
    book.update(status='CLOSED',closed_utc=result['closed_utc'],design_status=result['design_status'],scientific_status='REVISE',
        unused_budget_not_next_phase_authority=True,old_ledgers_and_inputs_unchanged=True)
    save(PRIVATE/'ledger.json',book)
    print(json.dumps({'phase_status':result['phase_status'],'design_status':result['design_status'],
        'scientific_status':'REVISE','retained_cpu_hours':charge/3600,'jobs':len(receipts),'next_census':'NOT_RELEASED'}))

if __name__=='__main__':
    guard=Guard('design-review-closeout-v1',cpu=60,stage='review',wall=120,memory_mib=256)
    try:validate_close()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS');finalize()
