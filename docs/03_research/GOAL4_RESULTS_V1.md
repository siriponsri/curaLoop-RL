# Goal 4 results: real-data planning and screening challenge

5 November 2026. **BOUNDED CHALLENGE COMPLETE; METHOD-ADVANCE GATE NOT PASSED.**

The fixed experiment selected M128 and produced small, inconsistent discovery differences.
Screening did not improve computation: it was 32.2% slower than the dense reference in
the prespecified matched timing check. The selected-M128 planner made zero optional
WAIT choices across its 256 crossed campaigns. These findings
do not support advancing the current computational-advantage claim to a final study.

## Design and actual execution

Owner-approved revision A passed 4/2/12 annotation-connected group quotas, with
6/2/16 development/validation/final assays. Goal 4 used only the six development
and two validation assays. Final outcomes remain reserved. These components are
not certified independent evolutionary families; residual chemical similarity remains.
See the [dataset card](FSMOL_DATASET_CARD_V2.md) and [frozen protocol](GOAL4_PROTOCOL_V1.md).

Uniform 16-label starts were sunk knowledge, including any zero-hit/one-class starts.
New-request budget was 12; costs and durations were simulated. Fourteen arms used
matched candidate-keyed schedules across eight explicit seeds and four operations.
Three development configurations varied only M32/M64/M128. The frozen family-macro
H(T) selection rule chose M128 before validation or held-out-operation access.

| Work | Completed |
| --- | ---: |
| Local all-arm canary | 84 campaigns |
| Development selection, all three M | 4,032 campaigns |
| Additional crossed evaluation, selected M | 2,240 campaigns |
| Alternating dense/screened compute check | 20 campaigns / 10 pairs |
| Fresh-process computational reexecution | 112 campaigns |
| Initial-model calibration diagnostics | 64 task/seed summaries |

The total is 6,488 campaign executions plus 64 calibration diagnostics, not new
biological repetitions. The selected-M crossed panel contains 3,584 unique campaigns;
its completed development/familiar cell is reused without counting those runs twice.

## Discovery results

H(T) counts new source-positive labels delivered by the simulated deadline, excluding
initial labels and pending requests. Average seeds/operations within assays, assays
within annotation groups, then groups equally. Values below are group-macro means.

| Method, M128 where applicable | Development familiar | Development shifted | Validation familiar | Validation shifted |
| --- | ---: | ---: | ---: | ---: |
| random | 4.2734 | 1.6406 | 4.7500 | 1.5625 |
| nearest_hit | 6.6719 | 2.3828 | 7.0938 | 2.4688 |
| frozen_greedy | 5.8047 | 2.1250 | 6.8438 | 2.7188 |
| greedy | 6.0078 | 2.2109 | 7.0312 | 2.6562 |
| parameter_ts | 4.9062 | 1.7344 | 5.1875 | 1.6250 |
| fingerprint_rf | 6.7031 | 2.1875 | 7.1562 | 2.4688 |
| count_ens | 5.7656 | 1.6719 | 7.2500 | 2.4688 |
| cpe_scheduler | 6.0078 | 2.2109 | 7.0312 | 2.6562 |
| greedy_rollout | 5.4375 | 2.0469 | 6.8125 | 2.3750 |
| event_dense | 6.1562 | 2.1562 | 7.3125 | 2.7188 |
| event_screened | 6.1562 | 2.1562 | 7.3125 | 2.7188 |
| no_wait | 6.1562 | 2.1562 | 7.3125 | 2.7188 |
| no_pending_information | 6.1250 | 2.1641 | 7.3125 | 2.6562 |
| timing_blind_tail | 5.9453 | 2.0234 | 7.1875 | 2.9062 |

Paired screened-minus-Greedy effects are shown with descriptive 95% group-bootstrap
intervals. There are only four development and two validation groups. These intervals
do not certify independent-population coverage or confirmatory significance; a narrow
two-group interval must not be interpreted as broad evidence of superiority.

| Population and operations | Mean difference in H(T) | Descriptive interval | Groups |
| --- | ---: | --- | ---: |
| development, familiar | +0.1484 | [-0.0938, +0.3906] | 4 |
| development, held_out | -0.0547 | [-0.1562, +0.0469] | 4 |
| validation, familiar | +0.2812 | [+0.2500, +0.3125] | 2 |
| validation, held_out | +0.0625 | [+0.0000, +0.1250] | 2 |

Nearest-hit and fingerprint RF are stronger than the planner on the development/familiar
point estimates. Validation shows positive point differences against several controls,
but the timing-blind ablation exceeds the planner in validation/shifted operations.
No material-effect threshold was prespecified; these are exploratory effects, not
equivalence, clinical relevance or a declared best method for a wider target population.

## Computational hypothesis and mechanism

All ten prespecified timing pairs had identical public-state sequences and scientific
signatures. On the largest development assay, CHEMBL1738549 (303 structures), seed101,
both familiar operations and five alternating-order repeats, the median screened/dense
policy wall-time ratio was **1.3219**. This is a 32.2%
increase, not a saving. It includes setup and decision costs on the same remote CPU;
it is not an end-to-end laboratory elapsed-time measurement.

At selected M, screening saved 741,182 of 6,170,698 candidate refinements (about 12.0%)
over 34,004 positive-tail branches; 26,236 branches used the declared dense fallback
(about 77.2%). There were zero zero-tail skips in this executed panel. The frozen
dense implementation nevertheless has an avoidable zero-tail calculation in general;
savings from that shortcut would not establish usefulness of the TV/chi-square bounds.

The planner made zero optional WAIT choices across its 256 selected-M crossed campaigns.
Forced waits are scheduler transitions, not learned or informative WAIT decisions.
The no-WAIT arm therefore has the same H(T) means. Pending-information and timing
ablations have mixed results; this panel does not demonstrate the intended WAIT mechanism.
Learned-controller action share is zero: no RL controller was trained or evaluated.

## Integrity, calibration and limits

Reexecution matched all 112 deterministic action/event/accounting signatures in fresh
processes. This is same-project computational reexecution, not external scientific
replication. Actual-log readback reconciled costs, seed exclusion, pending work,
deadline and area for all 6,404 remote campaigns; all 448 main dense/screened
scientific signatures match, including the three development configurations.

Initial-model Brier/log-loss diagnostics and all five-bin per-task/seed reliability
records are retained. They do not establish calibration throughout an adaptive campaign.
Source labels retain FS-Mol potency-threshold semantics. Operations assume candidate-
independent IID durations and negligible decision latency; actual lab cost/time is unknown.
Scaffold/analogue dependence, restricted assay populations, current annotation versions
and only two validation groups limit generalization. There is no chemical OOD claim.

Constructed evaluator checks passed 43 tests locally and in the isolated Linux runtime.
Four reporting-math regressions and seven preservation regressions also passed. Earlier
failed environment-selection evidence and every unsuccessful historical cohort remain
retained. Application/frontend/browser suites were not rerun; application code is unchanged.

## Research decision and journal implication

**REVISE METHOD BEFORE ANY FINAL STUDY.** The computational hypothesis is not supported
on this panel. Small validation discovery gains do not establish the intended broader
method contribution. Preserve final outcomes and review predictor/representation quality,
operational mechanism and a genuinely efficient computational reference before proposing
another frozen study. Such work requires a new bounded goal; no additional architecture
or outcome-driven final-panel revision was executed here.

JCAMD permits appropriate retrospective validation for novel computational strategies,
but this engineering/experimental completion does not establish novelty or submission
readiness ([journal scope](https://link.springer.com/journal/10822/aims-and-scope)).
The subscription publication route and fee budget do not change the scientific standard.

## Evidence and preservation

[Full aggregate results](../evidence/goal4-20261105-v1/results-v1.json),
[all-method cell CSV](../evidence/goal4-20261105-v1/method-cells-v1.csv),
[selection freeze](../evidence/goal4-20261105-v1/selection-freeze-v1.json),
[analysis review](../evidence/goal4-20261105-v1/analysis-independent-review-v1.json) and
the [evidence index](../evidence/goal4-20261105-v1/README.md) provide identities and limits.

Raw labels, delivered-event traces and complete task/environment returns remain ignored.
The [final closeout](../06_execution/PLAN_A_CLOSEOUT_20261105.md) records byte-complete
local preservation of 15,614 files, a conservative global charge of about 3.18 CPU-hours
and verified scoped remote deletion. Linux environment bytes are not a Windows-runnable or fully hermetic
environment; shared system Python/OS libraries are not fully vendored.
