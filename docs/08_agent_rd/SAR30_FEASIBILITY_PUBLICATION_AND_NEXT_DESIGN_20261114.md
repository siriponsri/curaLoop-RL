# Thirty-task option: qualification, publication strength and evidence-led redesign

Date: 14 November 2026, Asia/Bangkok.

Status: **PROPOSAL_FOR_OWNER_REVIEW — NO_NEW_EXECUTION_AUTHORIZED**.

Source checkpoint: `de3ceea1fc1d4cdff8f52c313cdc8c4f06fbc243` on `main`.
LR-SAR1 remains closed. Its 60-task condition, results, ledgers and preservation
pins are unchanged. This is a prospective new proposal, not a revised score
for that failed gate. The owner requested a plan before a new run.

## 1. Recommendation and direct answer

Thirty tasks can support a valid **bounded external study**, but the number
alone does not establish an ESE/JSS-ready contribution. The present 30 are only
static candidates, and their usable count will shrink after native execution,
source dependence and development-role checks.

**Recommended next authorization:** a qualification-only tranche of **16 fresh
CPU-hours + two allocated GPU-hours / 48 elapsed hours**, maximum four combined
CPU equivalents and one GPU. Do not download the actor model or begin comparative
agent inference in that tranche. First establish what the dataset actually supports.

A possible complete study envelope is described below: **96 CPU-hours + 48
allocated GPU-hours / seven days in total**, including qualification. It is a
planning ceiling, not measured consumption and not currently approved. The
remaining expanded-study portion would be 80 CPU-hours/46 GPU-hours/five days,
not another 96/48 added to the qualification tranche.

If qualification fails, produce the actual failure report plus the literature-
grounded redesign in section 10. Do not automatically shrink the cohort again,
substitute a dataset/model or start the redesigned experiment.

## 2. What the 30 candidates actually contain

Derived from the retained [102-task census](../evidence/lr-sar1-20261114-v1/static-census-v1.json),
without reading new benchmark targets or running a reference/model.

| Domain | Static candidate tasks |
| --- | ---: |
| Bioinformatics | 9 |
| Computational Chemistry | 5 |
| Geographical Information Science | 3 |
| Psychology and Cognitive science | 13 |
| Total | 30 |

They span 16 repository lineages. The largest two groups contain four tasks
each; CAMDA-DILI, BioPsyKit, NeuroKit and related repeated-repository tasks cannot
be treated as fully independent publications. Publication/shared-data connections
still need checking. Repository count is not a biological-family certificate.

The old [native admission table](../evidence/lr-dc2-local-20261113-v1/tables-v2/native-reference-admission.csv)
has historical reference passes for IDs 5, 16, 18, 19, 40 and 41; failures for
22, 26 and 85; 21 remaining candidate IDs had no such execution. Old passes are
not fresh environment qualification. Old failures are not agent-performance
failures and must not be discarded from the prospective admission denominator.

The [30-row planning inventory](SAR30_CANDIDATE_PLANNING_INVENTORY_20261114.csv)
lists every ID, source, domain and historical state. All current native and agent
execution columns remain NOT_RUN. No task is certified fully API-free solely
because its immediate evaluator lacks the visual-judge call.

## 3. What must be checked before spending on agent inference

| Check | Required evidence | Failure handling |
| --- | --- | --- |
| Source/version/rights | Reuse exact archive/annotation hashes; resolve source-specific terms and dependencies | UNKNOWN is not admitted; no silent new release |
| Exposure and dependence | Existing author/development roles, shared datasets, paper/repository links, prior model access | Preserve exclusions and group connected sources |
| Actual scoring path | Native binary predicate, helper/transitive calls, no required paid judge/live API | No substitute local judge or skipped mandatory rubric |
| Reference environment | Unchanged reference program succeeds under prespecified upstream-compatible recipe | Keep failure; one documented correction batch only |
| Runtime input completeness | Required data/checkpoints present in retained archive or lawfully retained cache; no scientific-input network dependency at runtime | No unlisted model/data download |
| Resource fit | Build, reference CPU/GPU, disk, RAM, wall-time and finite timeouts | Stop at caps; no repeated environment search |
| Grader behavior | Prespecified interface/error handling, repeatability and invalid-artifact rejection in evaluator isolation | No golden-value/tolerance edits to make it pass |
| Public-check feasibility | At least one meaningful scientific/algorithmic requirement beyond file existence/shape on a substantial subset | Do not call schema checking scientific verification |
| Outcome isolation | No gold or private native result in model prompts, check construction or repair | Quarantine/stop affected scope |

This tranche requests native reference execution and bounded software conformance,
not experimental agent outcomes. Gold/reference files remain evaluator-only.
The old final16/private CF1 rows/other protected outcomes remain closed.

Reference-side neural tasks may need the proposed two GPU-hours. That is not
actor inference. Any required scientific input absent from the retained package
must be listed with identity, size and rights for owner decision; it must not be
silently fetched. Bounded ordinary dependency/container retrieval needs its own
explicit release cap, proposed 30 GiB within 100 GiB task-owned storage.

## 4. Proposed prospective cohort and progression rules

The aim is to retain as many as possible of the 30, rather than promise 30 locked
tasks. Existing development IDs 2/3 remain development; qualification of task 3
can support engineering but does not replace multi-domain checks.

Before any new reference outcome, select two additional development lineages
from metadata by a fixed hash rule, restricted to lineages with one or two tasks
and chosen to add domain coverage beyond the old development material. Quarantine
whole selected lineages. Publish the salt, ordering and roles before execution;
do not select by historical success, convenience, new native outcome or agent score.
This removes two to four candidate tasks and two lineages. At most 26-28 remain
for locked qualification, before other exclusions.

Proposed conditions for considering the full small-cohort study:

- At least **24 native-valid locked tasks**, **12 source-lineage clusters** and
  **three domains**, after all exclusions and development assignment.
- No lineage supplies over one quarter of the locked tasks.
- At least half the locked tasks have a public scientific/algorithmic check
  beyond existence/schema, under a rule declared before native outcomes.
- All supplied checks have a disclosed public specification and conformance
  evidence; unavailable coverage stays visible. Native scoring remains separate.
- Measured development/native-cost projection fits the proposed total/stage caps
  with 25% contingency and planned return/report reserve.

These are **new proposed coverage/engineering conditions**, not journal rules,
statistical-power guarantees or claims that 23 tasks cannot yield useful research.
They deliberately limit spending on a small-cohort paper ambition. If they fail,
the full study does not start under this proposal. A still smaller exploratory
case study would be a different owner decision, not an automatic relaxation.

No positive agent effect is a qualification condition. The checks and role
selection must not use locked candidate performance. There is one native pass
and at most one bounded upstream-supported implementation correction batch;
no native gold/grader rewriting, third pass or replacement task.

## 5. Why sample size remains a serious limitation

Let D be the paired native-success difference, taking -1, 0 or +1; let q be the
discordant-pair probability. An illustrative independent-task normal half-width
at a zero effect is `1.96 * sqrt(q/n)`.

| Locked tasks | q=0.10 | q=0.25 | q=0.50 | Worst case q=1 |
| --- | ---: | ---: | ---: | ---: |
| 30 | 11.3 pp | 17.9 pp | 25.3 pp | 35.8 pp |
| 24 | 12.7 pp | 20.0 pp | 28.3 pp | 40.0 pp |

These are analytical scenarios, not observed rates or the final interval method.
Source dependence can widen uncertainty. Under the extreme illustration of
perfect within-repository correlation, the current group-size concentration
gives `30^2 / sum(group_size^2) = 12.16` effective equal-variance units. This is
not an estimated effective sample size, but shows why 30 is not 30 independent
scientific sources.

The proposed study is poorly suited to establishing a general 5-10 pp advantage.
More seeds or a second model improve stability/triangulation, not the number of
independent tasks. A near-zero result will usually mean uncertainty, not proof
of equivalence. No p-value threshold or invented practical-effect margin is used.

## 6. Conditional full comparison, if the owner later chooses it

Primary model: fixed Qwen2.5-Coder-7B-Instruct, exact revision/runtime locked.
One proposed robustness model: the already retained Typhoon 12B Q4_K_M, only if
identity/license/hardware checks permit it. It is selected prospectively, not
added if the primary model performs badly. No model search or replacement.

| Arm | Role |
| --- | --- |
| L | Initial public task, no interactive execution; contextual control |
| G | Ordinary code/filesystem tools plus a fixed self-debugging procedure |
| T | G plus full public checking definitions, probes, tolerances and applicability |
| P | Same criteria as T plus a prepared executable implementation |

Primary comparison remains P-T on native task completion. T can construct and
run its own checks. Match public facts, normal tool access, total calls/tokens,
timeouts and context rules; disclose the prepared-implementation difference.
Count checker preparation and qualification in cost. Reference programs are
evaluator sanity, not a deterministic autonomous-solver baseline.

Proposed fixed matrix: two seeds across all four arms on the primary model
(8N missions), plus one seed for T/P on the robustness model (2N). At N=24-28,
that is 240-280 missions, with a conservative cap of 300 if roles change only
through a separately approved pre-freeze scope. Seeds are nested in tasks;
the primary estimand averages seeds within task. Do not pool model/seed rows as
new independent tasks. Development is capped separately at 24 missions/72 calls.

Keep the previous candidate limits: three provider calls, 4,096 generated tokens
in total per mission, 16,384 context tokens, shared history handling. Only
development can establish whether these limits are adequate. If not, stop before
locked outcomes; no post-result enlargement or hidden extra reasoning calls.

Report task-weighted paired native effects with source-cluster uncertainty,
wins/losses/ties/both-fail, missingness and source-weighted sensitivity. Apply
frozen local diagnostics to final outputs of both T and P without returning
post-study feedback to T. Include checker availability/use, false reassurance
only where a certification was actually claimed, runtime errors and repair
opportunities. Native failure after a local pass is not automatically a hallucination.

No new manuscript until the owner has reviewed results. Qualitative scientific
judgments that lack an operational oracle are not automatically valid because
an AI or the developer labeled them. Keep such interpretation explicitly
exploratory and identify any later human-validation need honestly.

## 7. Budget and elapsed-time proposal

No resources below have been approved or booked; LR-SAR1's closed balance is
unavailable. All figures are planning caps subject to hardware/throughput checks.

| Stage | CPU h | Allocated GPU h | Elapsed allocation | Release condition |
| --- | ---: | ---: | --- | --- |
| Qualification-only tranche, recommended first | 16 | 2 | 48 h | New explicit owner release; no actor model download/inference |
| Fixed development/model setup | 16 | 6 | 24 h | Qualifying population and owner decision to proceed |
| Frozen two-model comparison | 40 | 32 | 72 h | Fixed model/checks/roles; measured cost projection passes |
| Analysis/reproduction/return | 16 | 4 | 12 h | Preserve every outcome and failure |
| Owner report and plan disposition | 8 | 0 | 12 h | No manuscript; may include bounded redesign documentation |
| Explicit GPU contingency | 0 | 4 | Within seven days | Execution overhead only |
| Full possible envelope, including qualification | 96 | 48 | Seven days | No automatic extension |

Maximum concurrency remains four CPU equivalents/one GPU, local one plus remote
three initially; remote RAM 32 GiB/local 2 GiB/task-owned disk 100 GiB. No paid
API/rental. If the expanded study is approved later, request at most 20 GiB for
the one new actor checkpoint; no model download in qualification. Shared models
and unrelated services must remain untouched.

At the full conservative cap, 324 missions including development allow up to
1.327 million output tokens. Merely dividing by a hypothetical 20 tokens/s gives
18.4 GPU-hours; at 10 tokens/s it gives 36.9 hours, before prompts, tools, loading
and idle allocation. These are illustrations, not measured throughput. The
32-hour main-matrix allowance therefore needs actual canary timing and 25%
contingency before freeze. CPU task/evaluator work is an additional cost.

Recommendation: authorize only the first 16/2 tranche initially. Its output can
justify or reject the remaining 80/46 portion on actual data. This avoids
committing the full envelope on static counts or assuming a paper is assured.

## 8. Would this be enough for ESE or JSS?

**Current answer: not yet. Conditional answer: possibly, for a carefully bounded
empirical contribution; not for general scientific-agent superiority.**

The inspected [ESE scope](https://link.springer.com/journal/10664/aims-and-scope)
welcomes original and replicated empirical studies. The
[JSS publisher description](https://shop.elsevier.com/journals/journal-of-systems-and-software/0164-1212)
welcomes replication and negative results, while requiring useful SE knowledge.
No fixed 60-task requirement was identified in those scope statements; 60 was
our earlier approved design choice, not an editorial acceptance threshold.

The [November 2026 LLM-in-SE guidance](https://doi.org/10.1007/s10664-026-10922-3)
emphasizes model/system/prompt/trace transparency, suitable controls, valid
measurement and limitations. It distinguishes benchmark-operationalized outcomes
from subjective constructs needing human validation. This supports a solo native-
scored study of a bounded endpoint, not broad unvalidated scientific judgments.

| Evidence situation | ESE/JSS assessment |
| --- | --- |
| Thirty static candidates only | Insufficient: no new agent result or qualified oracle |
| One model, one small subset, generic check wrapper | High rejection risk: weak increment over R2T and limited external validity |
| Qualified 24-28 tasks, controlled intervention, two-model sensitivity, reproducible disagreement/cost findings | Plausible empirical package; originality and insight still need convincing argument |
| Positive point estimate with broad interval or one-source concentration | Report cautiously; no general advantage or equivalence claim |
| Null/negative result with credible design and substantive failure explanation | Potentially useful replication, but not automatically publishable |
| Only native-qualification failure | Feasibility report; does not deliver the intended comparative research paper |

ESE remains the owner's primary target and JSS backup. No acceptance probability,
editorial preapproval or forced venue switch is asserted. A second model does
not cure a weak question or small independent-source sample.

## 9. Successful work reviewed, with limits retained

The owner requested research on work with positive outcomes. The following
primary papers/results were inspected; contradictory or limited outcomes were
kept rather than selecting only favorable headline numbers.

| Work | Reported positive evidence | Limit and lesson for this project |
| --- | --- | --- |
| [CRITIC, ICLR 2024](https://arxiv.org/abs/2305.11738) | Table 2: GPT-3.5 GSM8k rises from PoT 72.5 to 78.2; tool-free critique is 77.0 | Not a scientific-code benchmark or identical no-feedback compute budget; oracle-only correction is a distinct privileged arm. Ground feedback in execution and measure its actual incremental contribution |
| [Self-Debugging, ICLR 2024](https://arxiv.org/abs/2304.05128) | Table 2: Codex TransCoder 80.4 baseline to 92.5 with unit-test feedback/explanation; Spider 81.3 to 84.1 | Results depend on task/model/feedback; repeated generations are not free. Keep execution-assisted repair as a strong control |
| [Paper2Agent, Nature 2026](https://doi.org/10.1038/s41586-026-11044-y) | Author manuscript: Sonnet 4 scores 91.2% versus direct-repository 80.3% on 300 tutorial-derived queries; 74/100 papers agentified | This is a larger packaged-support intervention and uses commercial models; selected agentifiable papers and human/other grading limit direct transfer. Validated scientific actions are promising, but not proof of our checker effect |
| [Agentless, FSE 2025](https://arxiv.org/abs/2407.01489) | SWE-bench Lite 96/300 resolved, 32%, reported mean cost US$0.70 | Several external comparisons use reported leaderboard results rather than fully matched reruns; repair samples exceed our tiny call budget. Simple workflows remain mandatory strong competitors |
| [R2T, 2026 preprint](https://arxiv.org/abs/2610.00313) | One eight-ID repair cohort: text 13/16 versus checks 15/16 | Larger shared-definition cohort ties at 13/24; source-through-Python matches dedicated tool aggregate. Prepared checks are prior art; access/coverage and task context matter |
| [Failure Feedback, 2026 preprint](https://arxiv.org/abs/2610.14662) | Prespecified study reports +20 pp target repair for Qwen3-4B versus matched same-category feedback | Phi-4-mini increase is not significant; target repair does not establish held-out gain. Measure repaired failures and newly broken successes separately |

Paper2Agent publisher access redirected to an inaccessible login flow. The
published-result claims were checked in the authors'
[repository-hosted paper text](https://github.com/jmiao24/Paper2Agent/blob/main/skills/paper2agent/paper2agent-paper/references/paper.md).
It is distinguished from the older arXiv version, which predates the expanded
Nature results. CRITIC, Self-Debugging, Agentless, R2T and Failure Feedback were
read through primary extracted texts, including relevant methods/results.
No code from any paper was installed or executed.

## 10. If the 30-task route is not viable: a bounded stronger-direction proposal

Working idea: **validated scientific actions plus actionable diagnostics**, with
the research question: do prepared scientific actions and verification feedback
complement each other, or are the observed gains mostly reusable implementation
support rather than verification?

This derives from Paper2Agent's reusable-action gains, CRITIC/Self-Debugging's
execution-feedback gains, and R2T/Agentless's warnings about superficial tool
complexity. It is a **candidate empirical mechanism question**, not demonstrated
algorithmic novelty or a promised positive effect.

The product hypothesis is concrete: accept an R&D task, execute a bounded
scientific action, attach artifact-versioned evidence and diagnostics, repair
within budget, and distinguish delivered output from scientifically unsupported
claims. The research value must come from a controlled result, not that workflow
diagram or a renamed existing MCP wrapper.

A future four-cell design would separate:

| | No prepared verifier | Prepared verifier |
| --- | --- | --- |
| Ordinary code/tools | Strong self-debug control | Verification-only support |
| Prepared scientific actions | Action-only support | Combined support |

All cells share the same public scientific content and have matched total
resource limits; package preparation is counted. Native success is separate from
tool/check validity. The interaction contrast is a difference of differences;
it generally needs more information than the simple two-arm effect. Thirty
tasks are **not** automatically enough for that factorial study. No claim that
adding two published ideas is itself new or that a 10-pp benefit is detectable.

If this route is pursued, first produce a closest-work/estimand/protocol and
dataset-resource decision, capped at four CPU-hours/12 elapsed hours with no
inference or dataset intake. That design work can fit inside the report-stage
allowance if an eventual qualification release explicitly includes it. Its
completion test is a falsifiable mechanism and executable external measurement
plan, with unresolved novelty labeled, not a cosmetically exciting name.

One **candidate to investigate, not a substitute adopted now**, is SWE-bench
Verified for repository-repair mechanisms with native tests. The
[official harness documentation](https://www.swebench.com/SWE-bench/)
describes 500 engineer-confirmed problems and Docker-based scoring; the original
benchmark has an ICLR 2024 paper. Scientific-computing source scope, useful
prepared-action definitions, real source diversity, contamination, licenses,
storage and local runtime must still be established. It evaluates repository
repair, not pharmaceutical experimentation. No benchmark/model swap or full
cost authorization is implied.

Planning provenance note: its public HF preview displayed reference/test patch
snippets for `astropy__astropy-12907` and `astropy__astropy-13033` during this
literature review. Those IDs are author-exposed and must not be labeled unseen
if a future study is proposed. Connected-lineage decisions would be explicit;
no new dataset archive was downloaded or task executed here.

If a distinct, executable, resource-feasible hypothesis cannot be supported,
report NO_GO for the proposed redesign. Do not repeat mechanism renaming, use
post-result metric changes, reopen old final outcomes or buy a favorable result.

## 11. Decision requested and work completed now

Recommended next decision: approve **qualification only: 16 CPU-hours + two
GPU-hours / 48 hours**, with the prospective roles/coverage/check/resource rules
above and a report before expanded study. Alternatively the owner can request
a corrected scope before any new execution. The full 96/48/seven-day envelope
is a later conditional option, not a fresh active grant.

This response completed cached-census analysis, historical-admission comparison,
primary-literature review, publication assessment and a prospective plan.
No new reference/model run, model download, SSH, GPU reservation, scientific
outcome evaluation or manuscript was started. No closed account was reused.
The files are new local planning documents; prior frozen evidence is unchanged.
