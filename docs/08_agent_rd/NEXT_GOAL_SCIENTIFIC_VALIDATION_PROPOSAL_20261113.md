# Proposed LR-SC1: scientific validation beyond generic self-debugging

Status: PROPOSED, NOT AUTHORIZED OR STARTED. Prepared 13 November 2026.
This document releases no resources, changes no completed account and does not
authorize model inference, SSH, dataset intake or evaluator access. The completed
local-workflow account and all historical results remain closed/preserved.

## Decision and contribution

Recommend one bounded study, not another expansion of the old version-binding
experiment. Candidate title: **When Do Executable Scientific Contracts Improve
Local Coding Agents? A Compute-Matched Study on SciCode**.

The primary contribution would be new empirical evidence about whether semantic
scientific checks improve independently graded scientific correctness beyond
strong generic generated tests and self-debugging. A typed scientific-contract
compiler is the single candidate intervention: it converts the public problem
specification into executable checks with explicit applicability, tolerance and
failure diagnostics. Existing artifact/version binding is infrastructure.

Do not claim that hashes, provenance, contracts, dependency graphs, rule
generation, scoped repair or runtime enforcement are new. Important overlap:

- [Structure Before Intelligence](https://arxiv.org/abs/2610.19507) already studies
  scientific release control, tracked versions and recovery, including negative
  agent-benefit results in its limited workflows.
- [SciValidityBench](https://arxiv.org/abs/2610.34767) already evaluates scientific
  use validity and compiled decision-governing state.
- [AgentSpec](https://arxiv.org/abs/2503.18666) already includes runtime constraints
  and LLM-generated rules.
- [AuditCoder](https://github.com/puppet0x3f/AuditCoder) already links contracts,
  code ownership, versioned checks and bounded repairs.

Thus automatic check generation alone is also insufficient as a novelty claim.
The proposed contribution is the measured incremental scientific value, failure
boundaries and cost under independently held-out native grading. Distinctiveness
of this exact study is NOT YET ESTABLISHED. Gate 0 must check close work, including
metamorphic scientific-software testing. If a materially equivalent matched study
already exists and no defensible additional question remains, stop rather than
rename the old method or silently invent another intervention.

Research question: Under the same public specification, base model, tools and
total generation/execution caps, does a scientific-contract compiler increase
correctly delivered scientific subproblem outputs compared with a strong generic
test-generating coding agent? Which failures remain despite passed local checks?

## Dataset and scope

Use the existing **SciCode** benchmark, not a new benchmark authored by CuraLoop:
[NeurIPS 2024 paper](https://arxiv.org/abs/2407.13168),
[official code](https://github.com/scicode-bench/SciCode),
[official dataset](https://huggingface.co/datasets/SciCode1/SciCode).
The official inspect integration documents 15 validation main problems and 65
test main problems, and generates dependent substeps sequentially:
[evaluation instructions](https://github.com/scicode-bench/SciCode/blob/e3158ea011d4235245a547460d3688d7ccbf9900/eval/inspect_ai/README.md).

- Development: fixed six main problems from the official validation split,
  selected by metadata/seed before candidate results. Unused validation problems
  remain unused. No best-of selection, curriculum search or tuning trials.
- Evaluation target: all 65 official test main problems, retaining their native
  subproblem dependency structure. Do not isolate a convenient easy substep and
  present it as standard main-problem evaluation.
- Admission floor: at least 50 resource-eligible, native-scoreable test main
  problems. Exclusions are technical/rights-based, fixed before candidate runs,
  with the entire 65-problem denominator and reasons reported. No exclusion based
  on agent accuracy. This floor is a proposed study-design condition, not proof
  of power or 50 independent source publications.
- Preserve native numerical predicates/tolerances. Native tests and expected
  numeric data live in a separate evaluator; they never supply repair feedback
  or compiler targets. Agents use only official public task/background information
  and their own generated public checks. No LLM judge as the correctness oracle.
- Verify dataset/data-file rights separately from the repository's code license.
  Pin dataset, code, numeric-test file and environment hashes before freezing.
  The official numeric HDF5 availability and total size are not yet verified.
- Proposed intake ceilings: 10 GiB benchmark/data download, 10 GiB one new model
  download, 64 GiB owned working disk. If data exceed the ceiling or are blocked,
  ask the owner once with the exact source/path; do not substitute a benchmark.
  Candidate private path: `research/raw_data/external-benchmarks/scicode-2024/`.
- ScienceAgentBench and the six prior molecular examples are not the primary
  dataset and are not silently reopened. No original final16, CF1 private rows or
  old hidden outcomes are required. This new dataset/question does not revise the
  old failed four-lineage gate.

This is a scientific-software study spanning the benchmark's disciplines. It
does not establish pharmaceutical screening utility. Chemistry/biology/materials
subgroups are reported by official metadata and only interpreted at their actual
counts; there is no guaranteed subgroup size or chemistry-only superiority claim.

## Models and controls

Primary proposed model: official **Qwen2.5-Coder-14B-Instruct Q4_K_M**, one pinned
checkpoint. Secondary replication: the existing **Typhoon 2.1 Gemma3 12B Q4_K_M**.
No model search or replacement after seeing performance. Check primary model
license, download identity, runtime support and memory before any evaluation.
The new Qwen download is proposed, not covered by the closed old account.

| Arm | Implementation and role |
| --- | --- |
| L | Direct generation per official substep, without execution feedback; contextual LLM-only control |
| B1 | Strong tool-using self-debugging with standard scientific Python execution |
| B2 | Same solver with generic LLM-generated executable tests; primary comparator |
| P | Same solver with typed scientific-contract compilation and executable checks |
| A | P with semantic scientific predicates disabled, retaining schema/runtime checks |

Primary contrast: P minus B2 in the coding model. Secondary: P minus B1 and
P minus A. Replication runs B1/B2/P on Typhoon. Run L/B1/B2/P/A on Qwen.
At 65 test problems, this is **65 x (5 + 3) = 520 main-problem episodes**,
each containing the official sequential substeps. One fixed decoding seed per
model, task and arm; seeds are not treated as independent scientific units.
Two models support a limited cross-model check, not universal generalization.
The public benchmark may have appeared in model training. Pin model release dates,
disclose unknown contamination, and do not describe this as newly unseen science.

Common information: identical public problem text/background, libraries and
execution observations. P receives no additional reference, oracle, expert rule
or private numerical answer. Distinct representation/compilation is the declared
intervention. Compilation, check generation, revision and all failed calls count
against each arm's total budget. Equal maximum budgets do not imply equal actual
cost; both must be reported. Do not add a free model reviewer to P.

Proposed hard per-main-episode ceilings: 8,192 generated tokens, 65,536 cumulative
input tokens, 24 provider attempts and 20 minutes wall time, across every stage
and substep. At most one feedback-conditioned revision per substep; no repeated
sampling to choose a successful answer. Generated execution: network disabled,
no credentials/other-project mounts, at most two CPU equivalents / 4 GiB per
tool execution, and at most 120 aggregate tool CPU seconds per main episode.
These caps define a resource-bounded adaptation, not an official leaderboard
reproduction. Gate 2 must confirm they fit without modifying them after test runs.

There is no honest universal deterministic solver for arbitrary SciCode problems.
Native reference solutions audit the evaluator, not serve as a comparable agent.
Deterministic syntax/schema checks are a shared control layer. The existing
RDKit fixed implementation remains a separate product reference and must not be
counted as solving SciCode. Closest usable published algorithms identified in
Gate 0 must be represented fairly; inability to implement a required comparator
within this matrix stops the design before held-out generation, rather than
silently omitting it or adding an unbudgeted sixth arm.

## Outcomes, analysis and decision labels

Primary outcome: per-main-problem fraction of requested subproblems correctly
delivered under the unchanged native tests, macro-averaged across admitted main
problems. Wrong, missing, abstained and agent/resource-limit outputs count as
unsolved. Also score full main-problem success. Native-correct but withheld code
is reported separately; withholding everything cannot produce a good primary score.

Use paired effects and a pre-frozen 10,000-resample main-problem cluster bootstrap
with 95% intervals. Keep substeps inside main problems. Check shared-source
dependence where metadata permit and report its limits; a main problem is not
automatically an independent paper. Typhoon's contrast is reported separately.
Uncertainty is task-resampling uncertainty under this suite and one seed, not
estimated variation over all decoding seeds, researchers or pharmaceutical tasks.

Report all-attempt tokens, prompt tokens, model calls, actual and reserved CPU,
allocated GPU, wall time, compiler overhead, truncated runs, invalid checks,
false validations (local checks passed but native result failed), false blocking,
abstention and valid delivered coverage. Do not call zero observed errors a
zero-risk guarantee or use a degenerate bootstrap interval to prove safety.

- **COMPLETE_VALID_STUDY:** data/harness/controls/isolation/freeze passed and the
  admitted matrix is fully accounted for, including failures. A positive effect
  is not required to finish the goal or produce a manuscript.
- **SUPPORTED_INCREMENTAL_BENEFIT:** primary Qwen P-B2 95% interval lower bound
  >0, actual point effect and costs reported. This is a primary-model claim only.
  Mechanism support additionally requires Qwen P-A interval lower bound >0;
  cross-model replication additionally requires Typhoon P-B2 interval lower bound
  >0. Report these separately rather than using an undefined consistency rule.
  Secondary intervals are exploratory, without a family-wide confirmatory claim.
  Do not promote improvement only against L into the primary claim.
- **STRONG_SIGNAL:** additionally at least +10 percentage points on the primary
  outcome. This is a proposed engineering attention threshold, not a clinical
  minimum meaningful effect or an assertion of statistical power.
- **INCONCLUSIVE:** interval includes zero, model is at floor/ceiling, too many
  infrastructure failures, or attribution/replication remains uncertain.
- **NEGATIVE:** evidence favors the comparator or local check failures undermine
  the method. Preserve and report it; do not change method or denominator.

Before freeze, perform outcome-free power/sensitivity simulations for plausible
paired variance/correlation, including a +10-point scenario. Report expected
precision and detectable effects; 50-65 main problems do not guarantee adequate
power. Simulation is a disclosure, not permission to search for a favorable
sample size. The fixed suite remains fixed. Predeclare an imprecision flag when
the final primary 95% interval spans more than 20 percentage points: such results
cannot settle whether a +10-point improvement is practically plausible. A flag
does not trigger another run. If the full matrix cannot fit the time cap, stop
with a design feasibility report and request one material scope decision. Do not
inspect test outcomes to size the study.

## Fresh proposed budget and calendar

**128 CPU-hours + 96 allocated GPU-hours / 14 elapsed days from explicit owner
approval**, maximum four combined CPU equivalents and one GPU worker. Local one
CPU for data/control/analysis and dr-train up to three CPU equivalents; one free
GPU with at least 24 GiB usable VRAM preferred. Remote RAM cap 32 GiB, no swap;
local cap 2 GiB. No paid API, GPU rental, deployment or manuscript submission.
CPU/GPU figures are proposed hard ceilings, not measured runtime estimates.

| Stage | CPU-hour ceiling | GPU-hour ceiling | Stop/advance rule |
| --- | ---: | ---: | --- |
| 0: Distinct question and closest-work audit | 2 | 0 | A defensible empirical distinction and comparator definition; otherwise stop |
| 1: Official data/environment/evaluator admission | 14 | 2 | Rights, isolation, at least 50 scoreable main problems; one environment recipe plus at most one justified technical repair |
| 2: Fixed development and protocol freeze | 16 | 8 | Six fixed validation main problems; no hyperparameter/model search; full matrix + 25% runtime contingency fits remaining caps |
| 3: One locked comparative execution | 64 | 72 | At most 520 main episodes; all attempts accounted; no unplanned second run |
| 4: Analysis, scientific-software plugin demonstration, manuscript and return | 24 | 6 | Reproducible tables/figures, genuine local operation, limitations, full owned return/cleanup |
| Technical-failure reserve | 8 | 8 | Documented infrastructure only; never a result-improvement or new-model allowance |
| **Total** | **128** | **96** | Never borrow allowance from a closed account |

At least 25% timing margin is required before stage 3. The token maximum alone
does not establish runtime feasibility: profiling must include input prefill,
model loading, tool work, failures and GPU residence. Do not silently shrink the
task matrix, remove a baseline or exchange models to fit after freeze. Record a
development floor/ceiling flag when all six fixed development main problems have
zero solved substeps, or every requested substep is solved, respectively. This
flag is a limitation, not a model-replacement or tuning permission; retain the
fixed models and data. No model-selection loop follows the flag.

During locked execution: first three consecutive systemic infrastructure failures
pause the matrix. At most one logged infrastructure-only recovery, preserving
all attempts; never replay a completed or scientific-failure case. If it cannot
be resumed under the same frozen design/caps, close as incomplete/inconclusive.
There is no automatic extension, new dataset, method revision or resource refill.

## Deliverables and journal direction

One new versioned compiler/plugin in the existing workbench, actual model/code
trajectories, pinned benchmark access instructions, native scores and independent
evaluator process (not an independent human reviewer), complete failure/cost
ledger, analysis code, editable English manuscript with figures/tables and an
honest readiness decision. New code must remain separate from frozen old engines.

Because the primary contribution is empirical scientific-software reliability,
propose **Empirical Software Engineering, regular subscription route**, as the
working journal target rather than forcing JCAMD fit. Its official scope emphasizes
empirical software-engineering studies and replication; its publisher states no
APC for subscription publication:
[scope](https://link.springer.com/journal/10664),
[publishing options](https://link.springer.com/journal/10664/how-to-publish-with-us).
This proposed journal realignment is part of the owner decision, not an accepted
change. It is compatible with the previous US$300 publication ceiling on APC,
subject to author/funder requirements and any separately verified charges.
No acceptance guarantee; small, redundant or imprecise results may remain a
technical report. Do not claim that a generic SciCode gain proves drug discovery
impact. A later JCAMD claim would require separately justified molecular evidence.

Approval requested only for the complete proposed scope/resources/target above.
Passing gates proceeds through analysis/manuscript without routine phase prompts;
material data/rights/comparator/budget changes require one consolidated owner
decision. Nothing in this proposal starts a new goal automatically.
