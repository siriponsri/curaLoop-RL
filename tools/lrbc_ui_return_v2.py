"""Complete final snapshot using already returned v1 objects plus a verified delta.

Never releases cleanup until the base return and every final object are reread.
The final repair is not retroactively attributed to the earlier snapshot.
"""
import hashlib,json,shutil,subprocess,sys,zipfile,os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_return_v1 import CHECK as BASE_CHECK
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,REMOTE,HOST,OPTIONS,ssh,write,DATABASE
from research.longrun_v1.coordinator import Coordinator
EXPORT=REMOTE+'-return-v2'
CHECK=BASE_CHECK.replace(repr(REMOTE+'-return'),repr(EXPORT)).replace("str(root)+'-return'","str(root)+'-return-v2'")
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while raw:=f.read(1024*1024):h.update(raw)
 return h.hexdigest()
def pack():
 assert all(j['state'] in ('COMPLETED','FAILED','FAILED_RECONCILED') for j in Coordinator(DATABASE).snapshot()['jobs'])
 code=CHECK+r'''
import zipfile
base_export=Path(str(root)+'-return');base=json.loads((base_export/'manifest.json').read_text());basepins={r['path']:r for r in base['files']}
new=[]
for row in rows:
 old=basepins.get(row['path'])
 if old and all(old[k]==row[k] for k in ['path','bytes','mode','sha256']):row.update(object=old['object'],object_origin='base-v1')
 else:row.update(object=f'delta-{len(new):08d}.bin',object_origin='delta-v2');new.append(row)
assert not export.exists() and not export.is_symlink();os.umask(0o077);export.mkdir()
archive=export/'delta-v2.zip'
with zipfile.ZipFile(archive,'x',zipfile.ZIP_STORED) as z:
 for row in new:z.write(root/row['path'],row['object'])
manifest={'schema':'curaloop.ui.complete-return.v2','root':str(root),'export':str(export),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'files':rows,'symlinks':links,'directories':directories,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'base_export':str(base_export),'base_manifest_file_sha256':digest(base_export/'manifest.json'),'delta_archive_sha256':digest(archive),'delta_file_count':len(new),'delta_bytes':sum(r['bytes'] for r in new),'utility_cpu_seconds':time.process_time()}
(export/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
'''
 m=ssh(code,timeout=245);write(PRIVATE/'ui-full-return-manifest-v2.json',m);print(json.dumps({'status':'FINAL_SNAPSHOT_PACKED','files':m['file_count'],'bytes':m['total_bytes'],'delta_files':m['delta_file_count'],'delta_bytes':m['delta_bytes']}))
def reread(m):
 # Parallelize file I/O while bounding this one process (all its threads) to
 # exactly one allowed CPU. Every byte is still reread from the retained disk.
 if os.name=='nt':
  import ctypes
  from ctypes import wintypes
  kernel=ctypes.WinDLL('kernel32',use_last_error=True)
  kernel.GetCurrentProcess.restype=wintypes.HANDLE
  kernel.GetProcessAffinityMask.argtypes=[wintypes.HANDLE,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
  kernel.SetProcessAffinityMask.argtypes=[wintypes.HANDLE,ctypes.c_size_t]
  process=kernel.GetCurrentProcess();allowed=ctypes.c_size_t();system=ctypes.c_size_t()
  assert kernel.GetProcessAffinityMask(process,ctypes.byref(allowed),ctypes.byref(system))
  mask=allowed.value&-allowed.value;assert mask and kernel.SetProcessAffinityMask(process,mask)
  assert kernel.GetProcessAffinityMask(process,ctypes.byref(allowed),ctypes.byref(system)) and allowed.value==mask
 else:os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
 def verify(row):
  folder=PRIVATE/('remote-return/full-v1/files' if row['object_origin']=='base-v1' else 'remote-return/full-v2/files')
  p=folder/row['object'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 with ThreadPoolExecutor(max_workers=4) as pool:
  for index,_ in enumerate(pool.map(verify,m['files']),1):
   if index%10000==0:print('Reread '+str(index)+' final objects',flush=True)
def transfer():
 assert json.loads((PUBLIC/'complete-return-verified-v1.json').read_text())['status']=='PASS_COMPLETE_RETURN_AND_LOCAL_REREAD'
 m=json.loads((PRIVATE/'ui-full-return-manifest-v2.json').read_text());folder=PRIVATE/'remote-return/full-v2';folder.mkdir(exist_ok=False);target=folder/'files';target.mkdir()
 archive=folder/'delta-v2.zip';r=subprocess.run(['scp',*OPTIONS,HOST+':'+EXPORT+'/delta-v2.zip',str(archive)],capture_output=True,timeout=120);assert r.returncode==0 and sha(archive)==m['delta_archive_sha256']
 pins={r['object']:r for r in m['files'] if r['object_origin']=='delta-v2'}
 with zipfile.ZipFile(archive) as z:
  assert len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(pins)
  for name,row in pins.items():
   assert name.startswith('delta-') and '/' not in name and '\\' not in name and z.getinfo(name).file_size==row['bytes']
   with z.open(name) as src,(target/name).open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
 reread(m)
 write(PUBLIC/'complete-return-verified-v2.json',{'status':'PASS_COMPLETE_FINAL_SNAPSHOT_AND_LOCAL_REREAD','file_count':m['file_count'],'total_bytes':m['total_bytes'],'symlink_count':len(m['symlinks']),'directory_count':len(m['directories']),'delta_file_count':m['delta_file_count'],'delta_bytes':m['delta_bytes'],'manifest_sha256':sha(PRIVATE/'ui-full-return-manifest-v2.json'),'base_return':'complete-return-verified-v1.json','every_final_object_reread':True,'earlier_objects_retained':True,'utility_pack_cpu_seconds':m['utility_cpu_seconds']})
 print(json.dumps({'status':'PASS_COMPLETE_FINAL_SNAPSHOT_AND_LOCAL_REREAD','files':m['file_count'],'bytes':m['total_bytes']}))
def cleanup():
 proof=json.loads((PUBLIC/'complete-return-verified-v2.json').read_text());assert proof['status']=='PASS_COMPLETE_FINAL_SNAPSHOT_AND_LOCAL_REREAD'
 m=json.loads((PRIVATE/'ui-full-return-manifest-v2.json').read_text());reread(m)
 # Also reread obsolete base objects, preserving all earlier attempts before deleting their archives.
 base=json.loads((PRIVATE/'ui-full-return-manifest-v1.json').read_text())
 seen={r['object'] for r in m['files'] if r['object_origin']=='base-v1'}
 for row in base['files']:
  if row['object'] not in seen:assert sha(PRIVATE/'remote-return/full-v1/files'/row['object'])==row['sha256']
 code=CHECK+r'''
import shutil
assert export.resolve()==export and not export.is_symlink() and export.stat().st_uid==os.getuid()
old=json.loads((export/'manifest.json').read_text())
strip=lambda values:[{k:v for k,v in r.items() if k not in ('object','object_origin')} for r in values]
assert strip(rows)==strip(old['files']) and links==old['symlinks'] and directories==old['directories']
assert len(rows)==__COUNT__ and sum(r['bytes'] for r in rows)==__BYTES__
assert set(p.name for p in export.iterdir())=={'manifest.json','delta-v2.zip'} and digest(export/'delta-v2.zip')==old['delta_archive_sha256']
base_export=Path(str(root)+'-return');assert base_export.resolve()==base_export and not base_export.is_symlink() and base_export.stat().st_uid==os.getuid()
assert digest(base_export/'manifest.json')==old['base_manifest_file_sha256'];base=json.loads((base_export/'manifest.json').read_text())
assert set(p.name for p in base_export.iterdir())=={'manifest.json'}|{p['name'] for p in base['parts']}
assert all(digest(base_export/p['name'])==p['sha256'] for p in base['parts'])
shutil.rmtree(root);shutil.rmtree(base_export);shutil.rmtree(export)
print(json.dumps({'status':'PASS_EXACT_SCOPED_DELETE_AFTER_FINAL_AND_BASE_REREAD','deleted':[str(root),str(base_export),str(export)],'utility_cpu_seconds':time.process_time()}))
'''.replace('__COUNT__',repr(proof['file_count'])).replace('__BYTES__',repr(proof['total_bytes']))
 write(PUBLIC/'scoped-delete-v2.json',ssh(code,timeout=245))
 absent=ssh("import json,time;from pathlib import Path;paths="+repr([REMOTE,REMOTE+'-return',EXPORT])+";assert all(not Path(p).exists() and not Path(p).is_symlink() for p in paths);print(json.dumps({'status':'PASS_FRESH_SCOPED_ABSENCE','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'absent_paths':paths}))")
 write(PUBLIC/'fresh-absence-v2.json',absent);print(json.dumps(absent))
if __name__=='__main__':{'pack':pack,'transfer':transfer,'cleanup':cleanup}[sys.argv[1]]()
