"""Archive every frozen task regular file; never read values through SQL."""
import hashlib,json,os,shutil,stat,sys,tarfile,time
from pathlib import Path

p=Path(sys.argv[1]);permit=json.loads((p/'permit.json').read_text());root=Path(permit['root'])
started=time.monotonic()
def save(name,data):
    target=p/name;tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(target)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()
class CappedWriter:
    def __init__(self,stream):self.stream=stream;self.bytes=0
    def write(self,raw):
        self.bytes+=len(raw);assert self.bytes<=16*1024**3,'Return archive cap reached; preserve remote originals'
        if self.bytes%(64*1024**2)<len(raw):assert shutil.disk_usage(root).free>=16*1024**3
        return self.stream.write(raw)
    def flush(self):return self.stream.flush()
    def tell(self):return self.stream.tell()
try:
    assert root==Path('/home/chaw/curaloop-runs/chembl-taskfirst-dq-20261107-v1') and root.resolve()==root
    assert root.stat().st_uid==os.getuid() and p==Path(str(root)+'-export-v1')
    rows=[];aliases=[];directories=[];fold=set()
    for parent,dirs,files in os.walk(root,followlinks=False):
        for name in dirs+files:
            target=Path(parent)/name;meta=target.lstat();rel=target.relative_to(root).as_posix()
            assert meta.st_uid==os.getuid() and rel.casefold() not in fold;fold.add(rel.casefold())
            if stat.S_ISLNK(meta.st_mode):
                assert target.resolve().is_relative_to(root),'External alias requires owner review'
                aliases.append({'path':rel,'target':os.readlink(target),'mode':stat.S_IMODE(meta.st_mode)});continue
            if stat.S_ISDIR(meta.st_mode):directories.append({'path':rel,'mode':stat.S_IMODE(meta.st_mode)});continue
            assert stat.S_ISREG(meta.st_mode),'Special file requires owner review'
            rows.append({'path':rel,'bytes':meta.st_size,'sha256':sha(target),'mode':stat.S_IMODE(meta.st_mode)})
    rows.sort(key=lambda r:r['path']);assert len(rows)<=20000 and sum(r['bytes'] for r in rows)<=48*1024**3
    save('progress.json',{'status':'FULL_FROZEN_TASK_HASHED','files':len(rows),'bytes':sum(r['bytes'] for r in rows)})
    archive=p/'full-task-v1.tar.gz.part'
    with archive.open('xb') as stream:
        capped=CappedWriter(stream)
        with tarfile.open(fileobj=capped,mode='w|gz',compresslevel=1) as tar:
            for index,row in enumerate(rows):
                target=root/row['path'];info=tar.gettarinfo(str(target),arcname=row['path']);assert info.isfile() and info.size==row['bytes']
                with target.open('rb') as f:tar.addfile(info,f)
                if index%100==0:save('progress.json',{'status':'PACKING_ALL_TASK_FILES','files_written':index+1,'file_count':len(rows),'archive_bytes':capped.bytes})
        stream.flush();os.fsync(stream.fileno())
    archive.replace(p/'full-task-v1.tar.gz');archive=p/'full-task-v1.tar.gz'
    manifest={'schema':'curaloop.r0dq.complete-private-return.v1','root':str(root),'export':str(p),
        'files':rows,'directories':directories,'aliases':aliases,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),
        'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'source_sqlite_and_archive_included':True,
        'numeric_values_exported_as_private_source_bytes_only':True,'planner_value_projection':False}
    save('manifest.json',manifest)
    save('result.json',{'status':'PASS_COMPLETE_PRIVATE_EXPORT','file_count':len(rows),'total_bytes':manifest['total_bytes'],
        'archive_bytes':manifest['archive_bytes'],'archive_sha256':manifest['archive_sha256'],
        'manifest_sha256':sha(p/'manifest.json'),'wall_seconds':time.monotonic()-started})
except Exception as exc:
    save('result.json',{'status':'FAIL_RETURN_PRESERVE_REMOTE_DATA','error_type':type(exc).__name__})
    raise SystemExit(1)
