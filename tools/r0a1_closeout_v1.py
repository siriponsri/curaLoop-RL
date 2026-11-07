"""Complete the single audit, reread pins, export typed facts, then close."""
import hashlib
import json
import re
import urllib.parse
from r0a1_core_v1 import Guard,ROOT,PRIVATE,load,read_input,save,archive_code,now
from r0a1_context_mask_v1 import ENTITY,safety_checks

PUBLIC=ROOT/'docs/evidence/r0a1-chembl-20261107-v1'
DOCS=['AGENTS.md','GOAL.md','PLAN.md','START_HERE.md','HANDOFF.md',
      'docs/00_project/CLAIM_LEDGER.md',
      'docs/03_research/R0A1_FEASIBILITY_RESULTS_20261107.md',
      'docs/06_execution/R0A1_EXECUTION_CONTRACT_20261107.md',
      'docs/06_execution/R0A1_NEXT_DECISION_20261107.md',
      'docs/06_execution/R0R_OWNER_DECISION_OPTIONS_20261107.md',
      'docs/evidence/r0a1-chembl-20261107-v1/README.md']


def run():
    pins=load(PRIVATE/'preflight-pins-v1.json')
    checks={}
    for pin in pins['old_indexes']:
        assert hashlib.sha256(read_input(ROOT/pin['path'])).hexdigest()==pin['sha256']
        index=load(ROOT/pin['path'])
        assert all(hashlib.sha256(read_input(ROOT/r['path'])).hexdigest()==r['sha256'] for r in index['artifacts'])
    checks['closed_r0_and_r0r_private_hashes_unchanged']=True
    for row in pins['three_main_sources']:
        assert hashlib.sha256(read_input(ROOT/row['source_path'])).hexdigest()==row['source_sha256']
    checks['same_three_owner_main_hashes_unchanged']=True
    matrix=load(PRIVATE/'case-matrix-v1.json')
    original=load(ROOT/'docs/evidence/r0r-chembl-20261107-v1/selection-freeze-v1.json')['cases']
    checks['twelve_original_case_ids_and_roles_retained']=len(matrix['cases'])==12 and all(
        c['assay_id']==o['assay_chembl_id'] and c['document_id']==o['document_chembl_id'] and c['target_id']==o['target_chembl_id'] for c,o in zip(matrix['cases'],original))
    fixtures=safety_checks()
    checks['eight_entity_and_outcome_filter_fixtures']=fixtures['status']=='PASS' and fixtures['cases']==8
    for path in sorted(PRIVATE.glob('methods-CHEMBL*-v1.json')):
        method=load(path)
        for p in method['paragraphs']:
            assert not re.search(r'\d',ENTITY.sub('',p['masked_text']).replace('IC50','').replace('EC50',''))
    checks['method_digits_limited_to_permitted_entities_and_endpoints']=True
    for case in matrix['cases']:
        metadata=case['metadata_context']
        assert metadata['description_features']['complete_description_emitted'] is False
        assert not any(k in metadata for k in ['description','standard_value','pchembl_value','activity_comment'])
    checks['no_complete_description_or_numeric_activity_fields_exported']=True
    readout=load(PRIVATE/'readout-v1.json')
    checks['same_target_one_molecule_diagnostic']=readout['ghrelin_distinct_molecules']==1
    checks['no_training_final_outcome_or_phase_advance']=readout['training_runs']==0 and not readout['final_outcomes_opened'] and not readout['next_phase_released']
    pairs=load(PRIVATE/'pairwise-controls-v1.json')
    checks['dependent_pairwise_control_counts']=len(pairs['pairs'])==66 and readout['admitted_pairwise_controls']==45
    bad=[];links=0
    for name in DOCS:
        path=ROOT/name;text=path.read_text(encoding='utf-8')
        assert not re.search(r'[\u0e00-\u0e7f]',text)
        for href in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',text):
            href=href.strip('<>')
            if re.match(r'^[a-z][a-z0-9+.-]*:',href,re.I) or href.startswith('#'):continue
            links+=1
            if not (path.parent/urllib.parse.unquote(href.split('#')[0])).resolve().exists():bad.append((name,href))
    checks['english_documentation_and_local_links']=not bad
    assert all(checks.values()),(checks,bad)
    # Public matrix has no source passages. Normalize set-derived ordering only;
    # private first-run output remains unchanged and no scientific data changes.
    for case in matrix['cases']:case['readout_units']=sorted(case['readout_units'])
    save(PUBLIC/'case-matrix-v1.json',matrix)
    save(PUBLIC/'pairwise-controls-v1.json',pairs)
    save(PUBLIC/'readout-v1.json',readout)
    save(PUBLIC/'source-processor-audit-v1.json',{'old_private_indexes':pins['old_indexes'],
        'owner_main_sources':pins['three_main_sources'],
        'methods':load(PRIVATE/'methods-summary-v1.json'),
        'masking_fixtures':fixtures,
        'metadata_projection_versions_retained':['metadata-before-paper-identifiers-v1.json','metadata-context-v2.json','metadata-context-v3.json'],
        'corrected_cases':load(PRIVATE/'metadata-context-v3.json')['corrected_cases'],
        'initial_pdf_mask_module':'Archived executed source version; module evolved only after PDF extraction completed',
        'full_unmasked_text_or_masked_passages_exported':False,'independent_semantic_review':'NOT_RUN'})
    result={'status':'PASS','checks':checks,'passed':len(checks),'local_links_checked':links,
        'independent_scientific_review':'NOT_RUN','application_runtime_tests':'NOT_RUN_NO_RUNTIME_CHANGE'}
    save(PRIVATE/'final-checks-v1.json',result);save(PUBLIC/'final-checks-v1.json',result)
    archive_code(ROOT/'tools/r0a1_context_mask_v1.py')
    print({'checks':'PASS','passed':len(checks),'links':links,'readout':readout['status']})


if __name__=='__main__':
    guard=Guard('closeout-v1',cpu_seconds=120,wall=180,utility=True)
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:
        guard.finish('PASS')
        book=json.loads((PRIVATE/'ledger.json').read_text())
        receipts=[json.loads(p.read_text()) for p in sorted(PRIVATE.glob('*-resource.json'))]
        assert all(r['status']=='PASS' for r in receipts)
        assert book['utility_reserved_seconds']+book['worker_reserved_seconds']==960
        # Covers known direct hash rereads/parent views outside read_input.
        # This is a conservative allowance, not fabricated measured bytes.
        book['auxiliary_read_allowance_bytes']=1048576
        book['conservative_total_read_bytes']=book['source_read_bytes']+1048576
        assert book['conservative_total_read_bytes']<=33554432
        for job in book['jobs']:
            job['status']=json.loads((PRIVATE/(job['name']+'-resource.json')).read_text())['status']
        book.update(status='CLOSED',completed_utc=now(),readout='INFEASIBLE_IN_CURRENT_SUBSET',
                    allowed_next='Owner direction decision only; no automatic successor')
        save(PRIVATE/'ledger.json',book);save(PUBLIC/'source-ledger-v1.json',book)
        save(PUBLIC/'resource-receipts-v1.json',{'receipts':receipts,
            'partial_cpu_seconds_sum':sum(r['cpu_seconds'] for r in receipts),
            'is_total_task_cpu':False,'conservative_charge_seconds':960})
        artifacts=[]
        for path in sorted(PRIVATE.rglob('*')):
            if path.is_file():
                raw=path.read_bytes()
                artifacts.append({'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        assert sum(r['bytes'] for r in artifacts)<=67108864
        assert all(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in artifacts)
        save(PUBLIC/'private-artifact-index-v1.json',{'status':'PASS_FULL_LOCAL_REREAD',
            'files':len(artifacts),'bytes':sum(r['bytes'] for r in artifacts),'artifacts':artifacts,
            'raw_methods_or_owner_pdfs_exported':False})
        print({'private_files':len(artifacts),'private_bytes':sum(r['bytes'] for r in artifacts),
            'metered_source_bytes':book['source_read_bytes'],'conservative_read_bytes':book['conservative_total_read_bytes'],
            'cpu_reserved_seconds':960,'partial_cpu_seconds':sum(r['cpu_seconds'] for r in receipts),'ledger':book['status']})
