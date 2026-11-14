"""Continue only a proven-never-started guard; first actual dependency imports."""
import base64,json
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,reserve,settle,save,write_new,digest
from tools.sara_transport_v1 import invoke

REMOTE=r'''
import base64,hashlib,importlib.util,json,os,resource,subprocess,sys,time,traceback
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/lr-sara-20261114-v1')
assert hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
(t/'diagnostic-first-start-worker.py').write_bytes(base64.b64decode(p['remote_source_b64']))
assert not (t/'leases/diagnosis-v1').exists() and not (t/'leases/probe-cpu').exists()
v=json.loads(subprocess.check_output(['docker','inspect','curaloop-sara-probe-wall'],text=True))[0]
assert v['State']['Status']=='created' and not v['State']['Running'] and v['State']['Pid']==0 and v['State']['StartedAt'].startswith('0001-')
(t/'guard-never-started-proof-v1.json').write_text(json.dumps(v['State'],indent=2))
old=t/'leases/probe-wall/limits.json';(t/'leases/probe-wall/limits-before-first-start.json').write_bytes(old.read_bytes())
limits=json.loads(old.read_text());limits['deadline_epoch']=time.time()+3;old.write_text(json.dumps(limits,indent=2))
def command(args,timeout):
 r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if r.returncode:raise RuntimeError(json.dumps({'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}))
 return r
try:
 command(['docker','start','curaloop-sara-probe-wall'],15)
 w=command(['docker','wait','curaloop-sara-probe-wall'],30)
 assert w.stdout.strip()=='124'
 wall=json.loads((t/'leases/probe-wall/resources-final.json').read_text());assert wall['stop_reason']=='WALL_DEADLINE'
 spec=importlib.util.spec_from_file_location('owned_runtime',t/'docker-runtime-v1.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
 cpu=rt.run('probe-cpu','while True: pass\n',cpu=7,wall=30);assert cpu['state']['ExitCode']==124 and cpu['resources']['stop_reason']=='CPU_CAP'
 source=base64.b64decode(p['diagnostic_source_b64']);assert hashlib.sha256(source).hexdigest()==p['diagnostic_source_sha256']
 # Read the already frozen diagnostic PROGRAM constant without rerunning its main.
 import ast
 tree=ast.parse(source.decode());program=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='PROGRAM' for x in n.targets))
 receipt=rt.run('diagnosis-v1',program,cpu=180,wall=200,mounts=[(t/'retained-env','/retained-env',True)])
 diagnosis=json.loads((t/'leases/diagnosis-v1/diagnosis.json').read_text())
 result={'status':'FIRST_DIAGNOSTIC_EXECUTION_COMPLETED','prior_guard_never_started':True,
  'launcher_change':'Host virtual-address ceiling 1 GiB to 8 GiB, within approved 32 GiB aggregate; original Docker settings unchanged; cause of CLI exit 2 not proven',
  'guard_probes':{'wall':wall,'cpu':cpu},'container':receipt,'diagnosis':diagnosis,
  'remote_host_process_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime}
 (t/'diagnosis-receipt-v1.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
except BaseException as e:
 (t/'diagnostic-first-start-failure.json').write_text(json.dumps({'error':str(e),'traceback':traceback.format_exc()}));raise
'''

def main():
 r,l=authority('technical')
 proof=json.loads((ACCOUNT/'guard-start-inspection-v1.json').read_text())
 assert not proof['diagnosis_program_exists'] and proof['curaloop-sara-probe-wall']['state']['StartedAt'].startswith('0001-')
 assert 'remote-diagnosis-v1' in l['active_jobs']
 settle('remote-diagnosis-v1','FAIL_PRE_IMPORT_LAUNCHER_NO_CONTAINER_START',measured_cpu_seconds='NOT_ESTABLISHED',diagnostic_imports_executed=0)
 reserve('remote-diagnostic-first-start-v1','technical',600,remote=True,scope='First start of proven Created/Pid0 guard, CPU probe and sole actual imports 22/26; no native/reference attempts')
 source=ROOT/'tools/sara_diagnose_worker_v1.py'
 transport=invoke(REMOTE,dict(diagnostic_source_b64=base64.b64encode(source.read_bytes()).decode(),diagnostic_source_sha256=digest(source),
                            release_sha256=digest(RELEASE),remote_source_b64=base64.b64encode(REMOTE.encode()).decode()),timeout=350)
 write_new(ACCOUNT/'diagnostic-first-start-transport-v1.json',transport);assert transport['exit_code']==0,transport['stderr']
 result=json.loads(transport['stdout'])
 write_new(PUBLIC/'dependency-diagnosis-v1.json',result)
 l=json.loads((ACCOUNT/'ledger.json').read_text())
 for case in result['diagnosis']['cases']:l['attempts']['diagnostic_imports'][str(case['instance_id'])].update(status='CAPTURED',result=case['result']['status'],actual_import_attempts=1)
 save(l)
 settle('remote-diagnostic-first-start-v1','PASS_SOLE_IMPORT_CAPTURE',measured_remote_host_process_cpu_seconds=result['remote_host_process_cpu_seconds'],measured_container_cpu_seconds=result['container']['resources']['aggregate_cpu_seconds'])
 print(json.dumps(result))

if __name__=='__main__':
 # The transport executes REMOTE, not this local orchestration entrypoint.
 main()
