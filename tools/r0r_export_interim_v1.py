"""Export source-limited review evidence and retain the running R0-R clock."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from r0r_chembl_core_v1 import Guard,PRIVATE,ROOT,save

def run():
    evidence=ROOT/'docs/evidence/r0r-chembl-20261107-v1'
    evidence.mkdir(parents=True,exist_ok=True)
    book=json.loads((PRIVATE/'ledger.json').read_text())
    assert book['status']=='ACTIVE' and not (PRIVATE/'worker.lock').exists()
    summary=json.loads((PRIVATE/'review-preparation-summary-v2.json').read_text())
    projection=json.loads((PRIVATE/'accepted-projection-index-v1.json').read_text())
    identities=json.loads((PRIVATE/'molecule-dispositions-v1.json').read_text())
    requests=json.loads((PRIVATE/'owner-download-requests-v1.json').read_text())
    old_index=json.loads((ROOT/'docs/evidence/r0-chembl-20261107-v1/private-artifact-index-v1.json').read_text())
    assert all(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'] for row in old_index['artifacts'])
    assert all(row['status']=='NO_EXACT_PROTECTED_CANONICAL_MATCH' for row in identities['records'])
    assert len(projection['records'])==86 and len({row['assay_chembl_id'] for row in projection['records']})==10
    receipts=[json.loads(path.read_text()) for path in sorted(PRIVATE.glob('*-resource.json')) if path.name!='interim-export-v1-resource.json']
    assert all(row['status']!='RUNNING' for row in receipts)
    summary.update({'status':'AWAITING_OWNER_SOURCES_AND_REFERENCE_REVIEW',
        'phase_complete':False,'next_phase_released':False,'old_r0_private_artifacts_unchanged':True,
        'remaining_http_attempts':48-len(book['attempts']),
        'remaining_conservative_cpu_seconds':3600-summary['conservative_cpu_seconds_charged'],
        'deadline_utc':book['deadline_utc'],'clock_paused_or_reset':False})
    book.update(status='AWAITING_OWNER_INPUT',review_checkpoint_utc=datetime.now(timezone.utc).isoformat(),
                allowed_next='Owner-supplied methods and reference review within unchanged authority; no source retry')
    save(PRIVATE/'ledger.json',book)
    save(PRIVATE/'interim-summary-v3.json',summary)
    public_requests=[]
    for item in requests['records']:
        entry=dict(item)
        entry['target_path']=str(Path(item['target_path']).relative_to(ROOT))
        public_requests.append(entry)
    exports={
        'interim-summary-v3.json':summary,
        'source-ledger-v1.json':book,
        'preflight-report-v1.json':json.loads((PRIVATE/'preflight-report-v1.json').read_text()),
        'selection-freeze-v1.json':json.loads((PRIVATE/'selection-freeze-v1.json').read_text()),
        'projected-readout-metadata-v1.json':{'records':projection['records'],'numeric_activity_values_present':False,
             'accepted_assays':10,'failed_cases_not_replaced':2,'failed_response_record_counts':'NOT_RETAINED'},
        'molecular-dispositions-v1.json':identities,
        'reference-candidates-v1.json':json.loads((PRIVATE/'reference-candidates-v1.json').read_text()),
        'owner-source-requests-v1.json':{'records':public_requests},
        'source-checks-v1.json':{'methods_mask_checks':json.loads((PRIVATE/'methods-mask-offline-checks-v1.json').read_text()),
              'request_boundary_checks':summary['offline_boundary_checks'],
              'scientific_gold':'NOT_ESTABLISHED','independent_review':'NOT_RUN'},
    }
    for name,payload in exports.items():save(evidence/name,payload)
    print(json.dumps({'status':'INTERIM_REVIEW_EXPORTED','http_attempts':len(book['attempts']),
        'source_bytes':book['decoded_bytes'],'charge_seconds':summary['conservative_cpu_seconds_charged'],
        'pending_source_documents':6,'remaining_requests':48-len(book['attempts']),
        'deadline_utc':book['deadline_utc'],'old_r0_artifacts_unchanged':True},indent=2))

if __name__=='__main__':
    guard=Guard('interim-export-v1')
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:
        guard.finish('PASS',charged_to='600-second utility reservation')
        evidence=ROOT/'docs/evidence/r0r-chembl-20261107-v1'
        receipts=[json.loads(path.read_text()) for path in sorted(PRIVATE.glob('*-resource.json'))]
        save(evidence/'resource-receipts-v1.json',{'receipts':receipts,
             'partial_cpu_seconds_sum':sum(row['cpu_seconds'] for row in receipts),
             'is_total_task_cpu':False,'conservative_charge_seconds':2460})
        rows=[]
        for path in sorted(PRIVATE.rglob('*')):
            if path.is_file():
                data=path.read_bytes()
                rows.append({'path':str(path.relative_to(ROOT)),'bytes':len(data),
                             'sha256':hashlib.sha256(data).hexdigest()})
        assert sum(row['bytes'] for row in rows)<=64*1024**2
        for row in rows:
            assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
        save(evidence/'private-artifact-index-v1.json',{'status':'PASS_FULL_LOCAL_REREAD_AT_REVIEW_CHECKPOINT',
             'files':len(rows),'bytes':sum(row['bytes'] for row in rows),'artifacts':rows,
             'unmasked_article_bodies_publicly_exported':False,'raw_molecular_structures_publicly_exported':False,
             'remote_work':'NOT_RUN','clock_continues':True})
        print(json.dumps({'private_files_reread':len(rows),'private_bytes_reread':sum(row['bytes'] for row in rows),
                          'resource_receipts':len(receipts),'partial_measured_cpu_seconds':sum(row['cpu_seconds'] for row in receipts)}))
