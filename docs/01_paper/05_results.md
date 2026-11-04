# Results: preserved historical evidence

**Evidence state: RECORDED_HISTORICAL, not newly executed in this package.** Source: `docs/evidence/hiv-benchmark/summary.json`. Each policy has ten paired initialization runs with a 30-assay budget. Initial labels are excluded from new hits.

| Policy | Mean new active hits | Sample SD | Range | Controller fallback |
| --- | ---: | ---: | --- | --- |
| Random | 0.7 | 0.9487 | 0-3 | Not applicable |
| Greedy | 3.8 | 3.2592 | 0-9 | Not applicable |
| Uncertainty | 0.9 | 1.1972 | 0-3 | Not applicable |
| Q-learning | 3.8 | 3.2592 | 0-9 | 300/300 requests |
| Contextual bandit | 3.8 | 3.2592 | 0-9 | 300/300 requests |

The recorded exploratory Greedy-minus-Random mean paired difference is 3.1 hits, with a deterministic paired-bootstrap 95% percentile interval of 1.5 to 4.8. The Uncertainty-minus-Random difference is 0.2, with interval -0.8 to 1.0. These intervals reflect initialization variation within one assay. They are not uncertainty estimates across independent biological targets, and multiple contrasts were exploratory.

Both learned controllers invoked the explicit unseen-state Greedy fallback for every accepted request. Their identical aggregate outcomes therefore do not demonstrate transfer of the learned tables. The recorded evaluation supports a statement about the fallback execution path and the tested Greedy baseline, not superiority of Q-learning or bandits.

## Separate predictor audit

| Quantity | Recorded value |
| --- | ---: |
| Training / test molecules | 960 / 240 |
| Training / test actives | 36 / 6 |
| Shared Murcko scaffolds | 0 |
| AUROC | 0.5562678063 |
| Average precision | 0.0326585013 |
| Brier score | 0.0440829783 |
| Test prevalence | 0.025 |

The predictor result is weak on this small imbalanced test set. Campaign acquisition and static discrimination address different questions, so the recorded Greedy discovery result should be read alongside this limitation. The audit model was not used by the acquisition policies.

## Results not yet available

Multi-target pending-aware comparisons, deadline-based effects, learned-controller transfer, new ablations, external reproduction and prospective customer value are NOT_RUN. The absence of these results is explicit. No expected improvement, invented confidence interval or simulated revenue is inserted into the manuscript.
