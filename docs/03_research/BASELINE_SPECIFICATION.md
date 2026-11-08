# Baseline specification and objective matching

> **Current planning override, 8 November 2026:** use the [method-first design](METHOD_FIRST_DESIGN_20261108.md). The older question/roadmap below is historical. Preserve frozen
> scientific evidence and safeguards; it does not release QP/QC, a benchmark-
> publication fallback, new data/compute or final outcomes.

Goal 1 proposes a new planning-method research programme; see
[the thesis/validation decision](CONTRIBUTION_AND_VALIDATION_V1.md) and its
[closest-work review](../02_literature/GOAL_01_CLOSEST_WORK_20261104.md). Future
dispatch/wait work must assess adapted 2011 scheduling, ENS/batch ENS, adaptive
parallelism, simple content-aware waiting and matched-compute fantasy rollout
or MCTS. These comparators and a new planner remain NOT_RUN. The fixed-control
catalogue below describes preserved development evidence; it is not silently
expanded into a frozen final method allocation.

**State: partial development implementation; final catalogue incomplete.**
The [NCATS v1 pilot](NCATS_DEVELOPMENT_RESULTS_V1.md) executed Random,
frozen/retrained Greedy, nearest-hit, diversity and the matched pending-penalty
pair under [its frozen settings](NCATS_DEVELOPMENT_PROTOCOL_V1.md). These are
separate research modules, not new current-CLI policies. Explicit ensemble
uncertainty via a calibrated ensemble, a fixed mixture and a generalizing
controller remain unimplemented. A separate
[54-run Gaussian-surrogate adaptation](NCATS_GAUSSIAN_RESULTS_V1.md) now executes
explicit GP uncertainty and pending-location covariance conditioning; it is not
a calibrated Bernoulli model or a full BayBE integration.

## Required arms

| Arm | Selector and update contract | Why it is needed | Delivery state |
| --- | --- | --- | --- |
| Random | Uniform draw from feasible unlabelled, nonpending candidates; no predictor | Chance reference and one-class fallback | IMPLEMENTED; NCATS v1 executed |
| Frozen-model Greedy | Fit the matched predictor only on initial labels; rank by active score thereafter | Isolate retraining value from initial ranking | IMPLEMENTED; NCATS v1 executed |
| Retrained Greedy | Same predictor family; refit on revealed labels at each declared decision event | Strong exploitation control | IMPLEMENTED; NCATS v1 executed |
| Nearest-hit similarity | Maximize Morgan/Tanimoto similarity to any delivered active, including known initial actives | Strong inexpensive low-data control from R05 | IMPLEMENTED; NCATS v1 executed |
| Structural diversity | Maximize distance from the declared observed/reference set; fix ties deterministically | Control for chemical-space coverage | IMPLEMENTED; NCATS v1 executed; no within-batch adjustment |
| Explicit uncertainty | Freeze ensemble/score definition and direction; distinguish entropy, variance and disagreement | Avoid calling uncalibrated margin a posterior | Gaussian-surrogate std IMPLEMENTED/EXECUTED; ensemble and calibrated Bernoulli uncertainty NOT_RUN |
| Fixed mixture | Development-selected probability or schedule mixing explicit selectors | Test whether simple mixing explains adaptation | PLANNED |
| Matched pending-blind / pending-aware pair | Same predictor and feasible set; only the declared pending-conditioning term differs | Primary H1 contrast | IMPLEMENTED; NCATS v1 heuristic executed; final H1 remains untested |
| Asynchronous probabilistic comparator | Explicit finite-pool model with pending variance conditioning or fantasization and a matched multi-hit objective | Compare operational adaptation with established ideas | Gaussian binary-regression adaptation IMPLEMENTED/EXECUTED in separate v1; no within-batch conditioning or inherited regret claim |
| Generalizing controller | Freeze development-trained model and action mapping; log learned and fallback use | Conditional transfer question | PLANNED; legacy tables preserved separately |

When no active is observed, nearest-hit similarity has no reference. Use a prespecified Random fallback with a recorded reason rather than deleting the run. A frozen predictor that cannot fit a one-class start retains its declared fallback for that arm; it does not secretly retrain when the first new active arrives. A dynamic variant is a separately named arm.

## Matched pending pair

All selectors exclude already observed and already pending candidate IDs to prevent duplicate requests. That feasibility rule is common to both arms and does not count as the pending-aware treatment. The pending-blind score ignores the structures or hypothetical outcomes of the remaining pending set.

A tractable primary candidate is a similarity-penalized Greedy score: matched predicted activity minus `lambda * maximum_similarity_to_pending`. Use zero penalty when the pending set is empty. Set lambda to zero for the blind counterpart and select the nonzero coefficient on development data only. Batch size, refill opportunities, predictor update schedule, available quotes, tie rules and decision times are identical. Name this a finite-pool heuristic; do not label it a reproduction of PLAyBOOK or GP-BUCB. Choose and freeze the final pair before final experiments. If it fails to change decisions under heterogeneous schedules, report that diagnostic.

## Asynchronous comparator acceptance

For a GP-BUCB-style adaptation, explicitly describe the covariance/kernel, handling of binary observations, conditioning of variance on pending locations, confidence coefficient and finite-pool selection. Gaussian regression on Boolean labels is an approximation, not a calibrated Bernoulli GP. An adaptation must have a precise name and its own tested behavior. Alternatively, a fantasization method must specify how pending outcomes are sampled and integrated, without accessing their actual historical labels.

The objective is accumulation of new active outcomes by the deadline. Plain best-value expected improvement on a Boolean label can become uninformative after the first positive. It is not accepted merely because a BO package runs. Either define and validate a suitable multi-hit objective or explain why the selected acquisition is an informative heuristic for it. Compare under the same observation contract. External method theory is not automatically inherited by an approximation.

## Compute and batch fairness

Cache immutable fingerprints across arms. Never share fitted campaign models or acquired labels. Record fit/inference calls, update opportunities, actual batch sizes, CPU/GPU allocation, elapsed compute and timeouts. The fixed-batch primary comparison permits the same partial-capacity behavior for both members of a pair; variable batching is a sensitivity analysis.

Report simulated assay time and measured policy compute separately. The primary simulator assumes negligible policy latency unless a compute-aware scenario is explicitly frozen; it therefore cannot establish end-to-end elapsed savings. An optional wall-clock-aware analysis may include measured decision latency under controlled hardware. More frequent retraining is not free, and a deep-model baseline is not automatically stronger than a well-tuned fingerprint control.

## Reproduction vocabulary

Use **reproduction** only when data, preprocessing, initialization, objective, update schedule, code version and metric convention are sufficiently matched and deviations are disclosed. Otherwise use **adaptation** or **inspired baseline**. R05's known-active initialization and explicit argmin MI direction require particular care; see [the concordance](../02_literature/METRIC_AND_INITIALIZATION_CONCORDANCE.md). No comparator reproduction is claimed by this package.
