"""Bounded continuation after a retained local utility-controller limit."""
import json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
from tools.m2c_batch_v2 import admin_call
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2'


def write(value):
    value.update(pid=os.getpid(),updated_utc=datetime.now(timezone.utc).isoformat())
    path=TASK/'pipeline-status.json';tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');tmp.replace(path)


def main():
    permit=json.loads((TASK/'jobs/orchestration-recovery-v5/permit.json').read_text())
    guard=OrchestrationGuard(TASK/'durable-pipeline-resource-v5.json',1499.5,permit['deadline_utc'],wall_seconds=permit['wall_seconds']);status='FAIL'
    new(TASK/'durable-pipeline-pid-v5.json',{'pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat(),
      'cpu_limit_seconds':1499.5,'memory_bytes':536870912,'project_deadline_utc':permit['deadline_utc'],'wall_limit_seconds':permit['wall_seconds']})
    try:
        for script,arg in [('m2c_resume_main_v5.py',None),('m2c_run_study_v2.py','ablation'),('m2c_run_study_v2.py','transfer')]:
            write({'status':'RUNNING','step':arg or 'main-resume','script':script,'recovery_attempt':5,'final_outcomes_opened':False})
            print(json.dumps({'pipeline_step':arg or 'main-resume','status':'STARTING'}),flush=True)
            completed=subprocess.run(['rtk','python','tools/'+script]+([arg] if arg else []),cwd=ROOT,timeout=15000)
            assert completed.returncode==0,'PIPELINE_STEP_FAILED:'+str(arg)
        write({'status':'PASS_COMPLETE_FIXED_M2_MATRIX','next':'full return, audit, analysis, cleanup, owner report',
          'final_outcomes_opened':False,'m3_released':False,'finished_utc':datetime.now(timezone.utc).isoformat(),'recovery_attempt':5})
        status='PASS';guard.finish('PASS')
    except BaseException as exc:
        write({'status':'STOPPED_RETAINED_FAILURE','error':str(exc)[:300],'recovery_attempt':5,'final_outcomes_opened':False})
        guard.finish('FAIL_PIPELINE');raise
    finally:
        receipt=json.loads((TASK/'durable-pipeline-resource-v5.json').read_text())
        new(TASK/'jobs/orchestration-recovery-v5/resource.json',{'schema':'curaloop.m2_costed.resources.v2','attempt':'orchestration-recovery-v5',
          'host':'local','status':status,'cpu_seconds':receipt['aggregate_cpu_seconds'],'reservation_seconds':1500,
          'measurement_scope':'aggregate Windows Job including child controllers and SSH clients'})
        admin_call('settle','orchestration-recovery-v5')


if __name__=='__main__':main()
