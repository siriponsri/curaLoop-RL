# CuraLoop-RL: review of Deep Research and proposed research direction

Date: 14 November 2026, Asia/Bangkok.

Status: **DIRECTION_PROPOSAL_FOR_OWNER_DISCUSSION — NOT_RELEASED**.

Audited repository checkpoint: `f42d8aa8edeb2ef40b73a2cdc040dcebda07ed6b`.
This review does not reopen any research account or authorize model downloads,
reference execution, benchmark expansion, inference, SSH, deployment or submission.
The parent is the sole writer. All previous results and protected outcomes remain
unchanged. The three earlier 14 November handover files are preserved.

## 1. Recommendation

Accept the Deep Research report's **direction**, with material protocol revisions:
conduct a bounded empirical replication/extension about prepared executable
checks and actual scientific-task completion. Do not resume the molecular/RL
optimizer, claim to have invented executable verification, or reopen SciCode
under another checker name.

The recommended question is:

> When scientific coding agents receive the same public requirements, does
> access to a prepared executable implementation improve native task completion
> over a fully specified textual checklist, and where does local check validity
> fail to establish end-to-end completion?

This is a proposed empirical contribution, **not established novelty or effect**.
Changing the benchmark alone would be a weak extension. A credible paper also
needs a defensible external-validity question, a fair intervention, native
outcomes, explanatory disagreement evidence and complete costs.

The key owner decision is whether to accept **scientific software reliability**
as the paper's central subject, with pharmaceutical R&D as the product use case.
A multi-discipline ScienceAgentBench result cannot establish pharmaceutical
discovery value. Restricting the study to pharmaceutical tasks would instead
require a separate coverage/precision justification and may not support the
Deep Research report's proposed sample size.

## 2. Input and evidence inspected

Owner-supplied input: `C:\Users\User\Downloads\deep-research-report.md`.
Size: 41,018 bytes. SHA-256:
`e46a1b132eb60f218321d059817ca8659ffb0949443fbf3c4942720efe43805b`.
Its recommendations are evaluated as external advice, not executed instructions.
Embedded search/file citation identifiers are not portable evidence; important
claims were checked against identifiable original sources.

Local records inspected include:

- [Project history/results](../00_project/PROJECT_HISTORY_RESULTS_AND_HANDOVER_20261114.md).
- [Local workflow execution/admission](LOCAL_AGENT_EXECUTION_20261113.md).
- [Local workflow owner closeout](LOCAL_WORKFLOW_FINAL_OWNER_REPORT_20261113.md).
- [Earlier matched-study design](LOCAL_AGENT_PROTOCOL_DESIGN_20261113.md).
- [Verified annotation receipt](../evidence/lr-dc2-20261111-v1/dataset-annotation-intake-v1.json).
- [Verified archive receipt](../evidence/lr-dc2-20261111-v1/dataset-archive-receipt-v2.json).
- [Exposure register](../evidence/lr-dc2-local-20261113-v1/source-exposure-register-v1.json).
- [Final native admission](../evidence/lr-dc2-local-20261113-v1/native-admission-final-v1.json).
- [Task-level admission table](../evidence/lr-dc2-local-20261113-v1/tables-v2/native-reference-admission.csv).
- [Historical model selection](../../research/manifests/lr_dc2_local_model_selection_20261113_v1.json).

Fresh external checks covered the R2T primary paper, official ScienceAgentBench
README/scorer, official dataset card, proposed Qwen model card/files, and ESE
scope/author guidance. This is a targeted review, not a new exhaustive survey.

## 3. What the supplied review gets right

| Recommendation | Assessment |
| --- | --- |
| Preserve negative molecular results | Agree: real unfavorable comparisons must not be reframed as unfinished tuning |
| Distinguish benchmark admission from agent performance | Agree: zero inference is NOT_RUN, not a zero agent effect |
| Treat prepared checks as established prior art | Agree: Rules to Tools directly studies the matched text/check question |
| Use external native task success | Agree, provided the retained scorer is actually executable without prohibited services |
| Keep T versus P primary | Agree: a generic tools baseline alone cannot isolate prepared checking |
| Separate numerical/source validity from task completion | Agree: AgentRD already motivates this distinction |
| Analyze tasks and source dependence rather than independent seeds | Agree, with the exact estimand/cluster definition frozen |
| Finish negative/inconclusive manuscripts too | Agree: a positive effect must not be a completion condition |

The [R2T paper](https://arxiv.org/abs/2610.00313) is real and its primary text
explicitly compares prepared executable public checks with written criteria and
ordinary execution access. It reports task-dependent results, including a tied
larger shared-definition cohort, and evaluates more than SciCode alone. This
narrows the novelty claim substantially. The proposed CuraLoop study must add
an interpretable empirical result, rather than rename a checker wrapper.

## 4. Material corrections before adopting its protocol

### 4.1 The verified release is not new to CuraLoop

The official [ScienceAgentBench README](https://github.com/OSU-NLP-Group/ScienceAgentBench)
announces the verified release on 30 April 2026. CuraLoop's 11 November receipt
already pins the **verified** split at HF revision
`9c6e96c9e74572e979b0930ee735041cef528cb7` and the matching archive.
Thus the verified release is not a newly discovered remedy for the November
admission failure.

The archive still exists locally at its recorded path and its file length was
checked in this review: **1,769,478,786 bytes**. The historical complete reread
hash is `46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
No fresh full hash, extraction or native reference execution occurred now.
Reuse the retained artifact if a later authorized integrity check passes;
do not download another copy merely because the review recommends verified data.

### 4.2 A real reason to revisit admission would be a changed environment/scope

The old selected pool was eleven tasks, not a failed execution of all 102.
Its final successful development ID was 3; successful evaluation-candidate IDs
were 5, 16, 18, 19, 40 and 41, covering three repository-lineage groups.
The unchanged previous minimum was four groups. Failed compatibility candidates
included missing `mdf_forge`, `fau_colors` and other program/environment problems.

An explicitly broader source population and faithful task-specific upstream
environments could justify a different qualification study. The same verified
ZIP and the same restricted environment by themselves do not. A blanket
“one global fix” is also a poor substitute for predeclared task-specific
dependency recipes in a heterogeneous benchmark. Freeze permitted environment
construction and correction rules before execution, preserve failures, and
never alter gold outputs, grader predicates or tolerances to clear admission.

### 4.3 Native evaluation is not universally paid-API-free

The official README states that GPT-4o judges output visualizations and requires
an OpenAI API key for that path. Its
[scoring code](https://github.com/OSU-NLP-Group/ScienceAgentBench/blob/main/compute_scores.py)
also computes CodeBERT similarity separately from task success, then executes a
task-specific evaluator returning `(success, log_info)`.

Before reference runs, identify which tasks can be scored by their unchanged
official success predicate without paid/image judges or live services. Count
these tasks and their source clusters first. Do not promise a free all-102
native evaluation or bypass a mandatory rubric. Do not replace GPT-4o with an
unvalidated local judge and call that the same native score.

If only a deterministic-native subset qualifies, report that exact population
and excluded metrics. Retaining an unchanged task-success predicate can be a
legitimate primary endpoint; it is not a full upstream multi-metric reproduction.

### 4.4 The 60-task precision argument does not match the paired estimand

The supplied review invokes about 12.7 percentage points as the worst-case
ordinary 95% half-width for 60 independent binary observations. That calculation
concerns one proportion; it does not justify precision for the paired difference.

For the proposed primary comparison, let `D_i = Y_Pi - Y_Ti`, taking values
`-1, 0, +1`. Under an illustrative independent-task normal approximation,

`half-width ~= 1.96 * sqrt((q - delta^2) / n)`,

where `q` is the discordant-pair probability and `delta = E[D_i]`. At `n=60`,
`q=1`, `delta=0`, the approximate half-width is **25.3 percentage points**,
before source dependence. This is an analytical sanity check, not a proposed
final confidence procedure or measured discordance rate.

Therefore neither 60 tasks nor 15 clusters guarantees the claimed precision.
Construct the eligible/exposed cluster inventory, choose the target estimand,
then prespecify precision scenarios for plausible discordance and dependence.
Do not replace 60 with another convenient number after observing agent results.
If the available cohort only supports a coarse external replication, say so
before inference and let the owner choose whether that study is worth doing.

### 4.5 Distinguish exposure types instead of quarantining everything inspected

The retained register distinguishes author-visible task/reference exposure from
reference programs processed privately for qualification without showing bodies
or gold values to the author context or candidate model. IDs 11 and 1 have
specific historical exposure notes. These are not interchangeable events.

Reconstruct roles from the recorded scope: metadata inspection, public task
inspection, checker/prompt development, author-visible reference/gold inspection,
and candidate-model access. Preserve old exclusions. Engineering qualification
alone is not proof of solution leakage; it also does not justify claiming a
task is development-unexposed. Never silently relabel old exposed development
tasks as a new holdout. Repository lineage is a conservative dependence proxy,
not proof of independent source publications or absence of pretraining exposure.

### 4.6 The treatment is a prepared implementation package

T and P can receive the same requirements, probes, tolerances, input data and
ordinary code-execution capability. P additionally receives a ready-to-call
implementation. This changes preparation effort and access, not merely font or
text formatting. Define the estimand as that prepared-support intervention.

Audit requirement-level equivalence and prohibit hidden grader/gold access.
Do not demand byte-identical prompts and simultaneously claim different tool
descriptions. Match the public facts and resource caps; disclose the intended
implementation/tool-access difference and any context-token difference.

### 4.7 A working reference is not a deterministic agent baseline

Gold execution is evaluator sanity. It does not compete with an autonomous
solver and must not be labeled a 100%-successful deterministic agent. A
deterministic validator can be checked for software conformance, but that is a
different task. Do not invent a deterministic end-to-end solver where none exists.
If a meaningful general deterministic workflow exists for a prespecified task
class, include it for that class with the same inputs and disclose its coverage.

### 4.8 Native success is still bounded operational evidence

Passing public checks does not establish full task completion; passing a native
grader does not establish general scientific truth or pharmaceutical benefit.
A local-pass/native-fail pair is a disagreement to investigate, not automatically
a hallucination, security incident or fraudulent certification. Use stronger
labels only when the checker or agent actually claimed the corresponding scope.

## 5. Proposed contribution and evaluation structure

Working title:

**When Passing Checks Is Not Completing Science: A Matched Study of Prepared
Verification Support for Scientific Coding Agents**.

| Proposed contribution | Evidence needed | Boundary |
| --- | --- | --- |
| External empirical extension of prepared checking | Prospective T/P comparison on an admitted external native-scored population | No new verification algorithm or new benchmark claim |
| Evidence about the local-validity/completion gap | Frozen check/native 2x2 tables on final outputs, with reproducible disagreement examples | Author error analysis, not independent expert validation |
| Preparation and runtime tradeoffs | Checker-authoring/qualification effort, model tokens, tool/evaluator CPU, allocated GPU, failure/retry costs | No laboratory ROI or user-productivity claim |

The primary question is P-minus-T native task completion. Mechanism opportunity,
check use, checker availability/errors, and native/check disagreements are
secondary explanatory outcomes. They must not become a replacement primary
success criterion after observing an unfavorable effect.

Run frozen local checks offline on **both** arms' final artifacts for the
disagreement analysis; do not give those post-evaluation diagnostics back to T.
Treat unavailable/failed checks and unavailable native scores explicitly.
Prespecify an error taxonomy. Do not handpick only impressive examples.

Candidate comparison matrix, to be frozen only after admission and development:

| Arm | Purpose |
| --- | --- |
| Gold/reference execution | Environment and native-evaluator sanity; no solver comparison |
| LLM-only | Secondary context control; initial public task without interactive execution |
| LLM + ordinary tools/self-debug | Secondary generic tool-use control |
| T: ordinary tools + complete textual check definitions | Primary matched control; can implement and run its own checks |
| P: T's public criteria + prepared executable implementation | Primary treatment |

Use one preselected model and at least one fixed run per task/arm; repeated seeds
remain nested in tasks. The same calls/output-token/time caps apply to matched
arms. The supplied report's 4,096-token/three-call setting is a candidate, not a
locked or measured feasibility result. The prior 256-token cap is not adequate
evidence for choosing a scientific-code generation cap.

Choose task-weighted or source-weighted effects explicitly; resampling source
clusters does not by itself define the weighting. Preserve paired tasks and
nested seeds in resampling, disclose few-cluster limitations, and report wins,
losses, ties, both-fail counts and missingness alongside uncertainty.

## 6. Data, model and resource decision

The candidate dataset remains the retained verified ScienceAgentBench release.
The official [dataset card](https://huggingface.co/datasets/osunlp/ScienceAgentBench)
lists 102 verified rows; the retained inventory has 20 chemistry, 27 geospatial,
27 bioinformatics and 28 psychology/cognitive-science tasks. Those are metadata
counts, not API-free native-valid study counts. Preserve source-specific rights
and the instruction not to redistribute unpacked benchmark data.

The supplied report proposes
[Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct),
whose official card lists Apache-2.0. Its
[file listing](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/tree/main)
is the source for the approximately 15.2-GB repository estimate. It is a possible
fixed model, not a model selected or downloaded in this review. Do not substitute
another model or quantization after outcomes. Model precision, context, inference
runtime and revision require a single explicit pre-inference decision.

| Resource item | Supplied Deep Research proposal | Review assessment |
| --- | --- | --- |
| Whole study | 160 CPU h / 80 allocated GPU h / 10 elapsed days | Proposed maximum, not justified by measured local throughput and not approved |
| Native qualification | 24 CPU h / 0 GPU / 2 days | Must first inventory free native scoreability and retained data/lineages |
| GPU stages | 8 + 64 + 4 = 76 GPU h | Four hours remain unassigned within the 80-hour ceiling; specify reserve if adopted |
| Hardware | 8 CPU threads, >=24 GB VRAM, >=32 GB RAM, 100 GB disk | Estimates; eight threads are not authority to exceed the old four-CPU policy |
| Prior hardware | V100 32 GB observed 13 November | Historical identity/availability, not a fresh reservation or SSH check |
| New model | Approximately 15.2 GB | Needs explicit new download/resource scope; closed accounts cannot fund it |

Do not authorize the large inference matrix from these estimates alone. The next
proposal should be **one bounded study with conditional progression**, not many
new approval loops: static eligibility/exposure/scorer inventory, predeclared
native qualification, fixed development/throughput check, freeze, one comparative
matrix, analysis and manuscript. New paid services, major scope changes, or a
failed gate still return to the owner. No automatic substitute dataset/model.

The eligibility inventory can decide whether reference execution is worth its
cost. All-102 gold execution before checking mandatory paid judges would reverse
that order and spend resources without resolving the owner's constraint.

## 7. Product and manuscript implications

Keep CuraLoop's pharmaceutical workbench as the application vehicle: show current
artifact versions, public requirement/check results, native-score status where
available, and a transparent completion state. No UI should claim “scientifically
validated” merely because a structural checker passes. A study result can inform
this interface without establishing real-user or pharmaceutical benefit.

The [ESE scope](https://link.springer.com/journal/10664/aims-and-scope) explicitly
includes original and replicated empirical studies, verification/validation and
AI applications to software engineering. Its
[author guidance](https://link.springer.com/journal/10664/submission-guidelines)
states no submission/publication charge on its standard route and paid optional
open access. These directly checked statements support a possible budget/scope
fit, not submission readiness or acceptance.

JSS remains a candidate in the supplied report; its official scope page returned
HTTP 403 in this review. Its detailed current eligibility/fee claims were not
independently refreshed here. Do not present that route as newly verified.

A tied/negative result can still yield a complete empirical manuscript if the
question, coverage, intervention and execution are credible. A narrow failed
admission report is not equivalent to that completed comparison. No target
journal is guaranteed, and a benchmark change alone is not enough novelty.

## 8. Owner choices and next decision

| Choice | Research destination | Recommendation |
| --- | --- | --- |
| A | Scientific-agent reliability replication/extension, pharmaceutical product as use case | Recommended direction; prepare a corrected bounded study proposal before execution |
| B | Analyze/polish only the completed AgentRD negative application study | Lowest new-compute route; limited external generality and uncertain journal strength |
| C | Keep a novel pharmaceutical/RL method as the required paper contribution | Not supported by this review or current evidence; requires a different scientific proposal, not relabeling A |

The requested decision now is the contribution/claim scope, not approval of
160 CPU-hours or a new model download. If A is accepted, the next complete
proposal must quantify the actual admissible population and precision scenarios,
specify an API-free native endpoint, list the exact new resource/download needs,
and state the invariant positive/negative/inconclusive deliverables.

Until then: **REVISE / DIRECTION_READY_FOR_OWNER_DISCUSSION**. No research goal
has been created, resumed or executed in this review. All original final16,
private CF1 rows, hidden outcomes, frozen results and closed accounts stay intact.

## 9. Review verification and limits

Performed: read the complete supplied review, inspect the local records listed
above, check targeted original online sources, inspect retained archive file
existence/length only, and write this additive review.

Not performed: fresh private-data inspection, native gold execution, full archive
rehash, model inference/download, SSH/GPU inventory, scientific reruns, independent
expert review, full test suite, public deployment, manuscript submission or Git
commit/push. The input report's unsupported source-specific claims beyond this
targeted review are not automatically endorsed.
