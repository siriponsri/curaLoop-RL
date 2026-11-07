"""Reporting-only association repair; no job replay, source read or new clock."""
import hashlib,json,time
from pathlib import Path
from r0dq_core_v1 import PRIVATE,PUBLIC,save,now,archive_code

def load(path):return json.loads(path.read_text(encoding='utf-8'))
if __name__=='__main__':
    started=time.process_time();book=load(PRIVATE/'ledger.json');assert book['status']=='CLOSED'
    job=next(r for r in book['jobs'] if r['name']=='return-v1');assert job['status']=='NOT_RECONCILED'
    assert not (PUBLIC/'resource-receipts-v2.json').exists()
    capsule=PRIVATE/'remote-return/export-terminal';index=load(PRIVATE/'remote-return/export-capsule-index.json')
    pins={r['name']:r for r in index['files']}
    for name in ['payload-exit.json','result.json']:
        raw=(capsule/name).read_bytes();assert len(raw)==pins[name]['bytes'] and hashlib.sha256(raw).hexdigest()==pins[name]['sha256']
    result=load(capsule/'result.json');exit=load(capsule/'payload-exit.json')
    assert result['status']=='PASS_COMPLETE_PRIVATE_EXPORT' and exit['exit_code']==0 and exit['resource_limit'] is None
    full=load(PUBLIC/'complete-return-verified-v1.json');assert full['archive_sha256']==result['archive_sha256']
    save(PRIVATE/'ledger-before-export-reconciliation-v1.json',book)
    public=load(PUBLIC/'resource-receipts-v1.json');row=next(r for r in public['receipts'] if r['name']=='return-v1')
    assert row['status']=='NOT_RECONCILED'
    row.update(status='PASS',aggregate_tree_cpu_seconds=exit['cpu_seconds_tree'],wall_seconds=exit['wall_seconds'],
        stage_result=result['status'],terminal_cgroup_cpu_seconds=int(index['terminal']['CPUUsageNSec'])/1000000000,
        receipt_source='Verified private export-terminal capsule outside the task-root snapshot')
    public['reconciliation']={'reason':'Collector initially looked for the export receipt inside task/jobs; export helper has its separate terminal capsule',
        'utc':now(),'new_processing_or_budget_reset':False,'v1_retained':True}
    save(PUBLIC/'resource-receipts-v2.json',public)
    job['status']='PASS';book.setdefault('reconciliations',[]).append(public['reconciliation']);save(PRIVATE/'ledger.json',book)
    summary=load(PUBLIC/'qualification-summary-v1.json')
    summary['resource_reconciliation']=public['reconciliation'];summary['authoritative_resource_receipts']='resource-receipts-v2.json'
    summary['scientific_readout_or_closed_clock_changed']=False
    save(PUBLIC/'qualification-summary-v2.json',summary);archive_code(Path(__file__))
    assert all(j['status'] not in {'ADMITTED','RUNNING','NOT_RECONCILED'} for j in book['jobs'])
    print(json.dumps({'status':'PASS_REPORTING_ONLY_EXPORT_RECEIPT_RECONCILIATION','ledger_status':book['status'],
        'retained_cpu_seconds':book['worker_reserved_seconds']+book['utility_reserved_seconds'],'new_processing':False,
        'reporting_cpu_seconds':time.process_time()-started}))
