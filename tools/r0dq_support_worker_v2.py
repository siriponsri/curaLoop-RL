"""Complete identity graph, freeze candidates, then emit validity booleans only."""
import collections,hashlib,json,sqlite3,sys,time
from pathlib import Path
from r0dq_projection_v1 import protect_metadata_connection,PresenceValidator,SCALES
from research.taskfirst_dq_v1.selection import rank,auxiliary_choice,panel,molecule_role_owners
from rdkit import Chem,rdBase,RDLogger

p=Path(sys.argv[1]);root=p.parents[1];started=time.monotonic()
def save(name,obj):
    target=p/name;assert not target.exists();target.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def progress(obj):
    target=p/'progress.json';tmp=p/'progress.tmp';tmp.write_text(json.dumps(obj));tmp.replace(target)
try:
    assert rdBase.rdkitVersion=='2026.09.1';RDLogger.DisableLog('rdApp.*')
    frozen=root/'jobs/frame-v2/frame-frozen.json';frame=json.loads(frozen.read_text())
    assert json.loads((root/'jobs/frame-v2/result.json').read_text())['status']=='PASS_METADATA_FRAME_FROZEN'
    protection=json.loads((root/'inputs/protected-identities.json').read_text())
    exposure=json.loads((root/'inputs/exposure-register-v1.json').read_text())
    db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True)
    db.row_factory=sqlite3.Row;protect_metadata_connection(db)
    topology=[];assay_states=[];molecules=set();complete=[]
    for assay in sorted(frame['assays'],key=lambda a:rank(a['assay_id'])):
        aid=assay['assay_id']
        n=db.execute("SELECT COUNT(*) FROM activities WHERE assay_id=? AND standard_type IN ('Ki','Kd','IC50')",(aid,)).fetchone()[0]
        if len(topology)+n>1000000:
            assay_states.append({'assay_id':aid,'status':'INCOMPLETE_SUPPORT_ROW_CAP','catalog_rows':n});continue
        rows=[dict(r) for r in db.execute("SELECT activity_id,assay_id,molregno,standard_type,standard_units,standard_relation,doc_id FROM activities WHERE assay_id=? AND standard_type IN ('Ki','Kd','IC50')",(aid,))]
        assert len(rows)==n
        added={r['molregno'] for r in rows if r['molregno'] is not None}
        if len(molecules|added)>100000:
            assay_states.append({'assay_id':aid,'status':'INCOMPLETE_SUPPORT_MOLECULE_CAP','catalog_rows':n});continue
        topology.extend(rows);molecules.update(added);complete.append(aid)
        assay_states.append({'assay_id':aid,'status':'COMPLETE_OUTCOME_FREE_TOPOLOGY','rows':n})
    assert len(topology)<=1000000 and len(molecules)<=100000
    save('topology-outcome-free.json',{'frame_sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),
        'rows':topology,'assay_states':assay_states,'activity_values_present':False})
    progress({'status':'CANONICALIZING_PROTECTION_IDENTITIES','topology_rows':len(topology),'molecule_ids':len(molecules)})
    protected=set(protection['canonical_smiles']);exposed_ids=set(exposure['old_r0r_molecule_ids'])
    additional=root/'inputs/additional-exposure-v1.json'
    known_exposed=json.loads(additional.read_text())['canonical_smiles'] if additional.exists() else []
    incidental_mols=set(frame['incidental_molregnos']);canonical={};dispositions=[];exposed=set(known_exposed)
    for molregno in sorted(molecules):
        row=db.execute('''SELECT m.chembl_id,s.canonical_smiles FROM molecule_dictionary m
            LEFT JOIN compound_structures s ON s.molregno=m.molregno WHERE m.molregno=?''',(molregno,)).fetchone()
        mol=Chem.MolFromSmiles(row['canonical_smiles']) if row and row['canonical_smiles'] else None
        if mol is None:status='QUARANTINE_UNRESOLVED_STRUCTURE';smiles=None
        else:
            smiles=Chem.MolToSmiles(mol,canonical=True,isomericSmiles=True)
            status='EXCLUDE_PROTECTED_EXACT_IDENTITY' if smiles in protected else 'ADMITTED_IDENTITY'
            if row['chembl_id'] in exposed_ids or molregno in incidental_mols:exposed.add(smiles)
        if status=='ADMITTED_IDENTITY':canonical[molregno]=smiles
        dispositions.append({'molregno':molregno,'molecule_chembl_id':row['chembl_id'] if row else None,
            'status':status,'canonical_sha256':hashlib.sha256(smiles.encode()).hexdigest() if smiles else None})
    save('identity-dispositions.json',{'rdkit':rdBase.rdkitVersion,'normalization':'canonical isomeric SMILES only; no salt-charge-isotope-tautomer normalization',
        'records':dispositions,'chemical_OOD_certified':False,'protected_input_count':len(protected)})
    # Apply cross-role exact-identity ownership BEFORE any numerical query.
    assaymap={a['assay_id']:a for a in frame['assays'] if a['assay_id'] in complete}
    nominal=collections.defaultdict(set)
    for row in topology:
        if row['molregno'] in canonical and row['standard_relation']=='=' and row['standard_units'] in SCALES:
            nominal[row['assay_id']].add(canonical[row['molregno']])
    owners=molecule_role_owners(nominal,{aid:a['role'] for aid,a in assaymap.items()},exposed)
    edges=collections.defaultdict(lambda:collections.defaultdict(list));pruned=collections.Counter()
    for row in topology:
        aid=row['assay_id'];smiles=canonical.get(row['molregno'])
        if not smiles:pruned['protected_or_unresolved_structure_rows']+=1;continue
        if row['standard_relation']!='=' or row['standard_units'] not in SCALES:pruned['nonexact_or_unmapped_unit_rows']+=1;continue
        role=assaymap[aid]['role']
        if owners.get(smiles)!=role or (role=='final' and smiles in exposed):pruned['cross_role_or_exposed_final_rows']+=1;continue
        edges[(aid,row['standard_type'])][smiles].append(row['activity_id'])
    bytarget=collections.defaultdict(list)
    for key in edges:bytarget[assaymap[key[0]]['tid']].append(key)
    rawcandidates=[]
    for tid,keys in bytarget.items():
        for ref in sorted(keys,key=rank):
            if ref[1] not in {'Ki','Kd'} or len(edges[ref])<128:continue
            # One readout per auxiliary assay; two endpoint types never create
            # two independent assay contexts.
            aux_by_assay={}
            for aux in keys:
                if aux[0]==ref[0]:continue
                overlap=len(set(edges[ref])&set(edges[aux]))
                if overlap<32:continue
                prior=aux_by_assay.get(aux[0])
                if prior is None or (-overlap,rank(aux))<(-len(set(edges[ref])&set(edges[prior])),rank(prior)):
                    aux_by_assay[aux[0]]=aux
            auxsets={f'{a}:{t}':set(edges[(a,t)]) for a,t in aux_by_assay.values()}
            selected=auxiliary_choice(set(edges[ref]),auxsets)
            if not selected:continue
            auxkeys=[(int(k.split(':')[0]),k.split(':')[1]) for k in selected]
            assay=assaymap[ref[0]]
            rawcandidates.append({'bundle_id':'bundle-'+rank(str(ref)+'|'+str(auxkeys))[:20],
                'reference':list(ref),'auxiliary':[list(k) for k in auxkeys],
                'tid':tid,'target_chembl_id':assay['target_chembl_id'],'family_id':assay['family_id'],
                'component_id':assay['component_id'],'role':assay['role'],
                'context_distinctness':'PENDING_SOURCE_REVIEW','reference_construct':'PENDING_SOURCE_REVIEW',
                'nominal_reference_compounds':len(edges[ref]),
                'nominal_shared_union':len(set(edges[ref])&set().union(*(set(edges[k]) for k in auxkeys)))})
    # Deterministic round-robin across source/family components, max120 frozen.
    grouped=collections.defaultdict(list)
    for case in rawcandidates:grouped[case['component_id']].append(case)
    for cases in grouped.values():cases.sort(key=lambda c:rank(c['bundle_id']))
    candidates=[];offset=0
    while len(candidates)<120 and any(len(v)>offset for v in grouped.values()):
        for group in sorted(grouped,key=rank):
            if len(grouped[group])>offset and len(candidates)<120:candidates.append(grouped[group][offset])
        offset+=1
    save('candidates-frozen-before-values.json',{'status':'FROZEN_BEFORE_NUMERIC_SUPPORT_VALIDATION',
        'frame_sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'candidates':candidates,
        'candidate_pool_count':len(rawcandidates),'outcome_values_or_flags_used_for_selection':False,'refill_after_validation':False})
    wanted_keys={tuple(k) for c in candidates for k in [c['reference'],*c['auxiliary']]}
    allowed_ids={i for key in wanted_keys for ids in edges[key].values() for i in ids}
    save('numeric-query-allowlist.json',{'activity_ids':sorted(allowed_ids),'protected_identity_gate_applied':True,
        'candidate_freeze_sha256':hashlib.sha256((p/'candidates-frozen-before-values.json').read_bytes()).hexdigest()})
    # This is the ONLY real source-value interface. Arbitrary SQL is never
    # exposed to the planner. Values exist transiently inside check(), then die.
    validator_db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True)
    validator=PresenceValidator(validator_db,allowed_ids)
    valid=set();booleans=[]
    ordered=sorted(allowed_ids)
    for offset in range(0,len(ordered),1000):
        batch=validator.check(ordered[offset:offset+1000]);booleans.extend(batch)
        valid.update(r['activity_id'] for r in batch if r['exact_positive_finite_support'])
        if offset%10000==0:progress({'status':'VALIDATING_FROZEN_SUPPORT_ONLY','checked':min(offset+1000,len(ordered)),'allowlisted_rows':len(ordered),'numeric_values_emitted':False})
    save('restricted-support-booleans.json',{'records':booleans,'values_or_ranks_present':False})
    valid_edges={key:{s:min(i for i in ids if i in valid) for s,ids in edges[key].items() if any(i in valid for i in ids)} for key in wanted_keys}
    cases=[]
    for candidate in candidates:
        ref=tuple(candidate['reference']);aux=[tuple(k) for k in candidate['auxiliary']]
        selected=panel(set(valid_edges[ref]),{str(k):set(valid_edges[k]) for k in aux})
        record=dict(candidate);record['finite_reference_compounds']=len(valid_edges[ref])
        record['status']='PASS_FINITE_PANEL_SUPPORT' if selected else 'FAIL_FINITE_PANEL_SUPPORT'
        if selected:
            record['reference_panel']=[{'canonical_sha256':hashlib.sha256(s.encode()).hexdigest(),
                'reference_activity_id':valid_edges[ref][s],
                'auxiliary_activity_ids':{str(k):valid_edges[k][s] for k in aux if s in valid_edges[k]}} for s in selected]
            record['panel_compounds']=128
            record['panel_shared_union']=sum(any(s in valid_edges[k] for k in aux) for s in selected)
            record['panel_shared_per_auxiliary']={str(k):sum(s in valid_edges[k] for s in selected) for k in aux}
        cases.append(record)
    # Reserve two distinct reference assays per component, without replacing
    # failures from outside the prevalidation candidate frame.
    valid_by_group=collections.defaultdict(list)
    for case in cases:
        if case['status']=='PASS_FINITE_PANEL_SUPPORT':valid_by_group[case['component_id']].append(case)
    paired={};partial=[]
    for group,items in valid_by_group.items():
        chosen=[];seen=set()
        for item in sorted(items,key=lambda c:rank(c['bundle_id'])):
            if item['reference'][0] in seen:continue
            chosen.append(item);seen.add(item['reference'][0])
            if len(chosen)==2:break
        if len(chosen)==2:paired[group]=chosen
        else:partial.extend(chosen)
    reserved=[];groupcounts=collections.Counter()
    for role,quota in [('development',4),('validation',2),('final',12)]:
        groups=sorted([g for g,c in paired.items() if c[0]['role']==role],key=rank)[:quota]
        for group in groups:reserved.extend(paired[group]);groupcounts[role]+=1
    save('cohort-support-frozen.json',{'status':'CANDIDATE_SUPPORT_COHORT_NOT_REFERENCE_GOLD',
        'reserved':reserved,'all_candidates':cases,'partial_group_diagnostics':partial,
        'paired_group_roles_available':dict(collections.Counter(v[0]['role'] for v in paired.values())),
        'reserved_group_roles':dict(groupcounts),'certified_biological_families':0,
        'reference_constructs_and_context_distinctness':'PENDING_SOURCE_REVIEW',
        'numeric_utility_computed':False,'old_final_outcomes_queried':False,'parent_is_independent_adjudicator':False})
    save('result.json',{'status':'PASS_BOUNDED_SUPPORT_QUALIFICATION','topology_rows':len(topology),
        'complete_assays':len(complete),'incomplete_assays':len(frame['assays'])-len(complete),
        'molecule_ids':len(molecules),'identity_dispositions':dict(collections.Counter(d['status'] for d in dispositions)),
        'known_exposed_canonical_identity_count':len(exposed),
        'row_pruning':dict(pruned),'frozen_candidates':len(candidates),'numeric_validity_rows_checked':len(allowed_ids),
        'finite_support_rows':len(valid),'finite_panel_candidates':sum(c['status']=='PASS_FINITE_PANEL_SUPPORT' for c in cases),
        'available_paired_group_roles':dict(collections.Counter(v[0]['role'] for v in paired.values())),
        'reserved_bundles':len(reserved),'reserved_group_roles':dict(groupcounts),
        'context_and_reference_certification':'NOT_RUN','biological_family_certification':'NOT_RUN',
        'numeric_values_ranks_or_utility_emitted':False,'wall_seconds':time.monotonic()-started})
except Exception as exc:
    import traceback
    save('result.json',{'status':'FAIL_SUPPORT_QUALIFICATION','error_type':type(exc).__name__,
        'error_frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)],
        'numeric_values_emitted':False})
    raise SystemExit(1)
