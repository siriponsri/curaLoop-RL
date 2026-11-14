# Prepared verification and scientific-agent reliability: bounded study proposal

Date: 14 November 2026, Asia/Bangkok.

Status: **DRAFT_FOR_OWNER_RESOURCE_DECISION / NOT_RELEASED**.

Working study name: **LR-SAR1**. This is a proposed name, not an active goal.

The owner has [accepted the contribution direction](SCIENTIFIC_AGENT_RELIABILITY_DIRECTION_DECISION_20261114.md),
but has not approved this protocol, expenditure, downloads or experimental access.
Current research accounts remain closed. Baseline source checkpoint:
`f42d8aa8edeb2ef40b73a2cdc040dcebda07ed6b`.

## 1. Question, contribution and intended paper

Primary question:

> Does providing a prepared executable implementation of public requirements
> change native scientific-task completion compared with fully specified written
> check definitions, when model, public inputs, ordinary execution tools and
> inference limits are matched?

The intended contribution is an external empirical extension of prepared-check
research, with an explicit analysis of the gap between local check validity and
native task completion. It is not a new verification algorithm or new benchmark.
The distinction from [Rules to Tools](https://arxiv.org/abs/2610.00313) must cover
the scientific/task population, end-to-end generation rather than only repair,
interpretable disagreement evidence and costs. A dataset substitution alone is
not treated as sufficient novelty.

The pharmaceutical workbench supplies an application example and evidence
viewer. The paper's primary claim concerns scientific software agents, without
claims of pharmaceutical efficacy or business/user benefit.

## 2. Data identity and additional access requested

Candidate: existing official ScienceAgentBench verified release, 30 April 2026.
Use the retained annotation revision
`9c6e96c9e74572e979b0930ee735041cef528cb7` and archive:

`research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip`

Historical receipt: 1,769,478,786 bytes; SHA-256
`46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
The local file existed with this length at the preceding review; no new full
integrity reread is claimed. Do not redownload a matching retained archive.

The [retained structural inventory](../evidence/lr-dc2-20261111-v1/dataset-annotation-intake-v1.json)
contains 102 rows: 20 computational chemistry, 27 bioinformatics, 27 geospatial,
28 psychology/cognitive-science. These are not 102 admitted independent tasks.

Requested future access, if released: structural/source/scorer inventory of
these tasks; public task/input inspection; exact-scope archive extraction; and
isolated native reference/scorer execution. Benchmark gold/reference values stay
in the evaluator, unavailable to candidate agents and checker/prompt authoring.
This request concerns new ScienceAgentBench evaluation access, not permission
to open old CuraLoop final16, private CF1 rows or other protected outcomes.

Respect the [official source](https://github.com/OSU-NLP-Group/ScienceAgentBench)
and source-specific licenses. No unpacked dataset redistribution. Exclude paid
visual judges, required online services and tasks outside the execution envelope.
A mandatory GPT-4o rubric must not be silently replaced by a local judge.

## 3. Admission before inference

### G0: metadata, rights, scoring and exposure inventory

Create one 102-row census before native reference runs. Record task ID, domain,
source publication/repository lineage, previous exposure, native success interface,
mandatory judging services, dependency/environment recipe, output type, rights,
and exclusion reason. Preserve unresolved entries as UNKNOWN, not admitted.

Use the previous [exposure register](../evidence/lr-dc2-local-20261113-v1/source-exposure-register-v1.json)
and [admission records](../evidence/lr-dc2-local-20261113-v1/native-admission-final-v1.json).
Distinguish metadata inspection, engineering-only private qualification, author-
visible solution/gold, and actual checker/prompt development. Keep all old
exclusions. Engineering-only execution is neither automatic leakage nor proof
of complete development-unexposure. Shared datasets/repositories/publications
remain together where known; unresolved relevant links are quarantined.

If the census cannot possibly support the coverage floor below after development
and exposure exclusions, stop before gold execution, model download or inference.
Do not remove exclusions or add another dataset to reach the target.

### G1: fixed native/environment qualification

Use upstream task-specific dependency recipes, identified before outcome-based
debugging. Keep exact environment definitions, failed builds and resource costs.
The old eleven-task wrapper is not presumed to reproduce the full native harness.

For admitted tasks preserve the official binary success predicate. Separately
disclose omitted secondary metrics, such as CodeBERT similarity. Confirm that
the deterministic success path has no mandatory paid judge. No grader/tolerance,
reference-program or gold-output surgery is allowed.

There is one initial qualification pass and at most one bounded correction batch
for objective implementation/environment defects supported by upstream source.
It may address distinct predeclared environment recipes; it is not an unlimited
package/version search. Retain the original errors and exact patch/affected set.
No third qualification pass or task replacement. A failed task stays excluded
with its reason. Predefine stability/replay checks and their cost in this pass.

Proposed conservative coverage floor: **60 locked tasks, 15 source-lineage
clusters and three domains**, after role assignment. These are planning coverage
requirements, not a power calculation or a guarantee of publishability. They
retain the supplied review's broad-study intention; the corrected precision
limits are disclosed below. A smaller study would require a different owner
scope decision, not an automatic relaxed fallback in this account.

### G2: development, implementation qualification and throughput

Select up to eight development tasks by a deterministic ID/lineage rule frozen
before model output. Existing development roles remain development. Quarantine
all connected development clusters from the locked study. Native qualification
only provides evaluator health evidence, not a candidate performance result.

Freeze checker construction from public requirements. Check declared public
criteria, probes, tolerances, applicability and unavailable/error behavior.
Validate implementation conformance on development and constructed software
cases. Constructed faults cannot become natural primary agent failures.
No locked gold or grader-derived answers may shape the prepared checks.

Checker eligibility and public-binding rules must be frozen independently of
candidate success. Retain every prospective exclusion and denominator. If a
locked checker fails technically after freeze, retain the task with a recorded
unavailable tool under the assigned-support estimand; do not silently replace it.
Report supplied-check availability so an unexercised mechanism remains visible.

Development model cap: 32 missions, 96 provider calls, at most 4,096 generated
tokens per mission across calls. No model search or performance-selected checkpoint.
Freeze once after development. If context, truncation, throughput or meaningful
check coverage makes the intended study untenable, stop before locked inference;
do not enlarge limits automatically or choose an easier locked task set.

## 4. One proposed model and hardware envelope

Proposed fixed model:
[Qwen/Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct),
official unquantized checkpoint. The preceding review checked Apache-2.0 and an
approximately 15.2-GB repository. Pin the exact revision/tokenizer/weights and
runtime before inference. No automatic quantization/model substitution.

Requested maximums: four combined CPU equivalents, one GPU, remote RAM 32 GiB,
local RAM 2 GiB, task-owned persistent storage 100 GiB. Initial work allocation
is local one CPU plus remote three; one GPU worker only. V100 32-GB availability
was historical, not a current reservation. Fresh read-only inventory is a future
release task. Do not evict jobs, alter shared services, grant privileges or change
host permissions. Failure to fit the selected model/context ends preflight.

Requested transfer caps: 20 GiB new model files and 30 GiB dependencies/container
layers combined, within the 100-GiB owned storage cap. Reuse existing lawful cache
bytes only after identity checks. No substitute benchmark download. These are
ceilings, not estimates of required consumption or permission granted now.

## 5. Comparison matrix

| Arm | Definition | Role |
| --- | --- | --- |
| R | Official reference program in isolated evaluator | Health/sanity only; not a competing solver |
| L | LLM receives public task and initial public observations; no interactive execution | Secondary context control |
| G | LLM + ordinary filesystem/Python tools and fixed self-debug procedure | Secondary generic-tools control |
| T | G + complete textual public check definitions, including probes/tolerances/applicability | Primary matched control; may write/run its own checks |
| P | T's criteria + ready-to-call implementation | Primary prepared-support treatment |

A full deterministic solver is not invented as a benchmark baseline. Where an
actual general deterministic workflow exists, report its prespecified scope
separately; reference solutions do not qualify as such a workflow.

T/P share public requirements, task inputs, ordinary tool capabilities, initial
artifact condition, one model, decoding, calls/output/context ceilings and total
mission limits. The intended difference is access to a prepared implementation.
Expose corresponding rule and tool descriptions; disclose context-token
differences instead of falsely claiming byte-identical prompts. Preparatory
checker work and validation are part of the total cost of the treatment.

One fixed near-deterministic decoding run per task/arm; no best-of-three.
No claim of independent seed replication. Proposed mission limit: three model
calls and 4,096 total generated tokens, with full prompt and generation counts.
Proposed context ceiling: 16,384 tokens including reserved output. Freeze a
shared history-management rule on development; never drop scientific requirements
from one matched arm to make its prompt fit. Inability to fit the intended
public specification is a pre-freeze feasibility issue, not a post-result edit.
Timeout ceilings: 30 minutes per agent mission, five minutes per interactive
tool call, official final-evaluator limits where applicable. Record premature
termination and final evaluator availability separately. Resource projection
must cover these costs; limits do not promise every mission will consume them.

For N locked tasks, the matrix is 4N missions, conservatively no more than 408
missions and 1,224 provider calls, plus the separate fixed development maximum.
Freeze exact IDs, arm execution order, prompts, dependencies, checks, scoring,
limits, paths and analysis code before any locked generation. Balance paired
arm ordering deterministically; retain caching/load effects in cost interpretation.

## 6. Outcomes and analysis

Primary estimand: task-weighted mean `native_success(P) - native_success(T)`
over the prospectively admitted locked cohort. No general pharmaceutical or
all-ScienceAgentBench population claim. Source-weighted effects are secondary.

Report paired wins/losses/ties/both-fail, every missing or NOT_RUN unit, native
success rates and a source-cluster-respecting 95% interval. Resample source
clusters with paired tasks together; declare finite/few-cluster limitations.
Do not treat decoding runs, checker calls or provider responses as independent
tasks. Use all frozen attempted assignments; do not select completed successes.

No p-value, positive-effect or post-hoc meaningful-effect threshold gates
completion. Native failure remains failure when local checks pass. NOT_RUN or
unavailable scoring remains explicitly missing, not a fabricated binary score.
Report complete-pair coverage and conservative missing-outcome bounds when
appropriate; an incomplete native matrix cannot establish the intended effect.

Precision disclosure before freeze: under an illustrative independent paired
approximation, `SE ~= sqrt((q - delta^2)/N)`. At N=60 and delta=0, normal 95%
half-widths for discordance q=0.1/0.25/0.5/1 are approximately
8.0/12.7/17.9/25.3 percentage points. Source dependence can widen uncertainty.
These are analytical scenarios, not measured rates or the final estimator.
Prespecify additional dependence scenarios once source sizes are known, before
candidate output. The nominal floor does not guarantee detection of small effects.

Secondary outputs:

- Frozen local-check/native 2x2 outcomes for both T and P final artifacts.
- Native failure despite local validity, with reproducible failure categories.
- Checker invoked/unused/unavailable, feedback and repair opportunities.
- Execution, output/schema, numerical/source validity and task completion.
- Abstention, fallback, invalid response, truncation, timeout and interruption.
- Model tokens/calls, tool/evaluator CPU, allocated GPU, wall time and preparation.

Run post-study local diagnostics on T without returning them to its agent.
Native success is an operational benchmark endpoint, not universal scientific
truth. Local/native disagreements are not automatically hallucination or false
certification. Author error analysis is labeled author analysis, never independent
expert validation. Review all defined disagreement categories, not only anecdotes.

## 7. Fresh resource proposal and allocation

**Proposed new ceiling: 160 CPU-hours + 80 allocated GPU-hours / ten elapsed days,
maximum four combined CPU equivalents / one GPU. None is approved yet.**

| Stage | CPU h | Allocated GPU h | Elapsed allocation | Release rule |
| --- | ---: | ---: | --- | --- |
| G0/G1 census and native qualification | 24 | 0 | Days 1-2 | Stop early at impossible eligibility/rights/scoring/coverage |
| G2 fixed development and throughput | 24 | 8 | Days 3-4 | Only after native/role coverage passes |
| Frozen four-arm matrix | 80 | 64 | Days 5-8 | Only after measured projection and freeze |
| Reproduction/analysis/return audit | 24 | 4 | Day 9 | Retain failures and incomplete scope |
| Manuscript, limited evidence-view integration and delivery | 8 | 0 | Day 10 | No full UI redesign or broad new product features |
| Explicit GPU contingency, within total | 0 | 4 | Within the same ten-day deadline | Execution overhead only; no new science/model/tasks |
| Total | 160 | 80 | Ten days from a later actual release timestamp | No automatic extension |

All administrative/build/download failures, model startup, idle GPU leases,
checker qualification, tool execution, failed calls, audit/return and unmetered
allowances must be retained. A reservation is not measured CPU use. Preparation
not fully measurable is disclosed as unknown/retained, never zero.

Before the locked matrix, project remaining inference, tool/evaluator, return
and analysis cost from development timing, including **25% contingency**, against
both total and stage ceilings. If it does not fit, stop before evaluation.
Do not select fewer favorable tasks or delete comparison arms to fit the cap.

No outcome-driven retries. Persist raw responses before controller processing;
recovery may consume exact persisted bytes without regeneration. An actual
post-freeze defect stops the affected execution and is reported. No automatic
second locked matrix or altered scientific result; remaining work is truthful
analysis/closeout unless the owner separately changes scope.

## 8. Bounded progression and completion

One eventual resource release would allow automatic progression through passing
gates, without asking at every phase. The ten-day clock starts only at that
release, not at this direction decision or document creation.

| Event | Required disposition |
| --- | --- |
| Rights, paid native scorer, exposure or coverage cannot qualify | Stop before further expensive work; produce eligibility/admission report |
| Model/hardware, check support or throughput cannot fit | Stop before locked inference; produce feasibility report |
| Frozen matrix completes with favorable effect | Analyze and write the same bounded empirical manuscript; no superiority beyond scope |
| Frozen matrix completes with null, unfavorable or broad-uncertainty result | Analyze and finish the same negative/inconclusive manuscript |
| Matrix interrupted/incomplete | Report all attempts, NOT_RUN units and non-estimable or bounded effects; no selective completion claim |

No substitute benchmark, model search, protected-outcome access, paid API/rental,
external team writes, public deployment, outreach or manuscript submission.
Large scope/rights changes require owner decision. Preserve the same failures
and ledgers; do not reopen old accounts. Return and hash-reread the exact owned
remote files before exact cleanup, leaving shared models/services untouched.

## 9. Deliverables and publication

For a completed comparison: signed-off protocol/freeze, census and exposure roles,
environment/model identities, text/check equivalence audit, raw model/tool traces,
native/local scores, resource ledger, analysis code, tables/figures, limitations,
English manuscript and rights-aware reproduction instructions. Use only public
or legally releasable artifacts; retain private benchmark/gold data separately.

For failed admission: complete attempted-scope/failure report, exact receipts,
unrun-study list and evidence disposition. That branch closes the bounded goal
but does not deliver the intended comparative paper. No promise of a journal-
ready article from a qualification failure.

For the product: reuse the existing pharmaceutical workbench. Add only a limited
EN/TH evidence view/export if needed to show recorded check/native statuses,
missingness and artifact versions. Saved results must not be presented as a live
agent. Broader product work remains a separate decision.

Target fit: [Empirical Software Engineering](https://link.springer.com/journal/10664/aims-and-scope)
for empirical verification/reliability and replication. Its standard no-fee route
was checked in the preceding review; confirm current author requirements at
actual packaging. Journal fit/acceptance remains uncertain. The existing AgentRD
study is motivation and prior evidence, not new external confirmation.

## 10. Consolidated owner decision still needed

Approve or revise this **single conditional study package**: fresh numerical
budget/deadline, CPU/GPU/memory/storage limits, one fixed model/download cap,
expanded ScienceAgentBench access and isolated native-gold execution, coverage
floor, freeze/stop rules, complete negative/inconclusive reporting, exact return/
cleanup and eventual commit/push of the new study artifacts. No part is released
by the contribution-direction acceptance alone.

Until then, the state is **DIRECTION_ACCEPTED / EXECUTION_NOT_AUTHORIZED**.
The proposal was written and locally link/consistency checked; no new native
reference run, source-data qualification, SSH, inference or download occurred.
