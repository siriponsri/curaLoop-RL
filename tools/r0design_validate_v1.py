"""Protocol/authority checks and synthetic failure cases, not biology or efficacy."""
import ast,copy,itertools,json
from r0design_core_v1 import ROOT,PRIVATE,PUBLIC,Guard,save,sha,archive_code

CONFIG=ROOT/'research/configs/r0_design_review_protocol_20261107_v1.json'
def validate(c):
    assert c['execution_authorized'] is False and c['original_claim_retained'] is True
    assert (c['panel_floor'],c['shared_union_floor'],c['shared_per_auxiliary_floor'])==(128,64,32)
    assert c['task_target']['bundles']==36 and c['task_target']['isolation_units']==18
    assert c['task_target']['role_units']=={'development':4,'validation':2,'final':12}
    assert c['reference_types']==['Ki','Kd'] and not c['reference_types_pooled']
    assert c['family_policy']['independent_reviewers_required']==2
    assert not c['family_policy']['class_labels_are_family_certificates'] and not c['family_policy']['family_only_254_component_graph_adopted']
    assert c['family_policy']['legacy_87_label_component']=='HARD_NONFINAL_CONSTRAINT_UNCHANGED'
    assert c['isolation_policy']['closure_before_role_assignment'] and not c['isolation_policy']['old_role_provenance_rewritten']
    assert c['reference_unit']['pooling_permitted_only_after_certificate'] and not c['reference_unit']['null_variant_is_wild_type']
    assert not c['reference_unit']['same_target_paper_or_assay_group_sufficient']
    assert not c['sampling']['equal_functional_class_quota'] and c['sampling']['whole_target_graph_required']
    assert c['sampling']['capped_graph_or_auxiliary_search']=='UNKNOWN_NOT_ZERO'
    assert not c['sampling']['post_failure_refill'] and not c['sampling']['final_selection_by_paper_fact_effectiveness']
    assert c['comparison_contract']['all_permitted_metadata_to_all_arms'] and c['comparison_contract']['already_cached_facts_free_to_all_arms']
    assert c['comparison_contract']['same_predictor_features_update_rule_and_seed_schedule']
    assert c['comparison_contract']['zero_cost_full_context_optimal_policy_cannot_be_dominated_by_information_alone']
    q=c['next_census_proposal'];assert q['status']=='NOT_RELEASED' and q['start_utc'] is None and q['deadline_utc'] is None
    assert sum(q['allocation_seconds'].values())==q['cpu_cap_seconds']==10800
    assert q['elapsed_hours']==24 and q['max_combined_cpu_workers']==2
    assert q['source_http']==q['methods_bodies']==q['activity_value_and_presence_queries']==0
    assert not q['old_final_outcomes'] and not q['qualified_final_task_release'] and not q['new_family_or_reference_gold_certification']
    assert set(q['allowed_activity_projection'])=={'activity_id','assay_id','molregno','doc_id','standard_type','standard_relation','standard_units'}
    assert not q['raw_assay_parameter_values'] and q['full_return_and_local_reread_before_exact_cleanup']
    assert all(d['status'] in {'PENDING','NOT_CONFIRMED','NOT_RELEASED'} for d in c['remaining_decisions'])

def synthetic_disposition(old_roles,shared_source,legacy_exposed,alias_known,certified):
    # A minimal logical witness of the proposed contract; never applied to real
    # records, never a domain classifier or production split implementation.
    original=list(old_roles)
    blocked=(shared_source and len(set(old_roles))>1) or legacy_exposed or not alias_known or not certified
    return ('QUARANTINE_NEW_TASK' if blocked else 'READY_FOR_FUTURE_REVIEW',original)

def main():
    cfg=json.loads(CONFIG.read_text());validate(cfg);checks=['consistent_protocol_and_unreleased_next_grant']
    attacks=[]
    mutations=[('lower_floor',lambda c:c.update(panel_floor=64)),
        ('activity_value_projection',lambda c:c['next_census_proposal']['allowed_activity_projection'].append('standard_value')),
        ('fake_family_certificate',lambda c:c['family_policy'].update(class_labels_are_family_certificates=True)),
        ('automatic_next_phase',lambda c:c['next_census_proposal'].update(status='RELEASED')),
        ('manufactured_metadata_gap',lambda c:c['comparison_contract'].update(all_permitted_metadata_to_all_arms=False)),
        ('prefix_is_complete',lambda c:c['sampling'].update(whole_target_graph_required=False)),
        ('role_laundering',lambda c:c['isolation_policy'].update(old_role_provenance_rewritten=True))]
    for name,mutate in mutations:
        altered=copy.deepcopy(cfg);mutate(altered)
        try:validate(altered)
        except AssertionError:attacks.append(name)
        else:raise AssertionError('Unsafe contract mutation accepted: '+name)
    checks.append('reject_seven_contradictory_or_unauthorized_contract_mutations')
    roles=['development','final'];status,kept=synthetic_disposition(roles,True,False,True,True)
    assert status=='QUARANTINE_NEW_TASK' and roles==kept;checks.append('shared_source_conflict_quarantines_without_rewriting_old_roles')
    assert synthetic_disposition(['development'],False,True,True,True)[0]=='QUARANTINE_NEW_TASK'
    checks.append('new_family_label_cannot_clear_legacy_exposure')
    assert synthetic_disposition([],False,False,False,True)[0]=='QUARANTINE_NEW_TASK'
    assert synthetic_disposition([],False,False,True,False)[0]=='QUARANTINE_NEW_TASK'
    checks.append('unknown_alias_or_family_certificate_blocks_admission')
    ref=set(range(128));aux=[set(range(32)) for _ in range(8)]+[set(range(32,64))]
    exists=lambda sets:any(len(set().union(*combo))>=64 for n in range(1,4) for combo in itertools.combinations(sets,n))
    assert not exists(aux[:8]) and exists(aux) and all(len(x&ref)>=32 for x in aux)
    checks.append('synthetic_top_eight_prefix_counterexample_requires_search_completeness')
    pinned=json.loads((PRIVATE/'input-pins-v1.json').read_text())
    for row in pinned['inputs']+pinned['old_ledgers']:assert sha(ROOT/row['path'])==row['sha256']
    checks.append('all_existing_inputs_and_old_ledgers_unchanged')
    modules=list((ROOT/'tools').glob('r0design_*.py'))
    for p in modules:
        tree=ast.parse(p.read_text());archive_code(p)
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):assert not {x.name.split('.')[0] for x in node.names}&{'sqlite3','requests','urllib','paramiko'}
            if isinstance(node,ast.ImportFrom):assert (node.module or '').split('.')[0] not in {'sqlite3','requests','urllib','paramiko'}
    checks.append('review_helpers_have_no_source_db_or_network_client_imports')
    result={'status':'PASS_PROTOCOL_AUTHORITY_AND_SYNTHETIC_CONSTRAINT_CHECKS','checks':checks,'check_count':len(checks),
        'rejected_mutations':attacks,'protocol_sha256':sha(CONFIG),'modules_parsed':len(modules),
        'real_cohort_or_split_rebuilt':False,'real_activity_values_or_final_outcomes_used':False,
        'independent_biology_reference_or_novelty_validation':'NOT_RUN'}
    save(PUBLIC/'protocol-validation-v1.json',result)
    target=PUBLIC/'protocol-proposed-v1.json';assert not target.exists();target.write_bytes(CONFIG.read_bytes())
    print(json.dumps(result))
if __name__=='__main__':
    guard=Guard('protocol-consistency-validation-v1',cpu=180,stage='validation',wall=240,memory_mib=256)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
