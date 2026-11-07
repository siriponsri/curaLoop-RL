"""Pin existing review inputs and describe design failures without source intake."""
import collections,json,shutil
from pathlib import Path
from r0design_core_v1 import ROOT,PRIVATE,PUBLIC,Guard,save,sha,now

INPUTS=[
 'docs/03_research/R0_METHOD_FORMALIZATION_20261107.md',
 'docs/02_literature/R0_CLOSEST_WORK_20261107.md',
 'docs/03_research/CHEMBL_TASKFIRST_DATASET_BENCHMARK_PLAN_20261107.md',
 'docs/03_research/R0DQR_TAXONOMY_TASK_FEASIBILITY_20261107.md',
 'docs/06_execution/R0DQR_OWNER_DECISION_20261107.md',
 'docs/evidence/chembl-taskfirst-dqr-20261107-v1/phase-summary-v1.json',
 'docs/evidence/chembl-taskfirst-dqr-20261107-v1/taxonomy-granularity-diagnostic-v1.json',
 'docs/evidence/chembl-taskfirst-dqr-20261107-v1/exposure-quarantine-audit-v1.json',
 'docs/evidence/chembl-taskfirst-dqr-20261107-v1/source-access-readout-v1.json',
 '.local/chembl-taskfirst-dqr-20261107-v1/remote-return/files/jobs/nominal-v1/frame-frozen.json',
 '.local/chembl-taskfirst-dqr-20261107-v1/inputs/family-registry-v3.json',
 '.local/chembl-taskfirst-dqr-20261107-v1/inputs/r0dq-carried-exposure-v1.json',
 '.local/chembl-taskfirst-dqr-20261107-v1/inputs/exposure-register-v1.json',
]
OLD_LEDGER_PATHS=['.local/r0-chembl-20261107-v1/ledger.json','.local/r0r-chembl-20261107-v1/ledger.json',
 '.local/r0a1-chembl-20261107-v1/ledger.json','.local/chembl-taskfirst-dq-20261107-v1/ledger.json',
 '.local/chembl-taskfirst-dqr-20261107-v1/ledger.json']
def load(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def main():
    assert shutil.disk_usage(PRIVATE).free>=1024**3
    pins=[]
    for rel in INPUTS:
        path=ROOT/rel;assert path.is_file() and not path.is_symlink() and path.stat().st_size<32*1024**2
        pins.append({'path':rel,'bytes':path.stat().st_size,'sha256':sha(path)})
    old=[{'path':p,'sha256':sha(ROOT/p),'status':load(p)['status']} for p in OLD_LEDGER_PATHS]
    save(PRIVATE/'input-pins-v1.json',{'inputs':pins,'old_ledgers':old,'read_scope':'Existing written reviews and outcome-free returned derivations only'})
    frame=load(INPUTS[9]);audit=load(INPUTS[7]);summary=load(INPUTS[5]);amap={a['assay_id']:a for a in frame['assays']}
    tmap={t['tid']:t for t in frame['targets']}
    mixed={t for c in audit['shared_source_components_with_mixed_frame_roles'] for t in c['target_ids']}
    result={'status':'PASS_EXISTING_ARTIFACT_DESIGN_DIAGNOSTIC','base_commit':json.loads((PRIVATE/'release.json').read_text())['base_commit'],
        'frozen_targets':len(frame['targets']),'frozen_assays':len(frame['assays']),
        'selected_priority_targets':sum(t['nominal_priority'] for t in frame['targets']),
        'selected_reference_capable_assays':sum(any(a['nominal_counts'].get(k,0)>=128 for k in ['Ki','Kd']) for a in frame['assays']),
        'nominal_candidates':summary['nominal_support']['frozen_candidates'],
        'mixed_source_components':len(audit['shared_source_components_with_mixed_frame_roles']),
        'mixed_source_component_target_count':len(mixed),
        'mixed_source_targets_by_original_frame_role':dict(collections.Counter(tmap[t]['role'] for t in mixed)),
        'unresolved_planning_aliases':[r['chembl_id'] for r in audit['planning_identity_reconciliation'] if r['canonical_alias_coverage'].startswith('UNKNOWN')],
        'repairs_for_new_protocol':[
            'Global outcome-free support census before a bounded target intent frame; remove equal functional-class quotas and20-assay prefix sampling.',
            'Complete whole-target assay graphs and auxiliary-search completeness states; cap exhaustion is UNKNOWN, never evidence of zero support.',
            'Apply historical planning/canonical exposure and family/source closure before any proposed evaluation role; preserve old role provenance.',
            'Require independent family/procedure source review; no class-label certificate or default WT.',
            'Keep128/64/32 and36/18/4-2-12 as targets; do not change them based on favorable outcomes.'],
        'existing_candidate_or_role_labels_rewritten':False,'new_cohort_or_split_created':False,
        'new_source_queries_activity_records_or_outcomes':0,'source_http':0,'ssh':0,
        'literature_scope':'Cached7November review only; no fresh paper/version/novelty verification',
        'independent_domain_review':'NOT_RUN','utc':now()}
    save(PUBLIC/'design-diagnostic-v1.json',result)
    save(PUBLIC/'input-pins-v1.json',{'inputs':pins,'old_ledgers':old,'new_source_intake':False})
    print(json.dumps(result))
if __name__=='__main__':
    guard=Guard('existing-artifact-review-v1',cpu=180,stage='review',wall=300,memory_mib=256)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
