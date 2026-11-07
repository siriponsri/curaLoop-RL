"""Freeze a development source frame, then project bounded procedural metadata."""
import collections,hashlib,json,sqlite3,sys,traceback
from pathlib import Path
from r0dqr_context_projection_v1 import project_text,PARAM_INPUT,PARAM_VALUE
from research.taskfirst_dqr_v1.selection import rank

p=Path(sys.argv[1]);root=p.parents[1]
def save(name,obj):
    t=p/name;assert not t.exists();t.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
try:
    candidates=json.loads((root/'jobs/nominal-v1/candidates-frozen.json').read_text())['candidates']
    frame=json.loads((root/'jobs/nominal-v1/frame-frozen.json').read_text());amap={a['assay_id']:a for a in frame['assays']}
    projected=json.loads((root/'jobs/nominal-v1/context-metadata-projected.json').read_text());metas={a['assay_id']:a for a in projected['assays']}
    grouped=collections.defaultdict(list)
    for c in candidates:
        if c['role']=='development':grouped[c['sampling_stratum']].append(c)
    for v in grouped.values():v.sort(key=lambda c:rank(c['bundle_id']))
    ordered=[];offset=0
    while any(len(v)>offset for v in grouped.values()):
        for key in sorted(grouped,key=rank):
            if len(grouped[key])>offset:ordered.append(grouped[key][offset])
        offset+=1
    chosen=[];docs={};ids=set();deferred=[]
    for c in ordered:
        aids={aid for u in [c['reference'],*c['auxiliary']] for aid in u['assay_ids']}
        newdocs={amap[aid]['doc_id'] for aid in aids}
        if len(chosen)>=6 or len(set(docs)|newdocs)>12:deferred.append(c['bundle_id']);continue
        chosen.append(c);ids|=aids
        for aid in aids:
            a=amap[aid];docs[a['doc_id']]={k:a[k] for k in ['doc_id','document_chembl_id','doi','pubmed_id','year']}
    save('source-intent-frozen.json',{'status':'FROZEN_BEFORE_PROCEDURAL_PARAMETER_AND_SOURCE_READ','bundle_ids':[c['bundle_id'] for c in chosen],
        'documents':list(docs.values()),'assay_ids':sorted(ids),'deferred_bundles':deferred,'max_documents':12})
    db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True);db.row_factory=sqlite3.Row
    # This fixed role admits procedural assay parameters only, never activities.
    allowed={'assay_parameters':set('assay_param_id assay_id type units standard_type standard_units value standard_value'.split()),
        'variant_sequences':set('variant_id accession mutation isoform organism'.split())}
    def auth(action,a,b,c,d):
        if action==sqlite3.SQLITE_READ:return sqlite3.SQLITE_OK if a in allowed and b in allowed[a] else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK if action==sqlite3.SQLITE_SELECT else sqlite3.SQLITE_DENY
    db.set_authorizer(auth);records=[]
    for aid in sorted(ids):
        meta=dict(metas[aid]);assert meta['role']=='development';params=[]
        for raw in db.execute('SELECT assay_param_id,type,units,standard_type,standard_units FROM assay_parameters WHERE assay_id=?',(aid,)):
            item=dict(raw);label=(item['standard_type'] or item['type'] or '').strip()
            if PARAM_INPUT.fullmatch(label):
                values=db.execute('SELECT value,standard_value FROM assay_parameters WHERE assay_param_id=? AND assay_id=?',(item['assay_param_id'],aid)).fetchone()
                item['procedural_inputs']={k:str(values[k]) if values[k] is not None and len(str(values[k]))<128 and PARAM_VALUE.fullmatch(str(values[k])) else None for k in ['value','standard_value']}
                item['status']='PERMITTED_INPUT_TYPE_AND_FORMAT_ONLY'
            else:item['status']='OMITTED_UNVERIFIED_PARAMETER_SEMANTICS'
            params.append(item)
        meta['parameters']=params
        if meta['variant_id']:
            row=db.execute('SELECT variant_id,accession,mutation,isoform,organism FROM variant_sequences WHERE variant_id=?',(meta['variant_id'],)).fetchone()
            if row:
                variant=dict(row);variant['mutation_projection']=project_text(variant.pop('mutation'));meta['variant']=variant
        meta['null_variant_establishes_wild_type']=False;meta['source_equivalence']='PENDING_SOURCE_AND_DOMAIN_REVIEW';records.append(meta)
    save('development-packet.json',{'status':'DEVELOPMENT_FEASIBILITY_NOT_REFERENCE_GOLD',
        'bundles':chosen,'assays':records,'documents':list(docs.values()),'deferred_bundle_ids':deferred,
        'activity_values_or_presence_flags_emitted':False,'independent_gold':'NOT_RUN'})
    save('result.json',{'status':'PASS_DEVELOPMENT_SOURCE_PACKET','bundles':len(chosen),'targets':len({c['tid'] for c in chosen}),
        'diagnostic_strata':len({c['sampling_stratum'] for c in chosen}),'documents':len(docs),'assays':len(records),
        'activity_numeric_queries':0,'independent_biological_units_certified':0})
except Exception as exc:
    save('result.json',{'status':'FAIL_DEVELOPMENT_SOURCE_PACKET','error_type':type(exc).__name__,
        'error_frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)]})
    raise SystemExit(1)
