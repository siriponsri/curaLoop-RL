# LR-SARA-LR1 terminal owner report

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
starts at 2026-11-14T16:21:37+07:00 and ends at 2026-11-21T16:21:37+07:00.
It includes the limited targeted proposal; it is not an additional parallel
budget. The old account remains closed. One patch and one acceptance execution
were permitted; failed acceptance cannot trigger another recipe or matrix.

All 230 preservation pins passed. Original 30 roles
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

Retained bookings: **2.550000 CPU-hours**, **0 GPU-hours**. This includes
failures, evidence return and unmetered administration, not measured aggregate
consumption. Whole-host CPU use remains NOT_ESTABLISHED. Component resource
receipts are separate; missing measurements are not converted to zero. The old
10.833333333 CPU-hour booking remains unchanged in its own closed account.
See [resource summary](../evidence/lr-sara-lr1-20261114-v1/resource-summary-v1.json)
and [closed ledger](../evidence/lr-sara-lr1-20261114-v1/closed-resource-ledger-v1.json).
Unused nominal allowance is closed, not available for another attempt.

The returned workspace has 259 regular files,
8 symlinks, 89 directories and
5,476,032 regular-file bytes. Archive SHA-256:
`ecd67db90f1e67450be3a46a0acaebd5855edfc1429a849f454955a366e415c6`. Every file hash and link/directory metadata was
checked by independent local stream reread, without extraction/following links,
and a full remote reread before deletion. This is software integrity checking
by the developer, not independent expert validation.

Private local return:
`C:\Users\User\Desktop\myProject\curaloop-rl\.local\lr-sara-lr1-20261114-v1\remote-return-v1\owned-return.tar.gz`.
The exact owned task/export roots and 6 stopped
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
