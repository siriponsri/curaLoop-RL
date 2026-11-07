"""Parent-only source-feasibility readout; never invent independent truth."""
import json
from r0dq_core_v1 import PRIVATE,save,LocalGuard

if __name__=='__main__':
    guard=LocalGuard('development-context-review-v1',cpu_seconds=30,stage='context',wall=120,memory_mib=256)
    try:
        packet=json.loads((PRIVATE/'development-packet-v2.json').read_text())
        access=json.loads((PRIVATE/'oa-access-v2.json').read_text())
        assert len(packet['bundles'])==2 and len(packet['assays'])==4 and len(access['records'])==4
        assert all(row['status']=='NO_OPENALEX_OA_LOCATION' for row in access['records'])
        assert all(not assay['parameters'] for assay in packet['assays'])
        assert all(not assay['variant_id'] for assay in packet['assays'])
        assert all(not assay['description_projection']['unclassified_numerals_masked'] for assay in packet['assays'])
        records=[]
        for case in packet['bundles']:
            records.append({'bundle_id':case['bundle_id'],'target_chembl_id':case['target_chembl_id'],
                'reference_type':case['reference'][1],'reference_panel':case['panel_compounds'],
                'shared_union':case['panel_shared_union'],'context_distinctness':'PENDING_SOURCE_REVIEW',
                'reference_construct':'UNRESOLVED_NOT_ASSUMED_WILD_TYPE','incremental_paper_fact':'NOT_ESTABLISHED',
                'decision_or_molecular_utility':'NOT_RUN'})
        result={'status':'PENDING_SOURCE_AND_DOMAIN_REVIEW; FULL_SCALE_TARGET_UNMET',
            'candidate_decision_sensitive_groups':0,'clear_context_controls':0,
            'independent_gold_established':False,'independent_biological_family_certification':'NOT_RUN',
            'development_bundles_reviewed_at_metadata_level':2,'development_split_units':1,
            'full_methods_bodies_reviewed':0,'source_access_evidence':access['records'],'bundles':records,
            'metadata_visible_facts':[
                'Adenosine A3 pair: one description identifies CHO cells and a NECA radiotracer; the other is a general human A3 binding description.',
                'Histamine H3 pair: different named radiotracers are already explicit in ChEMBL descriptions. This is not an incremental paper-only fact.',
                'All four variant fields are null and assay-parameter lists empty. Null does not certify wild type or complete construct equivalence.'],
            'radiotracer_identifier_projection_repair':'Known isotope identifiers retained in packet v2; earlier packet preserved, no HTTP retry',
            'mask_omissions_credited_as_natural_uncertainty':False,
            'no_oa_route_does_not_prove_universal_unavailability':True,
            'no_source_access_is_not_negative_evidence_against_the_general_adaptive_evidence_hypothesis':True,
            'reviewer':'parent implementation author only; not a domain or independent reference adjudicator',
            'next_phase_authorized':False}
        save(PRIVATE/'context-review-v1.json',result)
        print(json.dumps({'status':result['status'],'metadata_reviewed_bundles':2,'split_units':1,'methods_bodies_reviewed':0,
            'candidate_decision_sensitive_groups':0,'clear_context_controls':0}))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
