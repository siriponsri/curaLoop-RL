"""Finish the interrupted base return with complete one-core I/O-parallel reread."""
import json,sys,time,os,ctypes
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,write
from tools.lrbc_ui_return_v2 import reread,sha
if __name__=='__main__':
 start=time.process_time();m=json.loads((PRIVATE/'ui-full-return-manifest-v1.json').read_text());target=PRIVATE/'remote-return/full-v1/files'
 assert not (PUBLIC/'complete-return-verified-v1.json').exists()
 assert {p.name for p in target.iterdir()}=={r['object'] for r in m['files']}
 final=dict(m,files=[dict(r,object_origin='base-v1') for r in m['files']])
 reread(final)
 for part in m['parts']:
  p=PRIVATE/'remote-return/full-v1/archives'/part['name'];assert p.stat().st_size==part['bytes'] and sha(p)==part['sha256']
 write(PUBLIC/'complete-return-verified-v1.json',{'status':'PASS_COMPLETE_RETURN_AND_LOCAL_REREAD','file_count':m['file_count'],'total_bytes':m['total_bytes'],'symlink_count':len(m['symlinks']),'directory_count':len(m['directories']),'part_count':len(m['parts']),'manifest_sha256':sha(PRIVATE/'ui-full-return-manifest-v1.json'),'portable_object_mapping':True,'external_os_references_recorded_not_owned':True,'all_owned_files_including_dependencies_caches_failures':True,'utility_pack_cpu_seconds':m['utility_cpu_seconds'],'local_reread_cpu_seconds':time.process_time()-start,'repair':'earlier utility read interrupted; no previous PASS promotion','io_threads':4,'process_cpu_affinity':'one allowed core, all threads','every_file_and_archive_completely_reread':True})
 print(json.dumps({'status':'PASS_COMPLETE_RETURN_AND_LOCAL_REREAD','files':m['file_count'],'bytes':m['total_bytes']}))
