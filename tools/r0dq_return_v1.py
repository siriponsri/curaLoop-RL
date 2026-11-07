"""Full private transport/streamed reread, then separately gated exact cleanup."""
import argparse,base64,hashlib,json,os,shlex,shutil,subprocess,tarfile
from pathlib import Path,PurePosixPath
from r0dq_core_v1 import PRIVATE,PUBLIC,ROOT,REMOTE,HOST,SSH_OPTIONS,DEADLINE,save,reserve,archive_code,now,LocalGuard
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard

EXPORT=REMOTE+'-export-v1'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()

def fetch():
    status=json.loads((PRIVATE/'return-v1-status.json').read_text())
    result=status.get('result.json') or {};assert result.get('status')=='PASS_COMPLETE_PRIVATE_EXPORT'
    assert (status.get('payload-exit.json') or {}).get('exit_code')==0
    assert status['state']['SubState']=='exited'
    proof=json.loads((PRIVATE/'return-v1-launch.json').read_text());permit=json.loads((PRIVATE/'return-v1-permit.json').read_text())
    # Stop the exited owned invocation, then freeze/fetch every small export
    # regular file. No raw helper output is displayed to the model.
    capsule=ssh(r'''
import os,json,hashlib,base64,subprocess
from pathlib import Path
p=Path(__EXPORT__);unit=__UNIT__
r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
s=dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
assert s.get('InvocationID')==__INVOCATION__ and s.get('SubState')=='exited'
terminal={k:s.get(k) for k in ['InvocationID','CPUUsageNSec','MemoryPeak','Result','ExecMainStatus','ActiveState','SubState']}
subprocess.run(['systemctl','--user','stop',unit],check=True,capture_output=True,timeout=10)
files=[]
for path in p.iterdir():
 assert path.is_file() and not path.is_symlink()
 if path.name=='full-task-v1.tar.gz':continue
 assert path.stat().st_size<4*1024**2
 raw=path.read_bytes();files.append({'name':path.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode()})
assert sum(row['bytes'] for row in files)<8*1024**2
print(json.dumps({'terminal':terminal,'files':files}))
'''.replace('__EXPORT__',repr(EXPORT)).replace('__UNIT__',repr(permit['unit'])).replace('__INVOCATION__',repr(proof['invocation_id'])))
    target=PRIVATE/'remote-return';target.mkdir(exist_ok=False)
    small=target/'export-terminal';small.mkdir()
    for row in capsule['files']:
        assert Path(row['name']).name==row['name']
        raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
        (small/row['name']).write_bytes(raw)
    save(target/'export-capsule-index.json',capsule)
    manifest=json.loads((small/'manifest.json').read_text());assert sha(small/'manifest.json')==result['manifest_sha256']
    assert manifest['archive_bytes']==result['archive_bytes']<=16*1024**3
    assert shutil.disk_usage(PRIVATE).free>=manifest['archive_bytes']+10*1024**3
    partial=target/'full-task-v1.tar.gz.part'
    ret=subprocess.run(['scp',*SSH_OPTIONS,HOST+':'+EXPORT+'/full-task-v1.tar.gz',str(partial)],capture_output=True,timeout=min(21600,(DEADLINE-__import__('datetime').datetime.now(__import__('datetime').timezone.utc)).total_seconds()))
    if ret.returncode:
        (target/'transport-error-private.txt').write_bytes(ret.stderr);raise RuntimeError('Return transfer failed; preserve all remote originals')
    assert partial.stat().st_size==manifest['archive_bytes'] and sha(partial)==manifest['archive_sha256']
    partial.replace(target/'full-task-v1.tar.gz')
    save(target/'transport-verified.json',{'status':'PASS_PRIVATE_ARCHIVE_TRANSPORT','archive_bytes':manifest['archive_bytes'],
        'archive_sha256':manifest['archive_sha256'],'manifest_sha256':result['manifest_sha256']})
    print(json.dumps({'status':'PASS_PRIVATE_ARCHIVE_TRANSPORT','archive_bytes':manifest['archive_bytes']}))

def verify():
    target=PRIVATE/'remote-return';manifestpath=target/'export-terminal/manifest.json';manifest=json.loads(manifestpath.read_text())
    transport=json.loads((target/'transport-verified.json').read_text());archive=target/'full-task-v1.tar.gz'
    with archive.open('rb+') as stream:stream.flush();os.fsync(stream.fileno())
    assert archive.stat().st_size==manifest['archive_bytes'] and sha(archive)==transport['archive_sha256']==manifest['archive_sha256']
    pins={r['path']:r for r in manifest['files']};assert len(pins)==manifest['file_count']
    seen=set();total=0;extracted=0;files=target/'files';files.mkdir(exist_ok=False)
    for row in json.loads((target/'export-capsule-index.json').read_text())['files']:
        path=target/'export-terminal'/row['name'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
    with tarfile.open(archive,'r|gz') as tar:
        for member in tar:
            rel=PurePosixPath(member.name)
            assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in member.name
            reserved={'CON','PRN','AUX','NUL'}|{a+str(i) for a in ['COM','LPT'] for i in range(1,10)}
            assert all(part and not part.endswith((' ','.')) and part.split('.')[0].upper() not in reserved
                and not any(ord(c)<32 or c in '<>:"|?*' for c in part) for part in rel.parts),'Nonportable entry preserved remotely pending review'
            assert member.isfile() and member.name in pins and member.name not in seen
            seen.add(member.name);pin=pins[member.name];assert member.size==pin['bytes']
            # Keep code, derivations and evidence as usable local files. Large
            # source SQLite/archive and vendor files are fully hashed in-stream,
            # and retained in the complete archive without local expansion.
            retain=rel.parts[0] in {'jobs','code','inputs','return-dispatch-v1'} or len(rel.parts)==1 and rel.suffix=='.json'
            if retain:
                assert member.size<512*1024**2 and extracted+member.size<=4*1024**3
                out=files.joinpath(*rel.parts);out.parent.mkdir(parents=True,exist_ok=True);dest=out.open('xb')
            else:dest=None
            h=hashlib.sha256();n=0
            try:
                with tar.extractfile(member) as stream:
                    for chunk in iter(lambda:stream.read(1024**2),b''):
                        h.update(chunk);n+=len(chunk)
                        if dest:dest.write(chunk)
            finally:
                if dest:dest.flush();os.fsync(dest.fileno());dest.close()
            assert n==pin['bytes'] and h.hexdigest()==pin['sha256'];total+=n
            if retain:extracted+=n
    assert seen==set(pins) and total==manifest['total_bytes']
    assert any(r['path']=='source/chembl_37.db' for r in manifest['files'])
    assert any(r['path']=='source/chembl_37_sqlite.tar.gz' for r in manifest['files'])
    for path in files.rglob('*'):
        if path.is_file():assert sha(path)==pins[path.relative_to(files).as_posix()]['sha256']
    proof={'status':'PASS_FULL_PRIVATE_RETURN_AND_STREAMED_LOCAL_REREAD','file_count':len(seen),'total_bytes':total,
        'archive_bytes':archive.stat().st_size,'archive_sha256':manifest['archive_sha256'],'manifest_sha256':sha(manifestpath),
        'extracted_code_evidence_derived_bytes':extracted,'all_regular_files_completely_hashed_locally':True,
        'source_database_expanded_locally':False,'private_source_values_projected_to_planner':False,'utc':now()}
    save(PUBLIC/'complete-return-verified-v1.json',proof);save(target/'complete-return-verified-v1.json',proof)
    print(json.dumps(proof))

def cleanup():
    target=PRIVATE/'remote-return';proof=json.loads((PUBLIC/'complete-return-verified-v1.json').read_text())
    assert proof['status']=='PASS_FULL_PRIVATE_RETURN_AND_STREAMED_LOCAL_REREAD'
    assert sha(target/'full-task-v1.tar.gz')==proof['archive_sha256']
    assert sha(target/'export-terminal/manifest.json')==proof['manifest_sha256']
    capsule=json.loads((target/'export-capsule-index.json').read_text())
    for row in capsule['files']:
        path=target/'export-terminal'/row['name'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
    reserve('remote-exact-cleanup-v1',600,'closeout')
    auth={'root':REMOTE,'export':EXPORT,'deadline_utc':DEADLINE.isoformat(),
        'cpu':json.loads((PRIVATE/'ssh-admission-v1.json').read_text())['least_busy_cpu'],
        'archive_sha256':proof['archive_sha256'],'manifest_sha256':proof['manifest_sha256'],
        'export_file_pins':{row['name']:{'bytes':row['bytes'],'sha256':row['sha256']} for row in capsule['files']}}
    worker=ROOT/'tools/r0dq_cleanup_worker_v1.py';archive_code(worker)
    # Must be identical to the cleanup source preserved in the complete return.
    assert worker.read_bytes()==(target/'files/return-dispatch-v1/cleanup-payload.py').read_bytes()
    raw=worker.read_text()+'\nrun('+repr(auth)+')\n'
    encoded=base64.b64encode(raw.encode()).decode()
    code=r'''
import subprocess,json
unit='curaloop-dq-cleanup-20261107-v1.service'
show=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
assert 'LoadState=not-found' in show.stdout
cmd=['systemd-run','--user','--no-ask-password','--collect','--wait','--pipe','--unit='+unit,'--service-type=exec']
props={'CPUAccounting':'yes','CPUQuota':'100%','CPUQuotaPeriodSec':'100ms','CPUAffinity':__CPU__,
'MemoryAccounting':'yes','MemoryMax':'4294967296','MemorySwapMax':'0','Nice':'19','TasksMax':'8',
'RuntimeMaxSec':'600s','TimeoutStopSec':'5s','KillMode':'control-group','Restart':'no','OOMPolicy':'kill','UMask':'0077'}
for k,v in props.items():cmd+=['-p',k+'='+str(v)]
cmd+=['--','/usr/bin/python3','-B','-c','import base64;exec(base64.b64decode('+repr(__ENCODED__)+'))']
r=subprocess.run(cmd,capture_output=True,text=True,timeout=620)
assert r.returncode==0,'Cleanup did not pass; preserve any remaining remote paths'
print(r.stdout)
'''.replace('__CPU__',repr(auth['cpu'])).replace('__ENCODED__',repr(encoded))
    result=ssh(code,timeout=650);save(PUBLIC/'scoped-delete-v1.json',result)
    absence=ssh('import json;from pathlib import Path;paths='+repr([REMOTE,EXPORT])+';assert all(not Path(p).exists() and not Path(p).is_symlink() for p in paths);print(json.dumps({"status":"PASS_FRESH_SCOPED_ABSENCE","paths":paths}))')
    save(PUBLIC/'fresh-absence-v1.json',dict(absence,utc=now()));print(json.dumps(result));print(json.dumps(absence))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['fetch','verify','cleanup']);args=parser.parse_args()
    if args.action=='verify':guard=LocalGuard('complete-return-reread-v1',cpu_seconds=1200,wall=10800,stage='closeout',memory_mib=256)
    else:guard=TransportGuard('return-'+args.action+'-v1',cpu_seconds=600 if args.action=='fetch' else 180,wall=21600 if args.action=='fetch' else 720,memory_mib=256)
    try:globals()[args.action]()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
