# Reviewed v2 intake and research readiness

> Historical intake checkpoint. The missing-input gate was subsequently resolved
> through the owner's new Drive source. See [local integration](07_audit/LOCAL_INTEGRATION.md)
> and [foundation progress](06_execution/FOUNDATION_CHECKPOINT.md). The earlier
> search, access denial and unverified state below are preserved as dated history.

Date: 2026-11-04 (Asia/Bangkok).
Status: **BLOCKED: required Reviewed v2 files are unavailable locally.**

The existing localhost POC remains intact. This is an intake/readiness report,
not the Reviewed v2 literature review, protocol, package verification or a new
scientific result. No overlay has been applied and no new dataset or controller
has been introduced.

## Verified destination and authority

- Checkout: `C:\Users\User\Desktop\myProject\curaloop-rl`.
- Git root resolves to that checkout. Both origin URLs are
  `https://github.com/siriponsri/curaLoop-RL.git`, matching the owner's clarification.
- Intake base: `2d287a170b39b0c07d02631ca027c2ba535c0df9`; branch `main` was clean.
  Live `git ls-remote origin refs/heads/main` returned the same commit.
- Local intake branch: `docs/reviewed-v2-intake-20261104`. Continue locally;
  this intake does not publish, push, deploy or change access.
- No `curaloop-rl-git` directory was found at the inspected Desktop project or
  Drug Discovery locations. Do not replace this checkout with a ZIP source tree.

The source conversation [“อธิบายการใช้ AI”](https://chatgpt.com/c/6aea91cd-7364-83ec-9ee5-78617b192b54?messageId=13424946-b55f-547f-81c8-5651a8417c16)
was read through the supported conversation tool. It describes a proposed
pending-aware, deadline-constrained, multi-assay study with a later RL extension
and a research-service business path. Its statements about a reviewed package,
PDF counts and prior apply/checksum checks are source-conversation claims;
they were not independently reproduced in this intake.

The existing project's scientific and privacy invariants still apply. Plans do
not establish novelty, cross-target performance, customer demand or business
returns. GPU authorization is separate from live host access and resource
availability. No remote job is necessary for this documentation intake.

## Missing inputs and access boundary

The sending task reported an explicit Library content denial:
`HTTP 403 scope_violation`. No alternate download/materialization route was used.
Library identifiers below were supplied by that handoff; their contents and
checksums have not been read or verified here.

| Supplied item | Handoff Library identifier | Current status |
| --- | --- | --- |
| Docs overlay, Reviewed v2 | `libfile_c4b0a4ca594881919ea6648c3996957c` | BLOCKED |
| START_HERE_TH_v2 | `libfile_d499d9d7fc7c8191848f1d291416ecf8` | BLOCKED; read first when available |
| Literature_Review_v2 | `libfile_6dccf091c86881918f2eec3c021d2422` | BLOCKED |
| Academic_Business_Masterplan_v2 | `libfile_b8d32a4d4b8881918e370cf7ed38a7cd` | BLOCKED |
| Full Academic_Business_Reviewed_v2 package | `libfile_57e5b9accb988191ba216e9d58abafeb` | BLOCKED; private reading material is optional for initial docs intake |
| Checksums | `libfile_c03e0052cff481918c434fc333c5182f` | BLOCKED |

A filename search covered Downloads, Desktop, the local Drug Discovery folder
and Codex attachments, excluding generated dependencies and Git internals. No
matching Reviewed v2 overlay, start document, review, masterplan or checksum was
found. This is a bounded search, not a claim that no copy exists elsewhere.
The ordinary local Drug Discovery folder was empty when inspected.

Required next input: an owner-supplied local folder path or newly attached
overlay and checksum files. Standalone start/review/masterplan files are needed
only if they are not included in that overlay. Do not reconstruct missing package
content from the conversation summary or treat its download links as permission
to bypass the Library denial.

## Current implementation versus proposed research

This map describes inspected source at the intake base, not the missing v2 files.

| Area | Current inspected implementation | What remains to resolve from Reviewed v2 |
| --- | --- | --- |
| Tasks/data | `domain.py:DATASETS` allows the frozen HIV replay and two synthetic fixtures; HIV pool is limited to 1,200 molecules. | Select actual additional assays, sources, rights, label rules, deduplication and development/final task separation. No LIT-PCBA ingestion is implemented. |
| Scheduling | `engine.py:Campaign` exposes pending IDs, remaining budget, slots and step; accepted requests have deterministic due steps and reserve budget. | Define campaign deadline semantics and any new public timing fields without exposing hidden labels. `Scenario` has no deadline field. |
| Policies | Random, retrained Logistic Greedy, margin Uncertainty, frozen tabular Q-learning and contextual bandit. Pending IDs are excluded from eligibility. | Freeze the specific pending-aware ranking method, matched ablation and comparator settings. No named pending-aware or similarity comparator is implemented. Existing controllers already use a pending-occupancy state component, which is distinct from the proposed ranking comparison. |
| Evaluator | `evaluation.py` reconciles delivered hits, missing results, reservations and discovery area against **budget** from public events. | Specify `H(T)`, delivery-at-deadline boundaries, time-based curves, censoring and summaries before final experiments. Existing event steps could support a separate time evaluator, but it has not been implemented or validated. |
| Statistical unit | `benchmark.py` uses paired seeds within the same HIV assay, with exploratory contrasts; its separate predictor audit uses a custom scaffold split. | Define independent task/target groups, paired contrasts, uncertainty, primary metric and multiplicity for the new study. Seed repeats are not independent biological tasks. |
| Learned controller | Frozen checkpoints trained on synthetic tasks; recorded HIV runs used Greedy fallback for 300/300 requests per learned controller. | Define a new versioned training/reward/evaluation protocol if the reviewed plan requires one. Do not modify or relabel original checkpoints/results. |
| Business evidence | The current POC and provenance support a demonstrable engineering workbench. | Turn the reviewed service proposal into explicit hypotheses, interview/pilot criteria and rights boundaries. No customer interview, willingness-to-pay, prospective saving or commercial effectiveness was measured in this intake. |

Source references: [domain](../src/curaloop/domain.py),
[engine](../src/curaloop/engine.py), [policy worker](../src/curaloop/policy_worker.py),
[learning](../src/curaloop/learning.py), [evaluation](../src/curaloop/evaluation.py),
[benchmark](../src/curaloop/benchmark.py),
[current evaluation limits](EVALUATION.md),
[current data provenance](RESEARCH_BENCHMARKS.md).

## Safe integration sequence after input arrives

1. Recheck Git status, active writers and the exact origin/base. Preserve any
   newer owner edits. Read `CuraLoopRL_START_HERE_TH_v2.md` first, then the actual
   review, masterplan, overlay instructions and checksum file.
2. Inventory the archive before extraction. Reject absolute paths, path traversal
   and links that escape staging. Stage outside the checkout and compare all
   supplied checksums with actual bytes. Record missing/extra entries and preserve
   the supplied files as received. Checksums establish byte consistency, not
   scientific validity or redistribution rights.
3. Keep `reading_room_private/` outside Git. Prefer an owner-approved folder
   outside the checkout. Never stage a full source/package ZIP or private papers
   as a shortcut; maintain separate code, dataset and paper rights records.
4. Preview every proposed documentation change against this repository, including
   its later English POC, SQLite recovery, README, branding and PDF manual. Use
   an explicit document allowlist; do not blindly overwrite `AGENTS.md`, active
   operator guidance, source, data, checkpoints or evidence with archive copies.
5. Reconcile proposed scientific choices against the existing protocol. Resolve
   significant ambiguity with the owner before changing datasets, labels,
   rewards, training, timing semantics or evaluation. Create separately versioned
   protocols/artifacts and retain old unfavorable results.
6. After the actual plan is understood, select the first bounded research task
   that can be accepted independently. Freeze required data/rights/contracts and
   evaluator checks before large runs. Use CPU for small validation; do not infer
   that GPU authorization means GPU compute is necessary.
7. Before a dr-train launch, verify permitted host access, the actual allocation,
   active jobs, live capacity/conflicts and the existing shared OS GPU lock.
   Respect the shared resource rules and preserve Patent-to-Pilot/other work.
   Recheck at launch; no idle observation reserves the resource. Do not copy
   credentials. No remote resource check or allocation was performed here.
8. Validate links, rights/provenance, changed contracts and preservation; run
   checks appropriate to the actual diff. Record exact candidate/evidence and
   scientific/business limitations. Keep continuation local under this round's
   direction; do not infer publication from a completed intake.

## Evidence for this intake

Current results are in [the intake evidence folder](evidence/reviewed-v2-intake-20261104/).
The original 136 Python / 18 frontend results remain historical release evidence;
they are not claimed as a fresh full-suite rerun for this documentation intake.
The new boundary-test report and preservation record identify the checks actually
executed now. No new multi-target benchmark, training, browser capture, customer
study, paid service, remote GPU job or package application was executed.

The local Windows snapshot found no selected Python/Node/SSH process whose
available command line explicitly identified CuraLoop or dr-train, and no listener
on the inspected application ports 8000/5173/8501. Generic processes and active
Codex tasks existed. This does not establish that all remote jobs are absent or
that a GPU slot is available. No owner process was stopped.

Continue from this checkpoint once the actual Reviewed v2 documents are available.
