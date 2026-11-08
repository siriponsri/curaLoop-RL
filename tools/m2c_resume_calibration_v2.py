"""Resume frozen calibration through in-process booking and batched SSH dispatch."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,batch
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
TASK=ROOT/'.local/m2-costed-20261108-v2'


def main():
    guard=OrchestrationGuard(TASK/'calibration-resume-resource.json',120,'2026-11-12T08:17:29Z')
    overrides=json.loads((TASK/'calibration-retry-overrides.json').read_text());order=json.loads((TASK/'technical-freeze-v1.json').read_text())['contexts']
    completed=[];pending=[]
    try:
        for entry in order:
            resolved=dict(entry);resolved.update(overrides.get(entry['job'],{}))
            path=TASK/'jobs'/resolved['job']/'result.json'
            if path.exists():
                result=json.loads(path.read_text());assert result['status']=='PASS_SYNTHETIC_CONTEXT' and result['spec']==entry['arguments']
                completed.append({'original_job':entry['job'],'job':resolved['job'],'status':result['status']})
            else:pending.append(resolved)
        failed=False
        for i in range(0,len(pending),3):
            selected=pending[i:i+3]
            for e in selected:admin_call('reserve',TASK/e['spec'])
            output=batch([e['job'] for e in selected])
            for e in selected:
                admin_call('settle',e['job'])
                result=json.loads((TASK/'jobs'/e['job']/'result.json').read_text())
                row={'job':e['job'],'status':result['status'],'scientific_cpu_seconds':result.get('scientific_cpu_seconds'),
                     'derived_cap_seconds':result.get('derived_cap_seconds')}
                completed.append(row);print(json.dumps(row),flush=True)
                failed=failed or result['status']!='PASS_SYNTHETIC_CONTEXT'
            if failed:break
        summary={'status':'PASS_84_REMAINING_CONTEXTS' if len(completed)==84 and not failed else 'STOP_TECHNICAL_ADMISSION',
                 'contexts':completed,'retained_orchestration_failures':3,'same_context_retries':3,'biological_labels_decoded':False}
        with (TASK/'technical-run-summary.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(summary,f,indent=2);f.write('\n')
        guard.finish('PASS' if not failed else 'FAIL_ADMISSION');print(json.dumps({'status':summary['status'],'contexts':len(completed)}),flush=True)
    except BaseException:
        guard.finish('FAIL_ORCHESTRATION');raise


if __name__=='__main__':main()
