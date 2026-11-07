"""Mechanical identity/metadata controls; no numerical outcome access."""
from collections import Counter
from itertools import combinations
import hashlib
import re
from r0a1_core_v1 import Guard,ROOT,PRIVATE,load,save,archive_code
from r0a1_context_mask_v1 import ENTITY,safety_checks

AVAILABLE={'CHEMBL1138492':'S1','CHEMBL1140224':'S2','CHEMBL1140235':'S3','CHEMBL1156448':'S4'}


def run():
    cases=load(PRIVATE/'metadata-context-v3.json')['cases']
    source=ROOT/'docs/evidence/r0r-chembl-20261107-v1'
    records=load(source/'projected-readout-metadata-v1.json')['records']
    by_id={c['assay_chembl_id']:c for c in cases}
    rows={key:[r for r in records if r['assay_chembl_id']==key] for key in by_id}
    molecules={key:{r['molecule_chembl_id'] for r in value} for key,value in rows.items()}
    pair_rows=[]
    for a,b in combinations(cases,2):
        ai,bi=a['assay_chembl_id'],b['assay_chembl_id']
        different_target=a['target_chembl_id']!=b['target_chembl_id']
        positions=lambda c:{e for e in c['description_features']['entities'] if re.fullmatch(r'(?:Ala|Arg|Asn|Asp|Cys|Gln|Glu|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)\d+',e)}
        pa,pb=positions(a),positions(b)
        visible_difference=bool(pa and pb and pa!=pb)
        if different_target:status='DIFFERENT_TARGET_ALREADY_VISIBLE'
        elif not rows[ai] or not rows[bi]:status='REJECTED_PROJECTION_NO_ADMITTED_SUPPORT'
        elif visible_difference:status='DISTINCT_RESIDUE_CONTEXT_ALREADY_VISIBLE'
        else:status='COMPATIBILITY_UNRESOLVED'
        pair_rows.append({'assays':[ai,bi],'metadata_control':status,
            'both_projections_admitted':bool(rows[ai] and rows[bi]),
            'shared_molecule_ids':sorted(molecules[ai]&molecules[bi]),
            'molecular_union_size':len(molecules[ai]|molecules[bi]),
            'unqualified_same_context_pooling_justified':False,
            'biological_transfer_incompatibility_proven':False,
            'paper_added_eligibility_change':'NOT_ESTABLISHED'})
    matrix=[]
    for case in cases:
        aid,doc=case['assay_chembl_id'],case['document_chembl_id']
        if doc not in AVAILABLE:
            mapping='SOURCE_UNAVAILABLE';reason='Owner-deferred paper; no imputation or replacement'
        elif doc=='CHEMBL1140235' and aid=='CHEMBL1000136':
            mapping='UNRESOLVED';reason='Metadata names 5HT1A; admitted methods name sigma subtypes and a separate growth assay, not an exact 5HT1A procedure'
        elif doc=='CHEMBL1140235':
            mapping='PARTIAL_METHOD_FAMILY_MATCH';reason='Sigma-1 binding context has a document-method anchor, but original protocol is cited elsewhere and projection stays rejected'
        elif doc=='CHEMBL1140224':
            mapping='PARTIAL_METHOD_FAMILY_MATCH';reason='Structured metadata already names K562; multiple source cytotoxicity procedures use that target cell, exact effector/procedure remains unresolved'
        elif doc=='CHEMBL1156448':
            mapping='PARTIAL_METHOD_FAMILY_MATCH';reason='COS-7/inositol context is already in metadata and source methods; residue-specific construct-to-procedure mapping remains unresolved'
        else:
            mapping='PARTIAL_METHOD_FAMILY_MATCH';reason='Prior S1 binding/lipid context retained; exact preparation unresolved and paired PKC target IDs differ'
        matrix.append({'assay_id':aid,'document_id':doc,'target_id':case['target_chembl_id'],
            'metadata_context':case,'source_note':AVAILABLE.get(doc),
            'readout_units':sorted({str((r['standard_type'],r['standard_units'])) for r in rows[aid]}),
            'admitted_record_count':len(rows[aid]),'distinct_molecules':len(molecules[aid]),
            'reference_mapping_draft':mapping,'reason':reason,
            'independent_adjudication':'NOT_RUN','post_source_eligibility_change':'NOT_ESTABLISHED',
            'molecular_decision_gain':'NOT_TESTED'})
    ghrelin=[c for c in cases if c['target_chembl_id']=='CHEMBL4616' and rows[c['assay_chembl_id']]]
    ghrelin_ids={m for c in ghrelin for m in molecules[c['assay_chembl_id']]}
    checks={
        'all_twelve_frozen_cases_retained':len(matrix)==12,
        'eighty_six_original_metadata_records_only':len(records)==86,
        'three_admitted_ghrelin_cases':len(ghrelin)==3,
        'ghrelin_each_one_record':all(len(rows[c['assay_chembl_id']])==1 for c in ghrelin),
        'no_unpermitted_digits_in_method_paragraphs':True,
        'masking_fixtures':safety_checks()['status']=='PASS',
    }
    for path in sorted(PRIVATE.glob('methods-CHEMBL*-v1.json')):
        method=load(path)
        assert method['status']=='MASKED_METHODS_DRAFT_AVAILABLE'
        for paragraph in method['paragraphs']:
            remainder=ENTITY.sub('',paragraph['masked_text']).replace('IC50','').replace('EC50','')
            checks['no_unpermitted_digits_in_method_paragraphs'] &= not bool(re.search(r'\d',remainder))
    assert all(checks.values())
    counts=dict(Counter(r['metadata_control'] for r in pair_rows))
    summary={'status':'INFEASIBLE_IN_CURRENT_SUBSET','scientific_phase_go':False,
        'scope':'Original twelve-case R0-R development slice and admitted record identities only; not ChEMBL as a whole',
        'selected_cases':12,'admitted_cases':10,'admitted_metadata_records':86,
        'document_method_cases':sum(c['document_id'] in AVAILABLE for c in matrix),
        'mapping_draft_counts':dict(Counter(c['reference_mapping_draft'] for c in matrix)),
        'pairwise_controls':counts,'all_pairwise_controls':len(pair_rows),
        'admitted_pairwise_controls':sum(p['both_projections_admitted'] for p in pair_rows),
        'admitted_ghrelin_cases':[c['assay_chembl_id'] for c in ghrelin],
        'ghrelin_distinct_molecule_ids':sorted(ghrelin_ids),
        'ghrelin_distinct_molecules':len(ghrelin_ids),
        'nondegenerate_ghrelin_choice_panel_established':len(ghrelin_ids)>1,
        'source_only_eligibility_changes_demonstrated':0,'molecular_decision_gain':'NOT_ESTABLISHED',
        'null_unit_records_unresolved':17,'independent_reference_gold':'NOT_ESTABLISHED',
        'independent_scientific_review':'NOT_RUN','assay_specific_mappings_adjudicated':0,
        'analysis_type':'Exploratory author feasibility audit; no blinded/policy comparison',
        'new_activity_records':0,'new_molecules':0,'training_runs':0,'network_requests':0,
        'final_outcomes_opened':False,'next_phase_released':False,'checks':checks,
        'interpretation':'Useful procedure anchors do not supply incremental decision value beyond complete permitted metadata; sparse same-target record support blocks a molecular-choice test in this slice',
        'not_established':'This does not prove that assay transfer is biologically impossible, that all context is free, or that the general research hypothesis is false'}
    save(PRIVATE/'case-matrix-v1.json',{'cases':matrix,'reference_status':'AUTHOR_DRAFT_NOT_GOLD'})
    save(PRIVATE/'pairwise-controls-v1.json',{'pairs':pair_rows,'rule':'Unqualified same-target/same-context pooling only; not a universal transferability rule'})
    save(PRIVATE/'readout-v1.json',summary)
    archive_code(ROOT/'tools/r0a1_context_mask_v1.py')
    print(summary)


if __name__=='__main__':
    guard=Guard('support-analysis-v1',cpu_seconds=60)
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
