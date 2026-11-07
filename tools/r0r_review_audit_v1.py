"""Reconcile the actual admitted cases and retain source-limited review status."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from r0r_chembl_core_v1 import Guard,PRIVATE,ROOT,save,validate_spec

def run():
    book=json.loads((PRIVATE/'ledger.json').read_text())
    accepted=json.loads((PRIVATE/'accepted-projection-index-v1.json').read_text())
    summary=json.loads((PRIVATE/'review-preparation-summary-v1.json').read_text())
    selection=json.loads((PRIVATE/'selection-freeze-v1.json').read_text())['cases']
    candidates=json.loads((PRIVATE/'reference-candidates-v1.json').read_text())
    valid_ids={row['assay_chembl_id'] for row in accepted['records']}
    assert len(valid_ids)==10 and len(accepted['records'])==86
    assert len(selection)==12 and len(candidates['cases'])==12
    # v1's defaultdict lookup created two empty groups while preparing cases.
    # Count distinct source IDs with actual admitted rows, not dictionary slots.
    summary['accepted_projection_assays']=len(valid_ids)
    summary['summary_revision']='v2-reconciled'
    summary['v1_empty_defaultdict_groups_corrected']=True
    summary['failed_projection_cases_retained']=2
    summary['failed_projection_record_counts']='NOT_CAPTURED_BEFORE_REJECTION; no scientific response reconstructed'
    before=next(row for row in book['attempts'] if row['source']=='status-before' and row['status']=='PASS')
    after=next(row for row in book['attempts'] if row['source']=='status-after' and row['status']=='PASS')
    assert json.loads((ROOT/before['output_path']).read_text())==json.loads((ROOT/after['output_path']).read_text())
    assert json.loads((ROOT/before['output_path']).read_text())['chembl_db_version']=='ChEMBL_37'
    for row in book['attempts']:
        if row['status']=='PASS':
            path=ROOT/row['output_path']
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['output_sha256']
    for row in accepted['records']:
        assert set(row)=={'activity_id','assay_chembl_id','document_chembl_id','molecule_chembl_id','standard_type','standard_units','type','units'}
    class_registry=json.loads((ROOT/'.local/goal4r2a3-20261106-v1/protection-inputs/family-registry-v3.json').read_text())
    family_map={row['uniprot_accession']:row['family_id'] for row in class_registry['assays']}
    targets=json.loads((ROOT/'.local/r0-chembl-20261107-v1/016-chembl37-selected-targets.html').read_text())['targets']
    target_map={row['target_chembl_id']:{family_map[c['accession']] for c in row['target_components'] if c['accession'] in family_map} for row in targets}
    frozen_components={group for row in selection for group in target_map[row['target_chembl_id']]}
    ids1={row['molecule_chembl_id'] for row in accepted['records'] if row['assay_chembl_id']=='CHEMBL1000240'}
    ids2={row['molecule_chembl_id'] for row in accepted['records'] if row['assay_chembl_id']=='CHEMBL1000241'}
    offline={}
    safe={'url':'https://www.ebi.ac.uk/chembl/api/data/activity.json?assay_chembl_id=CHEMBL1000240&only=activity_id,assay_chembl_id,document_chembl_id,molecule_chembl_id,standard_type,standard_units&limit=20&order_by=activity_id'}
    validate_spec(safe);offline['approved_projection_admitted']=True
    for label,bad in [
        ('numeric_value_projection_rejected',safe['url'].replace('standard_units','standard_value')),
        ('result_filter_rejected',safe['url']+'&standard_value__gt=0'),
        ('abstract_lookup_rejected','https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core')]:
        try:validate_spec({'url':bad})
        except ValueError:offline[label]=True
        else:offline[label]=False
    assert all(offline.values())
    summary.update({'status':'REVIEW_READY_SOURCE_LIMITED_NOT_PHASE_GO',
        'selected_frozen_annotation_components':len(frozen_components),
        'independent_biological_families_certified':False,
        'shared_molecule_ids_in_two_source_available_cases':len(ids1&ids2),
        'source_available_pair_has_different_target_ids':True,
        'pair_same_target_pooling_control':'ALREADY_INELIGIBLE_FROM_TYPED_METADATA',
        'pair_control_analysis':'EXPLORATORY_AFTER_SOURCE; not a prespecified policy comparison',
        'verified_molecular_decision_changes':'NOT_ESTABLISHED',
        'reference_status':'PENDING_OWNER_REVIEW',
        'independent_reference_gold':'NOT_ESTABLISHED',
        'http_attempts':len(book['attempts']),
        'successes':sum(row['status']=='PASS' for row in book['attempts']),
        'decoded_bytes':book['decoded_bytes'],
        'conservative_cpu_seconds_charged':book['utility_charge_seconds']+book['worker_reserved_seconds'],
        'cpu_cap_seconds':3600,'stopped_sources':book['stopped_sources'],
        'version_before_after_equal':True,'offline_boundary_checks':offline,
        'masked_xml_input_retrieval_hash_retained':True,
        'unmasked_full_article_retained':False,
        'mask_module_execution_hash_at_first_xml_request':'NOT_CAPTURED; function unchanged after PDF-helper addition',
        'masked_output_hashes_retained':True,
        'reference_interpretation_authorship':'Parent draft, not independent adjudication'})
    assert summary['http_attempts']<=48 and summary['decoded_bytes']<=32*1024**2
    assert summary['conservative_cpu_seconds_charged']<=3600
    save(PRIVATE/'review-preparation-summary-v2.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    guard=Guard('review-audit-v1')
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS',charged_to='600-second utility reservation')
