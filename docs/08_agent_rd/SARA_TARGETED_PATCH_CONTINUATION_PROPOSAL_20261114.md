# Targeted preparer patch and unfinished native-pass continuation

Status: **PROPOSED_ONLY / NOT_RELEASED**. Prepared 14 November 2026.
Inspected baseline: main `3aa640c79213184d29f07af4d09201ae4bbef5a7`.
Proposed goal identifier: **LR-SARA-P1**. No new experiment, SSH job, patch,
resource account or clock has been started by preparing this document.

## Decision and responsibility

The terminal failure belongs to our harness/preparer. It occurred before any
native reference, scorer or agent run. The downloaded `libgomp1` payload actually
appears in the returned manifest, including its 348,056-byte library and relative
symlink. This supports a metadata/extraction failure rather than a missing Debian
download. It does not establish that loading the complete overlay would succeed.

Correcting only `dpkg-deb -x` is insufficient. Inspection also found
`hashlib.file_digest` in the embedded SETUP program in
[the frozen worker](../../tools/sara_correction_worker_v1.py). It would run under
Python 3.10.22 after extraction. That API was added in Python 3.11; the installation
path has not reached this line, so this is a confirmed source/API incompatibility,
not an observed second installation traceback. The previous delivery exporter
repair did not change this separate SETUP program.

The recommended intervention is one small, frozen engineering patch covering
these two identified implementation defects, followed by the unfinished path.
It can plausibly remove the observed blocker. It cannot certify the remaining
package installs, native references or proposed agent contribution in advance.

Evidence: [terminal report](LR_SARA_FINAL_OWNER_REPORT_20261114.md),
[extraction failure](../evidence/lr-sara-20261114-v1/terminal-technical-stop-v1.json),
[frozen recipe](../evidence/lr-sara-20261114-v1/final-correction-plan-v1.json),
and the retained local-only `remote-return-v1/owned-manifest.json`.

## Patch boundary

1. Replace ownership-preserving package extraction with a content-only extractor
   into a fresh task-owned staging directory. Obtain the package payload using
   `dpkg-deb --fsys-tarfile`; validate every member before writing. Skip the `.`
   root metadata entry; do not restore archived owner/group/timestamps. Create
   files/directories and required relative links with explicit usable modes.
   Reject absolute paths, parent traversal, escaping links and special files;
   handle or reject hard links explicitly. Do not use unrestricted extractall.
   Verify payload file content and link targets, then publish the overlay only
   after the complete extraction passes. Do not swallow tar errors or accept a
   partially extracted overlay.
2. Replace `hashlib.file_digest` in the Python-3.10 SETUP path with a streaming
   SHA-256 loop, as already used successfully for evidence return. Retain the
   interpreter and image; do not upgrade Python to hide the incompatibility.
3. Inspect the directly executed embedded setup/import/return code for the same
   runtime/API mismatch before freezing. This inspection is not permission for
   a new dependency recipe or broad runtime refactor. A newly required change
   outside the two defined defect classes is a stop/report condition.
4. Put the patch in new versioned files. Pin the old worker, recipe, raw failure,
   closed ledger and all current release preservation files. Never rewrite old
   results or relabel the previous batch successful.

No added host capabilities, host package installation, root filesystem changes,
new base image, scientific code/scoring changes or new model are proposed.

## Exact continuation, without a restarted cohort qualification

Keep the fixed four development tasks (12/13/71/72), 26 locked candidates, source
roles and dependence rules. Do not redo literature selection, rights census,
role hashing, candidate search or the previous diagnostic imports on the old
environment. Import passes remain import evidence, not native-reference success.

The execution frontier is:

1. **One engineering acceptance matrix.** Run the frozen patch once in the exact
   retained Python 3.10 image and the same dropped-capability, read-only-root,
   writable-bind ownership arrangement. Cover all seven retained Debian files,
   payload/hash/link checks, root metadata handling, path/link rejection and
   hash compatibility. Synthetic malformed archive fixtures are software tests,
   not mock scientific or agent outcomes. Require unchanged mount-root
   owner/mode and no writes outside the owned staging tree.
2. **Complete unfinished environment preparation once.** Restore verified local
   artifacts to a new owned namespace. Reuse complete environment artifacts only
   where receipts and constraints support it. Never restore a failed partial
   environment as complete. Reuse the seven recorded Debian archives by hash;
   no new apt-update/version search is needed. For profiles that never completed,
   use the existing constraints and package names, one installation attempt each;
   record the resolved distribution hashes and versions. No alternative version,
   constraint relaxation, second resolver attempt or repeated failed build.
   Retain the already proposed writable caches and disk-backed temporary area.
3. **Check affected imports in the repaired environment once.** One post-patch
   Papyrus22 and ProLIF26 import, with full tracebacks. This is not a repeat of
   their sole diagnostic imports on the old environment. Dependencies for other
   references are checked as part of their first execution, rather than a new
   repeated all-task root-import selection loop.
4. **The first native-reference pass, not a repeated pass.** There have been zero
   previous reference/scorer attempts in SAR30/SARA. Prepare the missing native
   orchestration and freeze its exact input/output/scorer mapping, attempt keys,
   limits and conformance matrix before running it. This implementation work is
   required; a ready full native runner is not claimed. Each of the fixed 30
   references has at most one execution attempt, with unchanged isolated native
   scoring. Identical-artifact scorer repeatability and invalid-artifact tests
   may run only according to that frozen matrix, never as reference refitting.

Continuing the first native pass still requires runtime validation. Avoiding a
qualification loop does not justify bypassing that unperformed validation.
An engineering acceptance pass alone is not permission to claim 24 qualified
tasks or a successful research result.

## Proposed fresh budget and clock

The prior account is closed; its unused allowance is unavailable. This is a
proposed new limited envelope, not a reset of the old 80/26 account.

| Work | CPU-hour cap | Allocated GPU-hour cap | Latest finish from new approval |
| --- | ---: | ---: | --- |
| Patch, direct-path inspection and frozen engineering acceptance | 2 | 0 | 8 elapsed hours |
| Artifact restoration and one unfinished preparation/import continuation | 5 | 0 | 24 elapsed hours |
| First native-reference pass and fixed scorer conformance | 6 | 2 | 40 elapsed hours |
| Full evidence return, verification, cleanup, report and main delivery | 3 | 0 | 48 elapsed hours |
| **Total ceiling** | **16** | **2** | **48 elapsed hours** |

At most four combined CPU equivalents (local one, dr-train up to three), one
GPU, local RAM 2 GiB and remote aggregate RAM 32 GiB. GPU allocation is permitted
only if an unchanged reference needs it and the device is available; no actor
inference/model loading or shared-service eviction. GPU time includes idle/load
time. Use CPU quota equivalents with an initial assigned core as previously
authorized. Limits and watchdogs must be evidenced before dispatch.

Use the retained verified benchmark and returned files. Ordinary missing
dependencies may be retrieved under a fresh cumulative 20 GiB receive cap and
80 GiB owned peak-disk cap; no new scientific inputs/model weights, paid services
or system permission changes. Estimate the fixed task schedule before dispatch.
Its remaining worst-case reservations must fit the native bucket and deadline;
otherwise stop before the first reference. No new hardware availability is
assumed from the previous bootstrap snapshot.

Reserve the three CPU-hour return bucket from the start. Do not spend it on
another build/reference attempt. These are ceilings, not timing predictions or
guarantees that the cohort can finish. Keep prior retained 10.833333333 CPU-hours
separate; no historical debit is erased. The projected prior-plus-new reserved
ceiling is 26.833333333 CPU-hours and two GPU-hours for these two accounts only,
not for the complete project history.

## Frozen pass and stop conditions

**Engineering pass:** every acceptance case passes in the actual retained image;
the mount root is not mutated; extracted payload hashes/link targets agree; no
Python-3.10-incompatible hashing call remains on the new direct setup path.

**Native readiness pass:** at least 24 native-valid locked tasks, 12 connected
source groups, three domains, no source over 25%, and unchanged native scorer
conformance/isolation. Development tasks are not counted toward the locked floor;
development wiring canaries must also pass before locked execution. Retain every
row and reason, including tasks not reached after a terminal stop. Source roles
and dependence are not changed to improve the count.

Stop scientific/preparation work and report immediately on:

- failure of the one frozen engineering acceptance matrix or a need for broader
  patch scope, added capability, a changed image or a different dependency recipe;
- failure of a mandatory development wiring canary, scorer isolation/parity or
  conformance; a reference failure on a locked task is recorded once and cannot
  trigger a retry, exclusion-driven replacement or tuning;
- an optimistic remaining locked-task/source/domain bound falling below the
  unchanged readiness floors; stop even before all 30 tasks if success is impossible;
- a stage/total/deadline limit, unbudgetable fixed runtime projection, unresolved
  integrity/rights/protected-outcome issue or required new scientific input;
- a need to refit a failed reference, change its scientific implementation or
  scorer, alter roles, reduce a coverage floor, or search a new model/dataset.

There is one patch candidate after freeze, one acceptance matrix, one continuation
recipe and one first-reference attempt per task. No automatic repair amendment,
second native pass, replacement cohort or CORE-Bench migration. A timed-out
transport first gets state inspection; it is not permission to replay work.
Evidence-transfer recovery may continue without restarting scientific attempts.

## Exit and owner checkpoint

If passed, deliver **READY_FOR_COMPARATIVE_STUDY**, including admitted/excluded
rows, reference and conformance evidence, measured timings, artifact hashes,
all failures and resource accounting. This is a technical milestone, not evidence
for an agent contribution or ESE/JSS readiness. Use the timings to propose the
unchanged matched action-by-verification study with a 25% contingency; do not
change the contrast after reference outcomes or turn reference results into
agent effect estimates. Do not restart cohort qualification in that next study.

If failed, deliver **NO_GO_TARGETED_CONTINUATION** with the exact terminal cause,
remaining NOT_RUN work and no proposal to spend the unused balance automatically.
Both exits return/hash-reread all owned persistent files before exact remote
cleanup, preserve frozen old records, and include a main commit/push if the
owner's new release authorizes that delivery.

Full agent experiments, product features and manuscript are **outside this
limited proposal**. They need a subsequent owner decision after actual native
readiness/timing evidence. Final16, private CF1 rows and old hidden outcomes
remain closed. No independent expert, clinical or customer validation is claimed.

## Primary technical references

- [Debian dpkg-deb manual](https://manpages.debian.org/bookworm/dpkg/dpkg-deb.1.en.html):
  --extract modifies target-directory permissions; --fsys-tarfile exposes the
  payload stream. Content-only extraction is our proposed implementation, not
  a guarantee provided by that manual.
- [Python hashlib documentation](https://docs.python.org/3.11/library/hashlib.html#hashlib.file_digest):
  file_digest was introduced in Python 3.11. A streaming SHA-256 loop avoids that
  API dependency while preserving digest semantics.

Next actor: owner. Decide whether to release this **16 CPU-hour / two GPU-hour /
48-hour targeted continuation**. The current request authorized investigation
and this proposal only; none of its runtime steps have run.
