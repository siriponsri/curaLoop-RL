"""Keep full residue-position identifiers; preserve the initial parser output."""
import hashlib
from r0a1_core_v1 import Guard,ROOT,PRIVATE,save,load,archive_code
from r0a1_context_mask_v1 import description_features,safety_checks,mask


def run(output_name='metadata-context-v2.json',checks_name='mask-checks-v2.json'):
    previous=load(PRIVATE/'metadata-before-paper-identifiers-v1.json')
    source=ROOT/'.local/r0-chembl-20261107-v1/014-chembl37-selected-assays.html'
    rows={r['assay_chembl_id']:r for r in load(source)['assays']}
    corrections=[]
    for case in previous['cases']:
        prior=case['description_features']['entities']
        case['description_features']=description_features(rows[case['assay_chembl_id']].get('description'))
        for key in ['assay_organism','assay_tissue','assay_cell_type','assay_subcellular_fraction']:
            if case[key] is not None:case[key]=mask(case[key])[0]
        if prior!=case['description_features']['entities']:
            corrections.append({'assay_id':case['assay_chembl_id'],'before':prior,'after':case['description_features']['entities']})
    previous.update(parser_revision='Full dotted residue labels; initial partial-prefix matches retained in v1 only',
        freeze_order='V2 parsing correction after PDF identifier extraction; original pre-PDF v1 retained; exploratory, not a blinded comparison',
        corrected_cases=corrections,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    assert safety_checks()['status']=='PASS'
    assert not (PRIVATE/output_name).exists() and not (PRIVATE/checks_name).exists()
    save(PRIVATE/output_name,previous)
    save(PRIVATE/checks_name,safety_checks())
    archive_code(ROOT/'tools/r0a1_context_mask_v1.py')
    print({'status':'PASS','parser_corrected_cases':len(corrections),'masking_fixture_cases':safety_checks()['cases'],'corrections':corrections})


if __name__=='__main__':
    guard=Guard('metadata-parser-repair-v1',cpu_seconds=60)
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
