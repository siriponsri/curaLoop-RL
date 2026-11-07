"""Freeze a metadata-only target/assay frame before identity/value checks."""
import collections,hashlib,json,sqlite3,sys,time
from pathlib import Path
from r0dq_projection_v1 import protect_metadata_connection
from research.taskfirst_dq_v1.rules import RULES
from research.taskfirst_dq_v1.selection import known_family_map,rank,source_components

p=Path(sys.argv[1]);root=p.parents[1];started=time.monotonic()
def save(name,obj):
    target=p/name;assert not target.exists();target.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def query(sql,args=()):return [dict(row) for row in db.execute(sql,args)]
try:
    unpack_proofs=[json.loads(path.read_text()) for path in (root/'jobs').glob('unpack-v*/result.json')]
    assert sum(proof['status']=='PASS_VERIFIED_EXTRACTION_AND_SCHEMA' for proof in unpack_proofs)==1
    assert json.loads((p/'frame-rules-frozen.json').read_text())==RULES
    reg=json.loads((root/'inputs/family-registry-v3.json').read_text())
    protection=json.loads((root/'inputs/protected-identities.json').read_text())
    exposure=json.loads((root/'inputs/exposure-register-v1.json').read_text())
    fmap,oldroles,ambiguous=known_family_map(reg)
    protected_families=set(protection['family_ids']);protected_accessions=set(protection['uniprot_accessions'])
    oldassays=set(exposure['old_r0_assay_ids'])|set(protection['assay_ids'])
    forced={f for f,role in oldroles.items() if role in {'development','validation'}}
    db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True)
    db.row_factory=sqlite3.Row;protect_metadata_connection(db)
    # Explicitly reconcile the incidental planning exposure without its values.
    incidental=[];extra_assays=set();extra_targets=set();extra_docs=set();extra_molecules=set()
    for identity in exposure['planning_exposed_ids']:
        if isinstance(identity,dict):identity=identity.get('id') or identity.get('chembl_id')
        assert isinstance(identity,str)
        found=[]
        for table,field,output in [('molecule_dictionary','molregno',extra_molecules),('target_dictionary','tid',extra_targets),('assays','assay_id',extra_assays),('docs','doc_id',extra_docs)]:
            hits=query('SELECT '+field+' FROM '+table+' WHERE chembl_id=?',(identity,))
            for hit in hits:output.add(hit[field]);found.append(table)
        incidental.append({'chembl_id':identity,'entity_types':found,'resolved':len(found)==1})
    olddocs={r['doc_id'] for identity in exposure['old_r0_document_ids'] for r in query('SELECT doc_id FROM docs WHERE chembl_id=?',(identity,))}|extra_docs
    targetrows=query('''SELECT t.tid,t.chembl_id,t.target_type,t.organism,t.tax_id,c.accession,c.tax_id component_tax_id,c.organism component_organism
        FROM target_dictionary t JOIN target_components tc ON tc.tid=t.tid
        JOIN component_sequences c ON c.component_id=tc.component_id
        WHERE t.target_type='SINGLE_PROTEIN' ''')
    targetgroup=collections.defaultdict(list)
    for row in targetrows:targetgroup[row['tid']].append(row)
    catalog=[];attrition=collections.Counter();candidates=[]
    for tid,rows in targetgroup.items():
        if len(rows)!=1:attrition['target_multiple_components']+=1;continue
        row=rows[0];accession=row['accession'];family=fmap.get(accession)
        if not family:attrition['target_unmapped_or_ambiguous_family']+=1;continue
        if family in protected_families or accession in protected_accessions:attrition['target_protected_family_or_accession']+=1;continue
        if row['tax_id'] is None or row['tax_id']!=row['component_tax_id']:attrition['target_organism_unreconciled']+=1;continue
        row['family_id']=family
        if row['chembl_id'] in exposure['old_r0_target_ids'] or tid in extra_targets:forced.add(family)
        assays=query('''SELECT a.assay_id,a.chembl_id,a.tid,a.doc_id,a.assay_type,a.assay_test_type,a.assay_category,
            a.assay_organism,a.assay_tax_id,a.assay_strain,a.assay_tissue,a.assay_cell_type,a.assay_subcellular_fraction,
            a.confidence_score,a.relationship_type,a.bao_format,a.assay_group,a.variant_id,a.cell_id,a.tissue_id,a.src_id,
            d.chembl_id document_chembl_id,d.doi,d.pubmed_id,d.year
            FROM assays a JOIN docs d ON d.doc_id=a.doc_id WHERE a.tid=? AND a.confidence_score=9
            AND a.relationship_type='D' AND a.assay_type IN ('B','F') ''',(tid,))
        eligible={}
        for assay in assays:
            if assay['chembl_id'] in oldassays or assay['assay_id'] in extra_assays:attrition['assay_prior_or_protected']+=1;continue
            if not assay['doi']:attrition['assay_no_primary_doi']+=1;continue
            if assay['assay_tax_id'] is not None and assay['assay_tax_id']!=row['tax_id']:attrition['assay_organism_conflict']+=1;continue
            assay.update(family_id=family,accession=accession,target_chembl_id=row['chembl_id'])
            assay['metadata_counts']={};eligible[assay['assay_id']]=assay
            if assay['doc_id'] in olddocs:forced.add(family)
        if not eligible:continue
        # No standard_value, value-derived flag, pChEMBL, comment or rank.
        counts=query('''SELECT ac.assay_id,ac.standard_type,COUNT(DISTINCT ac.molregno) molecule_ids
            FROM activities ac JOIN assays a ON a.assay_id=ac.assay_id
            WHERE a.tid=? AND a.confidence_score=9 AND a.relationship_type='D' AND a.assay_type IN ('B','F')
            AND ac.standard_type IN ('Ki','Kd','IC50') AND ac.standard_relation='='
            AND ac.standard_units IN ('M','mM','uM','μM','nM','pM','fM')
            GROUP BY ac.assay_id,ac.standard_type ''',(tid,))
        for count in counts:
            if count['assay_id'] in eligible:eligible[count['assay_id']]['metadata_counts'][count['standard_type']]=count['molecule_ids']
        refs=[a for a in eligible.values() if any(a['metadata_counts'].get(t,0)>=128 for t in ['Ki','Kd'])]
        aux=[a for a in eligible.values() if max(a['metadata_counts'].values(),default=0)>=32]
        if not refs or len(aux)<2:attrition['target_no_nominal_reference_auxiliary_catalog']+=1;continue
        row.update(reference_capable_assays=len(refs),document_diversity=len({a['doc_id'] for a in aux}))
        row['assays']=aux;candidates.append(row)
        catalog.append({k:v for k,v in row.items() if k!='assays'})
    grouped=collections.defaultdict(list)
    for target in candidates:grouped[target['family_id']].append(target)
    for rows in grouped.values():rows.sort(key=lambda t:(-t['reference_capable_assays'],-t['document_diversity'],rank(t['tid'])))
    selected=[];offset=0
    while len(selected)<100 and any(len(v)>offset for v in grouped.values()):
        for family in sorted(grouped,key=rank):
            if len(grouped[family])>offset and len(selected)<100:selected.append(grouped[family][offset])
        offset+=1
    frame=[]
    for target in selected:
        assays=target.pop('assays')
        refs=sorted([a for a in assays if any(a['metadata_counts'].get(t,0)>=128 for t in ['Ki','Kd'])],key=lambda a:rank(a['assay_id']))[:4]
        chosen=list(refs);remaining=[a for a in assays if a not in refs]
        while remaining and len(chosen)<20:
            useddocs={a['doc_id'] for a in chosen}
            best=min(remaining,key=lambda a:(a['doc_id'] in useddocs,-sum(a['metadata_counts'].values()),rank(a['assay_id'])))
            chosen.append(best);remaining.remove(best)
        frame.extend(chosen)
    assert len(selected)<=100 and len(frame)<=2000
    mapping,components=source_components(frame,forced)
    for assay in frame:
        assay['component_id']=mapping[assay['family_id']]['component_id'];assay['role']=mapping[assay['family_id']]['role']
    frozen={'schema':'curaloop.r0dq.frame.v1','status':'FROZEN_BEFORE_VALUE_AND_METHODS_INSPECTION',
        'rules_sha256':hashlib.sha256((p/'frame-rules-frozen.json').read_bytes()).hexdigest(),
        'targets':selected,'assays':frame,'components':components,'catalog_candidate_target_count':len(catalog),'attrition':dict(attrition),
        'incidental_exposure_reconciliation':incidental,'incidental_molregnos':sorted(extra_molecules),
        'prior_exposed_document_ids':sorted(olddocs),'prior_family_roles_preserved':True,
        'numeric_source_columns_queried':False,'protected_final_outcomes_queried':False,
        'unmapped_accessions_quarantined':True,'biological_family_certification':'NOT_RUN'}
    save('frame-frozen.json',frozen)
    save('result.json',{'status':'PASS_METADATA_FRAME_FROZEN','targets':len(selected),'assays':len(frame),
        'typed_families':len({a['family_id'] for a in frame}),'family_source_components':len(components),
        'component_roles':dict(collections.Counter(c['role'] for c in components)),
        'frame_sha256':hashlib.sha256((p/'frame-frozen.json').read_bytes()).hexdigest(),
        'numeric_outcomes_emitted':False,'wall_seconds':time.monotonic()-started})
except Exception as exc:
    import traceback
    save('result.json',{'status':'FAIL_METADATA_FRAME','error_type':type(exc).__name__,
        'error_frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)],
        'numeric_outcomes_emitted':False})
    raise SystemExit(1)
