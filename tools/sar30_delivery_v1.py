"""Evidence-based completion audit and terminal settlement, no scientific execution."""
import argparse,ast,base64,json,subprocess
from datetime import datetime,timezone
from tools.sar30_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,digest,write_new,save_ledger

def audit():
    r,l=authority();checks={}
    failed=[k for k,v in r['preservation_pins'].items() if not (ROOT/k).is_file() or digest(ROOT/k)!=v]
    checks['all_109_preservation_pins']=len(r['preservation_pins'])==109 and not failed
    rows=json.loads((PUBLIC/'per-task-qualification-v1.json').read_text())
    summary=json.loads((PUBLIC/'qualification-summary-v1.json').read_text())
    freeze=json.loads((PUBLIC/'role-and-check-freeze-v1.json').read_text())
    envplan=json.loads((PUBLIC/'environment-plan-v1.json').read_text())
    checks['thirty_unique_tasks_retained']=len(rows)==30 and len({x['instance_id'] for x in rows})==30
    checks['metadata_split_before_processing']=next(b for b in l['reservations'] if b['id']=='role-freeze-v1')['finished_utc'] < next(b for b in l['reservations'] if b['id']=='static-audit-v1')['started_utc']
    checks['role_freeze_matches_environment']=envplan['role_freeze_sha256']==digest(PUBLIC/'role-and-check-freeze-v1.json')
    checks['four_development_twenty_six_locked']=sum(x['role']=='development' for x in rows)==4 and sum(x['role']=='locked_candidate' for x in rows)==26
    checks['native_and_agent_not_run']=all(x['native_score'] is None and x['native_reference_execution']=='NOT_RUN' and x['agent_execution']=='NOT_RUN' for x in rows)
    checks['failed_gate_not_relaxed']=summary['locked_optimistic_upper_bound']==23 and r['minimum_locked_native_valid_tasks']==24 and summary['status']=='NO_GO_FIXED_ENVIRONMENT_QUALIFICATION'
    checks['dependency_group_attempts_unique']=len(envplan['groups'])==len({g['name'] for g in envplan['groups']})
    returned=json.loads((PUBLIC/'owned-return-verification-v1.json').read_text())
    checks['full_local_return_verified']=returned['files']==50120 and digest(ACCOUNT/'remote-return-v1/owned-return.tar.gz')==returned['bundle_sha256']
    code="import json,subprocess;from pathlib import Path;p=Path('/home/chaw/curaloop-tasks/lr-sar30-qual-20261114-v1');r=subprocess.run(['docker','ps','-a','--filter','label=curaloop.task=lr-sar30-qual-20261114-v1','--format','{{.Names}}'],capture_output=True,text=True,timeout=15);print(json.dumps({'root_absent':not p.exists(),'owned_containers':r.stdout.splitlines(),'exit_code':r.returncode,'exports_absent':not (p.parent/(p.name+'-return.tar.gz')).exists() and not (p.parent/(p.name+'-return-manifest.json')).exists()}))"
    command='python3 -c "import base64;exec(base64.b64decode(\''+base64.b64encode(code.encode()).decode()+'\'))"'
    p=subprocess.run(['rtk','proxy','ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','100.77.149.83',command],capture_output=True,text=True,timeout=40)
    assert p.returncode==0,p.stderr
    remote=json.loads(p.stdout);write_new(PUBLIC/'fresh-remote-absence-v1.json',remote)
    checks['fresh_remote_absence']=remote['root_absent'] and remote['exports_absent'] and not remote['owned_containers'] and remote['exit_code']==0
    checks['no_actor_or_manuscript_authority']=not r['agent_inference_authorized'] and not r['manuscript_writing_authorized'] and r['model_download_cap_bytes']==0
    checks['cpu_gpu_caps']=sum(x['cpu_seconds'] for x in l['reservations'])+1800<=r['cpu_cap_seconds'] and sum(x['gpu_allocated_seconds'] for x in l['reservations'])==0
    checks['stage_caps']=all(sum(x['cpu_seconds'] for x in l['reservations'] if x['stage']==s)+(1800 if s=='report_delivery' else 0)<=v for s,v in r['stage_caps_seconds'].items())
    checks['elapsed_deadline']=datetime.now(timezone.utc)<datetime.fromisoformat(r['deadline_utc'])
    checks['required_owner_documents']=all((ROOT/'docs/08_agent_rd'/f).is_file() for f in ['LR_SAR30_QUALIFICATION_OWNER_REPORT_20261114.md','SAR30_HIGHER_IMPACT_DIRECTION_20261114.md'])
    snapshot=PUBLIC/'executed-source-v1';snapshot.mkdir(exist_ok=False)
    execution_map=[]
    for b in l['reservations']:
        if 'script' in b:
            source=ACCOUNT/'jobs'/b['id']/'executed-source.py.txt'
            assert digest(source)==b['script_sha256']
            dst=snapshot/(b['id']+'.py.txt');dst.write_bytes(source.read_bytes())
            execution_map.append(dict(id=b['id'],script=b['script'],status=b['status'],sha256=digest(dst),public_snapshot=dst.relative_to(ROOT).as_posix()))
    write_new(PUBLIC/'executed-source-map-v1.json',execution_map)
    syntax=[]
    for path in sorted((ROOT/'tools').glob('sar30_*.py')):
        tree=ast.parse(path.read_text(encoding='utf-8'))
        for node in tree.body:
            if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str) and any(isinstance(t,ast.Name) and t.id in {'REMOTE','SUPERVISOR','SETUP','CLEANUP'} for t in node.targets):
                compile(node.value.value,str(path),'exec')
        syntax.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path)))
    checks['worker_and_embedded_syntax']=bool(syntax)
    result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,preservation_failures=failed,
                final_source_identities=syntax,review_type='Implementer audit; not independent expert validation',
                comparison_results='NOT_RUN',manuscript='NOT_WRITTEN',checked_utc=datetime.now(timezone.utc).isoformat())
    write_new(PUBLIC/'completion-checks-v1.json',result)
    print(json.dumps(result))
    assert all(checks.values())

def settle():
    r,l=authority();assert not l['active_jobs']
    audit=json.loads((PUBLIC/'completion-checks-v1.json').read_text());assert audit['status']=='PASS'
    assert all((ROOT/k).is_file() and digest(ROOT/k)==v for k,v in r['preservation_pins'].items())
    assert all(b['id']!='delivery-administration-v1' for b in l['reservations'])
    l['reservations'].append(dict(id='delivery-administration-v1',stage='report_delivery',cpu_seconds=1800,gpu_allocated_seconds=0,
        status='RETAINED_UNMETERED_DELIVERY_ALLOWANCE',scope='Final preservation/link/index-byte verification, exact main commit/push and receipt; not whole-host measured CPU'))
    assert sum(x['cpu_seconds'] for x in l['reservations'])<=r['cpu_cap_seconds']
    assert all(sum(x['cpu_seconds'] for x in l['reservations'] if x['stage']==s)<=v for s,v in r['stage_caps_seconds'].items())
    l.update(status='CLOSED_NO_GO_FIXED_ENVIRONMENT_QUALIFICATION',closed_utc=datetime.now(timezone.utc).isoformat(),scientific_reruns=0,agent_calls=0,
             gpu_allocated_seconds=0,unused_balance_reusable=False)
    save_ledger(l)
    write_new(PUBLIC/'closed-resource-ledger-v1.json',l)
    summary=json.loads((PUBLIC/'qualification-summary-v1.json').read_text())
    final=dict(status='PASS_CLOSED_FAILED_GATE_DELIVERY_NOT_RESEARCH_SUCCESS',account_status=l['status'],active_jobs=[],
        release_sha256=digest(RELEASE),closed_private_ledger_sha256=digest(ACCOUNT/'ledger.json'),
        cpu_reserved_seconds=sum(x['cpu_seconds'] for x in l['reservations']),cpu_cap_seconds=r['cpu_cap_seconds'],
        gpu_allocated_seconds=0,gpu_cap_seconds=r['gpu_allocated_cap_seconds'],
        measured_guarded_local_job_cpu_seconds=sum(x.get('measured_cpu_seconds',0) for x in l['reservations']),
        measured_environment_and_probes_cpu_seconds=271.188213,
        aggregate_whole_host_cpu_seconds='NOT_ESTABLISHED',preservation_pins=len(r['preservation_pins']),preservation='PASS',
        qualification=summary['status'],native_reference_attempts=0,agent_calls=0,
        full_remote_return_and_fresh_absence='PASS',owner_results_checkpoint_required=True,manuscript='NOT_WRITTEN',
        main_delivery='AUTHORIZED_PENDING_GIT_RECEIPT',future_research_authorized=False,
        source_audit_sha256=digest(PUBLIC/'completion-checks-v1.json'))
    write_new(PUBLIC/'delivery-audit-v1.json',final)
    print(json.dumps(final))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['audit','settle']);a=p.parse_args()
    audit() if a.action=='audit' else settle()
