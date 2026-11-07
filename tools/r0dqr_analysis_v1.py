"""Analyze already returned metadata, without reopening a source DB or outcomes."""
import collections,hashlib,json
from r0dqr_core_v1 import PRIVATE,PUBLIC,LocalGuard,save,sha,now

def main():
    small=PRIVATE/'small-return/jobs';inventory=json.loads((small/'inventory-v1/taxonomy-inventory.json').read_text())
    frame=json.loads((small/'nominal-v1/frame-frozen.json').read_text());cases=json.loads((small/'nominal-v1/candidates-frozen.json').read_text())
    pools=json.loads((small/'nominal-v1/pooling-diagnostics.json').read_text());reg=json.loads((PRIVATE/'inputs/family-registry-v3.json').read_text())
    classes={c['protein_class_id']:c for c in inventory['protein_classes']}
    labels={key:classes.get(key,{}).get('pref_name',str(key)) for key in {t['sampling_stratum'] for t in frame['targets']}}
    groups={g for row in reg['family_records'] for g in row['provisional_groups']}
    def components(types):
        parent={g:g for g in groups}
        def find(g):
            if parent[g]!=g:parent[g]=find(parent[g])
            return parent[g]
        for edge in reg['typed_bridges']:
            if edge['type'] not in types:continue
            nodes=[g for g in edge['provisional_groups'] if g in parent]
            for g in nodes[1:]:
                a,b=find(nodes[0]),find(g)
                if a!=b:parent[max(a,b)]=min(a,b)
        parts=collections.defaultdict(list)
        for g in groups:parts[find(g)].append(g)
        return {'components':len(parts),'largest_component_provisional_labels':max(map(len,parts.values()),default=0),
            'component_size_histogram':dict(collections.Counter(map(len,parts.values())))}
    giant=max(reg['family_records'],key=lambda f:len(f['broad_names_merged']))
    sensitivity={'status':'DIAGNOSTIC_GRAPH_SENSITIVITY_NOT_A_NEW_SPLIT','provisional_label_nodes':len(groups),
        'bridge_types':dict(collections.Counter(e['type'] for e in reg['typed_bridges'])),
        'all_recorded_typed_edges':components({'family','homologous_superfamily'}),'family_typed_edges_only':components({'family'}),
        'existing_giant_family_id':giant['family_id'],'existing_giant_merged_labels':len(giant['broad_names_merged']),
        'old_roles_and_protected_component_membership_changed':False,'new_biological_family_certification':False,
        'interpretation':'Removing broad shared-domain bridges changes graph connectivity, not demonstrated independence. Never adopt based on yield or clear a protected/exposed component.'}
    save(PUBLIC/'taxonomy-granularity-diagnostic-v1.json',sensitivity)
    selected=[]
    for t in frame['targets']:
        selected.append({k:t.get(k) for k in ['tid','chembl_id','accession','organism','tax_id','family_id','inherited_role','role','prior_exposure','class_ids','class_paths','sampling_stratum','nominal_priority','final_status']})
    save(PUBLIC/'selected-target-crosswalk-v1.json',{'status':'METADATA_CROSSWALK_FOR_REVIEW_NOT_CERTIFIED_FAMILIES','records':selected,'protected_registry_sha256':sha(PRIVATE/'inputs/protected-identities.json'),
        'registry_sha256':sha(PRIVATE/'inputs/family-registry-v3.json'),'all_proposed_final_tasks_quarantined_pending_adjudication':True})
    summary={'schema':'curaloop.r0dqr.taxonomy-readout.v1','inventory_targets':len(inventory['targets']),
        'counts':inventory['target_counts'],'class_nodes_by_path_depth':inventory['class_nodes_by_path_depth'],
        'classification_nodes':len(classes),'catalog_targets_with_nominal_assays':frame['catalog_targets_with_nominal_assays'],
        'selected_targets':len(frame['targets']),'selected_assays':len(frame['assays']),
        'selected_priority_targets':sum(t['nominal_priority'] for t in frame['targets']),
        'reference_capable_selected_assays_before_canonical_pruning':sum(any(a['nominal_counts'].get(typ,0)>=128 for typ in ['Ki','Kd']) for a in frame['assays']),
        'selected_targets_by_stratum':[{'class_id':k,'label':labels[k],'targets':n} for k,n in collections.Counter(t['sampling_stratum'] for t in frame['targets']).items()],
        'selected_targets_by_inherited_role':dict(collections.Counter(t['role'] for t in frame['targets'])),
        'selected_targets_without_inherited_mapping':sum(t['family_id'] is None for t in frame['targets']),
        'candidate_bundles':len(cases['candidates']),'candidate_pool':cases['candidate_pool'],
        'candidate_records':[{k:v for k,v in c.items() if k!='panel_canonical_hashes'} for c in cases['candidates']],
        'pooling_diagnostics':pools,'certified_new_biological_families':0,
        'limitations':['Balanced coarse functional strata are coverage diagnostics, not a yield-optimal or exhaustive benchmark search.',
            'Only20assays per target and deterministic DOI balancing; do not infer universal ChEMBL infeasibility from this frame.',
            'Raw numeric activity and nonmissingness were never queried; nominal topology does not certify finite positive support.',
            'Masked or null context cannot prove procedural equivalence; same-target/source pools are ineligible.',
            'Taxonomy granularity and molecular scaffold/analogue leakage remain unadjudicated.']}
    save(PUBLIC/'taxonomy-and-task-feasibility-v1.json',summary)
    save(PUBLIC/'source-access-readout-v1.json',json.loads((PRIVATE/'methods-intake-v1.json').read_text()))
    save(PRIVATE/'metadata-analysis-v1.json',{'status':'PASS_RETURNED_METADATA_ANALYSIS','source_db_queries':0,
        'diagnostic_relabeling_applied':False,'utc':now(),'public_files':4})
    print(json.dumps({'status':'PASS_RETURNED_METADATA_ANALYSIS','graph_sensitivity':sensitivity}))

if __name__=='__main__':
    guard=LocalGuard('returned-metadata-analysis-v1',cpu_seconds=120,wall=180,stage='metadata',memory_mib=512)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
