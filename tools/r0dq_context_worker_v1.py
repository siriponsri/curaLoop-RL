"""Prepare bounded development metadata for a source-feasibility review."""
import collections,json,re,sqlite3,sys
from pathlib import Path
from r0dq_context_projection_v1 import project_text,PARAM_INPUT,PARAM_VALUE

p=Path(sys.argv[1]);root=p.parents[1]
def save(name,obj):(p/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
try:
    cohort=json.loads((root/'jobs/support-v1/cohort-support-frozen.json').read_text())
    frame=json.loads((root/'jobs/frame-v1/frame-frozen.json').read_text());amap={a['assay_id']:a for a in frame['assays']}
    cases=[c for c in cohort['reserved'] if c['role']=='development'][:8]
    ids=sorted({k[0] for case in cases for k in [case['reference'],*case['auxiliary']]})
    assert len(cases)<=8 and len(ids)<=32
    db=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True);db.row_factory=sqlite3.Row
    records=[];docs={}
    for aid in ids:
        assert amap[aid]['role']=='development'
        meta=dict(amap[aid]);raw=db.execute('SELECT description FROM assays WHERE assay_id=?',(aid,)).fetchone()[0]
        meta['description_projection']=project_text(raw)
        variant=meta.get('variant_id')
        if variant:
            row=db.execute('SELECT variant_id,accession,mutation,isoform,organism FROM variant_sequences WHERE variant_id=?',(variant,)).fetchone()
            if row:
                vr=dict(row);vr['mutation_projection']=project_text(vr.pop('mutation'))
                meta['variant']=vr
        meta['null_variant_is_wild_type']=False
        # Read candidate parameter TYPES first. Only known procedural types get
        # a fixed query for input values. Unsupported types remain explicit.
        parameters=[]
        for row in db.execute('SELECT assay_param_id,type,units,standard_type,standard_units FROM assay_parameters WHERE assay_id=?',(aid,)):
            item=dict(row);label=item['standard_type'] or item['type'] or ''
            if PARAM_INPUT.fullmatch(label.strip()):
                value=db.execute('SELECT value,standard_value FROM assay_parameters WHERE assay_param_id=? AND assay_id=?',(item['assay_param_id'],aid)).fetchone()
                values={}
                for key in ['value','standard_value']:
                    text=str(value[key]) if value and value[key] is not None else None
                    values[key]=text if text and len(text)<128 and PARAM_VALUE.fullmatch(text) else None
                item.update(procedural_input_projection=values,value_status='PERMITTED_INPUT_TYPE_FORMAT_CHECKED')
            else:item['value_status']='OMITTED_UNVERIFIED_PARAMETER_SEMANTICS'
            parameters.append(item)
        meta['parameters']=parameters
        meta['full_context_completeness']='PENDING_PROJECTION_AND_SOURCE_REVIEW'
        meta['omitted_metadata_may_not_be_called_natural_uncertainty']=True
        records.append(meta);docs[meta['doc_id']]={k:meta[k] for k in ['doc_id','document_chembl_id','doi','pubmed_id','year']}
    # Review no more than24 sources. Prioritize all reference documents, then
    # auxiliary depths across bundles; retain every deferred source explicitly.
    ordered=[]
    for depth in range(4):
        for case in cases:
            keys=[case['reference'],*case['auxiliary']]
            if depth<len(keys):
                doc=amap[keys[depth][0]]['doc_id']
                if doc not in ordered:ordered.append(doc)
    admitted=ordered[:24];deferred=ordered[24:]
    packet={'status':'DEVELOPMENT_SOURCE_FEASIBILITY_PACKET_NOT_GOLD','bundles':[{k:v for k,v in c.items() if k!='reference_panel'} for c in cases],
        'assays':records,'documents':[docs[d] for d in admitted],
        'documents_deferred_by_source_cap':[docs[d] for d in deferred],
        'independent_reference_review':'NOT_RUN','activity_values_or_utility_emitted':False}
    save('development-packet.json',packet)
    save('result.json',{'status':'PASS_DEVELOPMENT_METADATA_PACKET','bundles':len(cases),'groups':len({c['component_id'] for c in cases}),
        'assays':len(records),'documents':len(admitted),'documents_deferred_by_source_cap':len(deferred),'activity_outcomes_emitted':False})
except Exception as exc:
    import traceback
    save('result.json',{'status':'FAIL_CONTEXT_PACKET','error_type':type(exc).__name__,
        'error_frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)],
        'activity_outcomes_emitted':False})
    raise SystemExit(1)
