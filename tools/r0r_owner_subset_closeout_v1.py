"""Audit/export the owner's three-paper subset without publishing passages."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
from r0r_chembl_core_v1 import Guard, PRIVATE, ROOT, save
from r0r_owner_methods_mask_v2 import safety_checks

PUBLIC=ROOT/'docs/evidence/r0r-chembl-20261107-v1'
AVAILABLE={'CHEMBL1138492':'S1','CHEMBL1140224':'S2','CHEMBL1140235':'S3','CHEMBL1156448':'S4'}
DEFERRED={'CHEMBL1136971','CHEMBL1141686','CHEMBL1156685'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    book=json.loads((PRIVATE/'ledger.json').read_text())
    old=json.loads((PUBLIC/'source-ledger-v2.json').read_text())
    checks={}
    assert book['status']=='ACTIVE' and not (PRIVATE/'worker.lock').exists()
    checks['no_new_http_or_stopped_source_retry']=book['attempts']==old['attempts'] and book['stopped_sources']==old['stopped_sources']
    charge=book['worker_reserved_seconds']+book['utility_charge_seconds']
    checks['unchanged_resource_caps']=charge==3200 and book['decoded_bytes']==13076188 and charge<=3600 and book['decoded_bytes']<=32*1024**2
    checks['deadline_unchanged']=book['release_utc']==old['release_utc'] and book['deadline_utc']==old['deadline_utc']
    selection=json.loads((PRIVATE/'selection-freeze-v1.json').read_text())
    frozen=json.loads((PUBLIC/'selection-freeze-v1.json').read_text())
    questions=json.loads((PRIVATE/'pre_evidence_questions_v1.json').read_text())
    checks['all_twelve_frozen_cases_and_questions_retained']=selection==frozen and len(selection['cases'])==len(questions['cases'])==12
    accepted=json.loads((PRIVATE/'accepted-projection-index-v1.json').read_text())['records']
    keys={'activity_id','assay_chembl_id','document_chembl_id','molecule_chembl_id','standard_type','standard_units','type','units'}
    checks['exact_safe_projection_and_original_counts']=all(set(row)==keys for row in accepted) and len(accepted)==86 and len({r['assay_chembl_id'] for r in accepted})==10
    old_index=json.loads((ROOT/'docs/evidence/r0-chembl-20261107-v1/private-artifact-index-v1.json').read_text())
    checks['closed_r0_artifact_hashes_unchanged']=all(digest(ROOT/row['path'])==row['sha256'] for row in old_index['artifacts'])
    checks['original_r0r_input_hashes_unchanged']=all(digest(ROOT/row['output_path'])==row['output_sha256'] for row in book['attempts'] if row['status']=='PASS')
    inputs=json.loads((PRIVATE/'owner-file-metadata-v1.json').read_text())['records']
    checks['five_fixed_owner_files_hash_verified']=len(inputs)==5 and all(digest(ROOT/r['source_path'])==r['source_sha256'] and (ROOT/r['source_path']).stat().st_size==r['source_bytes']<=4194304 for r in inputs)
    mains=[r for r in book['local_source_intakes'] if r['source_part']=='main' and r['status']=='MASKED_METHODS_AVAILABLE_NOT_ADJUDICATED']
    checks['three_main_dois_and_masked_outputs_verified']=len(mains)==3 and all(r['doi_in_front_matter'] and digest(ROOT/r['output_path'])==r['output_sha256'] for r in mains)
    masks=[json.loads((ROOT/r['output_path']).read_text()) for r in mains]
    checks['no_unmasked_decimal_numerals_in_new_passages']=all(not re.search(r'\d', p['masked_text'].replace('IC50','').replace('EC50','')) for m in masks for p in m['paragraphs'])
    checks['methods_only_fixture_checks']=safety_checks()['status']=='PASS'
    supplements=[r for r in book['local_source_intakes'] if r['source_part']=='supplement']
    checks['supplements_not_promoted_to_extra_papers_or_references']=len(supplements)==2 and all(r['status'].startswith('QUARANTINE') and r['title_token_match'] for r in supplements)
    failed=[r for r in book['local_source_intakes'] if r['status']=='FAILED_RESOURCE_LIMIT_NO_MASKED_OUTPUT']
    repaired=[r for r in mains if r.get('local_processing_repair')]
    checks['failed_local_job_and_charge_retained']=len(failed)==len(repaired)==1 and failed[0]['cpu_reserved_seconds']==20 and repaired[0]['previous_charge_retained'] and not repaired[0]['network_source_retry']
    checks['no_scope_replacement']=set(r['document_chembl_id'] for r in selection['cases'])==set(AVAILABLE)|DEFERRED
    assert all(checks.values()), [k for k,v in checks.items() if not v]
    source_rows=[]
    for row in inputs:
        final=next(r for r in reversed(book['local_source_intakes']) if r['filename']==row['filename'])
        output=json.loads((ROOT/final['output_path']).read_text()) if final.get('output_path') else {}
        source_rows.append({**row,'association_status':final.get('association_status'),
                            'methods_status':final['status'],
                            'retained_paragraphs':len(output.get('paragraphs',[])),
                            'boundary_start':output.get('boundary_start'), 'boundary_end':output.get('boundary_end'),
                            'masked_output_sha256':final.get('output_sha256'),
                            'raw_source_redistributed':False})
    cases=[]
    for row in selection['cases']:
        assay,doc=row['assay_chembl_id'],row['document_chembl_id']
        records=[r for r in accepted if r['assay_chembl_id']==assay]
        available=doc in AVAILABLE
        cases.append({'assay_id':assay,'document_id':doc,'target_id':row['target_chembl_id'],
                      'assay_type':row['assay_type'],'accepted_projection_records':len(records),
                      'readout_pairs':[{'type':kind,'units':unit} for kind,unit in sorted({(r['standard_type'],r['standard_units']) for r in records}, key=str)],
                      'source_note':AVAILABLE.get(doc), 'document_methods_available':available,
                      'source_availability':'METHODS_DRAFT_AVAILABLE' if available else 'DEFERRED_BY_OWNER_NO_PURCHASE',
                      'reference_status':'PENDING_OWNER_REVIEW' if available else 'SOURCE_UNAVAILABLE_NOT_NEGATIVE',
                      'assay_specific_method_mapping':'UNRESOLVED' if available else 'NOT_EVALUABLE',
                      'pooling_authorized':False,'molecular_decision_gain':'NOT_ESTABLISHED',
                      'rejected_projection_retained':not bool(records)})
    covered=[r for r in accepted if r['document_chembl_id'] in AVAILABLE]
    null=[r for r in accepted if r['standard_units'] is None]
    summary=json.loads((PUBLIC/'interim-summary-v4.json').read_text())
    summary.update(status='OWNER_SUBSET_PROCESSING_COMPLETE_REFERENCE_REVIEW_PENDING',
        summary_revision='v5-owner-three-paper-subset',
        owner_articles_supplied=3,owner_related_supplements=2,owner_subset_processing_complete=True,
        methods_documents_available=4,cases_with_methods=sum(c['document_methods_available'] for c in cases),
        admitted_cases_with_document_methods=sum(c['document_methods_available'] and c['accepted_projection_records']>0 for c in cases),
        accepted_records_with_document_methods=len(covered),
        distinct_molecules_with_document_methods=len({r['molecule_chembl_id'] for r in covered}),
        new_masked_methods_paragraphs=sum(len(m['paragraphs']) for m in masks),
        unavailable_source_documents=sorted(DEFERRED),documents_needing_owner_source=0,
        further_downloads_requested=False,unavailable_sources_not_replaced=True,
        standard_unit_null_records=len(null),null_unit_source_documents=sorted({r['document_chembl_id'] for r in null}),
        null_units_resolved=0,assay_specific_method_mappings_adjudicated=0,
        verified_decision_changes='NOT_ESTABLISHED',verified_molecular_decision_changes='NOT_ESTABLISHED',
        independent_reference_gold='NOT_ESTABLISHED',independent_scientific_review='NOT_RUN',
        phase_complete=False,next_phase_released=False,reference_status='PENDING_OWNER_REVIEW',
        decoded_bytes=book['decoded_bytes'],conservative_cpu_seconds_charged=charge,
        remaining_conservative_cpu_seconds=3600-charge,owner_local_file_attempts=len(book['local_source_intakes']),
        owner_unique_files=5,retained_local_resource_failures=1,controlled_local_processing_repairs=1,
        new_http_requests=0,raw_source_bytes=sum(r['source_bytes'] for r in inputs),
        clock_paused_or_reset=False,owner_subset_checks=checks,
        scientific_gate='REVISE_PENDING_REFERENCE_REVIEW',publication_ready=False)
    book.setdefault('state_history',[]).append({'from':book['status'],'to':'AWAITING_OWNER_INPUT',
        'utc':datetime.now(timezone.utc).isoformat(),
        'reason':'Three supplied articles processed; other three deferred by owner; reference review needed, no next phase'})
    book.update(status='AWAITING_OWNER_INPUT',review_checkpoint_utc=datetime.now(timezone.utc).isoformat(),
                allowed_next='Owner reference review only; no automatic extra source intake, final outcomes or next phase')
    for name,payload in {'interim-summary-v5.json':summary,
        'owner-source-manifest-v1.json':{'records':source_rows,'owner_articles':3,'supplements':2,'deferred_document_ids':sorted(DEFERRED),'no_purchase':True},
        'reference-candidates-v2.json':{'status':'PENDING_OWNER_REVIEW','cases':cases,'independent_gold_established':False},
        'owner-subset-checks-v1.json':{'status':'PASS','checks':checks,'passed':len(checks),'independent_semantic_review':'NOT_RUN'}}.items():
        save(PRIVATE/name,payload);save(PUBLIC/name,payload)
    save(PRIVATE/'ledger.json',book)
    save(PUBLIC/'source-ledger-v3.json',book)
    print(json.dumps({'status':summary['status'],'cases_with_document_methods':summary['cases_with_methods'],
        'admitted_cases_with_document_methods':summary['admitted_cases_with_document_methods'],
        'records_with_document_methods':len(covered),'distinct_covered_molecules':summary['distinct_molecules_with_document_methods'],
        'checks_passed':len(checks),'conservative_cpu_seconds':charge,'decoded_bytes':book['decoded_bytes']}))


if __name__=='__main__':
    guard=Guard('owner-subset-closeout-v1')
    try:
        run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__)
        raise
    else:
        guard.finish('PASS',charged_to='Existing 600-second utility allocation')
        resources=[json.loads(path.read_text()) for path in sorted(PRIVATE.glob('*-resource.json'))]
        # File-phase receipts overlap their enclosing worker; never sum twice.
        workers=[r for r in resources if not r.get('enclosing_os_guard')]
        assert all(r['status']!='RUNNING' for r in resources)
        save(PUBLIC/'resource-receipts-v3.json',{'receipts':resources,
            'partial_process_cpu_seconds_sum':sum(r['cpu_seconds'] for r in workers),
            'overlapping_file_phase_receipts_excluded_from_sum':len(resources)-len(workers),
            'is_total_task_cpu':False,'conservative_charge_seconds':3200})
        index=[]
        for path in sorted(PRIVATE.rglob('*')):
            if path.is_file():
                raw=path.read_bytes()
                index.append({'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        assert sum(row['bytes'] for row in index)+5793019<=64*1024**2
        assert all(digest(ROOT/row['path'])==row['sha256'] for row in index)
        save(PUBLIC/'private-artifact-index-v3.json',{'status':'PASS_FULL_LOCAL_REREAD',
            'files':len(index),'bytes':sum(r['bytes'] for r in index),'artifacts':index,
            'owner_source_files_separately_hashed_in_manifest':5,'owner_source_bytes':5793019,
            'raw_article_or_passages_exported':False})
        print(json.dumps({'private_files_reread':len(index),'private_bytes_reread':sum(r['bytes'] for r in index),
            'old_r0_hashes_unchanged':True,'partial_process_cpu_seconds':sum(r['cpu_seconds'] for r in workers)}))
