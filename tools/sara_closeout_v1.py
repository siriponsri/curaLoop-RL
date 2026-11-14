"""Offline evidence consolidation and terminal account closeout; no scientific execution."""
import ast,hashlib,json,re,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,digest,reserve,save,settle,write_new

REPORT=ROOT/'docs/08_agent_rd/LR_SARA_FINAL_OWNER_REPORT_20261114.md'

def main():
 r,l=authority('analysis_return');assert not l['active_jobs']
 assert l['terminal_gate']=='NO_GO_FINAL_CORRECTION_OPERATION_FAILED'
 reserve('terminal-delivery-administration-v1','analysis_return',1800,scope='Retained unmetered offline source/audit/report/account and main delivery administration; no science')
 cleanup=json.loads((PUBLIC/'owned-cleanup-v1.json').read_text())
 absence=json.loads((PUBLIC/'owned-cleanup-fresh-absence-v1.json').read_text())
 returned=json.loads((PUBLIC/'owned-return-verification-v1.json').read_text())
 assert cleanup['status']=='PASS_EXACT_OWNED_CLEANUP' and absence['status']=='PASS_FRESH_SSH_ABSENCE'
 assert cleanup['verification']['content_and_metadata_match'] and returned['every_file_content_and_link_metadata_verified']
 assert not returned['returned_links_extracted_or_followed']
 assert not l['attempts']['native_references'] and not l['attempts']['provider_calls']
 assert l['attempts']['correction_batch']['number']==1
 assert all(x['actual_import_attempts']==1 for x in l['attempts']['diagnostic_imports'].values())
 bad=[k for k,v in r['preservation_pins'].items() if not (ROOT/k).is_file() or digest(ROOT/k)!=v];assert not bad,bad
 role=json.loads((ROOT/r['role_freeze_source']).read_text())
 rows=[]
 for item in role['roles']:
  row=dict(item,asset_preparation='PASS_PREPARED_NOT_EXECUTED',post_fix_import='NOT_RUN',native_reference='NOT_RUN',native_scorer='NOT_RUN',agent='NOT_RUN',
   terminal_reason='Global final-correction installation failed before native admission',fresh_native_validity='NOT_ESTABLISHED')
  row['sole_diagnostic_import']='FAIL_IMPORT' if item['instance_id'] in (22,26) else 'NOT_RUN'
  rows.append(row)
 assert len(rows)==30 and sum(x['role']=='locked_candidate' for x in rows)==26
 write_new(PUBLIC/'all-thirty-terminal-states-v1.json',dict(status='TERMINAL_ACCOUNTING_ALL_30_ROWS',rows=rows,
  exclusions=[],old_development_outside_thirty=[2,3],old_import_passes_promoted_to_current_native=False,
  new_native_attempts=0,new_agent_calls=0,effect='NOT_ESTIMABLE'))
 source_records=[]
 for p in sorted((ACCOUNT/'jobs').glob('*/executed-source.py.txt')):
  dest=PUBLIC/'executed-source'/p.parent.name/'executed-source.py.txt';dest.parent.mkdir(parents=True,exist_ok=False);shutil.copyfile(p,dest)
  record=dict(job=p.parent.name,path=dest.relative_to(ROOT).as_posix(),sha256=digest(dest))
  receipt=p.parent/'resources.json'
  if receipt.exists():
   target=dest.parent/'resources.json';shutil.copyfile(receipt,target);record['resource_receipt_sha256']=digest(target)
  source_records.append(record)
 for p in (ACCOUNT/'admin-incidents').glob('*'):
  if p.is_file():
   dest=PUBLIC/'admin-incidents'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 # These contain dependency/environment diagnostics only; no benchmark target bodies.
 for name in ['guard-start-inspection-v1.json','export-receipt-v2.json']:
  shutil.copyfile(ACCOUNT/name,PUBLIC/name)
 current={};embedded=[]
 for p in sorted((ROOT/'tools').glob('sara_*.py')):
  text=p.read_text(encoding='utf-8');tree=ast.parse(text,filename=p.name);compile(tree,p.name,'exec')
  for node in tree.body:
   if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
    names=[t.id for t in node.targets if isinstance(t,ast.Name)]
    if any(n in {'REMOTE','PROGRAM','SETUP','IMPORTS','SUPERVISOR','VERIFY','DELETE','ABSENCE'} for n in names):
     compile(node.value.value,p.name+':'+names[0],'exec');embedded.append(p.name+':'+names[0])
  current[p.relative_to(ROOT).as_posix()]=digest(p)
 write_new(PUBLIC/'source-identity-v1.json',dict(status='PASS_OFFLINE_SYNTAX_AND_IDENTITIES',current_sources=current,
  embedded_python_compiled=embedded,executed_job_snapshots=source_records,
  historical_failed_source_retained=True,syntax_is_not_runtime_validation=True))
 settle('terminal-delivery-administration-v1','RETAINED_UNMETERED_ADMINISTRATION',measured_cpu_seconds='NOT_ESTABLISHED')
 l=json.loads((ACCOUNT/'ledger.json').read_text());assert not l['active_jobs']
 cpu=sum(x['cpu_seconds'] for x in l['reservations']);gpu=sum(x['gpu_allocated_seconds'] for x in l['reservations'])
 stages={k:dict(cpu_seconds=sum(x['cpu_seconds'] for x in l['reservations'] if x['stage']==k),
  gpu_allocated_seconds=sum(x['gpu_allocated_seconds'] for x in l['reservations'] if x['stage']==k)) for k in r['stage_caps_seconds']}
 assert cpu<=r['cpu_cap_seconds'] and gpu==0
 assert all(v['cpu_seconds']<=r['stage_caps_seconds'][k]['cpu'] and v['gpu_allocated_seconds']<=r['stage_caps_seconds'][k]['gpu_allocated'] for k,v in stages.items())
 assert datetime.now(timezone.utc)<datetime.fromisoformat(r['deadline_utc'])
 l.update(status='CLOSED_NO_GO_FINAL_CORRECTION_OPERATION_FAILED',closed_utc=datetime.now(timezone.utc).isoformat(),
  remote_return_and_cleanup='PASS_VERIFIED',manuscript='NOT_RUN_OWNER_REVIEW_REQUIRED',whole_host_measured_cpu_seconds='NOT_ESTABLISHED')
 save(l);shutil.copyfile(ACCOUNT/'ledger.json',PUBLIC/'closed-resource-ledger-v1.json')
 resources=dict(status='PASS_CAPS_AND_CLOSED_ACCOUNT',cpu_reserved_seconds=cpu,cpu_reserved_hours=cpu/3600,
  gpu_allocated_reserved_seconds=gpu,gpu_allocated_reserved_hours=gpu/3600,stage_reservations=stages,
  whole_host_measured_cpu_seconds='NOT_ESTABLISHED',failed_and_unmetered_bookings_retained=True,
  reservation_is_not_actual_consumption=True,closed_ledger_sha256=digest(ACCOUNT/'ledger.json'))
 write_new(PUBLIC/'resource-summary-v1.json',resources)
 table='\n'.join(f"| {x['instance_id']} | {x['role']} | {x['repository_lineage']} | {x['sole_diagnostic_import']} | NOT_RUN | NOT_RUN |" for x in rows)
 report=f'''# LR-SARA: terminal route-A owner report

Status: **CLOSED_NO_GO_FINAL_CORRECTION_OPERATION_FAILED**. Prepared 14 November 2026.

The one authorized final harness correction batch failed while extracting a
Debian package into our task-owned system-library overlay. Scientific work
stopped immediately. There is no new native-reference result, native score,
agent comparison, effect estimate, or manuscript from this release. This is a
failure of our preparer implementation, not evidence that the benchmark or
agent mechanism is ineffective. The owner should review this result before any
new research decision. No automatic CORE-Bench migration or further repair ran.

## Approval and fixed contract

The owner approved route A in the
[A-versus-CORE decision](HARNESS_REPAIR_VS_CORE_BENCH_DECISION_20261114.md):
80 CPU-hours and 26 allocated GPU-hours over seven days, at most four combined
CPU equivalents and one GPU, local and dr-train. The
[immutable release](../../research/manifests/lr_sara_release_20261114_v1.json)
started at {r['start_bangkok']}; its overall deadline was
{r['deadline_bangkok']}. The technical tranche had 12 CPU-hours, two allocated
GPU-hours and a deadline of {r['technical_deadline_bangkok']}.

The finite contract permitted one diagnostic import for each unresolved lineage
(22 and 26), one documented correction batch, and at most one native-reference
attempt per task. Full evaluation required at least 24 native-valid locked
tasks, 12 connected source groups, three domains, no source above 25%, unchanged
native scoring, validated substantive checks, matched controls and a feasible
cost projection. These were investment gates, not journal acceptance rules.

## What actually ran

| Activity | Status | Observed result |
| --- | --- | --- |
| Restore retained dependency material | PASS | Prior archive members rehashed; selected base/Papyrus/ProLIF material restored |
| Real wall/CPU watchdog probes | PASS | Actual probe processes stopped for WALL_DEADLINE and CPU_CAP |
| Sole Papyrus22 diagnostic import | FAIL | Read-only /root/.data created by pystow during import |
| Sole ProLIF26 diagnostic import | FAIL | RDKit Draw cannot load libXrender.so.1 |
| Prepare retained 30-case assets | PASS, preparation only | 215 files; 1,725,612,166 expanded bytes; no reference/scorer execution |
| Freeze final correction recipe | PASS | One storage/cache/library/dependency recipe, frozen before the install |
| apt-update and library retrieval | PASS | Both operations returned 0; setup received 11,763,456 bytes |
| First package extraction | FAIL | extract-libgomp1 returned 2; setup container returned 1 |
| Post-fix import regression | NOT_RUN | Batch stopped before this step |
| Native reference/scorer qualification | NOT_RUN | Zero calls; no task freshly certified |
| Development or locked agent comparison | NOT_RUN | Zero provider/model calls; zero GPU allocation |
| New action/check plugin or product acceptance | NOT_RUN | Gate did not authorize downstream implementation |
| Manuscript | NOT_RUN | Owner results review comes first |

The complete dependency trace is in
[dependency diagnosis](../evidence/lr-sara-20261114-v1/dependency-diagnosis-v1.json).
The correction-plan SHA-256 is
`146e788c3db52d328768f10084d2da056114ccfaa0a8baaafe50b28483dcac96`.
See the [frozen plan](../evidence/lr-sara-20261114-v1/final-correction-plan-v1.json),
[installation result](../evidence/lr-sara-20261114-v1/final-correction-result-v1.json),
and [terminal raw failure](../evidence/lr-sara-20261114-v1/terminal-technical-stop-v1.json).

## Root cause and responsibility

`dpkg-deb -x` invokes tar to preserve package metadata. Its first extraction
reported that it could not change the time, owner or mode of `.` on the
task-owned bind mount, then exited 2. Our isolated container dropped all Linux
capabilities; the bind-mount root belonged to the ordinary SSH user. The
preparer selected an extraction operation incompatible with that ownership and
isolation arrangement. This implementation choice is ours.

The new evidence clarifies the previously missing Papyrus/ProLIF exception
messages. It does not prove that the complete revised environment would work,
that the earlier ENOSPC cause is fully resolved, or that native coverage is
adequate. No regression was run after the proposed fixes. A different unpacking
implementation is conceivable but **NOT_RUN** and outside the terminal batch.

## Full cohort accounting

All original 30 rows remain: four development tasks (12, 13, 71, 72) and 26
locked candidates. Earlier development tasks 2 and 3 remain outside this cohort.
No task was replaced or silently excluded. Earlier import passes remain
historical import results and are not promoted to fresh native validity.
The maximum candidate source diversity remains a design bound, not observed
qualified coverage. The [machine-readable table](../evidence/lr-sara-20261114-v1/all-thirty-terminal-states-v1.json)
also retains domains and all NOT_RUN states.

| Task | Fixed role | Repository lineage | Sole diagnostic import | New native reference | Agent |
| --- | --- | --- | --- | --- | --- |
{table}

## Operational failures retained, without scientific retries

1. The first bootstrap launcher passed a string to a bytes encoder and failed
   before SSH dispatch. Its executed source, failure and reservation remain.
   The first actual remote dispatch used corrected transport encoding.
2. The first Docker launcher returned 2 before starting the diagnostic guard.
   Inspection proved Created/Pid0/no StartedAt, with zero diagnostic imports.
   The first actual start used an 8 GiB host virtual-address ceiling, within the
   approved 32 GiB aggregate limit. Why the original Docker CLI returned 2 is
   not conclusively established. The same container settings remained fixed.
3. A terminal-inspection wrapper rejected dispatch while a local job was active,
   before any reservation or remote call. A control-only inspection then recorded
   the existing terminal failure; no installation was repeated.
4. Evidence exporter v1 used `hashlib.file_digest`, unavailable in its Python
   3.10 image. It failed before creating the archive. Delivery-only exporter v2
   used a streaming hash loop on the same read-only source. Both exporter
   sources/logs and reservations remain. This did not reopen scientific work.

Executed job source snapshots and resource receipts are mapped in
[source identities](../evidence/lr-sara-20261114-v1/source-identity-v1.json).
Source syntax checks are offline checks, not evidence of successful reference
or agent execution. Previously failed source is preserved rather than replaced
by a claim that the final source was used for every historical operation.

## Resources and delivery

Retained reservations total **{cpu/3600:.6f} CPU-hours**, including failed jobs,
return work and unmetered delivery administration, out of the 80-hour ceiling.
Allocated GPU reservations and actual allocated GPU work are zero. Reservations
are conservative retained bookings, not measured total consumption. Component
receipts measure particular local jobs, host processes or containers; aggregate
whole-host CPU use is **NOT_ESTABLISHED**. Unknown measurements were retained
as unknown rather than changed to zero. The full
[closed ledger](../evidence/lr-sara-20261114-v1/closed-resource-ledger-v1.json)
and [resource summary](../evidence/lr-sara-20261114-v1/resource-summary-v1.json)
retain stage and attempt details. Unused nominal allowance is closed.

The owned persistent workspace return contains **{returned['regular_files']:,}
regular files**, {returned['symlinks']} symlinks and {returned['directories']:,}
directories; regular-file bytes total {returned['regular_bytes']:,}. The compressed
archive is {returned['bundle_bytes']:,} bytes with SHA-256
`{returned['bundle_sha256']}`. Every regular-file hash and link/directory metadata
was checked by an independent local archive stream reread, without extracting
or following returned symlinks. A second remote reread matched the full manifest
before cleanup. This is an independently executed integrity check by our
software, **not independent expert validation**.

Local-only return archive:
`C:\\Users\\User\\Desktop\\myProject\\curaloop-rl\\.local\\lr-sara-20261114-v1\\remote-return-v1\\owned-return.tar.gz`.
Raw dependencies, evaluator programs and benchmark material are not published
in Git. Remote task and export directories and {len(cleanup['removed_containers'])}
owned stopped containers were removed after verification. A fresh SSH check
confirmed absence. Shared images, models and other services were not modified.
See [return verification](../evidence/lr-sara-20261114-v1/owned-return-verification-v1.json),
[cleanup](../evidence/lr-sara-20261114-v1/owned-cleanup-v1.json), and
[fresh absence](../evidence/lr-sara-20261114-v1/owned-cleanup-fresh-absence-v1.json).

## Research and publication assessment

The proposed contribution remains a question: whether reusable scientific
actions and executable diagnostic feedback provide separable benefits under
matched information and resources. That question was not tested in this release.
There is no primary effect estimate, confidence interval, null result or evidence
of equivalence. The correct result label is **UNMEASURED / NOT_ESTIMABLE**.

**Not ready for the proposed ESE or JSS manuscript.** This engineering admission
failure is useful project evidence but is insufficient empirical support for
the agent mechanism paper. It is also not a completed comparative negative-result
study. No independent validation, wet-lab, clinical, customer or commercial value
is established. Existing product and earlier computational outputs remain in
their original reports; this release does not revalidate or erase them.

## Owner checkpoint

This release is closed on its approved stop path. Review this report and its
evidence before selecting new scientific work. No further harness recipe,
model, dataset, CORE-Bench migration, full experiment or manuscript is activated.
The next decision is whether to retire this harness research branch or authorize
a separately justified direction. Another qualification round is not presumed.
Main commit/push delivery is authorized and is verified after this report and
the [delivery audit](../evidence/lr-sara-20261114-v1/delivery-audit-v1.json) are staged.
The actual pushed commit identifier is recorded in the delivery message/private
Git receipt, avoiding a self-referential report hash.
'''
 with REPORT.open('x',encoding='utf-8',newline='\n') as f:f.write(report)
 readme='''# LR-SARA evidence index

Start with [the owner report](../../08_agent_rd/LR_SARA_FINAL_OWNER_REPORT_20261114.md).
The terminal result is NO_GO_FINAL_CORRECTION_OPERATION_FAILED, not an agent score.

- release-v1.json: immutable scope, clocks and 164 historical preservation pins.
- dependency-diagnosis-v1.json: sole actual imports and real watchdog probes.
- final-correction-plan-v1.json / final-correction-result-v1.json: the one frozen batch and its failure.
- terminal-technical-stop-v1.json: unchanged stop and exact extraction error.
- all-thirty-terminal-states-v1.json: complete fixed-role accounting, no native/agent run.
- owned-return-verification-v1.json / owned-cleanup-v1.json / owned-cleanup-fresh-absence-v1.json: return, remote reread and exact cleanup.
- source-identity-v1.json / executed-source: current and actual historical source identities.
- closed-resource-ledger-v1.json / resource-summary-v1.json: retained bookings; whole-host CPU unknown.
- delivery-audit-v1.json: offline evidence, pin, cap and closeout verification.

Private raw archives remain under .local/lr-sara-20261114-v1; they are not Git artifacts.
No protected old outcomes, benchmark gold bodies, model weights or credentials are published here.
'''
 with (PUBLIC/'README.md').open('x',encoding='utf-8',newline='\n') as f:f.write(readme)
 links=[]
 for p in (REPORT,PUBLIC/'README.md'):
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' not in target and not target.startswith('#'):
    q=(p.parent/target.split('#')[0]).resolve()
    if q==PUBLIC/'delivery-audit-v1.json':continue
    assert q.exists(),(p,target);links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target))
 pins_status=dict(status='PASS',pins=len(r['preservation_pins']),failed=[])
 evidence={p.relative_to(ROOT).as_posix():digest(p) for p in PUBLIC.rglob('*') if p.is_file()}
 write_new(PUBLIC/'delivery-audit-v1.json',dict(status='PASS_CLOSED_TECHNICAL_NO_GO_DELIVERY',closed_status=l['status'],
  audited_utc=datetime.now(timezone.utc).isoformat(),preservation=pins_status,
  release_sha256=digest(RELEASE),closed_ledger_sha256=digest(ACCOUNT/'ledger.json'),cpu_caps_pass=True,gpu_allocated_seconds=0,
  correction_batches=1,diagnostic_imports_per_affected_lineage=1,native_references=0,native_scorer_calls=0,provider_calls=0,
  full_study='NOT_RUN',effect='NOT_ESTIMABLE',manuscript='NOT_RUN',core_migration=False,active_jobs=[],
  complete_owned_return_and_local_reread=True,complete_remote_reread=True,fresh_remote_absence=True,
  source_syntax_pass=True,markdown_links_checked=links,report_sha256=digest(REPORT),evidence_sha256=evidence,
  main_delivery='AUTHORIZED_PENDING_ACTUAL_COMMIT_PUSH_VERIFICATION',audit_is_independent_expert_validation=False))
 print(json.dumps(dict(status=l['status'],cpu_reserved_hours=cpu/3600,pins=len(r['preservation_pins']),report=str(REPORT))))

if __name__=='__main__':main()
