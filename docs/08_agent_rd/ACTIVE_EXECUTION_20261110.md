# AgentRD active execution checkpoint

Status: **PROTOCOL_FROZEN_READY_FOR_MAIN_COMMIT; LOCKED_EVALUATION_NOT_STARTED**.
Owner authorizes continuous A0 -> A1 -> necessary A2 -> evaluation -> analysis
and manuscript. Do not stop at A0/A1 or seek another routine phase approval.
Negative findings still require the complete report/manuscript. No external
expert/researcher/customer/wet lab is a prerequisite or claimed validation.

## Released resources

Option A explicitly approved: fresh 96 CPU-hours / 120 hours, local one CPU /
1 GiB and one dr-train model worker up to three CPU equivalents / aggregate
12 GiB / swap0. Conservative start 2026-11-10 11:10:00 UTC; deadline
**2026-11-15 11:10:00 UTC / 18:10 Bangkok**. Never reset the clock.
Release: `research/manifests/agent_rd_release_20261110_v1.json`.
Local task: `.local/agent-rd-run-20261110-v1`; ledger is ACTIVE.

One remote phase envelope is already fully retained: admission 6,600 seconds
(6,000 container + 600 host-client upper allowance), development 36,000 and
evaluation 201,600. These are reservations, not measured consumption. Local
controller/engineering jobs use the implementation bucket; do not double-book
the fully reserved remote phase buckets. Bootstrap descriptor and rejected
prelaunch attempts are retained; no model attempt ran on the rejected booking.

## Actual completed checks

- ZIP identity/payload hashes and clean base main/origin `3fa17f0` confirmed;
  no existing A0 output found. Fourteen old ledger identities and 66 scientific
  pins preserved. One old inactive raw status still says AWAITING_OWNER_INPUT;
  it was preserved rather than rewritten to CLOSED.
- Source/API/persistence/CF1 reuse map and targeted primary-source matrix written.
  Original CF2 NO_GO and CF1 study limits unchanged.
- Isolated offline CPU-only Ollama 0.12.6 runtime admitted on dr-train, original
  Typhoon 12B digest pinned. No paid API, new model download or shared-service
  change. Actual tiny JSON-format inference passed with GPU VRAM zero.
- Initial controller prototype, typed aggregate bridge, numerical verifier,
  separate mission store, immutable dossier, additive API and EN/TH page added.
  **44 actual component/oracle/CF1 regression checks passed**. EN/TH frontend
  type/lint/build and30 tests PASS. One legacy asynchronous route test initially
  timed out in the full single-core suite, passed isolated reproduction, then
  passed the full suite after an explicit bounded lazy-route wait; all receipts
  remain. Browser acceptance is in progress, not yet passed at this checkpoint.
- First real development mission exhausted its three-call cap in repeated
  compute actions and abstained. 2,422.747 container CPU seconds, 4,347 recorded
  tokens; retained as a negative canary, not a successful agent task.
- Prompt/schema revision1 shortened redundant fields and clarified action
  shape. Its real canary still abstained: two values were source-correct but
  metadata was incorrectly placed inside the numeric map. 1,016.813 container
  CPU seconds, 3,062 tokens. This is not a locked result or a completed task.
- Revision2 is a common typed interface/state-eligibility repair before freeze:
  required report fields, only admitted numeric keys, no redundant read after
  trusted preflight, compute only while useful, last call terminal. Applies to
  every model control equally. The third real canary completed one call with
  source-correct numbers:575.502 container CPU seconds,729 tokens. It returned
  extra permitted values; task accuracy is separate from the source check.
- Six fixed actual development probes completed: two comparison controls,
  interpretation, forbidden request, real public-file deletion and controlled
  interruption/recovery. Five task passes; P failed the refusal task by returning
  permitted aggregate numbers rather than abstaining. No protected data was
  read. Recovery reused the one recorded real response without regenerating it.
  These small probes do not estimate locked or real-user performance. No
  further outcome-driven prompt search is planned.

Do not describe successful process exits as successful scientific missions.
Read `development-real-mission-v1.json` and `-v2.json` for actual dispositions.
Also read `-v3.json` and `development-coverage-v1.json`. The coverage job's
startup source snapshot is the executed-source record; filesystem identity
fields in later development rows are not a Python loaded-module attestation.
Minor working-tree engineering edits occurred during that job; no prompt
changed. Frozen locked code will not be edited while evaluation runs.

## Current completed acceptance and next launch

Actual browser -> API -> real model -> dossier acceptance PASS: mission
788428ed-b5b2-4743-af1b-6324b4a441ad, two calls,2,054 tokens,904.552 container
CPU seconds; the separate authored task score passed. Source/manifest reread,
actual API restart without regeneration, EN/TH/mobile and legacy isolation PASS.
No need to relaunch it. The UI refinement reused this exact real record without
new inference; latest `screens-v2` were visually inspected.46 backend checks,
30 frontend checks/type/lint/build PASS. Latest frontend receipt is v3.

The one-time freezer passed after one retained import-order lint failure (no
freeze/model launch on that failed attempt).27 code/protocol/input pins and408
planned units are now locked. **Do not edit pinned files**, including this
track's protocol, engine/provider/contracts/store/dossier, evaluator/scorer/
oracle/analysis/cases, supervisor, runtime worker/transport, freezer or
`.gitattributes`. Read the actual freeze manifest for the exact list.

No locked model call or EVALUATION phase transition has occurred yet. Next:
publish the actual example, audit/stage/commit the freeze on main, transition
the remote phase once, then run the fixed evaluation via the local supervisor.
The supervisor keeps evaluation orchestration and registered document helpers
inside the same one-core/1GiB Windows Job, allowing local guide preparation
while the three-core remote model runs. Its internal queue is not an agent
tool, public service or extra CPU/memory allowance. Do not launch another
independent local resource job while the supervisor booking is RESERVED.

## Pre-freeze study artifacts

`research/agent_rd_eval_v1` now contains32 locked and16 development cards,
separate direct-CSV oracle, scorer, real source-fault/recovery executor, fixed
408-unit schedule definition and prespecified analysis. Source numeric operands
are rounded before deltas. B0 engineering conformance already passed all32
authored cards before freeze; this known ceiling is disclosed, not a blind
result. No locked-card model output has been run. Three decoding seeds, B0/B1/
B2/P plus24 no-repair anchor units;312 actual model missions are planned.
No gold is given to the model. Cases are author-defined on exposed data, not
independent biological or expert-validated tasks. See the full computational
protocol for exact denominators, limits, resource stopping and interpretation.

Do not run the one-time freezer until readiness receipts exist. It materializes
and pins cards/gold/schedule/code. Commit the freeze to main before entering
the remote EVALUATION phase once and launching `agent_rd_evaluate_v1.py`.
The evaluator supports operational batches, immutable unit IDs and exact-ID
reconciliation; no successful-retry selection. Primary comparison is
inconclusive if the planned matrix cannot finish within the same budget.

## Owned remote runtime

Host SSH uses existing chaw profile at 100.77.149.83. Owned task root:
`/home/chaw/curaloop-tasks/agent-rd-20261110-v1`; owned container:
`curaloop-agent-rd-20261110-v1`. No host/public ports, network=none, CPU cores
69/70/71, three-core quota, model memory 11.5 GiB plus host Python 0.5 GiB,
swap0, read-only root and existing model mount. Source/model cache is reused
read-only and is **not owned**; never delete it or existing Ollama services.

Docker CLI initially failed under address-space limits before any remote root
creation. The working control transport uses the already-authorized Docker
Unix API directly, without increasing permissions or the total memory ceiling.
A watchdog inside the same container cgroup enforces phase CPU/deadline. Phase
is currently DEVELOPMENT; do not re-enter/reset it. Only after actual freeze
may the parent advance once to EVALUATION.

Remote `worker.py` is original bootstrap; `worker-v2.py` adds a serialized,
cumulative 600-second host-client guard. Its source/hash is versioned and retained.
Both must return with all calls/config/control files before exact owned cleanup.
Later source formatting changes must not be misreported as executed remote bytes.
No private rows, final16 or hidden outcomes are mounted or read.

## Next concrete work

1. Finish the already running real browser acceptance; preserve all outcomes,
   actual screenshots and any failure. No duplicate canary/probe/model job.
2. Run component check v4 for the operator-session deadline/config change and
   remaining scorer/API conformance. Repair only supported technical issues;
   preserve legacy simulator/Confirmation navigation and database schema.
3. Write/finalize a source-derived case manifest, independent CSV oracle,
   frozen scoring, model/config/prompt/code pins and fair controls. No gold in
   model context/tools. No LLM self-judge. No implicit biological independence.
4. Run the complete predeclared locked comparisons within the existing account;
   report negative/tied/inconclusive effects, all failure/fallback/cost cells.
5. Produce analysis, standalone figures/tables, English manuscript and realistic
   publication-readiness assessment, actual screenshots/operator guide, full
   remote return/reread before exact owned cleanup, final preservation/budget
   closure and normal main commit/push. Do not stop with a plan or A1 report.

The original resource proposal is an immutable approval-time snapshot. Any
nonredundant ablation/sample-cost refinement is fixed before locked execution
and documented transparently, never selected from locked outcomes. No larger
model, GPU, paid provider, new biological dataset, external write, public deploy
or manuscript submission is released by unused budget.
