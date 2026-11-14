"""Close the failed engineering path with complete evidence; no research execution."""
import ast,json,re,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.saralr1_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,digest,reserve,settle,save,write_new

def main():
 r,l=authority('analysis_return');assert l['status']=='ACTIVE_CLOSEOUT_NO_GO' and not l['active_jobs']
 reserve('terminal-delivery-administration-v1','analysis_return',900,scope='Unmetered offline report/audit/closeout and scoped main delivery; no scientific work')
 result=json.loads((PUBLIC/'engineering-acceptance-v1.json').read_text());assert result['status']=='NO_GO_ENGINEERING_ACCEPTANCE'
 assert result['receipt']['state']['ExitCode']==1 and not result['receipt']['state']['Running']
 assert 'libX11.so.6' in result['log'] and l['attempts']['engineering']['actual_matrix_executions']==1
 assert not l['attempts']['native_references'] and not l['attempts']['provider_calls'] and not l['attempts']['installation_groups'] and not l['attempts']['post_patch_imports']
 returned=json.loads((PUBLIC/'owned-return-verification-v1.json').read_text());cleanup=json.loads((PUBLIC/'owned-cleanup-v1.json').read_text())
 absence=json.loads((PUBLIC/'owned-cleanup-fresh-absence-v1.json').read_text());assert returned['all_file_content_and_link_directory_metadata_verified'] and cleanup['status']=='PASS_EXACT_OWNED_CLEANUP' and absence['status']=='PASS_FRESH_SSH_ABSENCE'
 bad=[k for k,v in r['preservation_pins'].items() if not (ROOT/k).is_file() or digest(ROOT/k)!=v];assert not bad,bad
 roles=json.loads((ROOT/r['role_freeze_source']).read_text())['roles'];assert len(roles)==30
 rows=[dict(x,environment_continuation='NOT_RUN',post_patch_import='NOT_RUN',native_reference='NOT_RUN',native_scorer='NOT_RUN',agent='NOT_RUN',reason='Global engineering acceptance failed before preparation/native execution') for x in roles]
 write_new(PUBLIC/'all-thirty-terminal-states-v1.json',dict(status='ALL_30_FIXED_ROWS_RETAINED',rows=rows,excluded_or_replaced=[],effect='NOT_ESTIMABLE'))
 source_records=[]
 for source in sorted((ACCOUNT/'jobs').glob('*/executed-source.py.txt')):
  dest=PUBLIC/'executed-source'/source.parent.name/'executed-source.py.txt';dest.parent.mkdir(parents=True);shutil.copyfile(source,dest)
  receipt=source.parent/'resources.json';shutil.copyfile(receipt,dest.parent/'resources.json')
  source_records.append(dict(job=source.parent.name,path=dest.relative_to(ROOT).as_posix(),sha256=digest(dest),resource_receipt_sha256=digest(dest.parent/'resources.json')))
 admin=Path(r'C:\Users\User\Documents\ChatGPT\Drug Discovery')
 for name in ('saralr1_initialize_v1.py','saralr1_sync_sources_v1.py'):
  dest=PUBLIC/'executed-source'/('administration-'+name+'.txt');shutil.copyfile(admin/name,dest)
 current={};embedded=[]
 for source in sorted((ROOT/'tools').glob('saralr1_*.py')):
  tree=ast.parse(source.read_text());compile(tree,str(source),'exec')
  for node in tree.body:
   if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
    names=[x.id for x in node.targets if isinstance(x,ast.Name)]
    if any(n in {'REMOTE','EXPORT','SUPERVISOR'} for n in names):compile(node.value.value,source.name+':'+names[0],'exec');embedded.append(source.name+':'+names[0])
  current[source.relative_to(ROOT).as_posix()]=digest(source)
 matrix=json.loads((PUBLIC/'frozen-engineering-matrix-v1.json').read_text())
 assert digest(ROOT/'tools/saralr1_overlay_v1.py')==matrix['patch_source_sha256']
 assert digest(ROOT/'tools/saralr1_acceptance_program_v1.py')==matrix['acceptance_source_sha256']
 assert digest(ROOT/'tools/saralr1_runtime_v1.py')==matrix['runtime_source_sha256']
 write_new(PUBLIC/'source-identity-v1.json',dict(status='PASS_FROZEN_CANDIDATE_AND_OFFLINE_SOURCE_IDENTITIES',current_sources=current,executed_jobs=source_records,embedded_syntax_checked=embedded,offline_checks_are_not_runtime_acceptance=True))
 settle('terminal-delivery-administration-v1','RETAINED_UNMETERED_ADMINISTRATION',measured_cpu_seconds='NOT_ESTABLISHED')
 l=json.loads((ACCOUNT/'ledger.json').read_text());assert not l['active_jobs']
 cpu=sum(x['cpu_seconds'] for x in l['reservations']);gpu=sum(x['gpu_allocated_seconds'] for x in l['reservations']);assert cpu<=r['cpu_cap_seconds'] and gpu==0
 stages={name:dict(cpu_seconds=sum(x['cpu_seconds'] for x in l['reservations'] if x['stage']==name),gpu_allocated_seconds=sum(x['gpu_allocated_seconds'] for x in l['reservations'] if x['stage']==name)) for name in r['stage_caps_seconds']}
 assert all(x['cpu_seconds']<=r['stage_caps_seconds'][k]['cpu'] and x['gpu_allocated_seconds']<=r['stage_caps_seconds'][k]['gpu_allocated'] for k,x in stages.items())
 l.update(status='CLOSED_NO_GO_ENGINEERING_ACCEPTANCE',closed_utc=datetime.now(timezone.utc).isoformat(),whole_host_measured_cpu_seconds='NOT_ESTABLISHED',owned_return_and_cleanup='PASS',manuscript='NOT_RUN_OWNER_RESULTS_REVIEW')
 save(l);shutil.copyfile(ACCOUNT/'ledger.json',PUBLIC/'closed-resource-ledger-v1.json')
 write_new(PUBLIC/'resource-summary-v1.json',dict(status='PASS_CLOSED_CAPS',cpu_reserved_seconds=cpu,cpu_reserved_hours=cpu/3600,gpu_allocated_reserved_seconds=gpu,stage_reservations=stages,whole_host_measured_cpu_seconds='NOT_ESTABLISHED',failed_and_unmetered_bookings_retained=True,prior_account_unchanged=True,closed_ledger_sha256=digest(ACCOUNT/'ledger.json')))
 body=f'''# LR-SARA-LR1 terminal owner report

Status: **CLOSED_NO_GO_ENGINEERING_ACCEPTANCE**. Prepared 14 November 2026.

The one frozen engineering acceptance matrix failed while loading libXrender:
`OSError: libX11.so.6: cannot open shared object file: No such file or directory`.
Science stopped at this mandatory gate. No environment-profile installation,
post-patch Papyrus/ProLIF import, native reference/scorer, model call, comparative
study or manuscript ran. This is still our engineering implementation/acceptance
failure, not a measured negative agent effect or benchmark invalidity result.

## Authority and finite execution

The owner approved [LR-SARA-LR1](LONG_RUN_SARA_PATCH_TO_RESULTS_PROPOSAL_20261114.md)
with fresh 80 CPU-hours/26 allocated GPU-hours over seven days, maximum four
combined CPU equivalents/one GPU on local/dr-train. The
[release](../../research/manifests/lr_sara_lr1_release_20261114_v1.json)
starts at {r['start_bangkok']} and ends at {r['deadline_bangkok']}.
It includes the limited targeted proposal; it is not an additional parallel
budget. The old account remains closed. One patch and one acceptance execution
were permitted; failed acceptance cannot trigger another recipe or matrix.

All {len(r['preservation_pins'])} preservation pins passed. Original 30 roles
(four development, 26 locked) remain; no tasks, scores or source groups changed.
The [full table](../evidence/lr-sara-lr1-20261114-v1/all-thirty-terminal-states-v1.json)
retains all NOT_RUN states. Protected final16/private CF1/old hidden outcomes
remain closed. No new dataset, model, paid API, GPU allocation or CORE migration.

## Changes and actual evidence

New versioned source addressed two known defects without editing old workers:

- Content-only Debian payload extraction validates paths and links, skips the
  archive root entry and does not restore archived owner/group/timestamps.
- The Python-3.10 setup hash path uses a streaming SHA-256 implementation.

The [frozen matrix](../evidence/lr-sara-lr1-20261114-v1/frozen-engineering-matrix-v1.json)
pins patch, test program, retained image, seven Debian archive hashes and the
derived runtime guard. These three source hashes stayed unchanged after freeze.
The real retained image was Python 3.10.22, with read-only root, all capabilities
dropped, a writable task-owned bind and one-CPU quota/initial affinity.

| Step | Status and interpretation |
| --- | --- |
| Verify prior returned archive and select seven Debian inputs | PASS; no new apt/dependency/scientific download |
| Actual wall and CPU guard probes | PASS; observed WALL_DEADLINE and CPU_CAP process termination |
| Seven-package extraction loop and recorded libgomp hash check | Reached before the failing line by source/control-flow evidence; no complete per-test result JSON was emitted |
| libgomp absolute-path smoke load | Precedes libXrender in the loop; successful progression is inferred from source/error dependency, not a separately persisted test receipt |
| libXrender dependency loading | FAIL; libX11.so.6 lookup error, container exit 1 |
| Invalid-archive/root-mode/empty-file hash fixtures later in matrix | NOT_RUN after early abort; not counted as passing |
| Full patch acceptance | FAIL; never promoted from partial progress |
| Preparation, native admission, development and comparison | NOT_RUN |

The raw error, container state, guard receipts and zero-call counts are in
[engineering acceptance](../evidence/lr-sara-lr1-20261114-v1/engineering-acceptance-v1.json).
No second acceptance run or library load was performed after failure.

## What is known about libX11, and what remains unknown

Post-failure **static inspection only** found libX11.so.6 and its target
libX11.so.6.4.0 inside the extracted overlay, with matching SHA-256
`b03e563b316b8b53c7988f0ee91d6656cc425538e00947a8b14482d179e80099`.
The recorded LD_LIBRARY_PATH names that overlay directory. libXrender, libxcb,
libXau, libXdmcp and libgomp entries were also present with internal link targets.
Therefore the runtime error must not be reported as proof that the package was
not downloaded or that the library file was absent on disk.

The demonstrated problem is library discovery/loading in the chosen acceptance
process. The process created library directories after interpreter startup and
then attempted loading in that same process; process-start search behavior is
a possible explanation, not a confirmed cause. No loader rerun, import or new
configuration was executed to discriminate causes. The result does not establish
that a later fresh Python process would fail or pass. The implementation still
did not meet the agreed acceptance gate. This responsibility is ours.

See [static observation](../evidence/lr-sara-lr1-20261114-v1/post-failure-static-observation-v1.json).
The remaining rejection fixtures and final root-mode assertion cannot be claimed
passed just because their code exists. A future correction would require an
owner decision; this release does not activate it.

## Administration failures retained

Before any Docker container existed, the initial remote bootstrap omitted the
task-owned leases parent, causing FileNotFoundError. Inspection proved no
containers, no leases and no matrix execution. A bookkeeping continuation created
the missing parent and started the **same unchanged patch/matrix/runtime** for
the first actual execution. This did not repeat a test result.

After that actual matrix exited, its wrapper lacked a shutil import for disk
report serialization. A read-only collector retrieved the already completed
container artifacts. It did not repeat the matrix or amend the patch. Both
administration failures and their booked resources/source snapshots are retained
in [the incident record](../evidence/lr-sara-lr1-20261114-v1/engineering-administration-incidents-v1.json).
These were avoidable orchestration defects in our code and are not scientific
failures or independent validation. No source was silently overwritten.

## Resources and verified delivery

Retained bookings: **{cpu/3600:.6f} CPU-hours**, **0 GPU-hours**. This includes
failures, evidence return and unmetered administration, not measured aggregate
consumption. Whole-host CPU use remains NOT_ESTABLISHED. Component resource
receipts are separate; missing measurements are not converted to zero. The old
10.833333333 CPU-hour booking remains unchanged in its own closed account.
See [resource summary](../evidence/lr-sara-lr1-20261114-v1/resource-summary-v1.json)
and [closed ledger](../evidence/lr-sara-lr1-20261114-v1/closed-resource-ledger-v1.json).
Unused nominal allowance is closed, not available for another attempt.

The returned workspace has {returned['regular_files']} regular files,
{returned['symlinks']} symlinks, {returned['directories']} directories and
{returned['regular_bytes']:,} regular-file bytes. Archive SHA-256:
`{returned['bundle_sha256']}`. Every file hash and link/directory metadata was
checked by independent local stream reread, without extraction/following links,
and a full remote reread before deletion. This is software integrity checking
by the developer, not independent expert validation.

Private local return:
`C:\\Users\\User\\Desktop\\myProject\\curaloop-rl\\.local\\lr-sara-lr1-20261114-v1\\remote-return-v1\\owned-return.tar.gz`.
The exact owned task/export roots and {len(cleanup['removed_containers'])} stopped
owned containers were removed; a fresh SSH check confirmed absence. Shared
images/models/services were not modified. [Return verification](../evidence/lr-sara-lr1-20261114-v1/owned-return-verification-v1.json),
[cleanup](../evidence/lr-sara-lr1-20261114-v1/owned-cleanup-v1.json),
[fresh absence](../evidence/lr-sara-lr1-20261114-v1/owned-cleanup-fresh-absence-v1.json).

## Scientific result, publication assessment and next decision

Primary agent effect **NOT_ESTIMABLE**; comparison **NOT_RUN**. There is no null
effect, equivalence claim or completed negative comparative study here. One
engineering matrix failure is insufficient evidence for the proposed ESE/JSS
agent paper. Publication readiness remains **NOT_READY**. No manuscript was
written; no clinical/customer/business or independent-expert value is asserted.

The goal closes on its approved terminal-stop path. The next actor is the owner,
to review these actual results before deciding whether to retire this environment
path or separately authorize another direction. No automatic new qualification,
fix recipe, benchmark migration, study or manuscript is proposed as active work.

New source identities and executed snapshots are in
[source identity](../evidence/lr-sara-lr1-20261114-v1/source-identity-v1.json).
The [delivery audit](../evidence/lr-sara-lr1-20261114-v1/delivery-audit-v1.json)
checks pins, caps and artifacts. Main commit/push is authorized and verified
after staging; its actual pushed SHA is recorded in the delivery message and
local Git receipt, avoiding a self-referential report hash.
'''
 report=ROOT/'docs/08_agent_rd/LR_SARA_LR1_FINAL_OWNER_REPORT_20261114.md'
 with report.open('x',encoding='utf-8',newline='\n') as f:f.write(body)
 readme='''# LR-SARA-LR1 evidence

Start with [the owner report](../../08_agent_rd/LR_SARA_LR1_FINAL_OWNER_REPORT_20261114.md).

The sole frozen engineering matrix failed on libXrender/libX11 loading. It did
not execute native references or agents. Source-ordered partial progress is not
a passing matrix. Read engineering-acceptance-v1.json and the separate static
post-failure observation; libX11 was present on disk despite the loading error.

The administration incident record retains missing-directory and serialization
errors. Full return, local/remote rereads, exact cleanup and fresh absence have
separate receipts. Old evidence and closed ledgers remain pinned. Resource
bookings are not measured whole-host consumption. All 30 role rows remain.
No benchmark gold bodies, private outcomes, raw dependencies or credentials are
published in this evidence directory. Raw return remains local under .local.
'''
 with (PUBLIC/'README.md').open('x',encoding='utf-8',newline='\n') as f:f.write(readme)
 links=[]
 for p in (report,PUBLIC/'README.md'):
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' not in target:
    q=(p.parent/target).resolve()
    if q==PUBLIC/'delivery-audit-v1.json':continue
    assert q.exists(),(p,target);links.append(dict(path=p.relative_to(ROOT).as_posix(),target=target))
 evidence={p.relative_to(ROOT).as_posix():digest(p) for p in PUBLIC.rglob('*') if p.is_file()}
 write_new(PUBLIC/'delivery-audit-v1.json',dict(status='PASS_CLOSED_TERMINAL_NO_GO_DELIVERY',closed_status=l['status'],preservation_pins=len(r['preservation_pins']),failed_pins=[],release_sha256=digest(RELEASE),closed_ledger_sha256=digest(ACCOUNT/'ledger.json'),
  candidate_count=1,actual_matrix_executions=1,full_acceptance='FAIL',native_references=0,native_scorer_calls=0,provider_calls=0,gpu_allocated_seconds=0,full_comparison='NOT_RUN',effect='NOT_ESTIMABLE',manuscript='NOT_RUN',active_jobs=[],
  caps_pass=True,complete_owned_return_and_rereads=True,exact_cleanup_and_fresh_absence=True,syntax_checks_are_not_runtime_passes=True,
  report_sha256=digest(report),evidence_sha256=evidence,markdown_links=links,main_delivery='AUTHORIZED_PENDING_ACTUAL_PUSH_VERIFICATION'))
 old=(ROOT/'AGENTS.md').read_bytes();header=f'''# Current closeout: LR-SARA-LR1, 14 November 2026

LR-SARA-LR1 is CLOSED_NO_GO_ENGINEERING_ACCEPTANCE with zero active jobs.
Read docs/08_agent_rd/LR_SARA_LR1_FINAL_OWNER_REPORT_20261114.md and
docs/evidence/lr-sara-lr1-20261114-v1/delivery-audit-v1.json. The one frozen
matrix failed loading libXrender because libX11.so.6 was not found by the loader.
Static inspection found that library and its target in the overlay; exact loader
cause is unresolved. No matrix retry, new recipe or broader patch ran. Bootstrap
and serialization errors are retained, with proof of only one actual matrix run.
Environment continuation/native/scorer/agent/comparison/manuscript are NOT_RUN.
Effect NOT_ESTIMABLE; ESE/JSS NOT_READY. No automatic CORE migration or new work.

All {len(r['preservation_pins'])} old pins pass; protected outcomes remain closed.
Full {returned['regular_files']}-file/{returned['symlinks']}-symlink return and
local/remote rereads passed, followed by exact owned roots/{len(cleanup['removed_containers'])}
container cleanup and fresh absence. Retained bookings {cpu} CPU seconds,
zero allocated GPU; whole-host actual CPU NOT_ESTABLISHED. Accounts remain closed.
Owner receives results before any new scientific/manuscript decision. Scoped
main push is authorized; exact pushed SHA follows in the delivery/local receipt.
Lower releases/closeouts are preserved history, not reusable authority.

'''.encode();(ROOT/'AGENTS.md').write_bytes(header+old)
 print(json.dumps(dict(status=l['status'],cpu_reserved_hours=cpu/3600,pins=len(r['preservation_pins']),report=str(report))))
if __name__=='__main__':main()
