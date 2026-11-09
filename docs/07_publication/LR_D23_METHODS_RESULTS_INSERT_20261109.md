# LR-D23 methods and results insert

Disposition: **INCONCLUSIVE_D2; D3 not run because the frozen D2 gate was not met.**
This is an English development-study insert, not a complete submission manuscript.
It preserves the old M2/D1 manuscript and numerical records. Final16 outcomes
remain closed; independent/domain/author review and M3 are not completed here.

## Proposed method and relation to prior work

We evaluated a residual scheduler that chooses whether to refresh a molecular
predictor or reuse its cached scores. It predicts terminal new-positive gain
from UPDATE relative to REUSE, then overrides a fixed Gk2 incumbent only when
the predicted gain exceeds +0.25 or falls below -0.25. Eight features summarize
remaining assay/CPU budgets, stale labels, cached score statistics, observed
positive fraction, recent prequential Brier error and model availability.
Feature extraction and inference consume the campaign CPU budget. The deadband
is a heuristic and supplies no cumulative loss or policy-improvement guarantee.

Cost-aware retraining and finite-budget active search are established prior
work: [Regol et al., ICML 2025](https://proceedings.mlr.press/v267/regol25a.html)
and [Jiang et al., ICML 2017](https://proceedings.mlr.press/v70/jiang17d.html).
The question tested here is whether behavior-conditioned terminal-discovery
targets improve a repeated refresh decision under a measured CPU budget.
This experiment establishes neither a new RL algorithm nor certified novelty.
See the selected-method reading boundary and algorithm contract in
[the pre-outcome specification](../03_research/LR_D23_ALGORITHM_AND_FREEZE_20261109.md).

## Data and training

The study uses six previously exposed FS-Mol development assays, grouped into
four existing annotation components: 1,285 assay-specific candidate records and
1,107 unique canonical structures. No identical canonical structure crosses
components under the admitted normalization. Components are not certified
independent biological families; scaffold/analog separation is not claimed.
No new dataset, old validation or final16 payload was accessed.

For each outer held-out component, all state generation, targets, scaling and
fitting exclude that component. Round0 uses Gk2 trajectories and a common Gk2
continuation to fit v0. Round1 generates trajectories separately for each outer
fold using its v0 and uses the same frozen v0 continuation for either forced
operation. Final v1 is trained only on round1 targets. Each model is a
standardized Ridge regression with alpha=1 and equal total component weights.
The no-history feature ablation retains features 0, 1, 3, 4; its Gk2 incumbent still
uses history. It is not a completely memoryless policy.

Training uses the unchanged RF predictor adapter, B32, reference CPU, uniform
n0=0/16, three fixed training seeds and snapshots after 8/16/24 deliveries.
There are 216 complete prefixes and 1,296 paired continuation branches across
the two rounds. All 324 assigned state pairs per round have executed support;
outer-fold totals are 72/90/90/72. Four v0, four v1 and four no-history models
were fitted. No third round, hyperparameter search or evaluation-based model
substitution was performed.

## Evaluation and resources

The primary setting is RF/B32/Cref. Initialization is uniform; known initial
labels are sunk information and excluded from new-hit counts. Five evaluation
seeds and both initialization sizes are matched across seven primary arms,
giving 420 campaigns. Two prespecified attribution arms add 120 campaigns.
Random was not assigned in this LR-D23 matrix; older application demonstrations
and Random results belong to separate protocols.

Cref was frozen before molecular outcomes as 1.25 times the maximum complete
synthetic G1 CPU across public pool sizes 128/303 and three assigned cores.
RF/B32 caps are 3.417176 s at n0=0 and 3.799350 s at n0=16. Across three cores,
48 complete G1 campaigns plus24 constructed mechanism/guard checks passed.
Workers used one CPU-equivalent, 4 GiB RAM and zero swap each, with one numerical
thread. Same matched contexts and branch pairs used the same assigned core.
CPU is measured process time, not simulated assay delay or wet-lab expenditure.

Means give equal weight to annotation components, then equal weight to assays
within a component and matched n0/seed contexts. Conditional intervals enumerate
all 5^5 joint evaluation-seed resamples. They describe these exposed assays;
they do not estimate uncertainty over a biological population. The usefulness
gate was frozen before outcomes and has no post-result relaxation.

## Primary results

| Arm | Mean new positives, higher better | Mean scientific CPU (s), lower better | Mean new deliveries |
| :--- | ---: | ---: | ---: |
| G1 | 19.9250 | 2.7443 | 32.000 |
| Gk2 | 19.6000 | 1.3914 | 32.000 |
| Gk4 | 18.8000 | 0.7179 | 32.000 |
| T(k4,tau0.05) | 18.9750 | 3.4900 | 31.925 |
| Frozen-cache greedy | 16.4000 | 0.0558 | 32.000 |
| Nearest-hit | 18.7750 | 0.0107 | 32.000 |
| Round0 v0 attribution | 19.5375 | 1.8322 | 32.000 |
| No-history v1 attribution | 19.1250 | 1.4846 | 32.000 |
| Residual v1 candidate | 18.8375 | 1.5945 | 32.000 |

Relative to G1, v1 saves 41.90% scientific CPU but loses 1.0875 mean new positives,
exceeding the approved 0.25 loss preference. The v1-minus-G1 hit contrast has a
conditional 95% interval [-2.7500,0.2375]. Relative to Gk2, v1 loses 0.7625 hits and
uses 14.59% more CPU; Gk2 descriptively dominates its mean discovery/CPU point.
The corresponding hit interval is[-2.5125,0.7250], and this mean-point comparison
is not a claim of statistical population dominance.

Only one of four components meets the G1 hit-loss preference. Component v1-minus-G1
hit differences, in the frozen component order, are+0.20,-2.40,-0.40,-1.75.
Learned overrides occurred in every component, so complete incumbent fallback
does not explain the outcome. Nevertheless, no-history v1 has 0.2875 more hits
and lower mean CPU than full v1; the history-usefulness requirement fails.
Round1 v1 also has 0.7000 fewer hits than v0, while using less CPU. The v0 result
does not authorize choosing it as a replacement candidate after evaluation.

All 60 candidate campaigns deliver 32 new outcomes without interruption or
feasibility fallback. T's lower delivery mean and recorded interruptions remain
in the comparison. No failed campaign was dropped to improve the candidate's
reported performance. Full precision, component results and conditional
contrasts are in the [aggregate JSON](../evidence/lr-d23-20261109-v1/D2-aggregate-v1.json).

## Interpretation and limits

The proposed residual gate did not meet the prespecified usefulness or attribution
requirements. The current evidence supports stopping this candidate's D3 transfer
study and withholding protected evaluation. It does not establish that all
adaptive retraining is ineffective. The small exposed development population,
conditional intervals, one hardware/software setup and two-round approximation
limit generalization. Computational savings alone do not establish laboratory,
clinical, customer or business benefit.

This insert is useful negative development evidence and a reproducibility record.
It is insufficient to support a journal paper claiming superior molecular
discovery from this method. No final efficacy, broad transfer or deployment
claim should be made from it. A later study would require a separately approved
question/protocol, credible differentiation and independent biological evidence.

The historical D1 masked/full-pool explanation is corrected by
[the identifier-only erratum](../evidence/lr-d23-20261109-v1/pool-frame-erratum-v1.json):
the original training mask retained every compound in all six pools. Earlier
result bytes remain unchanged; seeds, interventions and estimands still differ.
