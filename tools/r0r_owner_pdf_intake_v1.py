"""Operator-triggered, bounded intake of an explicitly supplied source PDF.

No folder polling, source retries or unmasked source output. Run only after
the owner reports supplying one of the six requested articles.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from r0r_chembl_core_v1 import Guard,PRIVATE,ROOT,save,DEADLINE
from r0r_methods_mask_v1 import extract_masked_pdf_methods

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filename')
    args=parser.parse_args()
    requests=json.loads((PRIVATE/'owner-download-requests-v1.json').read_text())['records']
    matching=[row for row in requests if Path(row['target_path']).name==args.filename]
    if len(matching)!=1:raise ValueError('Filename is not one of the six fixed source requests')
    expected=matching[0]
    path=Path(expected['target_path'])
    assert path.resolve().parent==path.parent.resolve() and path.resolve().is_relative_to(ROOT.resolve()) and not path.is_symlink()
    if not path.is_file():raise FileNotFoundError('Requested owner source not present')
    if not 0<path.stat().st_size<=4*1024**2:raise ValueError('Owner PDF size requires review before intake')
    book=json.loads((PRIVATE/'ledger.json').read_text())
    if book['status'] not in ('ACTIVE','AWAITING_OWNER_INPUT'):raise RuntimeError('R0-R not available for local intake')
    if datetime.now(timezone.utc)>=DEADLINE:raise RuntimeError('Original R0-R window exhausted')
    if book['worker_reserved_seconds']+book['utility_charge_seconds']+20>3600:raise RuntimeError('CPU admission ceiling')
    if book['decoded_bytes']+path.stat().st_size>32*1024**2:raise RuntimeError('Remaining source-byte ceiling')
    if any(row['document_id']==expected['document_id'] for row in book.get('local_source_intakes',[])):
        raise RuntimeError('Local source already attempted; review retained result before any new version')
    record={'document_id':expected['document_id'],'doi':expected['doi'],'source_path':str(path.relative_to(ROOT)),
            'status':'RESERVED','start_utc':datetime.now(timezone.utc).isoformat(),'cpu_reserved_seconds':20,
            'owner_supplied':True,'rights_scope':'Internal methods review; redistribution/commercial use not inferred'}
    book.setdefault('local_source_intakes',[]).append(record)
    book['worker_reserved_seconds']+=20
    save(PRIVATE/'ledger.json',book)
    guard=Guard('owner-pdf-'+expected['document_id'],wall=60,cpu_seconds=20)
    try:
        import fitz
        original_stat=path.stat()
        if not 0<original_stat.st_size<=4*1024**2:raise ValueError('Source size changed beyond intake bound')
        with path.open('rb') as stream:raw=stream.read(4*1024**2+1)
        book['decoded_bytes']+=len(raw)
        record.update(source_bytes=len(raw),source_sha256=hashlib.sha256(raw).hexdigest())
        save(PRIVATE/'ledger.json',book)
        if len(raw)>4*1024**2 or book['decoded_bytes']>32*1024**2:raise RuntimeError('Local source-byte cap')
        if path.stat().st_size!=original_stat.st_size or path.stat().st_mtime_ns!=original_stat.st_mtime_ns:
            raise RuntimeError('Source changed during read')
        if not raw.startswith(b'%PDF') or b'%%EOF' not in raw[-4096:]:raise ValueError('Unverified/incomplete PDF')
        with fitz.open(stream=raw,filetype='pdf') as document:
            header=''.join(''.join(document[index].get_text().split()) for index in range(min(2,len(document)))).lower()
        if expected['doi'].lower() not in header:raise ValueError('Fixed DOI not verified in the source front matter')
        output=extract_masked_pdf_methods(raw)
        record['doi_verified']=True
        output_path=PRIVATE/('owner-'+expected['document_id']+'-masked.json')
        save(output_path,output)
        record.update(status='PASS_MASKED_EXTRACTION' if output['status']=='MASKED_METHODS_AVAILABLE_NOT_ADJUDICATED' else 'QUARANTINE_SECTION_BOUNDARIES',
                      output_path=str(output_path.relative_to(ROOT)),output_sha256=hashlib.sha256(output_path.read_bytes()).hexdigest(),
                      mask_module_sha256=hashlib.sha256((ROOT/'tools/r0r_methods_mask_v1.py').read_bytes()).hexdigest(),
                      unmasked_article_copied_to_private_root=False,reference_review='PENDING')
        save(PRIVATE/'ledger.json',book)
        guard.finish(record['status'])
        print(json.dumps({'status':record['status'],'document_id':record['document_id'],
                          'methods_paragraphs':len(output.get('paragraphs',[])),'doi_verified':True}))
        return 0
    except Exception as exc:
        record.update(status='STOP_LOCAL_SOURCE',error_type=type(exc).__name__,error=str(exc))
        save(PRIVATE/'ledger.json',book);guard.finish('STOP_LOCAL_SOURCE',error_type=type(exc).__name__)
        print(json.dumps({'status':'STOP_LOCAL_SOURCE','document_id':record['document_id'],'error':str(exc)}))
        return 2

if __name__=='__main__':raise SystemExit(main())
