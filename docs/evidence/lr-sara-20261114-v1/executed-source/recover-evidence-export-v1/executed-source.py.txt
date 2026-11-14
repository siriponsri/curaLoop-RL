"""Delivery-only Python 3.10 hash compatibility repair; scientific stop unchanged."""
import base64,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,digest,reserve,settle,write_new
from tools.sara_transport_v1 import invoke

REMOTE=r'''
import hashlib,json,os,resource,subprocess,sys
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1');out=t.parent/(t.name+'-export')
assert hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
v=json.loads(subprocess.check_output(['docker','inspect','curaloop-sara-owned-export-v1'],text=True))[0]
assert not v['State']['Running'] and v['State']['ExitCode']==1
assert "module 'hashlib' has no attribute 'file_digest'" in (out/'container-stderr.log').read_text()
assert not (out/'owned-manifest.json').exists() and not (out/'owned-return.tar.gz').exists()
source=(out/'export.py').read_text();old="def sha(p):\n with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()"
new="def sha(p):\n h=hashlib.sha256()\n with p.open('rb') as f:\n  while True:\n   block=f.read(1024**2)\n   if not block:break\n   h.update(block)\n return h.hexdigest()"
assert source.count(old)==1;source=source.replace(old,new);compile(source,'export-compatible-v2.py','exec')
path=out/'export-compatible-v2.py'
with path.open('x') as f:f.write(source)
name='curaloop-sara-owned-export-v2'
cmd=['docker','create','--name',name,'--label','curaloop.task=lr-sara-20261114-v1','--network=none','--cpus=1','--memory=2g','--memory-swap=2g',
 '--pids-limit=32','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',
 '--mount',f'type=bind,source={t},target=/source,readonly','--mount',f'type=bind,source={out},target=/return',
 'sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d','python','/return/export-compatible-v2.py']
x=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
(out/'create-receipt-v2.json').write_text(json.dumps({'exit_code':x.returncode,'stdout':x.stdout,'stderr':x.stderr}));assert x.returncode==0
ins=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
(out/'container-admission-v2.json').write_text(json.dumps({'id':ins['Id'],'image':ins['Image'],'host_config':ins['HostConfig']},indent=2))
assert ins['HostConfig']['NanoCpus']==1000000000 and not ins['HostConfig']['DeviceRequests'] and ins['HostConfig']['ReadonlyRootfs']
subprocess.run(['docker','start',name],check=True,capture_output=True,timeout=15)
try:wait=subprocess.run(['docker','wait',name],capture_output=True,text=True,timeout=5500)
except subprocess.TimeoutExpired:
 subprocess.run(['docker','kill',name],capture_output=True,timeout=15);raise
log=subprocess.run(['docker','logs',name],capture_output=True,timeout=15)
(out/'container-stdout-v2.log').write_bytes(log.stdout);(out/'container-stderr-v2.log').write_bytes(log.stderr)
assert wait.stdout.strip()=='0',log.stderr.decode(errors='replace')[-1000:]
result=json.loads((out/'export-result.json').read_text());result.update(export_root=str(out),source_root=str(t),container_name=name,
 remote_host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
 recovery_scope='Delivery only; original failed exporter and logs retained; no scientific retry')
print(json.dumps(result))
'''

def main():
 authority('analysis_return')
 settle('remote-owned-export-v1','FAIL_DELIVERY_HASHLIB_PYTHON310_COMPATIBILITY',measured_cpu_seconds='NOT_ESTABLISHED',scientific_execution=False)
 reserve('remote-owned-export-v2','analysis_return',6000,remote=True,scope='Delivery-only compatible hash loop; same read-only source tree, no reference/agent/correction rerun')
 value=invoke(REMOTE,{'release_sha256':digest(RELEASE)},timeout=5700);write_new(ACCOUNT/'export-recovery-transport-v1.json',value)
 assert value['exit_code']==0,value['stderr']
 result=json.loads(value['stdout']);write_new(ACCOUNT/'export-receipt-v2.json',result)
 settle('remote-owned-export-v2','PASS_FULL_EXPORT_RECOVERED',measured_export_container_cpu_seconds=result['export_container_cpu_seconds'],measured_remote_host_process_cpu_seconds=result['remote_host_process_cpu_seconds'])
 print(json.dumps(result))

if __name__=='__main__':main()
