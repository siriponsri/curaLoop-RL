"""Lossless evidence return and exact owned cleanup; never runs research code."""
import argparse,base64,hashlib,json,subprocess,sys,tarfile
from pathlib import Path,PurePosixPath
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.sar30_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,write_new,save_ledger

def fetch():
    authority();receipt=json.loads((ACCOUNT/'remote-export-receipt-v1.json').read_text())
    folder=ACCOUNT/'remote-return-v1';folder.mkdir(exist_ok=False)
    for remote,name in [(receipt['bundle_path'],'owned-return.tar.gz'),(receipt['manifest_path'],'owned-manifest.json')]:
        p=subprocess.run(['rtk','proxy','scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',
            '100.77.149.83:'+remote,str(folder/name)],capture_output=True,text=True,timeout=1500)
        write_new(folder/(name+'.transport.json'),dict(exit_code=p.returncode,stderr=p.stderr))
        assert p.returncode==0,'Preserve partial return; do not delete remote'
    bundle=folder/'owned-return.tar.gz';manifest_path=folder/'owned-manifest.json'
    assert bundle.stat().st_size==receipt['bundle_bytes'] and digest(bundle)==receipt['bundle_sha256']
    manifest=json.loads(manifest_path.read_text());seen={}
    with tarfile.open(bundle,'r|gz') as tar:
        for member in tar:
            p=PurePosixPath(member.name)
            assert member.isfile() and not p.is_absolute() and '..' not in p.parts and member.name not in seen
            assert member.name in manifest and member.size==manifest[member.name]['bytes']
            with tar.extractfile(member) as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
            seen[member.name]=dict(bytes=member.size,sha256=sha)
    assert seen==manifest and len(seen)==receipt['files']
    value=dict(status='PASS_ALL_PERSISTENT_OWNED_FILES_RETURNED_AND_STREAM_REREAD',files=len(seen),bytes=sum(x['bytes'] for x in seen.values()),
        bundle_bytes=bundle.stat().st_size,bundle_sha256=digest(bundle),manifest_sha256=digest(manifest_path),
        storage='Exact private archive plus per-member SHA256 manifest on local disk; every member independently rehashed without platform-dependent extraction',
        remote_cleanup='NOT_RUN',candidate_benchmark_data_or_model_weights_in_return=False)
    write_new(PUBLIC/'owned-return-verification-v1.json',value)
    # Only small diagnostic/control records leave the returned private archive.
    with tarfile.open(bundle,'r:gz') as tar:
        for name in ['control/environment-result.json','control/early-stop.json','control/guard-probes.json','control/resources-final.json',
                     'control/container-admission.json','control/create-receipt.json']:
            with tar.extractfile(name) as f:raw=f.read()
            path=PUBLIC/('remote-'+Path(name).name);assert not path.exists();path.write_bytes(raw)
    print(json.dumps(value))

CLEANUP=r'''
import hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(300,300));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/lr-sar30-qual-20261114-v1')
assert t.resolve()==t and t.parent.resolve()==Path('/home/chaw/curaloop-tasks') and not t.is_symlink()
m=t.parent/'lr-sar30-qual-20261114-v1-return-manifest.json';bundle=t.parent/'lr-sar30-qual-20261114-v1-return.tar.gz'
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(m)==p['manifest_sha256'] and sha(bundle)==p['bundle_sha256']
manifest=json.loads(m.read_text());seen={}
for q in t.rglob('*'):
 assert not q.is_symlink()
 if q.is_file():seen[q.relative_to(t).as_posix()]={'bytes':q.stat().st_size,'sha256':sha(q)}
assert seen==manifest,'Remote tree changed after export; preserve without cleanup'
names=['curaloop-sar30-env-20261114-v1','curaloop-sar30-env-20261114-v1-probe-wall','curaloop-sar30-env-20261114-v1-probe-cpu']
for name in names:
 state=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
 assert not state['State']['Running'] and state['Config']['Labels']['curaloop.task']=='lr-sar30-qual-20261114-v1'
# Root-owned package files are removed only through this exact task-owned bind.
# No image, shared cache, service, key, configuration or other task is changed.
t.chmod(0o777)
name='curaloop-sar30-cleanup-20261114-v1'
code="from pathlib import Path;import shutil; r=Path('/ownedtask'); [(shutil.rmtree(q) if q.is_dir() else q.unlink()) for q in r.iterdir()]"
cmd=['docker','create','--name',name,'--label','curaloop.task=lr-sar30-qual-20261114-v1','--network=none','--cpus=1',
 '--memory=256m','--memory-swap=256m','--pids-limit=32','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',
 '--mount',f'type=bind,source={t},target=/ownedtask','sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d',
 'python','-c',code]
created=subprocess.run(cmd,capture_output=True,text=True,timeout=20);assert created.returncode==0,created.stderr
subprocess.run(['docker','start',name],check=True,capture_output=True,timeout=10)
try:x=subprocess.run(['docker','wait',name],capture_output=True,text=True,timeout=90)
except subprocess.TimeoutExpired:
 subprocess.run(['docker','kill',name],capture_output=True,timeout=15);raise
assert x.stdout.strip()=='0',subprocess.check_output(['docker','logs',name],text=True)
assert not list(t.iterdir());t.rmdir()
for n in names+[name]:subprocess.run(['docker','rm',n],check=True,capture_output=True,timeout=15)
bundle.unlink();m.unlink()
assert not any(q.exists() for q in [t,bundle,m])
absence={n:subprocess.run(['docker','inspect',n],capture_output=True,timeout=10).returncode!=0 for n in names+[name]}
assert all(absence.values())
print(json.dumps({'status':'PASS_REMOTE_TREE_REREAD_AND_EXACT_OWNED_CLEANUP','files_reread':len(seen),
 'removed_root':str(t),'root_absent':not t.exists(),'exports_absent':not bundle.exists() and not m.exists(),
 'owned_container_absence':absence,'shared_images_models_services_untouched':True,
 'remote_control_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime}))
'''

def cleanup():
    r,l=authority();verify=json.loads((PUBLIC/'owned-return-verification-v1.json').read_text())
    assert verify['status'].startswith('PASS_ALL_PERSISTENT')
    assert all(b['id']!='remote-cleanup-v1' for b in l['reservations'])
    assert sum(b['cpu_seconds'] for b in l['reservations'] if b['stage']=='report_delivery')+600<=r['stage_caps_seconds']['report_delivery']
    assert sum(b['cpu_seconds'] for b in l['reservations'])+600<=r['cpu_cap_seconds']
    l['reservations'].append(dict(id='remote-cleanup-v1',stage='report_delivery',cpu_seconds=600,gpu_allocated_seconds=0,status='RESERVED_REMOTE_CLEANUP'))
    l['active_jobs'].append('remote-cleanup-v1');save_ledger(l)
    command='python3 -c "import base64;exec(base64.b64decode(\''+base64.b64encode(CLEANUP.encode()).decode()+'\'))"'
    p=subprocess.run(['rtk','proxy','ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','100.77.149.83',command],
                     input=json.dumps(verify),capture_output=True,text=True,timeout=500)
    write_new(ACCOUNT/'remote-cleanup-transport-v1.json',dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    assert p.returncode==0,'Preserve failure; do not broaden cleanup paths'
    result=json.loads(p.stdout);write_new(PUBLIC/'remote-cleanup-v1.json',result)
    l=json.loads((ACCOUNT/'ledger.json').read_text());b=next(b for b in l['reservations'] if b['id']=='remote-cleanup-v1')
    b.update(status='PASS_EXACT_OWNED_CLEANUP',measured_remote_control_cpu_seconds=result['remote_control_cpu_seconds'])
    l['active_jobs'].remove('remote-cleanup-v1');save_ledger(l)
    print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['fetch','cleanup']);a=p.parse_args()
    fetch() if a.action=='fetch' else cleanup()
