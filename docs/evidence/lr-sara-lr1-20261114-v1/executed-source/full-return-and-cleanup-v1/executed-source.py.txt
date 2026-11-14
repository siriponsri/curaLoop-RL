"""Delivery only after terminal engineering failure: full return, reread and cleanup."""
import ast,hashlib,json,subprocess,sys,tarfile
from pathlib import Path,PurePosixPath
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.saralr1_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,reserve,settle,write_new
from tools.saralr1_transport_v1 import invoke

EXPORT=r'''
import hashlib,json,os,resource,subprocess,sys
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(180,180));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/lr-sara-lr1-20261114-v1');out=t.parent/(t.name+'-export')
assert t.resolve()==t and not out.exists() and hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
ins=json.loads(subprocess.check_output(['docker','inspect','curaloop-saralr1-engineering-acceptance-v1'],text=True))[0]
assert not ins['State']['Running'] and ins['State']['ExitCode']==1
observed=[];payload=t/'overlay/payload'
for q in sorted(payload.rglob('*')):
 if '.so' in q.name:
  resolved=q.resolve();inside=resolved.is_relative_to(payload)
  item=dict(path=q.relative_to(t).as_posix(),symlink=q.is_symlink(),target=os.readlink(q) if q.is_symlink() else None,
   resolved_within_overlay=inside,target_exists=resolved.exists())
  if inside and resolved.is_file():
   h=hashlib.sha256()
   with resolved.open('rb') as f:
    while True:
     b=f.read(1024**2)
     if not b:break
     h.update(b)
   item['sha256']=h.hexdigest()
  observed.append(item)
forensic=dict(status='STATIC_POST_FAILURE_INSPECTION_ONLY',shared_library_entries=observed,
 env=[x for x in ins['Config']['Env'] if x.startswith(('LD_LIBRARY_PATH=','HOME='))],
 actual_library_reload_or_import=False,container_state=ins['State'],root_cause='Dynamic loader search failure observed; no new load was attempted to distinguish causes')
(t/'post-failure-static-observation.json').write_text(json.dumps(forensic,indent=2))
states={}
for ident in subprocess.check_output(['docker','ps','-aq','--filter','label=curaloop.task=lr-sara-lr1-20261114-v1'],text=True).split():
 i=json.loads(subprocess.check_output(['docker','inspect',ident],text=True))[0];assert not i['State']['Running'];states[i['Name']]=i
(t/'pre-export-docker-state.json').write_text(json.dumps(states,indent=2))
out.mkdir();out.chmod(0o777);(out/'export.py').write_text(p['program'])
name='curaloop-saralr1-owned-export-v1';image='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d'
cmd=['docker','create','--name',name,'--label','curaloop.task=lr-sara-lr1-20261114-v1','--network=none','--cpus=1','--memory=2g','--memory-swap=2g','--pids-limit=32','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--mount',f'type=bind,source={t},target=/source,readonly','--mount',f'type=bind,source={out},target=/return',image,'python','/return/export.py']
c=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert c.returncode==0,c.stderr
i=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0];assert i['HostConfig']['NanoCpus']==1000000000 and not i['HostConfig']['DeviceRequests']
(out/'admission.json').write_text(json.dumps(i,indent=2));subprocess.run(['docker','start',name],check=True,capture_output=True,timeout=15)
try:w=subprocess.run(['docker','wait',name],capture_output=True,text=True,timeout=800)
except subprocess.TimeoutExpired:
 subprocess.run(['docker','kill',name],capture_output=True,timeout=15);raise
logs=subprocess.run(['docker','logs',name],capture_output=True,timeout=15);(out/'stdout.log').write_bytes(logs.stdout);(out/'stderr.log').write_bytes(logs.stderr)
assert w.stdout.strip()=='0',logs.stderr.decode(errors='replace')
result=json.loads((out/'export-result.json').read_text());result.update(export_root=str(out),forensic=forensic)
print(json.dumps(result))
'''

def constant(path,name):
 tree=ast.parse(path.read_text())
 return next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))

def main():
 r,l=authority('analysis_return');assert l['status']=='ACTIVE_CLOSEOUT_NO_GO' and not l['attempts']['native_references']
 program=constant(ROOT/'tools/sara_return_worker_v1.py','PROGRAM')
 old="def sha(p):\n with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()"
 new="def sha(p):\n h=hashlib.sha256()\n with p.open('rb') as f:\n  while True:\n   block=f.read(1024**2)\n   if not block:break\n   h.update(block)\n return h.hexdigest()"
 assert program.count(old)==1;program=program.replace(old,new).replace('(5400,5400)','(600,600)').replace('signal.alarm(5400)','signal.alarm(700)');compile(program,'export-program','exec')
 reserve('remote-owned-export-v1','analysis_return',900,remote=True,scope='Static failed-artifact inspection and one read-only full owned-root export; no research rerun')
 value=invoke(EXPORT,dict(release_sha256=digest(ROOT/'research/manifests/lr_sara_lr1_release_20261114_v1.json'),program=program),timeout=900)
 write_new(ACCOUNT/'owned-export-transport-v1.json',value);assert value['exit_code']==0,value
 result=json.loads(value['stdout']);write_new(PUBLIC/'post-failure-static-observation-v1.json',result.pop('forensic'));write_new(ACCOUNT/'export-receipt-v1.json',result)
 settle('remote-owned-export-v1','PASS_FULL_OWNED_EXPORT',measured_export_container_cpu_seconds=result['export_container_cpu_seconds'])
 folder=ACCOUNT/'remote-return-v1';folder.mkdir()
 for name in ['owned-return.tar.gz','owned-manifest.json','export-result.json','export.py','admission.json','stdout.log','stderr.log']:
  v=subprocess.run(['rtk','proxy','scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','100.77.149.83:'+result['export_root']+'/'+name,str(folder/name)],capture_output=True,text=True,timeout=600)
  write_new(folder/(name+'.transport.json'),dict(exit_code=v.returncode,stderr=v.stderr));assert v.returncode==0
 bundle=folder/'owned-return.tar.gz';manifest=folder/'owned-manifest.json';assert digest(bundle)==result['bundle_sha256'] and digest(manifest)==result['manifest_sha256']
 expected=json.loads(manifest.read_text());files={};dirs={}
 with tarfile.open(bundle,'r|gz') as archive:
  for item in archive:
   p=PurePosixPath(item.name);assert not p.is_absolute() and '..' not in p.parts
   meta={k:getattr(item,k) for k in ('mode','uid','gid','mtime')}
   if item.isdir():assert item.name not in dirs;dirs[item.name]=meta
   elif item.issym():assert item.name not in files;files[item.name]=dict(type='symlink',target=item.linkname,**meta)
   else:
    assert item.isfile() and item.name not in files
    with archive.extractfile(item) as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    files[item.name]=dict(type='file',bytes=item.size,sha256=h,**meta)
 assert files==expected['files'] and dirs==expected['directories']
 returned=dict(result,status='PASS_FULL_RETURN_AND_LOCAL_STREAM_REREAD',all_file_content_and_link_directory_metadata_verified=True,returned_links_extracted_or_followed=False)
 write_new(PUBLIC/'owned-return-verification-v1.json',returned)
 # Reuse the previously verified ownership-aware cleanup mechanism without changing its safety checks.
 cleanup=constant(ROOT/'tools/sara_cleanup_v1.py','REMOTE');verify=constant(ROOT/'tools/sara_cleanup_v1.py','VERIFY');delete=constant(ROOT/'tools/sara_cleanup_v1.py','DELETE')
 cleanup=cleanup.replace('lr-sara-20261114-v1','lr-sara-lr1-20261114-v1').replace('curaloop-sara-','curaloop-saralr1-')
 reserve('remote-exact-cleanup-v1','analysis_return',3600,remote=True,scope='Full independent remote reread and exact owned namespace/export/stopped-container cleanup')
 v=invoke(cleanup,dict(release_sha256=digest(ROOT/'research/manifests/lr_sara_lr1_release_20261114_v1.json'),manifest_sha256=result['manifest_sha256'],verify_program=verify,delete_program=delete),timeout=3500)
 write_new(ACCOUNT/'owned-cleanup-transport-v1.json',v);assert v['exit_code']==0,v
 clean=json.loads(v['stdout']);write_new(PUBLIC/'owned-cleanup-v1.json',clean);settle('remote-exact-cleanup-v1','PASS_VERIFIED_EXACT_CLEANUP',measured_remote_verify_cpu_seconds=clean['verification']['cpu_seconds'])
 absence=constant(ROOT/'tools/sara_cleanup_v1.py','ABSENCE').replace('lr-sara-20261114-v1','lr-sara-lr1-20261114-v1')
 v=invoke(absence,{},timeout=45);write_new(ACCOUNT/'fresh-absence-transport-v1.json',v);assert v['exit_code']==0
 write_new(PUBLIC/'owned-cleanup-fresh-absence-v1.json',json.loads(v['stdout']))
 print(json.dumps(dict(status='PASS_DELIVERY_RETURN_REREAD_CLEANUP',files=result['regular_files'],symlinks=result['symlinks'],bytes=result['regular_bytes'],containers_removed=len(clean['removed_containers']))))
if __name__=='__main__':main()
