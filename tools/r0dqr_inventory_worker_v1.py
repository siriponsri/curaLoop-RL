"""Full target/classification inventory; labels are not family certificates."""
import collections,hashlib,json,sqlite3,sys,time,traceback
from pathlib import Path
from r0dqr_projection_v1 import protect_metadata_connection,SAFE_TABLES
from research.taskfirst_dqr_v1.rules import RULES
from research.taskfirst_dqr_v1.selection import known_family_map,rank

p=Path(sys.argv[1]);root=p.parents[1];start=time.monotonic()
def save(name,value):
    target=p/name;assert not target.exists();target.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
try:
    assert json.loads((root/'jobs/prepare-v1/result.json').read_text())['status']=='PASS_VERIFIED_EXTRACTION_AND_SCHEMA'
    assert json.loads((p/'frame-rules-frozen.json').read_text())==RULES
    db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True);db.row_factory=sqlite3.Row
    protect_metadata_connection(db)
    q=lambda sql,args=():[dict(r) for r in db.execute(sql,args)]
    columns={r['name'] for r in q('PRAGMA table_info(protein_classification)')}
    assert {'protein_class_id','parent_id'}<=columns
    selected=sorted(columns&SAFE_TABLES['protein_classification'])
    classes={r['protein_class_id']:r for r in q('SELECT '+','.join(selected)+' FROM protein_classification')}
    def ancestry(cid):
        path=[];seen=set()
        while cid is not None:
            assert cid not in seen and cid in classes;seen.add(cid);path.append(cid);cid=classes[cid]['parent_id']
        return path[::-1]
    for cid,row in classes.items():row['ancestry_from_root']=ancestry(cid)
    reg=json.loads((root/'inputs/family-registry-v3.json').read_text());fmap,roles,ambiguous=known_family_map(reg)
    protection=json.loads((root/'inputs/protected-identities.json').read_text())
    exposure=json.loads((root/'inputs/exposure-register-v1.json').read_text())
    carry=json.loads((root/'inputs/r0dq-carried-exposure-v1.json').read_text())
    targets=q("SELECT tid,chembl_id,target_type,organism,tax_id FROM target_dictionary WHERE target_type='SINGLE PROTEIN'")
    assert len(targets)<=RULES['inventory_limit']
    components=collections.defaultdict(list)
    for row in q('SELECT tc.tid,tc.component_id,tc.homologue,c.accession,c.tax_id component_tax_id,c.organism component_organism FROM target_components tc JOIN component_sequences c ON c.component_id=tc.component_id'):
        components[row['tid']].append(row)
    annotations=collections.defaultdict(list)
    for row in q('SELECT component_id,protein_class_id FROM component_class'):annotations[row['component_id']].append(row['protein_class_id'])
    counts=collections.Counter();depths=collections.defaultdict(set)
    for target in targets:
        comp=components[target['tid']];target['components']=comp
        if len(comp)!=1:target.update(gate='QUARANTINE_MULTIPLE_OR_MISSING_COMPONENT',family_id=None,role='quarantine');counts[target['gate']]+=1;continue
        c=comp[0];family=fmap.get(c['accession']);lineage_role=roles.get(family)
        ids=sorted(set(annotations[c['component_id']]));paths=[ancestry(cid) for cid in ids]
        for path in paths:
            for depth,cid in enumerate(path):depths[depth].add(cid)
        strata=sorted({path[1] if len(path)>1 else path[0] for path in paths})
        stratum=min(strata,key=rank) if strata else 'UNANNOTATED'
        exposed=target['chembl_id'] in set(exposure['old_r0_target_ids'])|set(carry['target_chembl_ids'])
        if c['accession'] in protection['uniprot_accessions'] or family in protection['family_ids']:gate='EXCLUDE_PROTECTED_LINEAGE'
        elif c['homologue'] not in (0,None):gate='QUARANTINE_HOMOLOGUE'
        elif target['tax_id'] is None or target['tax_id']!=c['component_tax_id']:gate='QUARANTINE_TAXON_CONFLICT'
        else:gate='ADMITTED_METADATA_FEASIBILITY'
        # A diagnostic stratum never clears an inherited lineage or creates a final role.
        role='development' if exposed or lineage_role=='development' or family is None else lineage_role or 'quarantine'
        final_status='QUARANTINE_UNCERTIFIED_BIOLOGICAL_MAPPING' if family is None else 'INHERITED_ROLE_ONLY_NO_NEW_FAMILY_CERTIFICATION'
        target.update(accession=c['accession'],family_id=family,inherited_role=lineage_role,role=role,
            prior_exposure=exposed,gate=gate,class_ids=ids,class_paths=paths,sampling_stratum=stratum,
            multiple_diagnostic_strata=len(strata)>1,final_status=final_status)
        counts[gate]+=1;counts['mapped_inherited_family' if family else 'unmapped_inherited_family']+=1
    save('taxonomy-inventory.json',{'status':'TRACEABLE_METADATA_INVENTORY_NOT_FAMILY_CERTIFICATION',
        'rules_sha256':hashlib.sha256((p/'frame-rules-frozen.json').read_bytes()).hexdigest(),
        'targets':targets,'protein_classes':list(classes.values()),'target_counts':dict(counts),
        'class_nodes_by_path_depth':{str(k):len(v) for k,v in depths.items()},
        'inherited_ambiguous_accessions':ambiguous,'registry_top_level_keys':list(reg),
        'all_inherited_roles_retained':True,'new_biological_family_certificates':0,'numeric_activity_queries':0})
    save('result.json',{'status':'PASS_TAXONOMY_INVENTORY','targets':len(targets),'classification_nodes':len(classes),
        'target_counts':dict(counts),'diagnostic_strata':len({t.get('sampling_stratum') for t in targets if t.get('sampling_stratum') is not None}),
        'new_biological_family_certificates':0,'numeric_activity_queries':0,'wall_seconds':time.monotonic()-start})
except Exception as exc:
    save('result.json',{'status':'FAIL_TAXONOMY_INVENTORY','error_type':type(exc).__name__,
        'error_frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)]})
    raise SystemExit(1)
