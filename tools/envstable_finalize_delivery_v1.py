"""Close accounting only after guarded jobs settle; make final scoped audit."""
import ast,json,sys
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from tools.envstable_control_v1 import ACCOUNT,PUBLIC,RELEASE,digest,save,write_new
l=json.loads((ACCOUNT/'ledger.json').read_text());r=json.loads(RELEASE.read_text());assert not l['active_jobs']
assert json.loads((PUBLIC/'fresh-absence-v1.json').read_text())['status']=='PASS_FRESH_SSH_ABSENCE'
native=json.loads((PUBLIC/'native-development-canaries-v1.json').read_text());cold=json.loads((PUBLIC/'offline-reconstruction-cold-starts-v1.json').read_text());assert cold['all_pass']
cycle=json.loads((PUBLIC/'engineering-cycle3.json').read_text())
for item in cycle['profiles']+cold['cold_starts']:
 assert item['receipt']['state']['ExitCode']==0 and item['receipt']['resources']['stop_reason'] is None
assert cold['reconstruction_receipt']['state']['ExitCode']==0
for c in native['cases']:
 if c['score']==1:assert c['reference']['state']['ExitCode']==0 and c['grader']['receipt']['state']['ExitCode']==0
status='ENVIRONMENT_READY' if native['all_pass'] else 'RUNTIME_ARTIFACT_PASS_NATIVE_ACCEPTANCE_FAILED'
details=[]
for c in native['cases']:
 rr=c['reference']['resources'];gr=(c.get('grader') or {}).get('result')
 details.append(dict(case_id=c['case_id'],reference_exit=c['reference']['state']['ExitCode'],stop_reason=rr.get('stop_reason'),aggregate_cpu_seconds=rr['aggregate_cpu_seconds'],score=c['score'],grader=gr))
write_new(PUBLIC/'native-outcome-interpretation-v1.json',dict(cases=details,scope='One unchanged development reference per task; no agent efficacy',resource_caps_are_our_engineering_allocation=True,capacity_failure_does_not_establish_dependency_or_algorithm_failure=True))
report=root/'docs/08_agent_rd/ENV_STABLE_LR_FINAL_OWNER_REPORT_20261114.md'
with report.open('a',encoding='utf-8',newline='\n') as f:
 f.write('\n## Exact native outcome interpretation\n\n')
 for d in details:f.write(f"- Task {d['case_id']}: exit {d['reference_exit']}, stop reason {d['stop_reason']}, CPU {d['aggregate_cpu_seconds']:.3f} seconds, score {d['score']}; grader result {json.dumps(d['grader'])}.\n")
 f.write('\nThe 2,100-second per-reference CPU allocation was our engineering budget choice, not a published benchmark requirement. It was frozen before native attempts but was not supported by full-training capacity calibration. A cap failure therefore identifies an allocation limitation in this run; it does not prove the unchanged source could not finish under the overall owner budget or different permitted hardware. The reference was not replayed or truncated to produce a passing answer.\n\nThe returned transfer archive was stream-verified without extraction. Complete restoration from that transfer archive on a second host was NOT_RUN. The demonstrated offline reconstruction was a byte copy of the installed artifact on the retained base, followed by two new worker/cache sets. Preserve this distinction. When restoring a transfer archive, use its manifest, validate relative paths, do not follow returned symlinks, and copy checked earlier-member aliases as separate files when metadata differs. Shared base image remains on dr-train; cross-host image provisioning was not tested.\n')
memory=root/'docs/00_project/ENGINEERING_MEMORY.md'
with memory.open('a',encoding='utf-8',newline='\n') as f:f.write('\n## EM-20261114-09: freeze resource estimates after capacity preflight\n\nThe native per-attempt CPU cap was an engineering allocation, not the benchmark requirement. Full-training throughput was not calibrated before freezing that cap. Preserve actual cap stops as capacity-limited/inconclusive; do not classify them as dependency failure or native score zero. Do not silently increase caps after observing outcomes or replay a scientific attempt. Future releases must justify allocation before freeze, while reusing the verified installed artifact and successful existing native evidence.\n')
attrs=root/'docs/00_project/.gitattributes';assert not attrs.exists();attrs.write_text('ENGINEERING_MEMORY.md -text whitespace=cr-at-eol\n',encoding='utf-8')
l.update(status='CLOSED_'+status,finished_utc=datetime.now(timezone.utc).isoformat(),owner_results_review_required_before_new_science=True,actor_calls=0,locked_references=0);save(l)
write_new(PUBLIC/'closed-ledger-v1.json',l)
by_stage={}
for stage,caps in r['stage_caps_seconds'].items():
 cpu=sum(x['cpu_seconds'] for x in l['reservations'] if x['stage']==stage);gpu=sum(x['gpu_allocated_seconds'] for x in l['reservations'] if x['stage']==stage)
 assert cpu<=caps['cpu'] and gpu<=caps['gpu_allocated'];by_stage[stage]=dict(booked_cpu_seconds=cpu,allocated_gpu_seconds=gpu,caps=caps)
total=sum(v['booked_cpu_seconds'] for v in by_stage.values());assert total<=r['cpu_cap_seconds']
components=[]
for x in l['reservations']:
 components.append({k:v for k,v in x.items() if k in ['id','stage','status','cpu_seconds','gpu_allocated_seconds'] or k.startswith('measured')})
write_new(PUBLIC/'resource-accounting-v1.json',dict(status='PASS_WITH_RETAINED_BOOKINGS',by_stage=by_stage,total_booked_cpu_seconds=total,total_booked_cpu_hours=total/3600,total_allocated_gpu_seconds=0,whole_host_actual_cpu='NOT_ESTABLISHED',bookings_are_actual_usage=False,components=components,ledger_sha256=digest(ACCOUNT/'ledger.json')))
pins={p:digest(root/p)==h for p,h in r['preservation_pins'].items()};assert all(pins.values())
before=(ACCOUNT/'project-memory-before.md').read_bytes();assert (root/'docs/00_project/ENGINEERING_MEMORY.md').read_bytes().startswith(before)
assert len(l['attempts']['engineering_cycles'])==3 and len(native['cases'])==4 and all(x['reference_attempt']==1 for x in native['cases'])
sources=[]
for p in sorted((root/'tools').glob('envstable_*.py')):
 compile(p.read_bytes(),str(p),'exec');sources.append(dict(path=p.relative_to(root).as_posix(),sha256=digest(p)))
write_new(PUBLIC/'delivery-audit-v1.json',dict(status='PASS_DELIVERY_WITH_RECORDED_NATIVE_OUTCOMES',readiness=status,preservation_pins=len(pins),all_pins_pass=True,source_syntax='PASS',sources=sources,cold_checks=26,workload_profiles=13,native_reference_attempts=4,native_passes=sum(x['score']==1 for x in native['cases']),failed_native_attempts_preserved=True,actor_calls=0,locked_reference_attempts=0,manuscript='NOT_RUN',ese_jss_readiness='NOT_ESTABLISHED',complete_return='PASS',local_and_remote_content_reread='PASS',exact_cleanup='PASS',fresh_absence='PASS',project_memory_append='PASS',total_booked_cpu_hours=total/3600,allocated_gpu_hours=0,active_jobs=[],git_delivery='AUTHORIZED_PENDING_VERIFIED_RECEIPT'))
(PUBLIC/'README.md').write_text('# ENV-STABLE-LR evidence\n\nRead [the final owner report](../../08_agent_rd/ENV_STABLE_LR_FINAL_OWNER_REPORT_20261114.md).\n\n`delivery-audit-v1.json` records the engineering readiness decision. Loader controls, all three engineering cycles (including failures), the frozen native protocol, offline reconstruction/two cold starts, four native canary outcomes, preservation, resource account, complete return and exact cleanup are retained here. Full dependency trees, data and native logs are private in the ignored local account. This is engineering evidence; no new agent efficacy or manuscript claim.\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(status='PASS_ACCOUNT_AND_DELIVERY_CLOSED',readiness=status,booked_cpu_hours=total/3600,gpu_hours=0,pins=len(pins))))
