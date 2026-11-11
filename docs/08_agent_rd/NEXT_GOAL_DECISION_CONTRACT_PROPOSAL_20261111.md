# Proposed next goal: LR-DC2

**Status: PROPOSED_NOT_RELEASED.** Prepared 11 November 2026, Asia/Bangkok.
No new goal/account, SSH session, model download, benchmark intake or inference
is started by this proposal. The completed AgentRD v1 account remains closed.
Baseline delivery: main `156593fc6bfeb5176cf00d52f0b540ff6dddacc3`.

## Decision and intended contribution

Run one bounded investigation of **question-conditioned executable contracts
and counterexample-guided repair for pharmaceutical analysis agents**. Its
deliverable is a method/application paper with actual external-task evidence,
or a complete negative/inconclusive report if the proposed mechanism fails.
An external benchmark is an evaluation instrument, not our publication product.
Do not repeat the 408-unit CF1 study or revive the rejected RL/CF2 claims.

Working question: can a controller improve complete, scientifically admissible
task execution over a strong, equally budgeted LLM-and-tools self-debugging
agent, without merely increasing abstention or receiving privileged answers?

The candidate contribution has three concrete parts:

1. Compile a user task into explicit obligations on entities, data roles,
   units, requested outputs, denominators, input/output lineage and admissible
   claims. The compiler uses public task instructions and a fixed operator
   vocabulary; its output is also checked, rather than presumed correct.
2. Bind each obligation to actual execution evidence. Return actionable
   counterexamples such as wrong cohort, missing requested comparison, wrong
   denominator or unsupported scope. Permit bounded targeted repair using only
   the same evidence/tools as the control, then release or explicitly abstain.
3. Measure native external-task completion and false certification, separating
   natural mistakes from constructed integrity faults and counting every repair,
   fallback and failure. Include the strong numerical/source-only v1 gate.

This is a **candidate** method contribution, not a certified novelty claim.
Generic tool use, provenance, executable verification, self-debugging and
selective abstention are established. A formal contract definition or a plugin
alone does not establish novelty. Gate 0 must identify a specific substantive
difference from the closest prior methods before building it.

Example: correctly copied values can still compare different test populations,
use the wrong denominator or omit the requested comparator. The proposed
controller must identify the missing obligation and recover the requested
analysis, not simply replace every uncertain answer with a refusal. It cannot
certify unrestricted scientific truth from an arbitrary natural-language answer.

## Why v1 is preserved rather than repeated

V1 completed 408 units. P and B2 both succeeded on 67/96, with identical output
sequences on all 96 pairs. Neither produced a terminal numerical/source-invalid
proposal for that repair branch to act on. P nevertheless failed 13/78 tasks
with a valid source check. B0's complete structured reference already had a
known ceiling. Increasing its seeds or generating more variants of those cards
would not resolve the task-semantic and external-validity gaps.

The old 32 cards, development probes and current product failure are exposed
design evidence, not a new holdout or independent validation set.

## Three milestones within one released goal

| Milestone | Work | Exit |
| --- | --- | --- |
| 1. Contribution/data/resource admission and freeze | Closest-work comparison; actual external-task/rights inventory; group split; separate oracle; one bounded development calibration; exact protocol/source/model freeze | GO once, or stop early with a documented reason; no open-ended dataset search |
| 2. One implementation and one locked evaluation | One contract mechanism; matched controls; fixed matrix and isolated ablation; actual calls, artifacts, errors and costs | All planned units receive a disposition; no tuning/replacement trials after freeze |
| 3. Analysis, localhost integration and manuscript | Prespecified primary analysis; risk/coverage/cost and mechanism audit; clean-environment replay; EN/TH plugin demo; English manuscript update and venue assessment | Complete package and owner decision; no automatic new study or submission |

Progress automatically between passed gates if the complete proposal is
approved. Report milestone results; do not request routine phase approvals.
Material changes to resources, source rights, task population or mechanism
require a consolidated owner decision, not silent substitution.

## Data plan: use published external tasks

**Primary candidate: ScienceAgentBench, verified release**, restricted to
computational chemistry/bioinformatics tasks with programmatic native scoring.
Its official repository records a verified update on 30 April 2026. Its overall
suite has 102 tasks from 44 publications; these totals are not our admitted
subset or a claim that 32 eligible tasks have already been checked.

Target **8 development tasks plus 32 locked tasks**, separated by source
publication/repository/data lineage, not by paraphrasing the same source task.
Development must span at least three separate source-publication clusters.
The locked population must span at least eight source-publication clusters and
two computational workflow types, with at least 16 directly molecular or
cheminformatics tasks. These are prospective feasibility requirements, not
asserted inventory or a power calculation. If they cannot be met, stop at
admission; do not silently relax them or build a replacement benchmark.

Select eligible groups using a published stable hash order before any candidate
model outcomes. Record all inclusions/exclusions. Do not select tasks for a
known favorable leaderboard score or because the candidate fails or wins.
Development and locked groups must not share the same underlying dataset or
task-specific solution. If the dependency graph prevents that split, report it.
Public benchmark exposure and possible pretraining contamination remain limits;
this is not a newly private blind benchmark.

Exclude tasks requiring paid/model-based image judges, live websites, wet-lab
actions, new deep-model training or unbounded jobs. Accept only tasks for which
the native reference/evaluator works inside a fixed CPU/time envelope. Do not
replace a native scoring rule with one favorable to our contracts. Report
adapted harness differences and do not compare our subset score to the full
official leaderboard as if they were identical protocols.

The generator receives only the public task and permitted inputs. Reference
solutions, hidden tests and scoring gold remain in a separate evaluator, never
in compiler prompts, tool feedback or model-visible mounts. They are new
benchmark evaluation assets, distinct from protected CuraLoop final16. Locked
native scoring is released only after system/protocol freeze. The owner would
be authorizing that separate benchmark access through this proposal.

CF1 remains a product/regression case only. No new ChEMBL family-cohort design,
assay pooling, private CF1 rows, original final16 or hidden simulator outcomes.

**SMDD-Bench is not automatically added.** Its paper-supported molecular tasks
are scientifically interesting, but the full suite adds Boltz/ADMET dependencies,
prediction-oracle interpretation and unresolved archive/version/rights checks.
That would be a different study. No artificial fault track substitutes for
natural performance on the primary external tasks.

## Method and controls

| Arm | Definition |
| --- | --- |
| D | Strong deterministic workflow/operator library on all selected tasks; complete published coverage and unsupported cases; no per-task gold hardcoding |
| L | Same model and initial public task/input description, no interactive tool execution; this secondary contrast explicitly changes tool availability |
| T | Same model/tools/runtime as the proposal, with executable-error feedback and generic self-debugging; no task-contract feedback |
| S | T plus a numerical/source-only gate, comparable to the old mechanism but adapted transparently to the new artifacts |
| C | T plus the proposed task contracts and targeted repair; primary comparison C minus T |
| C-no-feedback | Same contracts and release gate, with diagnostic content withheld during the same permitted repair opportunities; fixed eight-task anchor subset |

No contestant reads the separate oracle. C may not receive gold values or a
larger generation/search budget. T is a genuine self-debugging control, not an
intentionally weak agent that cannot inspect its own execution errors. Every
model arm has the same maximum three generations, 1,024 output tokens per
generation and 8,192-token context ceiling. Tool-enabled arms have the same
maximum six tool actions. Their actual paths may differ; matching limits does
not imply identical realized costs or observations after different actions.
An unused repair opportunity is still reported. Do not secretly add a repair
call after a final invalid response or count a deterministic replacement as
model success. Parser failures, cap hits and false refusals remain failures.
If compiling the contract requires model generation, that generation is part
of the same three-call budget, not a hidden extra model or helper call. A
deterministic compiler uses only its frozen public operator vocabulary. No
gold-derived task-specific assertion is installed in the production controller.
Generated-artifact execution is bounded to 60 cumulative CPU seconds and 4 GiB
per mission, with at most 60 elapsed seconds for any one execution action.
Native reference/scoring feasibility is checked against that envelope before
model outcomes are used; every execution and evaluator cost counts globally.

One mechanism only, at most one common interface/prompt revision on the fixed
development set. Then pin task IDs, source assets, prompts, compiler/operator
rules, control implementations, model artifacts, task order, output limits,
scorers, analysis and stop rules. A scientific change after locked scoring
invalidates that run as confirmation; preserve it and stop rather than rerun
until a win. Exact-ID recovery of the same cached call is not a new trial.

## Fixed experimental size and uncertainty

Two preselected checkpoints: existing Typhoon 12B Q4_K_M and one Qwen2.5 14B
Instruct Q4_K_M official GGUF artifact, pinned before inference. The second
checkpoint provides a different model family; it is not selected by pilot wins.
No fine-tuning, large model search or paid provider fallback.

The planned main model matrix is 32 tasks x 2 models x 3 decoding seeds x four
model conditions (L/T/S/C) = **768 real-model missions**. The fixed eight-task
C-no-feedback anchor study adds 48, giving **816 model missions**. D runs on
all 32 tasks; deterministic repetitions, if used for timing, are not independent
scientific cases. Development is capped at 96 provider calls total. Across the
entire goal: at most 2,600 provider calls and 3 million generated tokens,
including failures, repairs and calibration. No best-of-seed selection.

Primary endpoint: native programmatic task success, averaged over three seeds
within each task and equally over the two models, then over tasks. Official
success is not replaced by our contract's own approval. Report task-weighted
and publication-balanced effects, both model-specific effects and all units.

Use paired uncertainty resampling at the source-publication/dependency cluster,
keeping each task's models/seeds together; publish the exact resampling rule
before evaluation. These are computational repetitions, not biological
replicates. With 32 tasks and a limited number of source clusters, intervals
may be wide. This budget does not guarantee power for a ten-point difference.
No optional extra sample is triggered by the observed interval.

Secondary outcomes: false certification (contract accepts but native task
fails), incomplete-task releases, required-output coverage, legitimate-task
abstention, appropriate abstention where defined, risk versus answer coverage,
matched-coverage random abstention, malformed outputs, token caps, successful
repairs, reproducibility, CPU/GPU/wall time and total all-attempt cost.
Uncertifiable does not automatically mean false. Constructed integrity probes
are a separately labeled engineering track, never pooled into the natural
primary effect. No LLM judge is the primary oracle.

## Prospective gates and success criteria

These are proposed engineering/research decision thresholds for owner approval,
not clinical benefit thresholds, journal rules or thresholds learned from a
new pilot.

| Gate | Predeclared decision |
| --- | --- |
| 0: genuine distinction | Source-located comparison identifies a specific task-contract/repair mechanism beyond generic provenance, self-debugging and refusal; no task-specific hidden-answer code. If already equivalent to prior work, NO_GO before model evaluation |
| 1: admissible external evidence | Required 8/32 group split, at least eight locked publication clusters, at least 16 molecular tasks, native programmatic oracle and clear use/redistribution scope. If not, DATA_NOT_READY and stop; no automatic substitute corpus |
| 2: technical feasibility and natural opportunity | Fixed development T runs expose at least four naturally occurring execution-valid but task-invalid outputs across at least three development publications; the compiler checks are exercised without injecting the primary mistakes. Correct artifacts must also pass so an always-rejecting contract cannot qualify |
| 2: cost/format feasibility | Fixed development input/action schemas work; malformed generation rate at most 10%; measured timing plus 25% margin projects the complete fixed matrix inside its remaining CPU/GPU stage envelopes. Otherwise stop; no silent shorter matrix or model swap |
| 3: complete, auditable evidence | Every planned unit has a disposition; all attempts/failures retained; no protected-data access; no source/scoring drift or privileged feedback. Resource-limited missing units cannot be omitted from results |
| 4: positive method signal | Primary C minus T at least +10 percentage points, positive direction in both checkpoints, and the clustered 95% interval excludes zero. C must also outperform S directionally; otherwise a numerical/source-only gate may explain the effect |
| 4: mechanism and usefulness | Repair ablation supports the proposed contribution or the paper narrows the mechanism claim; false-certification risk and correct-answer yield are reported at matched coverage. A lower wrong-answer count achieved only by more refusals is not a method win |
| 4: cost guardrail | For a cost-efficient method claim, all-attempt model tokens per native successful task at most 1.5 times T. If either arm has zero successes the ratio is undefined and cost efficiency is NOT_ESTABLISHED; do not turn that into a false ratio or let it erase an otherwise measured efficacy result. Report actual wall/CPU/GPU costs separately |
| 5: manuscript readiness | Distinct mechanism, domain-relevant external evidence, valid controls/uncertainty, clean-environment deterministic replay, complete failures/limits and compatible journal scope/fees. Passing a p-value threshold alone does not pass this gate |

If the point effect is positive but uncertainty crosses zero, label INCONCLUSIVE.
If there is no advantage, record NO_INCREMENTAL_BENEFIT. If feasibility fails,
deliver the admission/development findings and unrun-task list. All outcomes
close this released scope; none automatically opens LR-DC3 or another tuning loop.
The owner may approve a separate investigation later, with the original evidence
retained. The scientific result does not have to win to be reported completely.

## Proposed fresh resources: one approval, no borrowing

**64 CPU-hours + 24 GPU-hours, within 168 elapsed hours (seven days) from
approval.** CPU-hours and GPU-hours are separate ceilings, not interchangeable
money or a promise of runtime. Maximum four CPU cores combined: local one
core/2 GiB, remote up to three cores/32 GiB/swap0. One GPU worker at a time,
one owner-allocated GPU with at least 24 GiB VRAM; checkpoints loaded serially.
GPU-hours count allocated elapsed GPU-worker time including loading, failed
attempts and idle allocation; retain unknown-cost failures conservatively.
Record actual process CPU and GPU time/VRAM/utilization separately.

| Bucket | CPU-hours | GPU-hours |
| --- | ---: | ---: |
| Literature/data/resource admission | 8 | 1 |
| Contract implementation and isolated tests | 12 | 0 |
| Fixed development/calibration | 6 | 3 |
| Locked matrix and ablation | 22 | 18 |
| Analysis, figures, product and manuscript | 8 | 0 |
| Complete return, exact cleanup and delivery | 4 | 0 |
| Technical failure reserve | 4 | 2 |
| Total | 64 | 24 |

GPU availability/identity has **not** been verified in this proposal. Admission
must identify an available owner-allocated device without evicting another
project. If unavailable, report BLOCKED_RESOURCE_ADMISSION before a long run;
do not silently fall back to multi-day CPU inference, rent hardware or change
machine configuration. Using the GPU is a new permission, not inherited from
the closed CPU-only v1 grant. No GPU training, Boltz run or paid API is proposed.

Proposed downloads: one official Qwen quantized checkpoint up to 12 GiB;
external benchmark archive/input assets up to 4 GiB compressed/12 GiB expanded;
necessary isolated environment dependencies up to 6 GiB; total new download
cap 22 GiB and task-owned disk cap 48 GiB. Metadata-only admission precedes
bulk transfer. If access or size exceeds this scope, present the exact combined
download/resource decision; no purchase or hidden alternate dataset.

Generated analysis code may execute only in new task-owned isolated workers
with no protected repository/raw-data mounts, credentials, privileged mode or
network during execution. Host files and other services remain unavailable.
This is an extension beyond the old fixed read/compute adapters and therefore
is included explicitly in the new approval request. No system permission or
global service changes are authorized by it.

Reserve a fresh named task/account after approval; never reopen the old ledger
or recreate its deleted root. Preserve all prior pins, negatives and statuses.
Enforce the original new deadline and both ceilings from admission onward.
Administrative work and measurement limitations must be disclosed; do not turn
reservations into a fabricated measured-consumption claim. Full owned remote
return/reread precedes exact cleanup. Retain shared model caches/services.

## Publication/product finish and boundaries

Deliver a versioned contract library/plugin, localhost EN/TH demonstration,
native external-task results, every attempted trace/failure (privately where
source terms require), rights-cleared public evidence/manifests/fetch scripts,
analysis, figures/tables and complete English manuscript. Reproduce scoring in
a new clean environment without new inference; do not call that independent
expert validation. Do not redistribute ScienceAgentBench's unzipped archive or
hidden tests against its official request. Per-task/source terms control any
public trace excerpts and data redistribution; an MIT code license does not
override them.

JCAMD remains a **conditional** target only if the work advances a computational
strategy for molecular analysis/design with adequate retrospective evidence.
Its subscription route may fit the owner's US$300 publishing budget; finance
does not establish scientific fit. If only generic agent reliability is shown,
do not force that into a molecular-method claim. Venue choice is an owner
decision on the actual evidence. JOSS is not an immediate promised fallback:
its current screening requirements include more than six months of public
development history and demonstrated research use.

No wet lab, external researcher or customer pilot is required for this solo
computational scope. No biological efficacy, user productivity, commercial
ROI or general-purpose scientific truth is inferred. No final16, private CF1
rows, old hidden outcomes, public deployment, external team writes, paid API
or manuscript submission. Any negative/inconclusive result still yields a
complete report, not an incentive to search for another positive experiment.

## Primary sources checked for this proposal

- [ScienceAgentBench paper](https://arxiv.org/html/2410.05080v3), selected
  formulation/evaluation/domain/source-license sections; [official repository](https://github.com/OSU-NLP-Group/ScienceAgentBench),
  verified-release, scoring, access and redistribution notes.
- [Structured tool validation and runtime-monitor study, v3](https://arxiv.org/html/2604.16706v3),
  selected structured-validator and Section 7 runtime-monitor text. Preprint;
  already studies same-coverage abstention and wrong-argument propagation.
- [Misattributed numerical claims, v2](https://arxiv.org/html/2610.38691v2),
  selected checker/provenance and limitations text. ArXiv source inspected;
  publisher acceptance status not independently verified.
- [SMDD-Bench paper](https://arxiv.org/html/2605.21740), selected task definitions,
  oracle/setup and Appendix B.1; [official repository](https://github.com/t7rs/SMDD-Bench),
  download/dependency notes. Candidate alternative reviewed, not selected.
- [Official Qwen model card](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-GGUF),
  model identity, license and supported quantizations. No weight downloaded.
- [JCAMD scope](https://link.springer.com/journal/10822/aims-and-scope),
  retrospective validation and molecular-analysis scope; [official publishing
  options/fees](https://link.springer.com/journal/10822/how-to-publish-with-us),
  no APC for subscription and US$4,390 before tax for open access at this check;
  [JOSS current submission requirements](https://joss.readthedocs.io/en/latest/submitting.html),
  development-history and research-impact gates.

This is a targeted update, not a systematic review, native reproduction of prior
agents or novelty certification. The previously recorded Paper2Agent/ChemCrow/
Coscientist review remains relevant; direct Nature access again redirected to
an unavailable identity endpoint, so no new full-text access is claimed.
