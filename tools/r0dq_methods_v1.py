"""One bounded development-only bibliographic/masked-methods intake."""
from datetime import datetime,timezone
import hashlib,json,re,urllib.error,urllib.parse,urllib.request
from r0dq_core_v1 import ROOT,PRIVATE,REMOTE,DEADLINE,save,archive_code,now
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard
from r0dq_context_projection_v1 import fixtures,project_methods

def normalize(doi):return str(doi or '').strip().lower().removeprefix('https://doi.org/').removeprefix('http://doi.org/')

def request(name,url,kind,limit):
    assert datetime.now(timezone.utc)<DEADLINE
    parsed=urllib.parse.urlparse(url)
    assert parsed.scheme=='https' and parsed.netloc=='www.ebi.ac.uk'
    if kind=='bibliographic_metadata':
        assert parsed.path=='/europepmc/webservices/rest/search'
        params=urllib.parse.parse_qs(parsed.query);assert params['resultType']==['lite'] and params['format']==['json']
        kindcap=56
    else:
        assert kind=='methods_xml' and re.fullmatch(r'/europepmc/webservices/rest/PMC\d+/fullTextXML',parsed.path) and not parsed.query
        kindcap=32
    book=json.loads((PRIVATE/'ledger.json').read_text());assert book['status']=='ACTIVE' and len(book['http_attempts'])<96
    assert sum(r['kind']==kind for r in book['http_attempts'])<kindcap
    assert not any(r['name']==name or r['url']==url for r in book['http_attempts'])
    inherited=json.loads((PRIVATE/'inherited-source-stops-v1.json').read_text())
    assert url not in inherited['stopped_urls']
    row={'name':name,'url':url,'kind':kind,'status':'ADMITTED','utc':now()};book['http_attempts'].append(row);save(PRIVATE/'ledger.json',book)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):raise RuntimeError('Redirect STOP; no alternate route')
    raw=b''
    try:
        with urllib.request.build_opener(NoRedirect).open(url,timeout=60 if kind=='methods_xml' else 30) as response:
            raw=response.read(limit+1);row.update(http_status=response.status,decoded_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        assert len(raw)<=limit and book['nonbulk_decoded_bytes']+len(raw)<=book['nonbulk_cap_bytes']
        row['status']='PASS_TRANSPORT';return raw
    except Exception as exc:
        if isinstance(exc,urllib.error.HTTPError):
            raw=exc.read(limit+1);row.update(http_status=exc.code,decoded_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        row.update(status='STOP_SOURCE',error_type=type(exc).__name__)
        book['stopped_sources'].append(name);return None
    finally:
        book['nonbulk_decoded_bytes']+=len(raw);save(PRIVATE/'ledger.json',book)

def main():
    assert fixtures()['status']=='PASS_PROCEDURAL_PROJECTION_FIXTURES'
    assert json.loads((PRIVATE/'context-v1-status.json').read_text())['result.json']['status']=='PASS_DEVELOPMENT_METADATA_PACKET'
    inherited=[];stopped_urls=set()
    for rel in ['.local/r0-chembl-20261107-v1/ledger.json','.local/r0r-chembl-20261107-v1/ledger.json']:
        path=ROOT/rel;raw=path.read_bytes();old=json.loads(raw)
        rows=[r for r in old['attempts'] if 'STOP' in str(r.get('status','')) or r.get('source') in old.get('stopped_sources',[])]
        for r in rows:
            if r.get('url'):stopped_urls.add(r['url'])
        inherited.append({'path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'stopped_sources':old.get('stopped_sources',[]),'stopped_attempts':rows})
    save(PRIVATE/'inherited-source-stops-v1.json',{'old_ledgers':inherited,'stopped_urls':sorted(stopped_urls),
        'old_pubchem_uniprot_and_publisher_stops_still_apply':True,'old_document_requests_repeated':False})
    packet=ssh('import json;from pathlib import Path;p=Path('+repr(REMOTE+'/jobs/context-v1/development-packet.json')+');assert p.stat().st_size<2097152;print(p.read_text())')
    assert packet['activity_values_or_utility_emitted'] is False
    save(PRIVATE/'development-packet-v1.json',packet)
    olddocids=set(json.loads((PRIVATE/'inputs/exposure-register-v1.json').read_text())['old_r0_document_ids'])
    documents=packet['documents'];assert len(documents)<=24
    save(PRIVATE/'methods-source-frame-v1.json',{'documents':documents,'frozen_before_source_requests':True,'max_methods':24})
    records=[];folder=PRIVATE/'methods';folder.mkdir(exist_ok=False)
    for doc in documents:
        identity=doc['document_chembl_id'];doi=normalize(doc['doi']);record={'document_chembl_id':identity,'doi':doi}
        if identity in olddocids:
            record['status']='DEFERRED_OLD_SOURCE_SCOPE_NO_RETRY';records.append(record);continue
        url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'DOI:"'+doi+'"','format':'json','resultType':'lite','pageSize':2})
        raw=request('dq-bibliography-'+identity,url,'bibliographic_metadata',2097152)
        if raw is None:
            record['status']='STOP_BIBLIOGRAPHIC_SOURCE';records.append(record);continue
        payload=json.loads(raw);(folder/(identity+'-bibliography.json')).write_bytes(raw)
        hits=[h for h in payload.get('resultList',{}).get('result',[]) if normalize(h.get('doi'))==doi]
        if len(hits)!=1:
            record['status']='UNRESOLVED_EXACT_DOI_ASSOCIATION';records.append(record);continue
        hit=hits[0];pmcid=hit.get('pmcid');record['pmcid']=pmcid
        if hit.get('isOpenAccess')!='Y' or not pmcid or not re.fullmatch(r'PMC\d+',pmcid):
            record['status']='NO_CONFIRMED_PMC_OPEN_ACCESS_ROUTE';records.append(record);continue
        methodurl='https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML'
        xml=request('dq-methods-'+identity,methodurl,'methods_xml',8388608)
        if xml is None:
            record['status']='STOP_METHODS_SOURCE';records.append(record);continue
        try:
            projected=project_methods(xml)
            assert doi in {normalize(value) for value in projected['article_dois']}
        except Exception as exc:
            record.update(status='QUARANTINE_SOURCE_PARSE_OR_DOI',error_type=type(exc).__name__);records.append(record);continue
        save(folder/(identity+'-projected-methods.json'),projected)
        record.update(status=projected['status'],raw_source_sha256=hashlib.sha256(xml).hexdigest(),
            raw_source_bytes=len(xml),retained_paragraphs=len(projected['paragraphs']),
            projection_sha256=hashlib.sha256((folder/(identity+'-projected-methods.json')).read_bytes()).hexdigest(),
            source_reference_adjudicated=False)
        records.append(record)
    summary={'status':'COMPLETE_BOUNDED_DEVELOPMENT_SOURCE_INTAKE','documents':records,'development_bundles':len(packet['bundles']),
        'development_groups':len({c['component_id'] for c in packet['bundles']}),'projected_sources':sum(r['status']=='PROJECTED_METHODS_PENDING_REVIEW' for r in records),
        'activity_values_or_reference_gold_emitted':False,'source_retries':0,'independent_domain_review':'NOT_RUN'}
    save(PRIVATE/'methods-intake-v1.json',summary);archive_code(ROOT/'tools/r0dq_context_projection_v1.py')
    print(json.dumps({'status':summary['status'],'documents':len(records),'projected_sources':summary['projected_sources'],
        'development_bundles':summary['development_bundles'],'development_groups':summary['development_groups']}))

if __name__=='__main__':
    guard=TransportGuard('development-methods-intake-v1',cpu_seconds=600,stage='context',wall=7200,memory_mib=512)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
