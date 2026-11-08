"""Bounded sequential continuation after the running branch stage; stop on any error."""
import json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
TASK=ROOT/'.local/m2-costed-20261108-v2'


def write(value):
    path=TASK/'pipeline-status.json';tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)


def main():
    # This enclosing limit includes the four remaining 500-second stage controllers
    # and their CLI children, not four additional utility allocations.
    guard=OrchestrationGuard(TASK/'remaining-pipeline-resource.json',2000,'2026-11-12T08:17:29Z')
    try:
        write({'status':'WAITING_FOR_BRANCH','final_outcomes_opened':False})
        limit=time.monotonic()+3600
        while not (TASK/'branch-summary.json').exists():
            resource=json.loads((TASK/'branch-orchestration-resource.json').read_text())
            assert resource['status']=='RUNNING','BRANCH_STAGE_STOPPED'
            assert time.monotonic()<limit,'BRANCH_WAIT_LIMIT'
            time.sleep(1)
        assert json.loads((TASK/'branch-summary.json').read_text())['status']=='PASS_COMPLETE_STAGE'
        for script,arg in [('m2c_fit_artifacts_v2.py','gates'),('m2c_run_study_v2.py','tuning'),
          ('m2c_fit_artifacts_v2.py','controls'),('m2c_run_study_v2.py','main'),
          ('m2c_run_study_v2.py','ablation'),('m2c_run_study_v2.py','transfer')]:
            write({'status':'RUNNING','step':arg,'script':script,'final_outcomes_opened':False})
            print(json.dumps({'pipeline_step':arg,'status':'STARTING'}),flush=True)
            completed=subprocess.run(['rtk','python','tools/'+script,arg],cwd=ROOT,timeout=20000)
            assert completed.returncode==0,'PIPELINE_STEP_FAILED:'+arg
        write({'status':'PASS_COMPLETE_FIXED_M2_MATRIX','next':'full return, audit, aggregate analysis, cleanup and owner report',
          'final_outcomes_opened':False,'m3_released':False,'finished_utc':datetime.now(timezone.utc).isoformat()})
        guard.finish('PASS')
    except BaseException as e:
        write({'status':'STOPPED_RETAINED_FAILURE','error':str(e)[:300],'final_outcomes_opened':False})
        guard.finish('FAIL_PIPELINE');raise


if __name__=='__main__':main()
