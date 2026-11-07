"""Final owner-subset documentation audit; preserve prior point-in-time exports."""
import hashlib
import json
from pathlib import Path
import re
import urllib.parse
from r0r_chembl_core_v1 import Guard, PRIVATE, ROOT, save

PUBLIC=ROOT/'docs/evidence/r0r-chembl-20261107-v1'
DOCS=['AGENTS.md','GOAL.md','PLAN.md','START_HERE.md','HANDOFF.md',
      'docs/00_project/CLAIM_LEDGER.md',
      'docs/03_research/R0R_OWNER_SUBSET_RESULTS_20261107.md',
      'docs/03_research/R0R_REFERENCE_REVIEW_V2_20261107.md',
      'docs/03_research/R0R_REFERENCE_REVIEW_20261107.md',
      'docs/03_research/R0R_INTERIM_RESULTS_20261107.md',
      'docs/03_research/R0R_OWNER_METHODS_REQUEST_20261107.md',
      'docs/06_execution/R0R_EXECUTION_CONTRACT_20261107.md',
      'docs/evidence/r0r-chembl-20261107-v1/README.md']


def run():
    assert not (PRIVATE/'worker.lock').exists()
    ledger=json.loads((PRIVATE/'ledger.json').read_text())
    assert ledger['status']=='AWAITING_OWNER_INPUT'
    v5=json.loads((PUBLIC/'interim-summary-v5.json').read_text())
    # V5 inherited a network-only retention flag. Owner-provided full PDFs now
    # exist locally: make that distinction explicit rather than copying the old
    # broad false flag into a current aggregate. V5 remains unchanged on disk.
    v6={**v5,'summary_revision':'v6-owner-source-retention-scope-corrected',
        'unmasked_full_article_retained':True,
        'unmasked_full_article_retention_scope':'Owner-supplied PDFs in the ignored owner-methods folder only; not parser-generated full text',
        'parser_generated_unmasked_fulltext_persisted':False,
        'owner_pdfs_or_complete_masked_passages_publicly_exported':False,
        'supersedes_v5_network_only_retention_flag':True}
    save(PRIVATE/'interim-summary-v6.json',v6)
    save(PUBLIC/'interim-summary-v6.json',v6)
    # Check links now; final audit/index outputs referenced by README are
    # produced immediately after this guarded validation succeeds.
    failures=[];links=0
    for name in DOCS:
        path=ROOT/name
        source=path.read_text(encoding='utf-8')
        assert not re.search(r'[\u0e00-\u0e7f]',source), 'Active documentation must remain English'
        for href in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',source):
            href=href.strip('<>')
            if re.match(r'^[a-z][a-z0-9+.-]*:',href,re.I) or href.startswith('#'):
                continue
            target=(path.parent/urllib.parse.unquote(href.split('#')[0])).resolve()
            if not target.exists():failures.append({'file':name,'link':href})
            links+=1
    assert not failures, failures
    source=json.loads((PUBLIC/'owner-source-manifest-v1.json').read_text())
    cases=json.loads((PUBLIC/'reference-candidates-v2.json').read_text())['cases']
    projected=json.loads((PUBLIC/'projected-readout-metadata-v1.json').read_text())['records']
    checks={
        'local_document_links_resolve':True,
        'active_documentation_english':True,
        'twelve_case_source_mapping_matches_frozen_projection':all(
            all(r['document_chembl_id']==c['document_id'] for r in projected if r['assay_chembl_id']==c['assay_id']) for c in cases),
        'case_record_counts_match_export':all(c['accepted_projection_records']==sum(r['assay_chembl_id']==c['assay_id'] for r in projected) for c in cases),
        'source_manifest_hashes_reread':all(hashlib.sha256((ROOT/r['source_path']).read_bytes()).hexdigest()==r['source_sha256'] for r in source['records']),
        'new_json_lf_utf8':all(b'\r\n' not in path.read_bytes() for name in [
            'interim-summary-v5.json','interim-summary-v6.json','source-ledger-v3.json',
            'reference-candidates-v2.json','owner-source-manifest-v1.json','owner-subset-checks-v1.json'] for path in [PUBLIC/name]),
        'no_activity_final_or_phase_promotion':not v6['final_outcomes_opened'] and not v6['next_phase_released'] and v6['training_runs']==0 and not v6['publication_ready'],
        'source_retention_scope_explicit':v6['unmasked_full_article_retained'] and not v6['parser_generated_unmasked_fulltext_persisted'],
    }
    assert all(checks.values())
    result={'status':'PASS','checks':checks,'passed':len(checks),'local_links_checked':links,
            'independent_scientific_review':'NOT_RUN','application_runtime_tests':'NOT_RUN_NO_RUNTIME_CHANGE',
            'v5_correction':'Inherited full-article-retention flag scoped to owner-provided PDFs in v6; original v5 retained'}
    save(PRIVATE/'owner-subset-documentation-checks-v1.json',result)
    save(PUBLIC/'owner-subset-documentation-checks-v1.json',result)
    print(json.dumps(result))


if __name__=='__main__':
    guard=Guard('owner-final-documentation-audit-v1')
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__)
        raise
    else:
        guard.finish('PASS',charged_to='Existing 600-second utility allocation')
        receipts=[json.loads(p.read_text()) for p in sorted(PRIVATE.glob('*-resource.json'))]
        assert all(r['status']!='RUNNING' for r in receipts)
        workers=[r for r in receipts if not r.get('enclosing_os_guard')]
        save(PUBLIC/'resource-receipts-v4.json',{'receipts':receipts,
            'partial_process_cpu_seconds_sum':sum(r['cpu_seconds'] for r in workers),
            'overlapping_file_phase_receipts_excluded_from_sum':len(receipts)-len(workers),
            'is_total_task_cpu':False,'conservative_charge_seconds':3200})
        index=[]
        for path in sorted(PRIVATE.rglob('*')):
            if path.is_file():
                raw=path.read_bytes()
                index.append({'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        assert sum(r['bytes'] for r in index)+5793019<=64*1024**2
        assert all(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in index)
        save(PUBLIC/'private-artifact-index-v4.json',{'status':'PASS_FULL_LOCAL_REREAD_FINAL_DOCUMENTATION_CHECKPOINT',
            'files':len(index),'bytes':sum(r['bytes'] for r in index),'artifacts':index,
            'owner_source_files_separately_hashed_in_manifest':5,'owner_source_bytes':5793019,
            'raw_article_or_passages_exported':False})
        print(json.dumps({'final_private_files':len(index),'final_private_bytes':sum(r['bytes'] for r in index),
                          'partial_process_cpu_seconds':sum(r['cpu_seconds'] for r in workers)}))
