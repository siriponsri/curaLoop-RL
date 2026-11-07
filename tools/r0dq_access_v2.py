"""Independent abstract-free OA-location metadata for the same frozen sources."""
from datetime import datetime,timezone
import hashlib,json,urllib.error,urllib.parse,urllib.request
from r0dq_core_v1 import PRIVATE,REMOTE,DEADLINE,save,now
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard
from r0dq_context_projection_v1 import fixtures,project_text

def main():
    assert fixtures()['status']=='PASS_PROCEDURAL_PROJECTION_FIXTURES'
    assert project_text('Displacement of [3H]NECA and [125I]Iodoproxyfan')['text']=='Displacement of [3H]NECA and [125I]Iodoproxyfan'
    packet=ssh('import json;from pathlib import Path;p=Path('+repr(REMOTE+'/jobs/context-v2/development-packet.json')+');assert p.stat().st_size<2097152;print(p.read_text())')
    save(PRIVATE/'development-packet-v2.json',packet)
    earlier=json.loads((PRIVATE/'methods-intake-v1.json').read_text());assert {r['doi'] for r in earlier['documents']}=={r['doi'].lower() for r in packet['documents']}
    records=[];stopped=False
    for doc in earlier['documents']:
        row={'document_chembl_id':doc['document_chembl_id'],'doi':doc['doi']}
        if stopped:row['status']='NOT_RUN_AFTER_PROVIDER_STOP';records.append(row);continue
        assert datetime.now(timezone.utc)<DEADLINE
        url='https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(doc['doi'],safe='/')+'?select=id,doi,open_access,best_oa_location,locations'
        book=json.loads((PRIVATE/'ledger.json').read_text());assert book['status']=='ACTIVE' and len(book['http_attempts'])<96
        assert sum(r['kind']=='bibliographic_metadata' for r in book['http_attempts'])<56
        assert not any(r['url']==url for r in book['http_attempts'])
        inherited=json.loads((PRIVATE/'inherited-source-stops-v1.json').read_text());assert url not in inherited['stopped_urls']
        attempt={'name':'dq-oa-location-'+doc['document_chembl_id'],'url':url,'kind':'bibliographic_metadata','status':'ADMITTED','utc':now()}
        book['http_attempts'].append(attempt);save(PRIVATE/'ledger.json',book)
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs):raise RuntimeError('Unknown redirect STOP')
        raw=b''
        try:
            with urllib.request.build_opener(NoRedirect).open(url,timeout=30) as response:
                raw=response.read(2097152);assert len(raw)<2097152
                attempt.update(status='PASS_TRANSPORT',http_status=response.status,decoded_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            obj=json.loads(raw);assert obj['doi'].lower().removeprefix('https://doi.org/')==doc['doi']
            save(PRIVATE/'methods'/(doc['document_chembl_id']+'-oa-locations.json'),obj)
            locations=[loc for loc in obj.get('locations',[]) if loc.get('is_oa')]
            row.update(status='OA_LOCATION_METADATA_AVAILABLE' if locations else 'NO_OPENALEX_OA_LOCATION',
                open_access=obj.get('open_access'),locations=locations)
        except Exception as exc:
            if isinstance(exc,urllib.error.HTTPError):
                raw=exc.read(2097152);attempt.update(http_status=exc.code,decoded_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            attempt.update(status='STOP_SOURCE',error_type=type(exc).__name__);book['stopped_sources'].append(attempt['name'])
            row.update(status='STOP_OA_METADATA_SOURCE',error_type=type(exc).__name__);stopped=True
        finally:
            book['nonbulk_decoded_bytes']+=len(raw);assert book['nonbulk_decoded_bytes']<=book['nonbulk_cap_bytes'];save(PRIVATE/'ledger.json',book)
        records.append(row)
    result={'status':'COMPLETE_INDEPENDENT_OA_LOCATION_CHECK','records':records,'source_documents_replaced':False,'prior_requests_retried':False,
        'radiotracer_identifiers_restored_without_outcomes':True,'methods_body_retrieved':False}
    save(PRIVATE/'oa-access-v2.json',result);print(json.dumps(result))

if __name__=='__main__':
    guard=TransportGuard('development-oa-access-v2',cpu_seconds=180,stage='context',wall=3600,memory_mib=512)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
