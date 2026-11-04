# Statistical analysis plan

## Estimand

For each eligible final-test task, average the paired difference in newly delivered active hits by deadline across the prespecified seeds. The primary estimand is the equally weighted mean of these task differences. It describes this task population and operational scenario, not every biological target or a real laboratory. Provide raw counts and a normalized view, since high-prevalence tasks can otherwise dominate interpretation.

The primary contrast isolates pending awareness using the same predictor and acquisition family. Select the exact comparator and one primary operational setting before final testing. Compare learned adaptation against the best development-selected fixed baseline as a separately declared contrast. Choosing the best baseline on final-test outcomes biases that contrast.

## Endpoints

Let H(t) count unique delivered active outcomes after the initial seed labels. Define the primary endpoint as H(T). Define the time-discovery area as the left-continuous integral of H(t) from 0 to deadline T, with the boundary convention recorded. Normalize by `T * maximum feasible new assays` only when a meaningful upper bound is available; otherwise report raw area and a documented scale. Use the same integration rule across policies.

Also report final hits versus accepted expenditure, legacy AUC-DB with its original definition, new active scaffold counts, first-hit time with censoring, occupied-capacity fraction, accepted/spent/reserved units, failure rate and policy compute seconds. No hits before T is a censored first-hit outcome, not time zero. Predictive AUROC, AP and calibration are secondary and evaluated on an independent labelled audit set.

## Uncertainty

Keep matched seeds and schedules paired. Use a hierarchical bootstrap that resamples independent task families/tasks first and repeated seeds within selected tasks, with pairing intact. Choose the number of bootstrap draws and bootstrap RNG seed in the frozen configuration; 10,000 draws is the proposed starting setting. When the number of independent task families is too small for stable intervals, show the task-level distribution and label inference as exploratory. Increasing seed repeats does not fix an insufficient number of biological units.

Report the primary point estimate, 95% interval, task-level effects and reliability outcomes. An interval containing zero is inconclusive about a directional advantage. To claim practical equivalence, prespecify an equivalence margin and use an appropriate analysis; a nonsignificant superiority test is insufficient. Multiple secondary contrasts remain exploratory or receive a prespecified multiplicity procedure.

## Pilot, power and material effect

Use development tasks to estimate variance, runtime and likely endpoint scarcity. The owner and study designer then select a material effect in the endpoint's units before the final run. A suggested planning question is whether an extra delivered active per 100 accepted assay units would justify the added computational/operational burden for the intended user; this is an unvalidated decision threshold, not a measured customer preference. Simulate the planned analysis under that effect to select task/repeat counts or narrow the claim.

## Missingness and failure

An assay with no delivered outcome does not become an inactive training label. Primary complete-outcome experiments avoid conflating scheduler and missing-data mechanisms. Sensitivity analyses cover outcome-independent missingness and a separately labelled activity-dependent stress condition. Report the mechanism and the number of affected requests.

Timeouts, invalid actions and numerical failures remain in a reliability table. Predeclare whether the scientific endpoint uses last valid state, a failure penalty or excludes scientifically uninterpretable runs with a transparent denominator. Report both method-level performance and failure frequency; do not cherry-pick successful seeds.

## Reproducible outputs

Produce per-run metrics, per-task contrasts, an aggregate summary, bootstrap settings, exclusion reasons and a figure-to-data manifest. Keep floating-point precision in machine-readable outputs and use rounded values only in presentation. The preserved historical bootstrap values are not recomputed under the new hierarchy or represented as cross-target inference.

## Metric and initialization amendments

Export the exact definitions in [metric/initialization concordance](../02_literature/METRIC_AND_INITIALIZATION_CONCORDANCE.md). Keep fixed-FPR, top-ranked-fraction and acquired-set enrichment separate. State the original pool prevalence and post-initialization remaining-pool prevalence used for reporting; these evaluator quantities are not policy inputs. Undefined EF/AUROC cases use null plus a reason, not a favorable default value.

Analyze uniform starts as the primary regime and conditional-known-hit starts as a named sensitivity. Pair methods within a regime; do not merge the two distributions to inflate sample size. For related assays, retain the task-family hierarchy. The ten-run SEM bands in R05 are not a template for claiming cross-target confidence, and its nonsignificant ALDH1 batch comparison is not evidence of equivalence in this study.

Prespecify the inclusion or exclusion of decision-compute latency in simulated time. Report actual compute even when it is excluded from the primary simulated horizon. Any economic interpretation must show which costs are measured and which are assumptions.
