"""Recover only the pinned original archive, with a complete outer-byte hash."""
import hashlib,json,os,shutil,tarfile,time
from pathlib import PurePosixPath
from r0dqr_core_v1 import PRIVATE,PRIOR,ARCHIVE_SHA,LocalGuard,save,sha

def main():
    assert json.loads((PRIVATE/'remote-quota-canary-v1.json').read_text())['status']=='PASS_REAL_QUOTA_CANARY'
    proof=json.loads((PRIOR/'remote-return/complete-return-verified-v1.json').read_text())
    assert proof['status']=='PASS_FULL_PRIVATE_RETURN_AND_STREAMED_LOCAL_REREAD'
    source=PRIOR/'remote-return/full-task-v1.tar.gz';manifestpath=PRIOR/'remote-return/export-terminal/manifest.json'
    assert source.stat().st_size==proof['archive_bytes'] and sha(manifestpath)==proof['manifest_sha256']
    manifest=json.loads(manifestpath.read_text());wanted='source/chembl_37_sqlite.tar.gz'
    pin=next(r for r in manifest['files'] if r['path']==wanted)
    assert pin['sha256']==ARCHIVE_SHA and pin['bytes']==5764252857
    folder=PRIVATE/'source';folder.mkdir(exist_ok=False);target=folder/'chembl_37_sqlite.tar.gz.part'
    started=time.monotonic();outer=hashlib.sha256();last=[time.monotonic()];scanned=[0]
    class Reader:
        def __init__(self,stream):self.stream=stream
        def read(self,n=-1):
            raw=self.stream.read(n);outer.update(raw);scanned[0]+=len(raw)
            if time.monotonic()-last[0]>=10:
                save(PRIVATE/'source-reuse-progress.json',{'status':'READING_VERIFIED_PRIVATE_RETURN','compressed_bytes_scanned':scanned[0],
                    'expected_compressed_bytes':proof['archive_bytes'],'elapsed_seconds':time.monotonic()-started,'activity_values_parsed':False})
                last[0]=time.monotonic()
            return raw
    seen=set();copied=0;digest=hashlib.sha256()
    with source.open('rb') as raw:
        reader=Reader(raw)
        with tarfile.open(fileobj=reader,mode='r|gz') as tar:
            for member in tar:
                rel=PurePosixPath(member.name)
                assert member.isfile() and not rel.is_absolute() and '..' not in rel.parts and '\\' not in member.name
                assert member.name not in seen;seen.add(member.name)
                if member.name!=wanted:continue
                assert member.size==pin['bytes']
                with tar.extractfile(member) as src,target.open('xb') as dst:
                    for chunk in iter(lambda:src.read(1024**2),b''):
                        dst.write(chunk);digest.update(chunk);copied+=len(chunk)
                        if copied%(256*1024**2)==0:assert shutil.disk_usage(PRIVATE).free>=10*1024**3
                    dst.flush();os.fsync(dst.fileno())
        while reader.read(1024**2):pass
    assert scanned[0]==proof['archive_bytes'] and outer.hexdigest()==proof['archive_sha256']
    assert len(seen)==manifest['file_count'] and wanted in seen
    assert copied==pin['bytes'] and digest.hexdigest()==ARCHIVE_SHA
    target.replace(folder/'chembl_37_sqlite.tar.gz')
    result={'status':'PASS_REUSED_PINNED_ARCHIVE_WITH_FULL_OUTER_HASH','source_bytes':copied,'source_sha256':digest.hexdigest(),
        'outer_return_sha256':outer.hexdigest(),'outer_return_bytes':scanned[0],'old_return_modified':False,
        'local_source_db_expanded':False,'numeric_activity_values_or_presence_flags_queried':False,
        'bulk_http_attempts':0,'wall_seconds':time.monotonic()-started}
    save(PRIVATE/'source-reuse-v1.json',result);print(json.dumps(result))

if __name__=='__main__':
    guard=LocalGuard('source-archive-reuse-v1',cpu_seconds=900,wall=3600,stage='source_return',memory_mib=256)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
