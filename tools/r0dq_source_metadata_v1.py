"""First source attempt: published checksum only, before the single bulk GET."""
import hashlib
import json
import re
from r0dq_core_v1 import LocalGuard,ROOT,PRIVATE,save,metadata_request


def main():
    assert json.loads((PRIVATE/'projection-fixtures-v2.json').read_text())['status']=='PASS_CONSTRUCTED_CONTRACT_FIXTURES'
    assert json.loads((PRIVATE/'remote-quota-canary-v1.json').read_text())['status']=='PASS_REAL_QUOTA_CANARY'
    review=json.loads((ROOT/'docs/evidence/chembl-taskfirst-plan-20261107-v1/source-review-v1.json').read_text())
    cache=[]
    for row in review['cached_official_metadata']:
        raw=(ROOT/row['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
        name={'008-chembl37-directory.html':'directory.html','009-chembl37-readme.html':'README',
              '010-chembl37-license.html':'LICENSE','011-chembl37-schema.html':'schema.html'}[(ROOT/row['path']).name]
        path=PRIVATE/'source-metadata'/name;path.parent.mkdir(exist_ok=True);path.write_bytes(raw)
        cache.append({'filename':name,'sha256':row['sha256'],'url':row['url'],'reused_authenticated_cache':True})
    url='https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/checksums.txt'
    raw=metadata_request('chembl37-published-checksums',url)
    lines=[line for line in raw.decode().splitlines() if 'chembl_37_sqlite.tar.gz' in line]
    assert len(lines)==1,'Published archive digest missing or ambiguous'
    matches=re.findall(r'\b[a-fA-F0-9]{32,128}\b',lines[0])
    assert len(matches)==1 and len(matches[0]) in {32,40,64,128}
    digest=matches[0].lower();algorithm={32:'md5',40:'sha1',64:'sha256',128:'sha512'}[len(digest)]
    record={'status':'PUBLISHED_DIGEST_PINNED','archive_filename':'chembl_37_sqlite.tar.gz',
        'archive_url':'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/chembl_37_sqlite.tar.gz',
        'algorithm':algorithm,'published_digest':digest,'checksum_source_sha256':hashlib.sha256(raw).hexdigest(),
        'exact_archive_bytes':'TO_BE_CHECKED_ON_SINGLE_GET','cached_metadata':cache,
        'database_terms':'CC-BY-SA-3.0 as supplied by official release LICENSE',
        'calculated_proprietary_properties_used':False,'commercial_use_clearance_claim':False}
    save(PRIVATE/'archive-source-pin-v1.json',record)
    print(json.dumps({k:record[k] for k in ['status','algorithm','published_digest','archive_filename']}))


if __name__=='__main__':
    guard=LocalGuard('source-metadata-v1',cpu_seconds=60,wall=90,stage='source',memory_mib=256)
    try:main()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
