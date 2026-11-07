"""Read the same three main PDFs once; preserve permitted entity digits only."""
import hashlib
from r0a1_core_v1 import Guard,ROOT,PRIVATE,save,load,read_input,archive_code
from r0a1_context_mask_v1 import pdf_methods,safety_checks


def run():
    import fitz
    assert safety_checks()['status']=='PASS'
    pins=load(PRIVATE/'preflight-pins-v1.json')
    summary=[]
    for row in pins['three_main_sources']:
        raw=read_input(ROOT/row['source_path'])
        assert hashlib.sha256(raw).hexdigest()==row['source_sha256']
        with fitz.open(stream=raw,filetype='pdf') as pdf:
            front=''.join(''.join(pdf[i].get_text().split()) for i in range(min(2,len(pdf)))).lower()
        assert row['expected_doi'].lower() in front
        result=pdf_methods(raw)
        result.update(document_id=row['document_id'],source_sha256=row['source_sha256'],doi_verified=True)
        target=PRIVATE/('methods-'+row['document_id']+'-v1.json')
        save(target,result)
        summary.append({'document_id':row['document_id'],'status':result['status'],
            'paragraphs':len(result['paragraphs']),'entities':sorted({e for p in result['paragraphs'] for e in p['permitted_entities']}),
            'masked_output_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    archive_code(ROOT/'tools/r0a1_context_mask_v1.py')
    save(PRIVATE/'methods-summary-v1.json',{'sources':summary,'new_http_requests':0,'supplements_read':False})
    print(summary)


if __name__=='__main__':
    guard=Guard('pdf-identifiers-v1',cpu_seconds=120,wall=180)
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
