"""Failed-gate settlement and lossless owned-file return preparation; no science."""
import base64,json,subprocess
from datetime import datetime,timezone
from tools.sar30_control_v1 import ACCOUNT, PUBLIC, authority, digest, write_new, save_ledger

REMOTE=r'''
import hashlib,json,os,resource,signal,tarfile,time
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(3000,3000));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))});signal.alarm(1800)
t=Path.home()/'curaloop-tasks/lr-sar30-qual-20261114-v1'
assert t.resolve()==Path('/home/chaw/curaloop-tasks/lr-sar30-qual-20261114-v1') and not t.is_symlink()
manifest={}
for p in sorted(t.rglob('*')):
 if p.is_symlink():raise RuntimeError('Unexpected symlink: preserve and inspect without following')
 if p.is_file():
  with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
  manifest[p.relative_to(t).as_posix()]={'bytes':p.stat().st_size,'sha256':h}
assert sum(v['bytes'] for v in manifest.values())<100*1024**3
m=t.parent/'lr-sar30-qual-20261114-v1-return-manifest.json'
with m.open('x') as f:json.dump(manifest,f,indent=2)
bundle=t.parent/'lr-sar30-qual-20261114-v1-return.tar.gz'
assert not bundle.exists()
with tarfile.open(bundle,'w:gz',compresslevel=1) as z:
 for p in sorted(t.rglob('*')):
  if p.is_file():z.add(p,arcname=p.relative_to(t).as_posix(),recursive=False)
with bundle.open('rb') as f:bundle_sha=hashlib.file_digest(f,'sha256').hexdigest()
errors={}
for name in ['install-lineage-02.log','install-lineage-03.log','import-private-22.log','import-private-26.log']:
 p=t/'control'/name
 if p.exists():errors[name]=p.read_text(errors='replace')[-6500:]
print(json.dumps({'status':'PASS_OWNED_EXPORT_PREPARED','files':len(manifest),'bytes':sum(v['bytes'] for v in manifest.values()),
 'bundle_bytes':bundle.stat().st_size,'bundle_sha256':bundle_sha,'bundle_path':str(bundle),'manifest_path':str(m),
 'remote_export_process_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
 'error_log_tails':errors}))
'''

def main():
    r,l=authority()
    snapshots=sorted((ACCOUNT/'monitor').glob('snapshot-*.json'))
    state=json.loads(snapshots[-1].read_text())
    assert state['state']['Running'] is False and state['early-stop.json']['status']=='FAIL_ENVIRONMENT_UPPER_BOUND'
    record=next(b for b in l['reservations'] if b['id']=='remote-environment-v1')
    record.update(status='FAIL_GATE_WORKER_STOPPED',measured_container_cpu_seconds=state['resources-final.json']['aggregate_cpu_seconds'],
                  measured_probe_cpu_seconds=sum(x['resources']['aggregate_cpu_seconds'] for x in state['guard-probes.json']['probes']))
    l['active_jobs'].remove('remote-environment-v1');l['status']='ACTIVE_CLOSEOUT_FAILED_ENVIRONMENT'
    write_new(PUBLIC/'qualification-stop-v1.json',dict(status='FAIL_ENVIRONMENT_UPPER_BOUND',
        invalid_locked_ids=state['early-stop.json']['invalid_locked_ids'],optimistic_locked_upper_bound=23,required=24,
        stopped_container=state['state'],guard_probes=state['guard-probes.json'],resources=state['resources-final.json'],
        native_reference_execution='NOT_RUN',agent_execution='NOT_RUN',gpu_allocated_seconds=0,
        benchmark_scientific_correctness='NOT_ESTABLISHED',result_scope='Failure of the fixed local qualification recipe, not proof these benchmark tasks are intrinsically invalid'))
    assert sum(b['cpu_seconds'] for b in l['reservations'] if b['stage']=='report_delivery')+3000<=r['stage_caps_seconds']['report_delivery']
    assert sum(b['cpu_seconds'] for b in l['reservations'])+3000<=r['cpu_cap_seconds']
    l['reservations'].append(dict(id='remote-return-v1',stage='report_delivery',cpu_seconds=3000,gpu_allocated_seconds=0,status='RESERVED_REMOTE_RETURN'))
    l['active_jobs'].append('remote-return-v1');save_ledger(l)
    command='python3 -c "import base64;exec(base64.b64decode(\''+base64.b64encode(REMOTE.encode()).decode()+'\'))"'
    p=subprocess.run(['rtk','proxy','ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',
                      '100.77.149.83',command],capture_output=True,text=True,timeout=1900)
    write_new(ACCOUNT/'remote-export-transport-v1.json',dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    assert p.returncode==0,'No export replay; inspect exact owned state'
    result=json.loads(p.stdout);write_new(ACCOUNT/'remote-export-receipt-v1.json',result)
    l=json.loads((ACCOUNT/'ledger.json').read_text());b=next(b for b in l['reservations'] if b['id']=='remote-return-v1')
    b.update(status='PASS_EXPORT_READY',measured_remote_process_cpu_seconds=result['remote_export_process_cpu_seconds'])
    l['active_jobs'].remove('remote-return-v1');save_ledger(l)
    print(json.dumps(result))

if __name__=='__main__':main()
