# Decision brief: repair the retained harness or move to CORE-Bench?

Date: 14 November 2026, Asia/Bangkok.
Status: **PROPOSAL_ONLY — NO_NEW_COMPUTE_OR_DATASET_RELEASE**.
Verified repository checkpoint: `94d3ab79b1d0f229a9f6efe3c1e51d1617670fa9`, main.
The SAR30 account remains closed. Its results, reservations and 109 preservation
pins are unchanged. This brief supersedes the earlier *preference* for CORE-Bench
as the next candidate; it does not edit that historical proposal.

## Recommendation

Choose **A: one final, bounded repair of our existing harness**, followed by a
fixed comparative study only if every prespecified readiness condition passes.
Do not switch to CORE-Bench merely because our preparer failed. Do not fund
another sequence of qualification-only rounds. Authorize at most one new staged
release, with one terminal technical decision, rather than renewing small
accounts until something passes.

This is a decision about the cost and credibility of reaching a real experiment,
not an assertion that a small ScienceAgentBench study guarantees an ESE/JSS
paper. CORE-Bench has a potentially broader paper-level population, but a more
suitable admitted cohort and a simpler local execution path have **not** been
established. Neither changing datasets nor repairing storage is a research
contribution by itself.

If the desired claim is a general 5–10 percentage-point superiority across
scientific agents, neither currently evidenced option is sufficient. If the
desired claim is a bounded, reproducible mechanism study with honest uncertainty
and cost, A is the better first investment under the present constraints.

## 1. Same research question for a fair comparison

Compare the datasets under the **same proposed mechanism question**:

> Under matched information and resource limits, when do reusable scientific
> actions make agentic verification unnecessary, and when does executable
> diagnostic feedback improve completion enough to justify its preparation and
> execution costs?

This differs from simply showing that a prepared checker beats prose. The
[Rules to Tools preprint](https://arxiv.org/abs/2610.00313) already studies that
intervention and reports task-dependent results, including a tied cohort and
an implementation accessed through Python matching a dedicated tool aggregate.
Our proposed contribution must instead explain the source of benefit and the
conditions under which the extra agent layer is useful. Novelty remains
unestablished; a matched study and a working plugin are artifacts, not proof of
novelty or a positive effect.

Four tool-enabled cells separate ordinary tools, prepared scientific actions,
prepared diagnostic checks, and both. Use **both versus actions alone** as the
primary paired comparison. Treat the interaction and the remaining cells as
secondary unless prospective precision justifies an interaction-first claim.
Add deterministic workflow and LLM-only contextual controls, with explicit
differences in execution capability. A reference program is evaluator sanity,
not an autonomous deterministic baseline.

Action implementations must come from permitted public repository methods,
not isolated benchmark gold programs or target answers. Both main arms receive
the same public facts, ordinary tools and per-mission caps. Report actual use,
failures, regressions, fallback, preparation and runtime costs. Where the claim
concerns invocation convenience, compare against the same implementation through
ordinary Python, rather than withholding its code from the control.

## 2. Side-by-side decision

| Dimension | A: repair retained ScienceAgentBench harness | B: CORE-Bench through a verified current adapter |
| --- | --- | --- |
| Native task construct | Generate a scientific program and grade its output | Reproduce released paper code and report specified output answers |
| Contribution fit | Direct fit to scientific program checking/repair | Better fit to reproducible workflow execution and result retrieval; scientific validity needs a separate argument |
| Population now evidenced | 26 locked candidates, at most 13 connected source groups, four domains; none freshly native-qualified | Official paper-level test split has 45 papers before exclusions; local admissible count unknown |
| Immediate blocker | Our recipe: ENOSPC plus two incompletely diagnosed imports | New capsule rights/assets, modality, adapter parity, local isolation and runtime fit |
| Existing material reused | Retained benchmark, role freeze, source audits and returned dependencies | Literature/source review only; no capsules or native local runs |
| Hard limit after repair | Cannot create more source diversity than this retained candidate pool | Could add paper-level diversity, but difficulty variants do not add independent papers |
| Closest-prior-work risk | A generic checker comparison is too close to R2T | A generic paper-to-tool/reproduction wrapper also overlaps prior work |
| Product connection | Python/RDKit action, artifact checking and bounded repair | Paper-to-execution workflow, provenance and answer extraction |
| Present execution uncertainty | Lower incremental uncertainty, still substantial untested native coverage | Higher; more setup and a different evaluation construct |
| Publication judgment | Most economical route to a bounded mechanism result, conditional on native and design readiness | Higher breadth ceiling only if a substantially larger lawful, scoreable paper cohort is actually admitted |

These are qualitative reviewer judgments, **not measured acceptance probabilities**.
JSS is not assumed easier than ESE. Both need a defensible SE contribution and
evidence; benchmark size alone does not establish either.

## 3. Why repairing A is justified, and what it cannot accomplish

The [closed SAR30 summary](../evidence/lr-sar30-qual-20261114-v1/qualification-summary-v1.json)
records seven locked root-import passes, one locked install failure and two
locked import failures. Sixteen locked tasks were not reached. No new reference,
native scorer or agent was run. Thus the evidence does not show that the
scientific tasks or the proposed method failed.

ENOSPC was observed for DeepPurpose development tasks 12/13 and locked Chemprop
task 15. The 4 GiB temporary mount is a likely bottleneck, not a confirmed
per-mount diagnosis. Papyrus task 22 returned OSError and ProLIF task 26 returned
ImportError without full exception text. Those observability and preparation
choices belong to our harness. Repair is worthwhile for that reason, rather
than because we have already invested in this dataset.

Even a perfect repair leaves at most **26 locked tasks and 13 connected groups**,
before additional ancestry or native exclusions. The old 24-task/12-cluster floor
is therefore tight: losing two whole groups can fail coverage even if 24 tasks
remain. A successful install cannot pass this gate; real unchanged references,
native scoring and checker conformance are required.

An independent-task illustration at discordance q=0.25 gives a paired 95% normal
half-width near 20.0 percentage points for n=24 and 14.6 points for n=45. These
are planning illustrations, not estimated intervals or a cluster-adjusted power
analysis. Repeated sources can widen uncertainty. Approximately 97 independent
tasks would be needed for a 10-point half-width under that same illustration.
Extra seeds, questions and difficulty levels do not provide those independent
tasks. We should target bounded mechanisms and costs, not a universal small gain.

## 4. What the additional CORE-Bench reading changed

The [CORE-Bench paper, v2](https://arxiv.org/pdf/2409.11363v2), sections 2.1–2.2
and Appendix A, gives 90 papers split 45/45 into development and test. Its three
difficulty variants share origins. Easy supplies existing outputs; Medium
provides execution instructions/environment; Hard removes setup assistance.
The endpoint is successful code reproduction and output reporting, not proof
that the original paper's scientific conclusion is correct. It includes text
and figure questions. These facts limit both the eligible population and the
claim we could make.

The [official old repository](https://github.com/siegelz/core-bench) recommends
HAL and says its old harness is no longer maintained. The
[HAL README](https://github.com/princeton-pli/hal-harness) documents general local
Docker support but describes CORE-Bench specifically with Azure VMs. That is
not proof that local operation is impossible, or that its local path is ready.
Neither Azure spending nor migration work is currently authorized.

The inspected [current adapter source](https://github.com/princeton-pli/hal-harness/blob/main/hal/benchmarks/corebench.py)
uses typed/numerical answer comparisons. It loads answer records and can download
capsules during construction. Its Medium/Hard file filters differ, and Hard
also removes some training/cache/checkpoint files. This makes source-version
parity, no-download inspection and evaluator/actor separation explicit readiness
work. It does not justify silently substituting another scoring rule.

Additional interpretation:

- Figure questions are an **agent-input modality** issue; they do not by
  themselves imply a paid scoring judge. A text-only model plus unqualified
  image extraction cannot be assumed to handle the full cohort.
- Removing vision-only papers might sharply reduce diversity. The paper's
  parsed modality table also has inconsistent totals; no exact text-only
  held-out count is certified from it. A future metadata audit must resolve this.
- Native answer correctness and evidence that the current code really ran are
  distinct. Keep native scoring intact and report execution/provenance evidence
  separately. Correct answers alone do not certify scientific correctness.
- A single difficulty level and existing train/test roles should be fixed before
  evaluation. Moving old training papers into a new test set to inflate size is
  not the default plan.

Only public papers and adapter source were read here. No task-answer file was
decrypted, capsule downloaded, model acquired or code executed. Source snippets
from the paper exposed numerical example outputs for capsule 826891; other
named identifiers include 5507257, 4299879, 8234136 and 8807709. A future intake
must map and quarantine relevant author-exposed examples rather than call them
unseen. No exact target values are copied into this brief.

## 5. Proposed budgets: one release for the chosen route, not both

All figures below are **fresh planning ceilings, not approved spending or measured
consumption**. Old accounts stay closed. Both routes allow at most four combined
CPU equivalents and one GPU on local/dr-train; no paid API, cloud rental,
protected-outcome access, public deployment or manuscript submission.

| Stage | A CPU h | A allocated GPU h | B CPU h | B allocated GPU h |
| --- | ---: | ---: | ---: | ---: |
| One terminal technical/native readiness decision | 12 | 2 | 16 | 4 |
| Fixed development, checks, controls and protocol freeze | 16 | 4 | 20 | 6 |
| Frozen comparative runs | 32 | 16 | 40 | 30 |
| Analysis, return, cleanup and owner report | 20 | 4 | 20 | 8 |
| Total ceiling | **80** | **26** | **96** | **48** |
| Elapsed ceiling, including technical decision | **7 days** | | **7 days** | |
| Technical decision deadline from release | **36 hours** | | **48 hours** | |

CPU/GPU units are cumulative ceilings, not concurrency or guaranteed hardware
availability. Stages may use less and cannot borrow from a closed account. GPU
allocation includes idle/loading time. Reserve reporting/return and 25% execution
contingency before the locked matrix, not after overspending it.

For A, reuse the existing checkpoint subject to hash/license/runtime checks;
do not search models. Ordinary dependency retrieval would be capped at 20 GiB,
task-owned peak disk 80 GiB, remote aggregate RAM 32 GiB/local 2 GiB. Place
installation temporary files and writable caches on measured task-owned disk,
not an unexamined 4 GiB RAM filesystem. No new scientific input or actor-model
download is proposed for A. Current free space/GPU availability must be checked
before booking; shared models/services cannot be evicted to make the plan fit.

B would additionally require a capsule byte/rights manifest, explicit input
modality/model choice and a download/storage ceiling before capsule retrieval.
Those sizes are currently unknown, so the 96/48 envelope is **not yet a complete
execution authorization package**. Its initial metadata gate must stop before
download if these cannot be specified within the source-readiness tranche.
Do not assume original per-capsule size bounds imply the total fits local disk.

An illustrative A matrix, if admitted, has two main arms/two seeds, G and V
secondary cells/one common seed, and LLM-only/one seed: at most 7N model missions
for N<=26 (182), plus at most 16 development missions (198 total). Deterministic
workflow runs add execution cost, not new independent observations. The secondary
factorial contrast uses the common seed; extra main-arm seeds cannot be pooled
as a balanced four-cell design. Freeze per-mission limits before development;
the previous three-call/4,096-output-token caps are the starting proposal, not
proof of adequate throughput. Actual development timing must show that this
fixed matrix plus 25% contingency fits every stage. Otherwise stop before locked
agent outcomes rather than changing the model, seeds or budget after results.

## 6. A's finite repair contract

This explicitly separates bounded software diagnosis from a scientific rerun:

1. **One diagnostic capture per affected lineage.** Inspect returned logs and
   package files; permit one diagnostic import for 22 and 26 to obtain the lost
   traceback. Log per-mount free bytes/inodes, temporary paths, writable HOME/
   caches and exact imports. No benchmark gold values or agent outcomes are
   exposed. If the cause still requires an open-ended version search, stop.
2. **One correction batch total.** Freeze documented storage/cache, system-library
   and dependency fixes from that evidence. No sequence of alternative package
   recipes and no second correction batch. Installation/build commands have one
   planned attempt each; a failed build is terminal under this release.
3. **One native admission pass.** Retain the existing four new development tasks,
   26 locked candidates and original exposure roles. Each selected reference
   gets at most one new execution attempt; the previous SAR30 round executed
   none. Reference fitting is not repeated. Repeated scorer calls on the same
   artifact may test repeatability/invalid-artifact rejection only, with a fixed
   conformance matrix; they cannot become another scientific fit.
4. **One terminal decision within 12 CPU-hours/2 GPU-hours/36 elapsed hours.**
   Require >=24 native-valid locked tasks, >=12 connected source groups, >=3
   domains, no group >25%, and unchanged isolated native scoring. Stop as soon
   as an optimistic bound cannot meet these conditions. No task replacement or
   smaller floor. These are the existing design investment gates, not journal
   submission rules or guarantees of statistical power.
5. **Advance directly under the same release only if all technical gates pass.**
   During bounded development require meaningful public checks with conformance
   on at least half the locked tasks, working matched controls, adequate logging
   and a cost/precision assessment consistent with the intended bounded claim.
   If checks are merely schema/existence tests, or the claimed causal contrast
   cannot be identified, stop before locked agent runs. Do not reopen admission.

The non-admitted tasks remain in the full accounting with reasons; the qualified
population and prospective exclusion mechanism are disclosed. Reference
readiness selection cannot support claims about all ScienceAgentBench tasks.

## 7. B's finite alternative contract

If the owner prefers B, replace A's release rather than append B automatically:

- One metadata/source decision first: existing official roles, rights, modality,
  author exposure, byte limits, evaluator parity and no paid/live scoring need.
  Use Medium as the proposed execution-focused level, rather than treating Easy
  output reading as a scientific execution experiment. A change of level needs
  a new pre-execution rationale, not selection by score.
- For the larger-population justification, prospectively require **at least 30
  eligible held-out paper clusters across three domains**. This is a proposed
  investment gate, not a journal rule or a known available cohort. If metadata
  cannot support it, stop before capsule downloads; do not add training papers,
  duplicate difficulty levels or replace figure questions to reach the count.
- At most four development-paper canaries selected by a fixed metadata rule,
  with one fixed local adapter/configuration and one attempt per canary. Include
  the declared languages/modalities/hardware requirements; do not choose by
  successful outputs. Then one native cohort admission pass within the same
  16 CPU-hour/4 GPU-hour/48-hour tranche, including return reserve. Failure of a
  mandatory parity/isolation canary is terminal; no second adapter or canary set.
- Before full comparison, the admitted population must still meet the declared
  paper/domain coverage and have validated public diagnostics appropriate to
  the reproduction endpoint. If only answer extraction is measurable, revise
  the proposed scientific-validity claim in an owner decision; do not silently
  redefine the endpoint or claim.

No paid VM is inferred from the old harness's instructions. No generic HAL
local-execution statement substitutes for a CORE-specific working canary.

## 8. Common stop rules and publication decision

The chosen release has one technical decision, one frozen comparison and one
owner report. Stop on any stage/total/deadline cap, unresolved rights or access,
inadequate eligible population, grader disagreement, outcome leakage, ambiguous
dependency cause beyond the single diagnosis, unsupported modality, missing
required input, inadequate scientific-check conformance or an unaffordable
fixed-matrix projection. Preserve all failures, bookings, code and native rules.

A transport timeout has uncertain outcome, not automatic permission to replay;
inspect the same job/receipt. Recovering an already completed evidence transfer
or producing a truthful closeout is allowed, while scientific attempts remain
bounded. Do not use delivery recovery as an experiment retry loophole.

**Do not stop or redesign merely because a valid full study has a null/negative
effect.** Complete its frozen analysis, costs and limitations. A wide interval
means uncertainty, not equivalence. No new model, seed, dataset or contrast is
added to obtain significance. The owner receives results before a manuscript.

The [ESE scope](https://link.springer.com/journal/10664/aims-and-scope) includes
original/replicated empirical studies and supporting research infrastructure.
The [official JSS description](https://shop.elsevier.com/journals/journal-of-systems-and-software/0164-1212)
requires SE knowledge beyond the application and welcomes replication and
negative results. Neither scope supplies the numerical admission gates above.

Reviewer judgment:

- Harness repair alone: **not sufficient** for the proposed agent paper.
- CORE migration alone: **not sufficient** either.
- A completed, fair, mechanism-distinguishing A study: **potentially assessable**
  as a bounded empirical result; source concentration and one model constrain
  its claims. Actual results and closest-work distinction decide readiness.
- A completed B study with a genuinely larger qualified paper cohort: **greater
  breadth potential**, but its reproduction/reporting construct must match the
  contribution; local feasibility is currently less established.
- Existing evidence today: **neither route is ready for manuscript submission**.
  There is no defensible numerical probability of acceptance from these records.

The best next owner choice is A under this finite contract. If it fails, deliver
the terminal report and close that branch. CORE-Bench remains a separately
justified decision, not an automatically renamed qualification round. No
independent expert validation, clinical benefit or customer/business outcome is
claimed from a solo computational study.
