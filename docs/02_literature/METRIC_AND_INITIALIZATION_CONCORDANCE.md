# Metric, budget and initialization concordance

This table prevents numeric comparisons between differently defined experiments. It is an interpretation aid, not a reproduction result. All new-study quantities below remain proposed.

| Item | Source / definition | CuraLoop consequence |
| --- | --- | --- |
| R03 early EF1% | Enrichment at a constant 1% false-positive rate; HAL PDF p. 10 | Name `EF_at_FPR_0.01`; retain source formula/implementation if reproduced |
| Ranked-fraction enrichment | Active fraction among top-ranked k divided by full-pool active fraction | Name `EF_top_fraction`; specify k, rounding and ties; this is a different cutoff |
| R05 acquisition enrichment | Hits in acquired molecules relative to random acquisition of the same count; main PDF p. 6 | Record whether starts enter numerator/budget before any reproduction; use explicit acquired-set denominator |
| New-study acquisition EF | `(H_new / k_new_delivered) / prevalence_remaining_pool_after_initialization` | Name `EF_acquired`; freeze pool and count definition; undefined when denominator is zero or no new outcome delivered |
| Deadline discovery | Count unique new active outcomes delivered at or before T | Primary `H(T)` excludes known initial actives and predictions; report accepted and pending exposure |
| Legacy AUC-DB | Preserved left-step discovery-versus-settled-cost integral with original normalization | Never rename AUROC, AP or time-discovery area |
| Predictor discrimination | AUROC and AP on a separate audit set | Does not substitute for hit discovery; undefined one-class audit cases stay visible |
| Source uncertainty bands | R05 examples use standard error across ten initializations; BayBE examples state confidence intervals | Preserve the actual band type; task-population inference requires independent task/family units |

## Initial-information regimes

The preserved HIV pilot and proposed primary multi-target study sample starting labels uniformly without looking at activity. Runs with zero actives remain eligible. A one-class model fallback is logged rather than removed. This estimates performance under the specified unconditional start distribution.

R05's inspected preprint begins each start with a known active and draws the rest uniformly. A matching sensitivity condition is **conditional known-hit initialization**. The chosen active is prior information and is not counted as a new discovery. It must not be presented as an unbiased draw or used to replace the uniform primary regime. Costs of obtaining that prior active are outside the source's stated retrospective start; a total-cost claim would need to account for them separately.

Fix whether the budget includes initial labels, whether spent or accepted commitments constrain selection, and whether unfinished assays are charged. The new study treats initial labels as sunk knowledge, reserves quoted cost at acceptance and counts only delivered new hits at the deadline. A comparison with another convention must be labelled as an adaptation.

At fixed count k, freeze how simultaneous deliveries are ordered or grouped and how a partially complete group is treated. Never select an ordering after seeing which members are active. For deadline results, process all due outcomes at T atomically under the scheduler contract.

## Reporting contract

For each metric export `name`, `definition_version`, `value_or_null`, `units`, `numerator`, `denominator`, `pool_hash`, `initialization_regime`, `budget_convention`, `deadline`, `tie_rule` and `undefined_reason`. Retrospective evaluator access to full-pool prevalence is allowed for reporting only; hidden prevalence and labels never enter the policy observation unless explicitly part of the scenario's public prior.
