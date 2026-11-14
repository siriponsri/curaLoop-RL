"""Full content-deduplicated return, independent local validation and exact cleanup."""
import argparse,hashlib,json,subprocess,sys,tarfile
from pathlib import Path,PurePosixPath
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,digest,reserve,settle,write_new
from tools.envstable_transport_v1 import call,invoke
from tools.envstable_cleanup_programs_v1 import VERIFY,DELETE,REMOTE,ABSENCE
def export():
 authority('analysis_return');reserve('remote-full-export-v1','analysis_return',2400,remote=True,scope='All owned files including installed/reconstructed artifacts, deduplicate identical bytes only in transfer archive')
 result=call(ROOT/'tools/envstable_return_worker_v1.py',{},ACCOUNT/'export-transport-v1.json',timeout=3900)
 write_new(ACCOUNT/'export-receipt-v1.json',result);write_new(PUBLIC/'full-export-summary-v1.json',result)
 settle('remote-full-export-v1','PASS_EXPORTED',measured_export_container_cpu_seconds=result['export_container_cpu_seconds'],measured_remote_host_process_cpu_seconds=result['remote_host_process_cpu_seconds']);print(json.dumps(result))
def fetch():
 authority('analysis_return');result=json.loads((ACCOUNT/'export-receipt-v1.json').read_text());folder=ACCOUNT/'remote-return-v1';folder.mkdir()
 for name in ['owned-return.tar.gz','owned-manifest.json','export-result.json','export.py','container-admission.json','create-receipt.json','container-stdout.log','container-stderr.log']:
  p=subprocess.run(['rtk','proxy','scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','100.77.149.83:'+result['export_root']+'/'+name,str(folder/name)],capture_output=True,text=True,timeout=5400)
  write_new(folder/(name+'.transport.json'),dict(exit_code=p.returncode,stderr=p.stderr));assert p.returncode==0
 bundle=folder/'owned-return.tar.gz';mp=folder/'owned-manifest.json';assert digest(bundle)==result['bundle_sha256'] and digest(mp)==result['manifest_sha256']
 manifest=json.loads(mp.read_text());seen={};dirs={};aliases=0
 with tarfile.open(bundle,'r|gz') as tar:
  for member in tar:
   path=PurePosixPath(member.name);assert not path.is_absolute() and '..' not in path.parts
   meta={k:getattr(member,k) for k in ('mode','uid','gid','mtime')}
   if member.isdir():assert member.name not in dirs;dirs[member.name]=meta
   elif member.issym():assert member.name not in seen;seen[member.name]=dict(type='symlink',target=member.linkname,**meta)
   elif member.islnk():
    # Validate an earlier independently hashed regular member, never extract/follow links.
    assert member.name not in seen and member.linkname in seen and seen[member.linkname]['type']=='file'
    prior=seen[member.linkname];seen[member.name]=dict(type='file',bytes=prior['bytes'],sha256=prior['sha256'],**meta);aliases+=1
   else:
    assert member.isfile() and member.name not in seen;h=hashlib.sha256()
    with tar.extractfile(member) as f:
     while b:=f.read(1024**2):h.update(b)
    seen[member.name]=dict(type='file',bytes=member.size,sha256=h.hexdigest(),**meta)
 assert seen==manifest['files'] and dirs==manifest['directories']
 value=dict(status='PASS_COMPLETE_OWNED_RETURN_AND_INDEPENDENT_LOCAL_STREAM_REREAD',regular_files=result['regular_files'],symlinks=result['symlinks'],directories=result['directories'],regular_bytes=result['regular_bytes'],bundle_bytes=bundle.stat().st_size,bundle_sha256=digest(bundle),manifest_sha256=digest(mp),content_deduplicated_aliases=aliases,every_file_content_and_link_metadata_verified=True,returned_links_extracted_or_followed=False,remote_cleanup='NOT_RUN')
 write_new(PUBLIC/'owned-return-verification-v1.json',value);print(json.dumps(value))
def cleanup():
 authority('analysis_return');r=json.loads((PUBLIC/'owned-return-verification-v1.json').read_text());assert r['every_file_content_and_link_metadata_verified']
 reserve('remote-exact-cleanup-v1','analysis_return',1800,remote=True,scope='Independent remote full reread then exact owned root/export and stopped containers only')
 value=invoke(REMOTE,dict(release_sha256=digest(RELEASE),manifest_sha256=r['manifest_sha256'],verify_program=VERIFY,delete_program=DELETE),timeout=3600)
 write_new(ACCOUNT/'cleanup-transport-v1.json',value);assert value['exit_code']==0,value
 result=json.loads(value['stdout']);write_new(PUBLIC/'owned-cleanup-v1.json',result);settle('remote-exact-cleanup-v1',result['status'],measured_verification_container_cpu_seconds=result['verification']['cpu_seconds'],measured_remote_host_process_cpu_seconds=result['remote_host_process_cpu_seconds'])
 fresh=invoke(ABSENCE,{},timeout=45);write_new(ACCOUNT/'fresh-absence-transport-v1.json',fresh);assert fresh['exit_code']==0;write_new(PUBLIC/'fresh-absence-v1.json',json.loads(fresh['stdout']));print(result['status'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['export','fetch','cleanup']);a=p.parse_args();globals()[a.action]()
