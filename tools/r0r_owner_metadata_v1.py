"""Metadata-only inspection of the owner's fixed three papers and supplements."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
from r0r_chembl_core_v1 import Guard,PRIVATE,ROOT,save,DEADLINE

FILES={
    'CHEMBL1140224.pdf':('CHEMBL1140224','10.1021/jm801063n','main'),
    'CHEMBL1140224_supplement.pdf':('CHEMBL1140224','10.1021/jm801063n','supplement'),
    'CHEMBL1140235.pdf':('CHEMBL1140235','10.1021/jm800965b','main'),
    'CHEMBL1140235_supplement.pdf':('CHEMBL1140235','10.1021/jm800965b','supplement'),
    'CHEMBL1156448.pdf':('CHEMBL1156448','10.1074/jbc.M609796200','main'),
}
def run():
    import fitz
    book=json.loads((PRIVATE/'ledger.json').read_text())
    assert book['status']=='AWAITING_OWNER_INPUT' and datetime.now(timezone.utc)<DEADLINE
    assert book['worker_reserved_seconds']+book['utility_charge_seconds']+20<=3600
    assert not (PRIVATE/'owner-file-metadata-v1.json').exists()
    book.setdefault('state_history',[]).append({'from':book['status'],'to':'ACTIVE',
        'utc':datetime.now(timezone.utc).isoformat(),'reason':'Owner supplied three requested papers and associated supplements; explicitly use only these, no purchase'})
    book['status']='ACTIVE';book['worker_reserved_seconds']+=20
    save(PRIVATE/'ledger.json',book)
    folder=ROOT/'research/raw_data/external-benchmarks/chembl-37-r0r/owner-methods'
    records=[]
    known={'experimentalsection':'METHODS','experimentalprocedures':'METHODS',
       'materialsandmethods':'METHODS','methods':'METHODS','results':'RESULTS',
       'resultsanddiscussion':'RESULTS','discussion':'DISCUSSION','references':'REFERENCES',
       'acknowledgment':'ACKNOWLEDGMENT','acknowledgments':'ACKNOWLEDGMENT',
       'acknowledgement':'ACKNOWLEDGMENT','acknowledgements':'ACKNOWLEDGMENT',
       'supportinginformation':'SUPPORTING_INFORMATION','biologicalassays':'BIOLOGICAL_METHODS_CANDIDATE',
       'biologicalevaluation':'BIOLOGICAL_SECTION_UNVERIFIED'}
    for name,(document,doi,kind) in FILES.items():
        path=folder/name
        assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT.resolve())
        size=path.stat().st_size
        assert 0<size<=4*1024**2 and book['decoded_bytes']+size<=32*1024**2
        with path.open('rb') as stream:raw=stream.read(4*1024**2+1)
        book['decoded_bytes']+=len(raw)
        save(PRIVATE/'ledger.json',book)
        assert len(raw)==size and raw.startswith(b'%PDF') and b'%%EOF' in raw[-4096:]
        headings=[]
        with fitz.open(stream=raw,filetype='pdf') as pdf:
            front=''.join(''.join(pdf[index].get_text().split()) for index in range(min(2,len(pdf)))).lower()
            page_count=len(pdf)
            for number in range(len(pdf)):
                for line in pdf[number].get_text().splitlines():
                    if len(line)>100:continue
                    norm=re.sub('[^a-z]','',line.casefold())
                    if norm in known:headings.append({'page':number+1,'kind':known[norm]})
            record={'filename':name,'document_id':document,'source_part':kind,
                    'expected_doi':doi,'expected_doi_in_front_matter':doi.lower() in front,
                    'pdf_pages':page_count,'section_markers':headings,
                    'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),
                    'source_path':str(path.relative_to(ROOT)),'unmasked_text_emitted':False}
        records.append(record)
    save(PRIVATE/'owner-file-metadata-v1.json',{'records':records,'owner_main_articles':3,
        'related_supplements':2,'unavailable_other_sources':'DEFERRED_BY_OWNER_NO_PURCHASE'})
    save(PRIVATE/'ledger.json',book)
    print(json.dumps({'status':'OWNER_FILE_METADATA_INSPECTED','records':records,
        'current_decoded_bytes':book['decoded_bytes'],
        'current_cpu_charge_seconds':book['worker_reserved_seconds']+book['utility_charge_seconds']},indent=2))

if __name__=='__main__':
    guard=Guard('owner-metadata-v1',wall=60,cpu_seconds=20)
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS',charged_to='20-second additional worker reservation')
