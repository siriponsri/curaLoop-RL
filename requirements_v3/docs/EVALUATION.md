# Evaluation and statistics

## One primary endpoint

**Cumulative unique confirmed active hits recovered vs total assay budget spent**, reported as a curve and as area under the discovery-versus-budget curve (AUC-DB), with clear normalization. For each target also report `hits_at_B` for predeclared budget milestones. Avoid labeling predicted positives as true hits.

## Secondary outcomes

- Hit rate (`confirmed_hits / delivered_assays`), enrichment against random and accessible pool prevalence, if prevalence is available to evaluator only.
- Diversity of confirmed actives: unique Bemis-Murcko scaffolds and fingerprint diversity (predefine metric).
- Budget: units spent and reserved; queue utilization; number of decision rounds; simulated calendar time to `k` hits.
- Predictor: AUROC/AUPRC when appropriate on evaluator-held-out data; reliability/ECE/Brier score, calibration drift.
- Agent: regret vs a clearly marked omniscient oracle upper bound (not a deployable baseline), decision latency, training CPU/GPU time, RAM, hyperparameter search cost.
- Under shift: degradation relative to within-target and scaffold-disjoint settings.

## Required comparisons

- Uniform random (many seeds).
- Greedy highest predicted active probability.
- Uncertainty sampling and random-within-high-uncertainty.
- Greedy-diversity (max-min / scaffold coverage).
- Epsilon-greedy and cost-aware acquisition (`expected utility / cost`).
- A credible Bayesian-optimization or diversity-aware AL comparator if computationally feasible.
- Contextual bandit or a simple adaptive heuristic against any more complex RL.
- If a GLARE reproduction is infeasible, explain why and compare methodological differences without claiming state-of-the-art superiority.

## Equal-comparison rules

All runs on a target/scenario/seed must share the exact initial labeled IDs and classifier/featurizer settings. Stop at equal spent budget, not merely equal rounds. Provide identical access to observed outcomes, delay schedule and candidate metadata. When a method uses extra labeled training data or pretrained molecular encoders, report that advantage as a separate setting. Preprocessing and split selection cannot use all test labels to improve the learner or the RL policy.

## Leakage checks that must fail loudly

1. Unrequested hidden labels never appear in observations, log metadata or model-training frames.
2. An agent cannot import or deserialize the oracle's truth array directly in a benchmark run.
3. Repeating the same request cannot increase `confirmed_hits` twice or charge twice without an explicit confirmatory assay action.
4. Delayed outcomes may not affect scores/updates until their release event.
5. Policy training/validation/test target IDs are non-overlapping for generalization claims.
6. Parameter selection is not re-tuned on final reported test targets.
7. Molecular duplicates, canonical tautomer/salt normalization differences and scaffold leakage are audited.

## Statistics

- Use paired seeded runs per target (identical `D0`) rather than independent random sets when comparing policies.
- Report distributions across biological targets and multiple initializations; avoid treating hundreds of correlated episodes on one target as independent biological replicates.
- Report target-level effect sizes with bootstrap confidence intervals across targets, plus within-target seed variability.
- If there are only a few heterogeneous targets, report per-target plots and uncertainty rather than exaggerating `p` values.
- Clearly distinguish pre-registered contrasts from exploratory analyses; correct for numerous comparisons when doing significance testing.
- Make logs, random seeds, datasets version and analysis scripts available for reproduction.

## Simulation VVUQ

**Verification:** unit/property tests prove simulator implements intended cost, queue and label-reveal semantics.

**Validation:** compare modeled distributions of assay prevalence, result delay, cost (if measured) and uncertainty calibration against independent empirical data where available. If unavailable, record `UNVALIDATED_SYNTHETIC_SCENARIO`.

**Uncertainty quantification:** vary scenario assumptions and measure policy-rank stability. A policy that wins only under one arbitrary synthetic setting is a hypothesis for future testing, not a validated lab improvement.

## Publishing threshold

A credible paper needs a clear gap relative to GLARE/SimDMTA/MF-BO, strong baselines, multiple independent tasks, significant (or clearly interpretable null) results, carefully described replay limitations, ablations, and reproducible open code/data accesses. Do not phrase the software framework itself as a new pharmacological discovery.
