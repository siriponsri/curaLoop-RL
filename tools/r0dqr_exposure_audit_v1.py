"""Append-only lineage audit of the frozen frame; no new cohort or source query."""
import collections,json
from r0dqr_core_v1 import ROOT,PRIVATE,PRIOR,PUBLIC,LocalGuard,save,sha

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    files=PRIVATE/'remote-return/files';frame=load(files/'jobs/nominal-v1/frame-frozen.json')
    cases=load(files/'jobs/nominal-v1/candidates-frozen.json')['candidates'];ident=load(files/'jobs/nominal-v1/identity-dispositions.json')['records']
    exposure=load(PRIVATE/'inputs/exposure-register-v1.json');carry=load(PRIVATE/'inputs/r0dq-carried-exposure-v1.json')
    priorframe=PRIOR/'remote-return/files/jobs/frame-v3/frame-frozen.json';priorident=PRIOR/'remote-return/files/jobs/support-v1/identity-dispositions.json'
    assert sha(priorframe)==carry['prior_frame_sha256'] and sha(priorident)==carry['prior_identity_sha256']
    oldframe=load(priorframe);oldident=load(priorident)['records'];planning=[]
    for item in exposure['planning_exposed_ids']:
        identity=item['id'] if isinstance(item,dict) else item
        rows=[r for r in ident+oldident if r['molecule_chembl_id']==identity]
        hashes=sorted({r['canonical_sha256'] for r in rows if r['canonical_sha256']})
        planning.append({'chembl_id':identity,'prior_entity_reconciliation':[r for r in oldframe['incidental_exposure_reconciliation'] if r['chembl_id']==identity],
            'current_source_id_matches':sum(r['molecule_chembl_id']==identity for r in ident),
            'canonical_hashes_in_returned_derivations':hashes,
            'canonical_alias_coverage':'RESOLVED_FROM_EXISTING_DERIVATION' if hashes else 'UNKNOWN_NO_NEW_SOURCE_QUERY',
            'final_use':'WITHHELD_PENDING_FULL_RECONCILIATION'})
    olddocs=set(exposure['old_r0_document_ids'])|set(carry['document_chembl_ids'])
    exposed_assays=[a for a in frame['assays'] if a['document_chembl_id'] in olddocs]
    parent={t['tid']:t['tid'] for t in frame['targets']}
    def find(t):
        if parent[t]!=t:parent[t]=find(parent[t])
        return parent[t]
    sources=collections.defaultdict(set)
    for a in frame['assays']:
        sources[('doi',a['doi'].strip().lower())].add(a['tid'])
        if a['assay_group'] not in (None,'',0,'0'):sources[('assay_group',str(a['assay_group']))].add(a['tid'])
    for values in sources.values():
        nodes=sorted(values)
        for t in nodes[1:]:
            x,y=find(nodes[0]),find(t)
            if x!=y:parent[max(x,y)]=min(x,y)
    components=collections.defaultdict(list)
    for t in frame['targets']:components[find(t['tid'])].append(t)
    conflicts=[{'target_ids':[t['tid'] for t in group],'inherited_frame_roles':sorted({t['role'] for t in group}),
        'status':'QUARANTINE_SHARED_SOURCE_ROLE_REVIEW'} for group in components.values() if len({t['role'] for t in group})>1]
    assert all(c['role']=='development' for c in cases)
    audit={'status':'PASS_APPEND_ONLY_EXPOSURE_AUDIT_NO_FINAL_RELEASE','frozen_frame_sha256':sha(files/'jobs/nominal-v1/frame-frozen.json'),
        'candidate_freeze_sha256':sha(files/'jobs/nominal-v1/candidates-frozen.json'),
        'planning_identity_reconciliation':planning,'old_exposed_document_assays':len(exposed_assays),
        'old_exposed_document_assays_by_frame_role':dict(collections.Counter(a['role'] for a in exposed_assays)),
        'shared_source_components_with_mixed_frame_roles':conflicts,
        'frozen_candidate_roles':dict(collections.Counter(c['role'] for c in cases)),
        'new_final_tasks_released':0,'all_proposed_final_tasks_withheld':True,
        'construction_limit':'The frozen worker retains historical inputs but does not yet propagate every old document/planning-identity and shared-source join into a certified final split. This audit does not retroactively repair or refill that frame.',
        'before_any_future_qualification':['Resolve the incidental planning molecule canonical aliases under an approved metadata-only source query.',
            'Propagate old document exposure and shared-source/assay-group links before any split or candidate qualification; preserve original role labels as provenance.',
            'Independently adjudicate biological family and procedure mappings; unknown joins block final use.'],
        'new_activity_values_presence_flags_or_source_queries':0,'new_candidates_or_refill':False,'independent_family_certification':False}
    save(PUBLIC/'exposure-quarantine-audit-v1.json',audit);print(json.dumps(audit))
if __name__=='__main__':
    guard=LocalGuard('frozen-frame-exposure-audit-v1',cpu_seconds=60,wall=120,stage='metadata',memory_mib=256)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
