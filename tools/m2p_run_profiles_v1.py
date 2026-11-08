"""Run the frozen synthetic matrix serially; preserve every failure and stop on censoring."""
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'.local/m2-cpu-profile-20261108-v1'


def call(args):
    began=datetime.now(timezone.utc).isoformat()
    r=subprocess.run(['rtk','python',*args],cwd=ROOT,capture_output=True,text=True,timeout=330)
    record={'command':['rtk','python',*args],'start_utc':began,'end_utc':datetime.now(timezone.utc).isoformat(),
            'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
    with (TASK/'orchestration-records.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
    return r


def main():
    assert json.loads((TASK/'jobs/checks-v1/result.json').read_text())['status']=='PASS_PROFILE_INSTRUMENTATION_CHECKS'
    frozen=json.loads((TASK/'profile-freeze-v1.json').read_text());completed=[]
    for entry in frozen['order']:
        name=entry['job']
        r=call(['tools/m2p_admin_v1.py','reserve',str(TASK/entry['spec'])]);assert r.returncode==0,r.stderr[-1000:]
        run=call(['tools/m2p_remote_v1.py','profile',name])
        resource=TASK/'jobs'/name/'resource.json'
        if resource.exists():
            r=call(['tools/m2p_admin_v1.py','settle',name]);assert r.returncode==0,r.stderr[-1000:]
        result_path=TASK/'jobs'/name/'result.json'
        result=json.loads(result_path.read_text()) if result_path.exists() else {'status':'FAIL_NO_RESULT'}
        summary={'job':name,'status':result['status'],'cpu_seconds':result.get('scientific_cpu_seconds'),
                 'startup_cpu_seconds':result.get('startup_cpu_seconds')}
        completed.append(summary);print(json.dumps(summary),flush=True)
        if run.returncode!=0 or result['status']!='PASS_COMPLETE_SYNTHETIC_PROFILE':break
    status='PASS_COMPLETE_12_PROFILES' if len(completed)==12 and all(c['status']=='PASS_COMPLETE_SYNTHETIC_PROFILE' for c in completed) else 'STOP_RETAINED_PROFILE_FAILURE'
    with (TASK/'matrix-run-summary.json').open('x',encoding='utf-8') as f:json.dump({'status':status,'profiles':completed,'biological_data_accessed':False},f,indent=2);f.write('\n')
    print(json.dumps({'status':status,'completed':len(completed)}),flush=True)


if __name__=='__main__':main()
