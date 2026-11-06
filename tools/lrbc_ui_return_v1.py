"""Complete UI return with portable object mapping and exact guarded cleanup.

Regular files are stored as numbered objects to preserve Linux case/name identity
on Windows. Symlinks are metadata, never followed or recreated on Windows. Only
the three pre-existing OS-Python references may resolve outside the owned root.
"""
import argparse,hashlib,json,shutil,sqlite3,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,DATABASE,ssh,write
from research.longrun_v1.coordinator import Coordinator
EXPORT=REMOTE+'-return'
CHECK=r'''
import os,json,hashlib,stat,time,resource,signal
from pathlib import Path
root=Path(__ROOT__);export=Path(__EXPORT__)
assert str(root)=='/home/chaw/curaloop-rl/lrbc-ui-20261106-v1' and str(export)==str(root)+'-return'
assert root.resolve()==root and not root.is_symlink() and root.stat().st_uid==os.getuid()
# One single-thread utility process, bounded inside the retained utility reserve.
os.nice(19);os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
resource.setrlimit(resource.RLIMIT_CPU,(120,120));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));signal.alarm(240)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while data:=f.read(1024*1024):h.update(data)
 return h.hexdigest()
active=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit() or int(p.name)==os.getpid():continue
 try:
  cmd=(p/'cmdline').read_bytes().split(bytes([0]))
  if any(str(root).encode() in value for value in cmd):active.append(int(p.name))
 except (OSError,ValueError):pass
assert not active, 'Owned processing still active'
rows=[];links=[];directories=[]
allowed_external={'qa-env/bin/python','qa-env/bin/python3','qa-env/bin/python3.12'}
for parent,dirs,files in os.walk(root,followlinks=False):
 for name in sorted(dirs+files):
  p=Path(parent)/name;s=p.lstat();assert s.st_uid==os.getuid()
  rel=p.relative_to(root).as_posix()
  if stat.S_ISLNK(s.st_mode):
   resolved=p.resolve(strict=True);external=not resolved.is_relative_to(root)
   row={'path':rel,'target':os.readlink(p),'mode':stat.S_IMODE(s.st_mode),'external':external}
   if external:
    assert rel in allowed_external and resolved==Path('/usr/bin/python3.12')
    row.update(resolved=str(resolved),sha256=digest(resolved),bytes=resolved.stat().st_size,ownership='preexisting OS interpreter reference; not copied or deleted')
   else:row['resolved_relative']=resolved.relative_to(root).as_posix()
   links.append(row)
  elif stat.S_ISDIR(s.st_mode):directories.append({'path':rel,'mode':stat.S_IMODE(s.st_mode)})
  else:
   assert stat.S_ISREG(s.st_mode),'Unsupported owned entry'
   rows.append({'path':rel,'bytes':s.st_size,'mode':stat.S_IMODE(s.st_mode),'sha256':digest(p)})
rows.sort(key=lambda r:r['path']);links.sort(key=lambda r:r['path']);directories.sort(key=lambda r:r['path'])
assert len(rows)<100000 and sum(r['bytes'] for r in rows)<8*1024**3
for i,row in enumerate(rows):row['object']=f'{i:08d}.bin'
'''.replace('__ROOT__',repr(REMOTE)).replace('__EXPORT__',repr(EXPORT))

def inventory_pack():
 snap=Coordinator(DATABASE).snapshot();assert all(r['state'] in ('COMPLETED','FAILED','FAILED_RECONCILED') for r in snap['jobs'])
 with sqlite3.connect(DATABASE) as src,sqlite3.connect(PRIVATE/'coordinator-terminal-ui.sqlite') as dst:src.backup(dst)
 code=CHECK+r'''
import zipfile
assert not export.exists() and not export.is_symlink();assert export.parent.resolve()==root.parent and export.parent.stat().st_uid==os.getuid()
os.umask(0o077);export.mkdir();parts=[];group=[];size=0
def pack(group):
 name=f'part-{len(parts):03d}.zip';archive=export/name
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_STORED,allowZip64=True) as z:
  for row in group:z.write(root/row['path'],row['object'])
 parts.append({'name':name,'bytes':archive.stat().st_size,'sha256':digest(archive),'objects':[r['object'] for r in group]})
for row in rows:
 if group and size+row['bytes']>256*1024**2:pack(group);group=[];size=0
 group.append(row);size+=row['bytes']
if group:pack(group)
manifest={'schema':'curaloop.ui.complete-return.v1','root':str(root),'export':str(export),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'files':rows,'symlinks':links,'directories':directories,'parts':parts,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'utility_cpu_seconds':time.process_time(),'utility_max_cpu_seconds':120,'symlinks_followed':False}
(export/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
'''
 manifest=ssh(code,timeout=245);write(PRIVATE/'ui-full-return-manifest-v1.json',manifest)
 print(json.dumps({'status':'PACKED_NOT_YET_RETURNED','files':manifest['file_count'],'bytes':manifest['total_bytes'],'parts':len(manifest['parts'])}))

def transfer():
 manifest=json.loads((PRIVATE/'ui-full-return-manifest-v1.json').read_text());assert shutil.disk_usage(PRIVATE).free>2*manifest['total_bytes']+512*1024**2
 archive_folder=PRIVATE/'remote-return/full-v1/archives';target=PRIVATE/'remote-return/full-v1/files';archive_folder.mkdir(parents=True,exist_ok=True);target.mkdir(exist_ok=True)
 pins={r['object']:r for r in manifest['files']}
 def sha(p):
  h=hashlib.sha256()
  with p.open('rb') as f:
   while raw:=f.read(1024*1024):h.update(raw)
  return h.hexdigest()
 for part in manifest['parts']:
  archive=archive_folder/part['name']
  if not archive.exists() or sha(archive)!=part['sha256']:
   r=subprocess.run(['scp',*OPTIONS,HOST+':'+EXPORT+'/'+part['name'],str(archive)],capture_output=True,timeout=240);assert r.returncode==0
  assert sha(archive)==part['sha256'] and archive.stat().st_size==part['bytes']
  with zipfile.ZipFile(archive) as z:
   assert len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(part['objects'])
   for info in z.infolist():
    pin=pins[info.filename];assert info.file_size==pin['bytes'] and '/' not in info.filename and '\\' not in info.filename
    p=target/info.filename
    if p.exists():assert p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'];continue
    with z.open(info) as src,p.open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
  print('Returned '+part['name'],flush=True)
 assert {p.name for p in target.iterdir()}==set(pins)
 for name,pin in pins.items():assert (target/name).stat().st_size==pin['bytes'] and sha(target/name)==pin['sha256']
 write(PUBLIC/'complete-return-verified-v1.json',{'status':'PASS_COMPLETE_RETURN_AND_LOCAL_REREAD','file_count':manifest['file_count'],'total_bytes':manifest['total_bytes'],'symlink_count':len(manifest['symlinks']),'directory_count':len(manifest['directories']),'part_count':len(manifest['parts']),'manifest_sha256':sha(PRIVATE/'ui-full-return-manifest-v1.json'),'portable_object_mapping':True,'external_os_references_recorded_not_owned':True,'all_owned_files_including_dependencies_caches_failures':True,'utility_pack_cpu_seconds':manifest['utility_cpu_seconds']})
 print('PASS complete local reread',manifest['file_count'],manifest['total_bytes'])

def cleanup():
 proof=json.loads((PUBLIC/'complete-return-verified-v1.json').read_text());assert proof['status']=='PASS_COMPLETE_RETURN_AND_LOCAL_REREAD'
 manifest=json.loads((PRIVATE/'ui-full-return-manifest-v1.json').read_text())
 for row in manifest['files']:
  p=PRIVATE/'remote-return/full-v1/files'/row['object'];h=hashlib.sha256()
  with p.open('rb') as f:
   while raw:=f.read(1024*1024):h.update(raw)
  assert p.stat().st_size==row['bytes'] and h.hexdigest()==row['sha256']
 code=CHECK+r'''
import shutil
assert export.resolve()==export and not export.is_symlink() and export.stat().st_uid==os.getuid()
old=json.loads((export/'manifest.json').read_text());assert rows==old['files'] and links==old['symlinks'] and directories==old['directories']
assert len(rows)==__COUNT__ and sum(r['bytes'] for r in rows)==__BYTES__
assert set(p.name for p in export.iterdir())=={'manifest.json'}|{p['name'] for p in old['parts']}
assert all(digest(export/p['name'])==p['sha256'] for p in old['parts'])
shutil.rmtree(root);shutil.rmtree(export)
print(json.dumps({'status':'PASS_EXACT_SCOPED_DELETE_AFTER_FULL_REREAD','root':str(root),'export':str(export),'utility_cpu_seconds':time.process_time()}))
'''.replace('__COUNT__',repr(proof['file_count'])).replace('__BYTES__',repr(proof['total_bytes']))
 write(PUBLIC/'scoped-delete-v1.json',ssh(code,timeout=245))
 absence=ssh("import json,time;from pathlib import Path;paths="+repr([REMOTE,EXPORT])+";assert all(not Path(p).exists() and not Path(p).is_symlink() for p in paths);print(json.dumps({'status':'PASS_FRESH_SCOPED_ABSENCE','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'absent_paths':paths}))")
 write(PUBLIC/'fresh-absence-v1.json',absence);print(json.dumps(absence))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['pack','transfer','cleanup']);mode=p.parse_args().mode
 {'pack':inventory_pack,'transfer':transfer,'cleanup':cleanup}[mode]()
