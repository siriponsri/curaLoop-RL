# Research protocol v1.1: constrained molecular screening

**State: PROPOSED_NOT_EXECUTED.** Freeze an implementation-specific amendment before final experiments. The historical v0.1 HIV benchmark is a separate completed study with its own definitions. This protocol does not retroactively preregister those results.

The separate [NCATS development amendment](NCATS_DEVELOPMENT_PROTOCOL_V1.md)
was frozen before its [108 executed development runs](NCATS_DEVELOPMENT_RESULTS_V1.md).
It does not freeze or execute this full confirmatory protocol. The exposed
development endpoints cannot become untouched final tasks.

The owner's subsequent [preparatory design direction](DESIGN_SENSITIVITY_V1.md)
is 12+ families and estimation with uncertainty, without a confirmatory
material-effect threshold. This supersedes the earlier requirement to select
such a threshold. The final population, contrast, interval procedure and CPU
allocation remain unfrozen; no final compound outcomes have been inspected.

## Research question and contribution

Determine when selection that accounts for pending experiments improves the discovery of historical active compounds under limited budget, assay capacity and a simulated deadline. A second contribution is a reusable benchmark that exposes every accepted action, pending commitment and delivered outcome. A third, conditional contribution is an adaptive controller that transfers across held-out biological tasks. The controller contribution is dropped or narrowed if the results do not support it.

Novelty remains provisional. Compare with MolPAL (R04), GLARE (R07), ALF (R08), PAL (R09), PLAyBOOK (R10), GP-BUCB (R13), BayBE (R26) and SimDMTA (R27). Existing methods already cover model-guided screening, learned acquisition and asynchronous optimization. The proposed value is a well-defined empirical result and reusable evaluation, not the mere presence of any of those components.

## Prespecified hypotheses

| ID | Testable statement | Role |
| --- | --- | --- |
| H1 | Pending-aware acquisition improves mean confirmed hits delivered by a fixed deadline over a matched pending-blind counterpart under heterogeneous duration | Primary, directional; may fail |
| H2 | The H1 effect changes with capacity and duration variability | Mechanistic secondary |
| H3 | An adaptive controller improves on a development-selected fixed policy on held-out targets | Conditional secondary |
| H4 | Increasing a common delay without a deadline often changes elapsed steps but not final selected sets | Sanity/invariance check |
| H5 | Discovery performance and predictor discrimination can move differently | Descriptive secondary |

H1 uses the same predictor, candidate pool, initial labels and per-candidate operational realization on both sides. Its comparator differs in the pending-awareness component alone. Comparing different models or arbitrary batch sizes is not an H1 test.

## Population and experimental units

The initial engineering pilot uses 3-5 development tasks. Current owner direction seeks 12+ biological families, with separate validation groups if source rights, endpoints, independence and compute permit. This is a design target, not a power guarantee or a cleared dataset. If fewer eligible families exist, report the attrition and narrow the claim; do not count additional seeds or related endpoints as independent families.

A biological task is an assay/target endpoint with a fixed candidate pool and label semantics. Random seeds repeat initialization within that task. They do not create new biological replications. Assays sharing the same target or endpoint family are grouped for splitting and uncertainty analysis. HIV remains a regression task unless it was excluded from all controller development; previous inspection prevents calling it an untouched final test.

## Task roles and freezing

Assign task families to controller development, validation and final test before optimizing the controller. Record target identifiers, assay IDs, sample hashes, duplicate exclusions and split reasons. Random-split and scaffold-split predictor questions are distinct from task-level controller transfer. A second dataset is an external check only if it was untouched by development and its endpoint is suitable.

Freeze the exact primary setting, contrast, eligibility rules, estimand/interval procedure, seed list and compute cap after the engineering pilot and before inspecting final test labels or aggregate results. Record that no confirmatory material-effect threshold is selected. Retain a timestamped protocol hash in every run. Final-test results may motivate a new study but not undisclosed tuning of the same study.

## Operational conditions

Use a small declared grid: zero/common delay sanity scenarios, heterogeneous duration, low/high capacity, and deadline pressure. Derive cost and duration from public descriptors or a seeded external process that does not read hidden activity. Reuse each task/seed/candidate schedule across policies through common random numbers. The primary analysis assumes complete assay outcomes. Missingness is a separate sensitivity experiment with its own mechanism, since activity-dependent missingness can change the estimand.

The deadline is an absolute simulated time horizon. Accept a request only if its cost can be reserved and capacity is available. At the deadline count only delivered outcomes. Do not add late hits to the primary metric or release pending reservations as if they were never committed. Report spent, reserved and accepted exposure together.

## Policies and allocation

Mandatory controls are Random, retrained Greedy, frozen-model Greedy, nearest-delivered-hit similarity, structural diversity, uncertainty with an explicit uncertainty model, a simple explore/exploit mixture and at least one genuine asynchronous acquisition method matched to multi-hit retrieval. [Baseline specification](BASELINE_SPECIFICATION.md) defines selectors, retraining, no-active fallbacks and pending-conditioning acceptance. Add learned controllers after the controls work. Keep predictor/representation settings matched for acquisition comparisons; assess model changes in a separate factorial subset. A relabelled heuristic is not presented as a reproduction of a published algorithm.

## Endpoints and decisions

Primary endpoint: newly delivered active labels at the fixed deadline. Current estimation proposal: average paired repeats within tasks and tasks within families, then weight families equally, with uncertainty respecting that hierarchy. Freeze the exact population and interval procedure before final access. Secondary endpoints are time-integrated discovery, budget-integrated discovery, early enrichment, active scaffold coverage, failure frequency and compute overhead. Never identify the legacy budget integral with AUROC.

Publish all valid seeds and task-specific results. Report infeasible actions, fallback shares, one-class predictor states, timeouts and missing outcomes. Stop a run only for prespecified completion or a logged execution failure. A method failure stays visible and contributes to reliability analysis. Do not silently omit difficult targets or replace a zero-hit seed.

## Interpretation and manuscript decision

Report the H1 effect estimate, uncertainty, family-specific behavior and failure denominator. With no confirmatory material-effect threshold, do not declare practically meaningful superiority, equivalence or noninferiority. Any zero-test result is exploratory unless separately prespecified. A wide interval is inconclusive, not evidence of equivalence. If H3 fails, report the transfer limitation and retain the benchmark contribution. Simulator findings support decisions under declared assumptions; they do not establish real laboratory savings. Register all deviations, their timing and whether final outcomes had been inspected.

## Full-text review amendment, 4 November 2026

R05's inspected ChemRxiv v3 conditions starts on a known active; that differs from the uniform primary regime here. Retain zero-hit starts and add a clearly labelled conditional-known-hit sensitivity, without counting its initial active as a new discovery. Do not discard a seed to make training feasible. Record source task ascertainment: the original LIT-PCBA panel selects targets partly through baseline screening enrichment and is not a random population of all targets.

Freeze metric names and denominators using [metric/initialization concordance](../02_literature/METRIC_AND_INITIALIZATION_CONCORDANCE.md). Resolve endpoint conflicts against exact release and assay metadata before import. The unresolved VDR caption difference is a data-identity gate; the MI optimization-direction question is a reproduction gate, not a reason to assert that the underlying source data are wrong.

The primary event-time analysis keeps measured policy compute separate from assumed assay duration. A laboratory elapsed-time or cost-saving claim requires measured operational evidence. BayBE's backtesting and stopping precedents inform comparison, but their reaction-yield objective and case-specific savings are not CuraLoop results.
