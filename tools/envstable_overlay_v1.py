"""Python 3.10 content-only Debian payload extraction without root metadata restore."""
import hashlib,os,shutil,stat,subprocess,tarfile
from pathlib import Path,PurePosixPath

def file_sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while True:
   block=f.read(1024**2)
   if not block:break
   h.update(block)
 return h.hexdigest()

def member_path(root,name):
 p=PurePosixPath(name)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe archive path')
 parts=[x for x in p.parts if x not in ('','.')] ;q=root.joinpath(*parts)
 if not q.is_relative_to(root):raise ValueError('Path outside overlay')
 for parent in [q,*q.parents]:
  if parent==root:break
  if parent.is_symlink():raise ValueError('Archive link used as a write path')
 return q

def link_destination(root,path,target,hard=False):
 p=PurePosixPath(target)
 if p.is_absolute():raise ValueError('Absolute link target')
 base=root if hard else path.parent
 combined=os.path.normpath(str(base.joinpath(*p.parts)))
 dest=Path(combined)
 if not dest.is_relative_to(root):raise ValueError('Escaping link target')
 return dest

def extract_stream(stream,root):
 root=Path(root).absolute();assert root.is_dir() and not root.is_symlink()
 records=[];hard=[];total=0
 with tarfile.open(fileobj=stream,mode='r|') as archive:
  for item in archive:
   path=member_path(root,item.name)
   if path==root:
    if not item.isdir():raise ValueError('Non-directory archive root')
    continue
   if item.isdir():
    path.mkdir(parents=True,exist_ok=True)
    if not path.is_dir() or path.is_symlink():raise ValueError('Directory collision')
    continue
   path.parent.mkdir(parents=True,exist_ok=True)
   if path.exists() or path.is_symlink():raise ValueError('Duplicate archive member')
   if item.isfile():
    total+=item.size
    if total>1024**3:raise ValueError('Unexpected Debian expanded payload size')
    h=hashlib.sha256();written=0
    with archive.extractfile(item) as src,path.open('xb') as dst:
     while True:
      block=src.read(1024**2)
      if not block:break
      written+=len(block);h.update(block);dst.write(block)
    if written!=item.size or file_sha(path)!=h.hexdigest():raise ValueError('Payload integrity failure')
    path.chmod(0o755 if item.mode&0o111 else 0o644)
    records.append(dict(path=path.relative_to(root).as_posix(),type='file',bytes=written,sha256=h.hexdigest()))
   elif item.issym():
    link_destination(root,path,item.linkname);os.symlink(item.linkname,path)
    if os.readlink(path)!=item.linkname:raise ValueError('Link mismatch')
    records.append(dict(path=path.relative_to(root).as_posix(),type='symlink',target=item.linkname))
   elif item.islnk():
    target=link_destination(root,path,item.linkname,hard=True);hard.append((path,target))
   else:raise ValueError('Special archive node denied')
 for path,target in hard:
  member_path(root,target.relative_to(root).as_posix())
  if not target.is_file() or target.is_symlink():raise ValueError('Invalid hard link')
  if path.exists() or path.is_symlink():raise ValueError('Hard link collision')
  os.link(target,path);records.append(dict(path=path.relative_to(root).as_posix(),type='file',bytes=path.stat().st_size,sha256=file_sha(path),hardlink_target=target.relative_to(root).as_posix()))
 return records

def extract_deb(package,root):
 # --fsys-tarfile emits content; none of dpkg-deb's target metadata restoration runs.
 with subprocess.Popen(['dpkg-deb','--fsys-tarfile',str(package)],stdout=subprocess.PIPE,stderr=subprocess.PIPE) as child:
  try:
   records=extract_stream(child.stdout,root);child.stdout.close();error=child.stderr.read();code=child.wait(timeout=30)
  except BaseException:
   child.kill();child.wait();raise
  if code:raise RuntimeError('Debian payload reader failed: '+error.decode(errors='replace'))
 return dict(package=Path(package).name,package_sha256=file_sha(package),members=records)
