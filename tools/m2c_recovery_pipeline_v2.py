"""New bounded orchestration attempt, preserving the first stopped pipeline."""
import json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
from tools.m2c_batch_v2 import admin_call
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2'


def write(value):
    path=TASK/'pipeline-status.json';tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)


def main():
    permit=json.loads((TASK/'jobs/orchestration-recovery-v2/permit.json').read_text())
    guard=OrchestrationGuard(TASK/'recovery-pipeline-resource-v2.json',1999.5,permit['deadline_utc']);status='FAIL'
    try:
        for script,arg in [('m2c_resume_study_v2.py',None),('m2c_fit_artifacts_v2.py','controls'),
          ('m2c_run_study_v2.py','main'),('m2c_run_study_v2.py','ablation'),('m2c_run_study_v2.py','transfer')]:
            write({'status':'RUNNING','step':arg or 'tuning-resume','script':script,'recovery_attempt':2,'final_outcomes_opened':False})
            print(json.dumps({'pipeline_step':arg or 'tuning-resume','status':'STARTING'}),flush=True)
            completed=subprocess.run(['rtk','python','tools/'+script]+([arg] if arg else []),cwd=ROOT,timeout=20000)
            assert completed.returncode==0,'PIPELINE_STEP_FAILED:'+str(arg)
        write({'status':'PASS_COMPLETE_FIXED_M2_MATRIX','next':'full return, audit, analysis, cleanup, owner report',
          'final_outcomes_opened':False,'m3_released':False,'finished_utc':datetime.now(timezone.utc).isoformat(),'recovery_attempt':2})
        status='PASS';guard.finish('PASS')
    except BaseException as e:
        write({'status':'STOPPED_RETAINED_FAILURE','error':str(e)[:300],'recovery_attempt':2,'final_outcomes_opened':False})
        guard.finish('FAIL_PIPELINE');raise
    finally:
        receipt=json.loads((TASK/'recovery-pipeline-resource-v2.json').read_text())
        new(TASK/'jobs/orchestration-recovery-v2/resource.json',{'schema':'curaloop.m2_costed.resources.v2','attempt':'orchestration-recovery-v2',
          'host':'local','status':status,'cpu_seconds':receipt['aggregate_cpu_seconds'],'reservation_seconds':2000,
          'measurement_scope':'aggregate Windows Job including all child controllers/CLI clients; no double counting child receipts'})
        admin_call('settle','orchestration-recovery-v2')


if __name__=='__main__':main()
