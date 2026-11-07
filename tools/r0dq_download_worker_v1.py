"""Single exact HTTPS archive attempt; never emits archive contents."""
from datetime import datetime,timezone
import hashlib,json,os,shutil,sys,time,urllib.request
from pathlib import Path


def save(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,sort_keys=True)+'\n');os.replace(tmp,path)


def main():
    job=Path(sys.argv[1]).resolve();permit=json.loads((job/'permit.json').read_text())
    root=Path(permit['root']);pin=permit['source_pin']
    assert job.is_relative_to(root) and root==Path.home()/'curaloop-runs/chembl-taskfirst-dq-20261107-v1'
    assert pin['archive_url']=='https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/chembl_37_sqlite.tar.gz'
    source=root/'source';source.mkdir(exist_ok=True)
    partial=source/'chembl_37_sqlite.tar.gz.part';final=source/'chembl_37_sqlite.tar.gz'
    assert not partial.exists() and not final.exists(),'No source retry/overwrite'
    assert shutil.disk_usage(root).free>=24*1024**3
    deadline=datetime.fromisoformat(permit['deadline_utc'])
    record={'status':'REQUEST_ADMITTED','url':pin['archive_url'],'started_utc':datetime.now(timezone.utc).isoformat(),
            'bytes':0,'numeric_outcomes_emitted':False,'attempt_number':1}
    save(job/'progress.json',record)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):raise RuntimeError('Unknown redirect; source STOP')
    digest=hashlib.new(pin['algorithm']);sha=hashlib.sha256();last=time.monotonic();started=last
    try:
        with urllib.request.build_opener(NoRedirect).open(pin['archive_url'],timeout=30) as response:
            length=response.headers.get('Content-Length');expected=int(length) if length else None
            assert response.status==200 and (expected is None or 0<expected<=8589934592)
            record.update(status='DOWNLOADING_PRIVATE_ARCHIVE',http_status=response.status,content_length=expected,
                          content_type=response.headers.get('Content-Type'))
            with partial.open('xb') as stream:
                while True:
                    if datetime.now(timezone.utc)>=deadline or time.monotonic()-started>=21600:raise TimeoutError('Source/phase absolute deadline')
                    chunk=response.read(1024**2)
                    if not chunk:break
                    record['bytes']+=len(chunk)
                    assert record['bytes']<=8589934592
                    digest.update(chunk);sha.update(chunk);stream.write(chunk)
                    if time.monotonic()-last>=10:
                        assert shutil.disk_usage(root).free>=16*1024**3
                        record['elapsed_seconds']=round(time.monotonic()-started,3);save(job/'progress.json',record);last=time.monotonic()
                stream.flush();os.fsync(stream.fileno())
        assert expected is None or record['bytes']==expected
        assert digest.hexdigest()==pin['published_digest'],'Published digest mismatch'
        os.replace(partial,final)
        record.update(status='PASS_ARCHIVE_DIGEST',sha256=sha.hexdigest(),published_algorithm=pin['algorithm'],
                      published_digest=digest.hexdigest(),path=str(final.relative_to(root)))
        save(job/'progress.json',record);save(job/'result.json',record)
        print(json.dumps({'status':record['status'],'bytes':record['bytes'],'sha256':record['sha256']}))
    except Exception as exc:
        record.update(status='STOP_SOURCE',error_type=type(exc).__name__,error=str(exc),partial_retained=partial.exists())
        save(job/'progress.json',record);save(job/'result.json',record)
        raise RuntimeError('Archive source stopped; no automatic retry') from None


if __name__=='__main__':main()
