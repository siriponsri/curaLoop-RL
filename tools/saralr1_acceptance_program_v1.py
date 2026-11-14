"""One frozen engineering matrix, using actual retained Debian archives and image."""
import ctypes,hashlib,io,json,os,stat,sys,tarfile
from pathlib import Path
sys.path.insert(0,'/code')
from saralr1_overlay_v1 import extract_deb,extract_stream,file_sha

root=Path('/overlay');before=root.stat();plan=json.loads(Path('/control/matrix.json').read_text());results=[]
payload=root/'payload';payload.mkdir()
packages=[]
for row in plan['debian_packages']:
 path=Path('/packages')/row['name'];assert file_sha(path)==row['sha256']
 result=extract_deb(path,payload);packages.append(result)
results.append(dict(test='all-seven-recorded-debian-payloads',pass_=len(packages)==7))
lib=payload/'usr/lib/x86_64-linux-gnu/libgomp.so.1.0.0'
assert file_sha(lib)=='6456b504ac347bd50c419667440b691f6966ad8aff5309d2f06c977fe2f9debe'
results.append(dict(test='retained-independent-libgomp-content-hash',pass_=True))
for library in ('libgomp.so.1','libXrender.so.1'):
 ctypes.CDLL(str(payload/'usr/lib/x86_64-linux-gnu'/library))
 results.append(dict(test='actual-shared-library-load-'+library,pass_=True))

def fixture(entries):
 b=io.BytesIO()
 with tarfile.open(fileobj=b,mode='w') as t:
  for name,kind,target in entries:
   x=tarfile.TarInfo(name);x.mode=0o000;x.uid=12345;x.gid=12345;x.mtime=1
   if kind=='dir':x.type=tarfile.DIRTYPE;t.addfile(x)
   elif kind=='file':x.size=3;x.mode=0o755;t.addfile(x,io.BytesIO(b'abc'))
   elif kind=='symlink':x.type=tarfile.SYMTYPE;x.linkname=target;t.addfile(x)
   elif kind=='hardlink':x.type=tarfile.LNKTYPE;x.linkname=target;t.addfile(x)
   else:x.type=tarfile.FIFOTYPE;t.addfile(x)
 b.seek(0);return b

valid=root/'fixture-valid';valid.mkdir();old=valid.stat()
extract_stream(fixture([('.', 'dir',''),('./bin/a','file',''),('./bin/b','symlink','a'),('./bin/c','hardlink','bin/a')]),valid)
new=valid.stat();assert (old.st_uid,old.st_gid,stat.S_IMODE(old.st_mode))==(new.st_uid,new.st_gid,stat.S_IMODE(new.st_mode))
assert (valid/'bin/a').read_bytes()==b'abc' and (valid/'bin/b').read_bytes()==b'abc' and (valid/'bin/c').read_bytes()==b'abc'
assert (valid/'bin/a').stat().st_mode&0o111 and os.readlink(valid/'bin/b')=='a'
results.append(dict(test='hostile-root-metadata-skipped-valid-content-links-executable-mode',pass_=True))
invalid=[('absolute-member',[('/tmp/escape','file','')]),('parent-traversal',[('../escape','file','')]),
 ('escaping-symlink',[('a','symlink','../outside')]),('absolute-link',[('a','symlink','/etc/passwd')]),
 ('symlink-write-parent',[('link','symlink','inside'),('link/escape','file','')]),
 ('escaping-hardlink',[('a','hardlink','../../outside')]),('fifo',[('special','fifo','')]),
 ('duplicate-member',[('same','file',''),('same','file','')])]
for name,entries in invalid:
 dest=root/('fixture-'+name);dest.mkdir();denied=False
 try:extract_stream(fixture(entries),dest)
 except ValueError:denied=True
 assert denied,name;results.append(dict(test='deny-'+name,pass_=True))
empty=root/'empty';empty.write_bytes(b'')
assert file_sha(empty)==hashlib.sha256(b'').hexdigest()
assert file_sha(valid/'bin/a')=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
results.append(dict(test='python310-streaming-sha-empty-and-known-bytes',pass_=True))
after=root.stat();assert (before.st_uid,before.st_gid,stat.S_IMODE(before.st_mode))==(after.st_uid,after.st_gid,stat.S_IMODE(after.st_mode))
results.append(dict(test='bind-root-owner-group-mode-preserved',pass_=True))
out=dict(status='PASS_FROZEN_ENGINEERING_MATRIX',python_version=sys.version,tests=results,packages=packages,
 root_before=dict(uid=before.st_uid,gid=before.st_gid,mode=stat.S_IMODE(before.st_mode)),root_after=dict(uid=after.st_uid,gid=after.st_gid,mode=stat.S_IMODE(after.st_mode)),native_references=0,provider_calls=0)
Path('/control/acceptance-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(status=out['status'],tests=len(results))))
