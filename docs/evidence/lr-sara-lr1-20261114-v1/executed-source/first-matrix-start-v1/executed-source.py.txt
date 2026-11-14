"""Complete missing owned lease-directory bookkeeping before the first matrix start."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.saralr1_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,save,settle,stop,write_new
from tools.saralr1_transport_v1 import invoke

REMOTE=r'''
import hashlib,importlib.util,json,os,resource,subprocess,sys,textwrap
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(180,180));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/lr-sara-lr1-20261114-v1')
assert t.resolve()==t and hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
ids=subprocess.check_output(['docker','ps','-aq','--filter','label=curaloop.task=lr-sara-lr1-20261114-v1'],text=True).split()
assert not ids and not (t/'leases').exists() and not (t/'engineering-outcome.json').exists()
matrix=json.loads((t/'engineering-matrix.json').read_text())
assert hashlib.sha256((t/'code/saralr1_overlay_v1.py').read_bytes()).hexdigest()==matrix['patch_source_sha256']
assert hashlib.sha256((t/'code/saralr1_acceptance_program_v1.py').read_bytes()).hexdigest()==matrix['acceptance_source_sha256']
assert hashlib.sha256((t/'code/saralr1_runtime_v1.py').read_bytes()).hexdigest()==matrix['runtime_source_sha256']
proof=dict(status='PROVEN_ZERO_CONTAINERS_ZERO_MATRIX_STARTS',owned_containers=[],lease_directory_existed=False,
 patch_program_and_runtime_unchanged=True,bookkeeping_action='Create previously omitted task-owned leases parent; no patch or recipe modification')
(t/'first-start-proof.json').write_text(json.dumps(proof,indent=2));(t/'leases').mkdir()
spec=importlib.util.spec_from_file_location('runtime',t/'code/saralr1_runtime_v1.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
source=(t/'engineering-worker.py').read_text()
tail=textwrap.dedent(source[source.index(' # Probe actual stop mechanisms'):source.index("\nif __name__=='__main__'")])
assert 't.mkdir()' not in tail and "rt.run('engineering-acceptance-v1'" in tail
exec(compile(tail,'unchanged-engineering-worker-tail','exec'))
'''

def main():
 r,l=authority('engineering');prior=json.loads((ACCOUNT/'engineering-transport-v1.json').read_text())
 assert "FileNotFoundError" in prior['stderr'] and '/leases/wall-probe-v1' in prior['stderr']
 assert l['active_jobs']==['remote-engineering-v1', 'first-matrix-start-v1'] or set(l['active_jobs'])=={'remote-engineering-v1','first-matrix-start-v1'}
 value=invoke(REMOTE,dict(release_sha256=l['release_sha256']),timeout=500);write_new(ACCOUNT/'first-matrix-start-transport-v1.json',value)
 assert value['exit_code']==0,value
 result=json.loads(value['stdout']);write_new(PUBLIC/'engineering-acceptance-v1.json',result)
 write_new(PUBLIC/'pre-matrix-bookkeeping-incident-v1.json',dict(status='RECORDED_PRE_MATRIX_LAUNCH_ERROR',prior_failure=prior,
  first_execution_continuation=True,patch_and_matrix_changed=False,actual_matrix_executions=1,
  explanation='Missing owned leases parent prevented all Docker creation and tests; no acceptance result was retried'))
 settle('remote-engineering-v1',result['status'],measured_remote_final_host_cpu_seconds=result['remote_host_process_cpu_seconds'],prior_host_cpu_seconds='NOT_ESTABLISHED')
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['attempts']['engineering'].update(status=result['status'],actual_matrix_executions=1,bootstrap_failure_retained=True);save(l)
 if result['status']!='PASS_ENGINEERING_ACCEPTANCE':stop('NO_GO_ENGINEERING_ACCEPTANCE','Frozen first actual acceptance failed; no repeat or patch amendment')
 else:l['status']='ACTIVE_PREPARATION';save(l)
 print(json.dumps(dict(status=result['status'],tests=len((result.get('result') or {}).get('tests',[])),native_references=0,provider_calls=0)))
if __name__=='__main__':main()
