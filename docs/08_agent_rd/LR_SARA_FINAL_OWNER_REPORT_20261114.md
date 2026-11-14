# LR-SARA: terminal route-A owner report

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
started at 2026-11-14T12:12:38+07:00; its overall deadline was
2026-11-21T12:12:38+07:00. The technical tranche had 12 CPU-hours, two allocated
GPU-hours and a deadline of 2026-11-16T00:12:38+07:00.

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
| 5 | locked_candidate | psa-lab/predicting-activity-by-machine-learning | NOT_RUN | NOT_RUN | NOT_RUN |
| 12 | development | kexinhuang12345/deeppurpose | NOT_RUN | NOT_RUN | NOT_RUN |
| 13 | development | kexinhuang12345/deeppurpose | NOT_RUN | NOT_RUN | NOT_RUN |
| 15 | locked_candidate | swansonk14/admet_ai | NOT_RUN | NOT_RUN | NOT_RUN |
| 16 | locked_candidate | felixjwong/antibioticsai | NOT_RUN | NOT_RUN | NOT_RUN |
| 18 | locked_candidate | anikaliu/camda-dili | NOT_RUN | NOT_RUN | NOT_RUN |
| 19 | locked_candidate | anikaliu/camda-dili | NOT_RUN | NOT_RUN | NOT_RUN |
| 21 | locked_candidate | geopandas/geopandas | NOT_RUN | NOT_RUN | NOT_RUN |
| 22 | locked_candidate | olivierbeq/papyrus-scripts | FAIL_IMPORT | NOT_RUN | NOT_RUN |
| 26 | locked_candidate | chemosim-lab/prolif | FAIL_IMPORT | NOT_RUN | NOT_RUN |
| 29 | locked_candidate | neuropsychology/neurokit | NOT_RUN | NOT_RUN | NOT_RUN |
| 34 | locked_candidate | neuropsychology/neurokit | NOT_RUN | NOT_RUN | NOT_RUN |
| 35 | locked_candidate | neuropsychology/neurokit | NOT_RUN | NOT_RUN | NOT_RUN |
| 37 | locked_candidate | mad-lab-fau/biopsykit | NOT_RUN | NOT_RUN | NOT_RUN |
| 40 | locked_candidate | anikaliu/camda-dili | NOT_RUN | NOT_RUN | NOT_RUN |
| 41 | locked_candidate | anikaliu/camda-dili | NOT_RUN | NOT_RUN | NOT_RUN |
| 44 | locked_candidate | mad-lab-fau/biopsykit | NOT_RUN | NOT_RUN | NOT_RUN |
| 45 | locked_candidate | mad-lab-fau/biopsykit | NOT_RUN | NOT_RUN | NOT_RUN |
| 53 | locked_candidate | rasterio/rasterio | NOT_RUN | NOT_RUN | NOT_RUN |
| 58 | locked_candidate | nriesterer/syllogistic-nvc | NOT_RUN | NOT_RUN | NOT_RUN |
| 60 | locked_candidate | nriesterer/syllogistic-nvc | NOT_RUN | NOT_RUN | NOT_RUN |
| 67 | locked_candidate | brand-d/cogsci-jnmf | NOT_RUN | NOT_RUN | NOT_RUN |
| 71 | development | zitonglu1996/eeg2eeg | NOT_RUN | NOT_RUN | NOT_RUN |
| 72 | development | zitonglu1996/eeg2eeg | NOT_RUN | NOT_RUN | NOT_RUN |
| 85 | locked_candidate | mad-lab-fau/biopsykit | NOT_RUN | NOT_RUN | NOT_RUN |
| 87 | locked_candidate | scitools/iris | NOT_RUN | NOT_RUN | NOT_RUN |
| 90 | locked_candidate | brand-d/cogsci-jnmf | NOT_RUN | NOT_RUN | NOT_RUN |
| 92 | locked_candidate | brand-d/cogsci-jnmf | NOT_RUN | NOT_RUN | NOT_RUN |
| 101 | locked_candidate | ppdebreuck/modnet | NOT_RUN | NOT_RUN | NOT_RUN |
| 102 | locked_candidate | ppdebreuck/modnet | NOT_RUN | NOT_RUN | NOT_RUN |

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

Retained reservations total **10.833333 CPU-hours**, including failed jobs,
return work and unmetered delivery administration, out of the 80-hour ceiling.
Allocated GPU reservations and actual allocated GPU work are zero. Reservations
are conservative retained bookings, not measured total consumption. Component
receipts measure particular local jobs, host processes or containers; aggregate
whole-host CPU use is **NOT_ESTABLISHED**. Unknown measurements were retained
as unknown rather than changed to zero. The full
[closed ledger](../evidence/lr-sara-20261114-v1/closed-resource-ledger-v1.json)
and [resource summary](../evidence/lr-sara-20261114-v1/resource-summary-v1.json)
retain stage and attempt details. Unused nominal allowance is closed.

The owned persistent workspace return contains **78,825
regular files**, 2 symlinks and 7,975
directories; regular-file bytes total 6,619,794,912. The compressed
archive is 4,262,086,277 bytes with SHA-256
`1b549fc2841150a92c84e0678ad31c01cf9c16fe42f088117b87430b268aff53`. Every regular-file hash and link/directory metadata
was checked by an independent local archive stream reread, without extracting
or following returned symlinks. A second remote reread matched the full manifest
before cleanup. This is an independently executed integrity check by our
software, **not independent expert validation**.

Local-only return archive:
`C:\Users\User\Desktop\myProject\curaloop-rl\.local\lr-sara-20261114-v1\remote-return-v1\owned-return.tar.gz`.
Raw dependencies, evaluator programs and benchmark material are not published
in Git. Remote task and export directories and 8
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
