"""Three bounded remote slots, serial ledger ownership, immediate admission stop."""
import concurrent.futures as futures
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
TASK=ROOT/'.local/m2-costed-20261108-v2'


def run(args):
    r=subprocess.run(['rtk','python',*args],cwd=ROOT,capture_output=True,text=True,timeout=200)
    with (TASK/'calibration-orchestration.jsonl').open('a',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps({'command':['rtk','python',*args],'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})+'\n')
    return r


def main():
    g=OrchestrationGuard(TASK/'calibration-orchestration-resource.json',240,'2026-11-12T08:17:29Z')
    records=[];failed=False
    try:
        order=json.loads((TASK/'technical-freeze-v1.json').read_text())['contexts']
        for index in range(0,len(order),3):
            batch=order[index:index+3]
            for e in batch:
                r=run(['tools/m2c_admin_v2.py','reserve',str(TASK/e['spec'])]);assert r.returncode==0,r.stderr[-1000:]
            with futures.ThreadPoolExecutor(max_workers=3) as pool:
                outputs=list(pool.map(lambda e:run(['tools/m2c_remote_v2.py','calibration',e['job']]),batch))
            for e,r in zip(batch,outputs):
                job=TASK/'jobs'/e['job'];resource=job/'resource.json'
                if resource.exists():
                    settled=run(['tools/m2c_admin_v2.py','settle',e['job']]);assert settled.returncode==0,settled.stderr[-1000:]
                path=job/'result.json';result=json.loads(path.read_text()) if path.exists() else {'status':'FAIL_NO_RESULT'}
                row={'job':e['job'],'status':result['status'],'scientific_cpu_seconds':result.get('scientific_cpu_seconds'),
                     'derived_cap_seconds':result.get('derived_cap_seconds'),'envelope':result.get('admission_envelope_seconds')}
                records.append(row);print(json.dumps(row),flush=True)
                failed=failed or r.returncode!=0 or row['status']!='PASS_SYNTHETIC_CONTEXT'
            if failed:break
        result={'status':'PASS_84_REMAINING_CONTEXTS' if len(records)==84 and not failed else 'STOP_TECHNICAL_ADMISSION',
                'contexts':records,'biological_labels_decoded':False}
        with (TASK/'technical-run-summary.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
        g.finish('PASS' if not failed else 'FAIL_ADMISSION');print(json.dumps({'status':result['status'],'contexts':len(records)}),flush=True)
    except BaseException:
        g.finish('FAIL_ORCHESTRATION');raise


if __name__=='__main__':main()
