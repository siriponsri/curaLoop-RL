"""Outcome-free bounded nominal support; procedure pools remain hypotheses."""
import collections,hashlib,json,sqlite3,sys,time,traceback
from pathlib import Path
from r0dqr_projection_v1 import protect_metadata_connection
from r0dqr_context_projection_v1 import project_text
from research.taskfirst_dqr_v1.rules import RULES
from research.taskfirst_dqr_v1.selection import rank,auxiliary_choice,panel
from rdkit import Chem,rdBase,RDLogger

p=Path(sys.argv[1]);root=p.parents[1];start=time.monotonic()
def save(name,value):
    target=p/name;assert not target.exists();target.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def progress(value):
    t=p/'progress.tmp';t.write_text(json.dumps(value));t.replace(p/'progress.json')
def rr(groups,limit):
    for values in groups.values():values.sort(key=lambda x:rank(x.get('bundle_id',x.get('assay_id',x.get('tid')))))
    result=[];offset=0
    while len(result)<limit and any(len(v)>offset for v in groups.values()):
        for key in sorted(groups,key=rank):
            if len(groups[key])>offset and len(result)<limit:result.append(groups[key][offset])
        offset+=1
    return result
try:
    assert rdBase.rdkitVersion=='2026.09.1';RDLogger.DisableLog('rdApp.*')
    assert json.loads((p/'frame-rules-frozen.json').read_text())==RULES
    inventory=json.loads((root/'jobs/inventory-v1/taxonomy-inventory.json').read_text())
    targets={t['tid']:t for t in inventory['targets'] if t['gate']=='ADMITTED_METADATA_FEASIBILITY'}
    exposure=json.loads((root/'inputs/exposure-register-v1.json').read_text())
    protection=json.loads((root/'inputs/protected-identities.json').read_text())
    carry=json.loads((root/'inputs/r0dq-carried-exposure-v1.json').read_text())
    oldassays=set(exposure['old_r0_assay_ids'])|set(protection['assay_ids'])
    db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True);db.row_factory=sqlite3.Row
    # Only temporary query planning; source connection is read-only and immutable.
    db.execute('PRAGMA temp_store=MEMORY');db.execute('PRAGMA cache_size=-65536');protect_metadata_connection(db)
    q=lambda sql,args=():[dict(r) for r in db.execute(sql,args)]
    progress({'status':'COUNTING_NOMINAL_IDS_NO_VALUES_OR_PRESENCE_FLAGS'})
    counts=collections.defaultdict(dict)
    sql="""SELECT assay_id,standard_type,COUNT(DISTINCT molregno) n FROM activities
        WHERE standard_type IN ('Ki','Kd','IC50') AND standard_relation='='
        AND standard_units IN ('M','mM','uM','μM','nM','pM','fM')
        GROUP BY assay_id,standard_type HAVING COUNT(DISTINCT molregno)>=1"""
    for row in db.execute(sql):counts[row['assay_id']][row['standard_type']]=row['n']
    catalog=collections.defaultdict(list);attrition=collections.Counter()
    rows=db.execute("""SELECT a.assay_id,a.chembl_id,a.tid,a.doc_id,a.assay_type,a.assay_test_type,a.assay_category,
        a.assay_organism,a.assay_tax_id,a.assay_strain,a.assay_tissue,a.assay_cell_type,a.assay_subcellular_fraction,
        a.bao_format,a.assay_group,a.variant_id,a.cell_id,a.tissue_id,a.src_id,
        d.chembl_id document_chembl_id,d.doi,d.pubmed_id,d.year
        FROM assays a JOIN docs d ON d.doc_id=a.doc_id WHERE a.confidence_score=9
        AND a.relationship_type='D' AND a.assay_type IN ('B','F')""")
    for raw in rows:
        a=dict(raw);t=targets.get(a['tid'])
        if t is None or a['assay_id'] not in counts:continue
        if a['chembl_id'] in oldassays:attrition['old_or_protected_assay']+=1;continue
        if not a['doi']:attrition['no_primary_doi']+=1;continue
        if a['assay_tax_id'] is not None and a['assay_tax_id']!=t['tax_id']:attrition['assay_taxon_conflict']+=1;continue
        a.update(nominal_counts=counts[a['assay_id']],accession=t['accession'],family_id=t['family_id'],
            role=t['role'],sampling_stratum=t['sampling_stratum'],target_chembl_id=t['chembl_id'],
            final_status=t['final_status'])
        catalog[a['tid']].append(a)
    grouped=collections.defaultdict(list)
    for tid,assays in catalog.items():
        priority=any(max(a['nominal_counts'].get('Ki',0),a['nominal_counts'].get('Kd',0))>=128 for a in assays) and len(assays)>=2
        target=dict(targets[tid],nominal_priority=priority)
        grouped[target['sampling_stratum']].append(target)
    # Priority before fixed hash, within each diagnostic stratum.
    for values in grouped.values():values.sort(key=lambda t:(not t['nominal_priority'],rank(t['tid'])))
    selected=[];offset=0
    while len(selected)<200 and any(len(v)>offset for v in grouped.values()):
        for key in sorted(grouped,key=rank):
            if len(grouped[key])>offset and len(selected)<200:selected.append(grouped[key][offset])
        offset+=1
    frame=[]
    for t in selected:
        docs=collections.defaultdict(list)
        for a in catalog[t['tid']]:docs[a['doi'].strip().lower()].append(a)
        frame.extend(rr(docs,20))
    assert len(frame)<=4000
    save('frame-frozen.json',{'status':'FROZEN_BEFORE_COMPLETE_GRAPH_AND_SOURCE_INTERPRETATION','targets':selected,'assays':frame,
        'catalog_targets_with_nominal_assays':len(catalog),'nominal_catalog_counts_not_finite_support':True,
        'attrition':dict(attrition),'numeric_values_or_presence_flags_used':False,'new_family_certificates':0})
    progress({'status':'BUILDING_COMPLETE_BOUNDED_TOPOLOGY','targets':len(selected),'assays':len(frame)})
    topology=[];molecules=set();states=[];complete=[]
    for a in sorted(frame,key=lambda a:rank(a['assay_id'])):
        aid=a['assay_id'];where="assay_id=? AND standard_type IN ('Ki','Kd','IC50')"
        n=db.execute('SELECT COUNT(*) FROM activities INDEXED BY fk_act_assay_id WHERE '+where,(aid,)).fetchone()[0]
        if len(topology)+n>2000000:states.append({'assay_id':aid,'status':'INCOMPLETE_ROW_CAP','catalog_rows':n});continue
        rows=q('SELECT activity_id,assay_id,molregno,doc_id,standard_type,standard_relation,standard_units FROM activities INDEXED BY fk_act_assay_id WHERE '+where,(aid,))
        assert len(rows)==n;added={r['molregno'] for r in rows if r['molregno'] is not None}
        if len(molecules|added)>100000:states.append({'assay_id':aid,'status':'INCOMPLETE_MOLECULE_CAP','catalog_rows':n});continue
        topology.extend(rows);molecules.update(added);complete.append(aid);states.append({'assay_id':aid,'status':'COMPLETE','rows':n})
    save('topology-outcome-free.json',{'rows':topology,'assay_states':states,'activity_values_or_presence_flags_present':False})
    progress({'status':'CANONICALIZING_IDENTITY_ONLY','rows':len(topology),'molecules':len(molecules)})
    protected=set(protection['canonical_smiles']);known=set(json.loads((root/'inputs/additional-exposure-v1.json').read_text())['canonical_smiles'])
    carryhash=set(carry['canonical_sha256']);oldids=set(exposure['old_r0r_molecule_ids'])
    identity={};dispositions=[];exposed_hash=set(carryhash)
    for molid in sorted(molecules):
        row=db.execute('SELECT m.chembl_id,s.canonical_smiles FROM molecule_dictionary m LEFT JOIN compound_structures s ON s.molregno=m.molregno WHERE m.molregno=?',(molid,)).fetchone()
        mol=Chem.MolFromSmiles(row['canonical_smiles']) if row and row['canonical_smiles'] else None
        canonical=Chem.MolToSmiles(mol,canonical=True,isomericSmiles=True) if mol else None
        digest=hashlib.sha256(canonical.encode()).hexdigest() if canonical else None
        status='QUARANTINE_UNRESOLVED' if not canonical else 'EXCLUDE_PROTECTED_EXACT_IDENTITY' if canonical in protected else 'ADMITTED_IDENTITY'
        if canonical and (canonical in known or row['chembl_id'] in oldids):exposed_hash.add(digest)
        if status=='ADMITTED_IDENTITY':identity[molid]=digest
        dispositions.append({'molregno':molid,'molecule_chembl_id':row['chembl_id'] if row else None,'canonical_sha256':digest,'status':status})
    save('identity-dispositions.json',{'records':dispositions,'rdkit':rdBase.rdkitVersion,
        'normalization':'canonical isomeric SMILES; no salt/charge/isotope/tautomer normalization','chemical_OOD_certified':False})
    amap={a['assay_id']:a for a in frame if a['assay_id'] in complete};edges=collections.defaultdict(set);pruned=collections.Counter()
    for r in topology:
        s=identity.get(r['molregno']);a=amap[r['assay_id']]
        if not s:pruned['protected_or_unresolved']+=1;continue
        if r['standard_relation']!='=' or r['standard_units'] not in RULES['nominal_units']:pruned['relation_or_unit']+=1;continue
        if a['role']!='development' and s in exposed_hash:pruned['known_exposure_outside_development']+=1;continue
        edges[(r['assay_id'],r['standard_type'])].add(s)
    # Preserve higher-priority inherited role ownership across exact identities.
    priority={'development':0,'validation':1,'final':2,'quarantine':-1};owners={}
    for (aid,_),values in edges.items():
        role=amap[aid]['role']
        for s in values:
            if priority[role]>priority.get(owners.get(s),-2):owners[s]=role
    edges={k:{s for s in v if owners[s]==amap[k[0]]['role']} for k,v in edges.items()}
    signatures=collections.defaultdict(list);metadata=[]
    for aid,a in amap.items():
        raw=db.execute('SELECT description FROM assays WHERE assay_id=?',(aid,)).fetchone()[0]
        projection=project_text(raw);meta=dict(a,description_projection=projection,construct_status='UNKNOWN_UNTIL_SOURCE_REVIEW')
        metadata.append(meta)
        if projection['text']:
            signature=tuple(a.get(k) for k in ['tid','doc_id','assay_organism','assay_tax_id','assay_type','variant_id','cell_id','tissue_id','assay_cell_type','assay_tissue','assay_subcellular_fraction','bao_format'])+(projection['text'],)
            for typ in RULES['reference_types']:
                if (aid,typ) in edges:signatures[(signature,typ)].append(aid)
    save('context-metadata-projected.json',{'assays':metadata,'raw_passages_emitted':False,'complete_context_gold':False})
    units=[{'unit_id':str(aid)+':'+typ,'assay_ids':[aid],'type':typ,'kind':'single_assay','tid':amap[aid]['tid'],'values':v} for (aid,typ),v in edges.items()]
    pools=[]
    for (sig,typ),ids in signatures.items():
        if len(ids)<2:continue
        values=set().union(*(edges[(aid,typ)] for aid in ids))
        pools.append({'unit_id':'pending-pool-'+rank((ids,typ))[:20],'assay_ids':sorted(ids),'type':typ,
            'kind':'same_projected_metadata_signature_PENDING_SOURCE','tid':amap[ids[0]]['tid'],'values':values,
            'procedure_equivalence':'NOT_ESTABLISHED','construct_concordance':'UNKNOWN','eligible_pool':False})
    bytarget=collections.defaultdict(list)
    for unit in units:bytarget[unit['tid']].append(unit)
    rawcases=[]
    for ref in units+pools:
        if ref['type'] not in {'Ki','Kd'} or len(ref['values'])<128:continue
        aux={u['unit_id']:u for u in bytarget[ref['tid']] if not set(u['assay_ids'])&set(ref['assay_ids'])}
        choices=auxiliary_choice(ref['values'],{k:v['values'] for k,v in aux.items()})
        if not choices:continue
        t=targets[ref['tid']];chosen=panel(ref['values'],{k:aux[k]['values'] for k in choices});assert chosen
        rawcases.append({'bundle_id':'bundle-'+rank((ref['unit_id'],choices))[:20],
            'tid':ref['tid'],'target_chembl_id':t['chembl_id'],'accession':t['accession'],'family_id':t['family_id'],
            'role':t['role'],'final_status':t['final_status'],'sampling_stratum':t['sampling_stratum'],
            'reference':{k:v for k,v in ref.items() if k!='values'},'auxiliary':[{k:v for k,v in aux[c].items() if k!='values'} for c in choices],
            'nominal_reference_compounds':len(ref['values']),'panel_canonical_hashes':chosen,
            'panel_shared_union':len(set(chosen)&set().union(*(aux[c]['values'] for c in choices))),
            'panel_shared_per_auxiliary':{c:len(set(chosen)&aux[c]['values']) for c in choices},
            'numerical_support':'NOT_QUERIED','procedure_reference_gold':'NOT_ESTABLISHED'})
    bystratum=collections.defaultdict(list)
    for c in rawcases:bystratum[c['sampling_stratum']].append(c)
    cases=rr(bystratum,120)
    save('candidates-frozen.json',{'status':'FROZEN_NOMINAL_CANDIDATES_NOT_QUALIFIED_TASKS','candidates':cases,
        'candidate_pool':len(rawcases),'no_activity_values_or_nonmissingness_flags':True,'no_source_interpretation_refill':True})
    upper=collections.defaultdict(set)
    for (aid,typ),v in edges.items():upper[(amap[aid]['tid'],typ)].update(v)
    save('pooling-diagnostics.json',{'pending_signature_pools':[{k:v for k,v in u.items() if k!='values'}|{'nominal_compounds':len(u['values'])} for u in pools],
        'accepted_source_verified_pools':0,'strict_complete_context_pools':0,
        'unrestricted_target_type_128_upper_bound_units':sum(typ in {'Ki','Kd'} and len(v)>=128 for (_,typ),v in upper.items()),
        'unrestricted_upper_bound_is_ineligible':True,'null_variant_is_wild_type':False})
    result={'status':'PASS_BOUNDED_NOMINAL_FEASIBILITY','targets':len(selected),'assays':len(frame),'complete_assays':len(complete),
        'topology_rows':len(topology),'molecule_ids':len(molecules),'incomplete_assays':len(frame)-len(complete),
        'diagnostic_strata':len({t['sampling_stratum'] for t in selected}),'known_inherited_family_ids':len({t['family_id'] for t in selected if t['family_id']}),
        'candidate_pool':len(rawcases),'frozen_candidates':len(cases),'single_assay_candidates':sum(c['reference']['kind']=='single_assay' for c in cases),
        'pending_pool_candidates':sum(c['reference']['kind']!='single_assay' for c in cases),'accepted_source_verified_pools':0,
        'candidate_roles':dict(collections.Counter(c['role'] for c in cases)),
        'candidate_targets':len({c['tid'] for c in cases}),'candidate_diagnostic_strata':len({c['sampling_stratum'] for c in cases}),
        'certified_biological_families':0,'source_activity_numeric_or_presence_queries':0,
        'identity_dispositions':dict(collections.Counter(r['status'] for r in dispositions)),'row_pruning':dict(pruned),
        'wall_seconds':time.monotonic()-start}
    save('result.json',result)
except Exception as exc:
    save('result.json',{'status':'FAIL_NOMINAL_FEASIBILITY','error_type':type(exc).__name__,
        'error_frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)]})
    raise SystemExit(1)
