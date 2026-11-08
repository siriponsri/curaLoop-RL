"""Retain a proven not-dispatched SSH batch and book identical-context recovery."""
import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,ssh_script
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2';REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'


def main():
    probe=json.loads((TASK/'tuning-recovery-probe-v1.json').read_text());mapping={}
    ledger=json.loads((TASK/'ledger.json').read_text());active=[j['job'] for j in ledger['jobs'] if j['state']=='RESERVED']
    assert set(active)=={r['job'] for r in probe['results']} and len(active)==3
    new(TASK/'pipeline-status-stopped-v1.json',json.loads((TASK/'pipeline-status.json').read_text()))
    for r in probe['results']:
        assert r['job_exists']is False and r['unit_state']['LoadState']=='not-found'
        name=r['job'];spec=json.loads((TASK/'specs'/(name+'.json')).read_text());assert spec['handler']=='tuning'
        new(TASK/'jobs'/name/'dispatch-failure.json',{'status':'RETAINED_NOT_DISPATCHED_TRANSPORT_FAILURE',
          'error':'SSH connect to 100.77.149.83 port 22: Connection timed out','fresh_probe':r,
          'completed_tuning_units_before_failure':174,'final_outcomes_opened':False})
        new(TASK/'jobs'/name/'resource.json',{'schema':'curaloop.m2_costed.resources.v2','attempt':name,
          'host':'dr-train','status':'FAIL','cpu_seconds':0,'reservation_seconds':spec['reservation_seconds'],
          'cpu_measurement_scope':'NOT_MEASURED_NO_REMOTE_WORKER_DISPATCHED; fresh exact job/unit absence verified',
          'source_error':'SSH_CONNECT_TIMEOUT','reservation_retained_in_full':True})
        admin_call('settle',name)
        retry=copy.deepcopy(spec);retry['job']=name+'-r1';retry['bucket']='analysis_return_cleanup_retry_delivery'
        new(TASK/'specs'/(retry['job']+'.json'),retry);mapping[name]=retry['job']
    new(TASK/'execution-retry-resolution-v1.json',{'schema':'curaloop.m2_costed.retry_resolution.v2','mapping':mapping,
      'method_seed_input_cap_cpu_unchanged':True,'retained_failed_attempts':3,'utc':datetime.now(timezone.utc).isoformat()})
    matrix=json.loads((TASK/'execution-matrix-v1.json').read_text())
    for e in matrix['entries']:
        if e['job']in mapping:e['original_job']=e['job'];e['job']=mapping[e['job']]
    new(TASK/'control-fit-matrix-v2.json',matrix)
    raw=(TASK/'control-fit-matrix-v2.json').read_bytes()
    import base64,hashlib
    code='''import base64,hashlib,json,os,resource
from pathlib import Path
os.sched_setaffinity(0,{69});resource.setrlimit(resource.RLIMIT_CPU,(20,20));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
root=Path(__ROOT__);assert root.resolve()==root and root==Path.home()/'curaloop-tasks/m2-costed-20261108-v2'
raw=base64.b64decode(__RAW__);assert hashlib.sha256(raw).hexdigest()==__SHA__
with (root/'control-fit-matrix-v2.json').open('xb') as f:f.write(raw)
print(json.dumps({'status':'PASS_IDENTICAL_CONTEXT_RETRY_MATRIX','sha256':hashlib.sha256(raw).hexdigest()}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__RAW__',repr(base64.b64encode(raw).decode())).replace('__SHA__',repr(hashlib.sha256(raw).hexdigest()))
    new(TASK/'control-fit-matrix-stage-v2.json',ssh_script(code,60))
    path=TASK/'specs/orchestration-recovery-v2.json'
    new(path,{'job':'orchestration-recovery-v2','host':'local','handler':'orchestration_recovery','bucket':'engineering_guards',
      'reservation_seconds':2000,'wall_seconds':25000,'memory_bytes':536870912,'arguments':{
       'scope':'remaining tuning, frozen controls, main+ablations and transfer; same scientific units, no outcome inspection'},
      'guard_cpu_seconds':1999.5})
    admin_call('reserve',path);print(json.dumps({'status':'PASS_RECOVERY_BOOKED','mapping':mapping,'additional_orchestration_envelope':2000}))


if __name__=='__main__':main()
