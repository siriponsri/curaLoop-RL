"""One frozen development-source intake; no retry, results or article retention."""
from datetime import datetime,timezone
import hashlib,json,re,urllib.error,urllib.parse,urllib.request
from r0dqr_core_v1 import ROOT,PRIVATE,DEADLINE,save,sha,now,archive_code
from r0dqr_transport_guard_v1 import TransportGuard
from r0dqr_context_projection_v1 import fixtures,project_methods

def norm(doi):return str(doi or '').strip().lower().removeprefix('https://doi.org/').removeprefix('http://doi.org/')
def request(name,url,kind,limit,stops):
    assert datetime.now(timezone.utc)<DEADLINE and url not in stops
    parsed=urllib.parse.urlparse(url);assert parsed.scheme=='https'
    if kind=='metadata':
        assert parsed.netloc in {'www.ebi.ac.uk','api.openalex.org'}
        if parsed.netloc=='www.ebi.ac.uk':
            assert parsed.path=='/europepmc/webservices/rest/search' and urllib.parse.parse_qs(parsed.query)['resultType']==['lite']
        else:assert urllib.parse.parse_qs(parsed.query)['select']==['id,doi,open_access,best_oa_location,locations']
    else:assert kind=='methods' and parsed.netloc=='www.ebi.ac.uk' and re.fullmatch(r'/europepmc/webservices/rest/PMC\d+/fullTextXML',parsed.path)
    book=json.loads((PRIVATE/'ledger.json').read_text());assert book['status']=='ACTIVE'
    assert sum(r['kind']==kind for r in book['http_attempts'])<book[kind+'_request_cap']
    assert not any(r['url']==url or r['name']==name for r in book['http_attempts'])
    assert book['nonbulk_bytes']+limit+1<=book['nonbulk_cap_bytes']
    row={'name':name,'url':url,'kind':kind,'status':'ADMITTED','utc':now()};book['http_attempts'].append(row);save(PRIVATE/'ledger.json',book)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):raise RuntimeError('Unknown redirect STOP')
    raw=b''
    try:
        with urllib.request.build_opener(NoRedirect).open(url,timeout=40) as response:
            raw=response.read(limit+1);row.update(http_status=response.status,decoded_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        assert len(raw)<=limit;row['status']='PASS_TRANSPORT';return raw
    except Exception as exc:
        if isinstance(exc,urllib.error.HTTPError):
            raw=exc.read(limit+1);row.update(http_status=exc.code,decoded_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        row.update(status='STOP_SOURCE',error_type=type(exc).__name__);book['stopped_sources'].append(name);return None
    finally:
        book['nonbulk_bytes']+=len(raw);save(PRIVATE/'ledger.json',book)

def main():
    assert fixtures()['status']=='PASS_PROCEDURAL_PROJECTION_FIXTURES'
    packet=json.loads((PRIVATE/'small-return/jobs/context-v1/development-packet.json').read_text());assert len(packet['documents'])<=12
    stops=set();oldpins=json.loads((PRIVATE/'inputs/old-ledger-pins-and-stops-v1.json').read_text())
    for pin in oldpins['records']:
        path=ROOT/pin['path'];assert sha(path)==pin['sha256'];book=json.loads(path.read_text())
        for row in book.get('attempts',book.get('http_attempts',[])):
            if 'STOP' in str(row.get('status','')) or row.get('name',row.get('source')) in book.get('stopped_sources',[]):
                if row.get('url'):stops.add(row['url'])
    save(PRIVATE/'inherited-stopped-urls-v1.json',{'urls':sorted(stops),'all_older_provider_and_source_stops_remain':True})
    cached={norm(r['doi']):r for r in json.loads((PRIVATE/'inputs/prior-access-cache-v1.json').read_text())['records']}
    olddocs=set(json.loads((PRIVATE/'inputs/exposure-register-v1.json').read_text())['old_r0_document_ids'])
    save(PRIVATE/'methods-source-frame-v1.json',{'documents':packet['documents'],'frozen_before_source_requests':True,
        'candidate_freeze_sha256':sha(PRIVATE/'small-return/jobs/nominal-v1/candidates-frozen.json')})
    records=[];folder=PRIVATE/'methods';folder.mkdir(exist_ok=False);epmc_stopped=False;oa_stopped=False
    for doc in packet['documents']:
        identity=doc['document_chembl_id'];doi=norm(doc['doi']);row={'document_chembl_id':identity,'doi':doi}
        if doi in cached:row.update(status='REUSED_PRIOR_ACCESS_METADATA_NO_HTTP',cached_record=cached[doi]);records.append(row);continue
        if identity in olddocs:row['status']='DEFERRED_INHERITED_DOCUMENT_SCOPE';records.append(row);continue
        if not epmc_stopped:
            url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'DOI:"'+doi+'"','format':'json','resultType':'lite','pageSize':2})
            raw=request('dqr-bibliography-'+identity,url,'metadata',2*1024**2,stops)
            if raw is None:row['europepmc']='STOP_SOURCE';epmc_stopped=True
            else:
                obj=json.loads(raw);(folder/(identity+'-bibliography.json')).write_bytes(raw)
                hits=[h for h in obj.get('resultList',{}).get('result',[]) if norm(h.get('doi'))==doi]
                if len(hits)!=1:row['europepmc']='UNRESOLVED_EXACT_DOI'
                else:
                    hit=hits[0];pmcid=hit.get('pmcid');row['pmcid']=pmcid
                    row['europepmc']='NO_CONFIRMED_PMC_OA_ROUTE'
                    if hit.get('isOpenAccess')=='Y' and pmcid and re.fullmatch(r'PMC\d+',pmcid):
                        xml=request('dqr-methods-'+identity,'https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML','methods',8*1024**2,stops)
                        if xml is None:row['methods_status']='STOP_SOURCE'
                        else:
                            try:
                                projected=project_methods(xml);assert doi in {norm(d) for d in projected['article_dois']}
                                out=folder/(identity+'-projected-methods.json');save(out,projected)
                                row.update(methods_status=projected['status'],projection_sha256=sha(out),
                                    source_sha256=hashlib.sha256(xml).hexdigest(),source_bytes=len(xml),paragraphs=len(projected['paragraphs']))
                            except Exception as exc:row.update(methods_status='QUARANTINE_PARSE_OR_DOI',error_type=type(exc).__name__)
        else:row['europepmc']='NOT_RUN_AFTER_PROVIDER_STOP'
        if not oa_stopped:
            url='https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(doi,safe='/')+'?select=id,doi,open_access,best_oa_location,locations'
            raw=request('dqr-oa-'+identity,url,'metadata',2*1024**2,stops)
            if raw is None:row['openalex']='STOP_SOURCE';oa_stopped=True
            else:
                obj=json.loads(raw);assert norm(obj.get('doi'))==doi;save(folder/(identity+'-oa-locations.json'),obj)
                locations=[loc for loc in obj.get('locations',[]) if loc.get('is_oa')]
                row.update(openalex='OA_LOCATION_METADATA' if locations else 'NO_OPENALEX_OA_LOCATION',locations=locations)
        else:row['openalex']='NOT_RUN_AFTER_PROVIDER_STOP'
        row['status']=row.get('methods_status','COMPLETE_ACCESS_METADATA_ONLY');records.append(row)
    result={'status':'COMPLETE_FROZEN_SOURCE_FEASIBILITY','documents':records,
        'projected_sources':sum(r.get('methods_status')=='PROJECTED_METHODS_PENDING_REVIEW' for r in records),
        'independent_reference_gold':'NOT_RUN','numerical_activity_queries':0,'source_retries':0,
        'raw_articles_retained':False,'doi_scope':'frozen development frame only; no substitute papers'}
    save(PRIVATE/'methods-intake-v1.json',result);archive_code(ROOT/'tools/r0dqr_context_projection_v1.py')
    print(json.dumps(result))
if __name__=='__main__':
    guard=TransportGuard('development-methods-intake-v1',cpu_seconds=600,wall=1800,stage='context',memory_mib=512)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
