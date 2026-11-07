"""Reconcile added public-repository checks and controlled masking verification."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from r0r_chembl_core_v1 import Guard,PRIVATE,ROOT,save

def run():
    evidence=ROOT/'docs/evidence/r0r-chembl-20261107-v1'
    book=json.loads((PRIVATE/'ledger.json').read_text())
    assert book['status']=='ACTIVE'
    rows=book['attempts']
    assert len(rows)<=48 and book['decoded_bytes']<=32*1024**2
    original=next(row for row in rows if row['source']=='methods-CHEMBL1138492')
    verification=next(row for row in rows if row['source']=='verification-S1-masked-methods')
    assert verification['status']=='PASS'
    assert original['transit_sha256']==verification['transit_sha256']
    assert original['output_sha256']==verification['output_sha256']
    assert verification['full_text_doi_verified']=='10.1021/jm900186m'
    assert (PRIVATE/'code'/(verification['mask_module_sha256']+'.py')).exists()
    before=next(row for row in rows if row['source']=='status-before')
    final=next(row for row in rows if row['source']=='status-final')
    assert json.loads((ROOT/before['output_path']).read_text())==json.loads((ROOT/final['output_path']).read_text())
    for row in rows:
        if row['status']=='PASS':
            assert hashlib.sha256((ROOT/row['output_path']).read_bytes()).hexdigest()==row['output_sha256']
    summary=json.loads((PRIVATE/'interim-summary-v3.json').read_text())
    summary.update(summary_revision='v4-current-review-checkpoint',http_attempts=len(rows),
        successes=sum(row['status']=='PASS' for row in rows),decoded_bytes=book['decoded_bytes'],
        conservative_cpu_seconds_charged=book['utility_charge_seconds']+book['worker_reserved_seconds'],
        stopped_sources=book['stopped_sources'],remaining_http_attempts=48-len(rows),
        remaining_conservative_cpu_seconds=3600-book['utility_charge_seconds']-book['worker_reserved_seconds'],
        repository_handles_resolved=4,repository_pages_with_no_admitted_attachment=2,
        repository_pages_http403=2,
        controlled_mask_reextraction={'status':'PASS_SAME_INPUT_AND_MASKED_OUTPUT_HASHES',
            'source':'verification-S1-masked-methods','module_sha256':verification['mask_module_sha256'],
            'full_text_doi_verified':verification['full_text_doi_verified'],
            'historical_first_module_hash_retroactively_inferred':False,'independent_scientific_review':False})
    book.setdefault('state_history',[]).append({'from':book['status'],'to':'AWAITING_OWNER_INPUT',
        'utc':datetime.now(timezone.utc).isoformat(),
        'reason':'Independent public repository checks and controlled extraction verification complete; sources and reference review still required'})
    book.update(status='AWAITING_OWNER_INPUT',review_checkpoint_utc=datetime.now(timezone.utc).isoformat())
    save(PRIVATE/'ledger.json',book)
    save(PRIVATE/'interim-summary-v4.json',summary)
    save(evidence/'interim-summary-v4.json',summary)
    save(evidence/'source-ledger-v2.json',book)
    public_requests=json.loads((evidence/'owner-source-requests-v1.json').read_text())
    for item in public_requests['records']:
        if item['document_id']=='CHEMBL1140235':item['additional_repository_check']='Two listed institutional records returned HTTP403'
        elif item['document_id'] in ('CHEMBL1140224','CHEMBL1156685'):item['additional_repository_check']='Handle resolved and page returned, but no admitted PDF/download link or citation metadata was extracted'
    save(evidence/'owner-source-requests-v2.json',public_requests)
    print(json.dumps({'status':summary['status'],'attempts':summary['http_attempts'],
        'successes':summary['successes'],'source_bytes':summary['decoded_bytes'],
        'conservative_cpu_seconds':summary['conservative_cpu_seconds_charged'],
        'remaining_requests':summary['remaining_http_attempts'],
        'mask_verification':summary['controlled_mask_reextraction']['status']},indent=2))

if __name__=='__main__':
    guard=Guard('finish-checkpoint-v2')
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:
        guard.finish('PASS',charged_to='600-second utility reservation')
        evidence=ROOT/'docs/evidence/r0r-chembl-20261107-v1'
        receipts=[json.loads(path.read_text()) for path in sorted(PRIVATE.glob('*-resource.json'))]
        save(evidence/'resource-receipts-v2.json',{'receipts':receipts,
            'partial_cpu_seconds_sum':sum(row['cpu_seconds'] for row in receipts),
            'is_total_task_cpu':False,'conservative_charge_seconds':3060})
        index=[]
        for path in sorted(PRIVATE.rglob('*')):
            if path.is_file():
                data=path.read_bytes()
                index.append({'path':str(path.relative_to(ROOT)),'bytes':len(data),
                              'sha256':hashlib.sha256(data).hexdigest()})
        assert sum(row['bytes'] for row in index)<=64*1024**2
        for row in index:assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
        save(evidence/'private-artifact-index-v2.json',{'status':'PASS_FULL_LOCAL_REREAD_AT_CURRENT_REVIEW_CHECKPOINT',
            'files':len(index),'bytes':sum(row['bytes'] for row in index),'artifacts':index,
            'raw_unmasked_article_bodies_exported':False,'clock_continues':True})
        print(json.dumps({'private_files_reread':len(index),'private_bytes_reread':sum(row['bytes'] for row in index),
            'resource_receipts':len(receipts),'partial_measured_cpu_seconds':sum(row['cpu_seconds'] for row in receipts)}))
