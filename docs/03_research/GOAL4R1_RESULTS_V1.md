# Goal 4R1 results: predictor value versus planning value

5 November 2026. **FIXED DIAGNOSTIC CHALLENGE COMPLETE.**

**Decision: STOP_CURRENT_ACQUISITION_THESIS.** Retain the direct Tanimoto GP as
a promising development predictor repair. Most observed improvement in familiar
conditions is associated with stronger Greedy prediction; an additional benefit
from the current event planner is not established. This conclusion concerns the
fixed models, planner, six exposed assays and known operating regimes evaluated
here. It is not a general result about every planning method.

The bounded 4R1 diagnostic objective is complete with a stop decision. The broader
Goal4 scientific-advance gate remains **NOT_PASSED**, the final-study design
**NOT_FROZEN**, and P1/4R2/Goal5 unstarted.

## Authorized design and evidence population

The owner approved [4R1](../06_execution/GOAL4R1_EXECUTION_CONTRACT_20261105.md)
with an 8 CPU-hour ceiling, a 12-hour window and at most four CPU workers, then explicitly directed CPU work
to dr-train. All scientific fitting, tests, campaigns and analysis ran there;
local work prepared code and verified returned files. The new window began
5 November 14:43:55 UTC (21:43:55 Bangkok), ending 6 November 02:43:55 UTC
(09:43:55 Bangkok). No GPU or new paid service was used.

Only the six previously exposed development assays/four annotation-connected
components were used. Former validation groups were excluded from selection;
the final 12-component/16-assay outcome panel stayed reserved. The four operating
regimes had also been evaluated previously. Original `held_out` flags remain
provenance labels, not a fresh operating validation claim. There is no certified
evolutionary-family independence or chemical OOD claim.

The [frozen protocol](../../research/configs/goal4r1_protocol_v1.json) fixes the
old anchor predictor and exactly two repairs: anchor features divided by 8, and
a direct Tanimoto logistic Bernoulli GP with covariance `4 + T + 1e-8 I`.
All use M128 and the same binary Morgan1024 representation. GP observed-coordinate
MAP/Laplace inference produces correlated whole-pool function draws, conditioned
through the unchanged finite-mixture recourse interface. This remains an
approximate model, not a calibrated biological posterior or a new GP method.

## What actually ran

| Work | Completed cases |
| --- | ---: |
| Latest constructed numerical/privacy/resource checks | 22 tests |
| Earlier constructed run, retained separately | 18 tests |
| Reporting integrity/aggregation checks | 7 tests |
| Timing-only predictor canary | 12 diagnostic fits |
| Main predictor diagnosis | 576 diagnostic records |
| Timing-only campaign canary | 52 campaigns |
| Main predictor × acquisition cross | 2,496 campaigns |
| Selected-repair mechanism ablations | 576 campaigns |
| Fresh-process computational reexecution | 52 campaigns |

The actual campaign total is **3,176**, including canary/reexecution. Scientific
comparisons use the 3,072 main/ablation campaigns only. Predictor diagnosis has
588 actual records including its separate canary. Repeated fits/seeds are not
new biological samples. Every actual campaign event log reconciled, and all
52 fresh-process scientific signatures matched. This is same-project
computational reexecution, not external scientific replication.

Uniform 16-label initial knowledge remained sunk; no start was excluded for zero
hits or one class. The new request budget was 12. All arms used the same source population,
starts, candidate-keyed durations, capacity/deadline rules and public-only state.
Frozen/retrained Greedy and the dense event planner were crossed with each joint
predictor; RF, Tanimoto-kNN, nearest-hit and Random supplied cheap controls.
The selected repair also had no-WAIT, no-pending-information and timing-blind
ablations. No new controller or learned RL action was introduced.

## Predictor diagnosis and locked selection

Supports of 16/28 labels were nested; both used the same query complement of the 28-label
support. Means first average seeds within assay, assays within component, then
the four components equally. No cross-task representation or prior was trained.
The primary 16-support component-macro log loss selected one of the two repairs,
before campaign results were used for interpretation.

| Predictor, 16 known labels | Log loss ↓ | Brier ↓ | Average precision ↑ | Top-12 precision ↑ |
| --- | ---: | ---: | ---: | ---: |
| Original anchor | 0.701531 | 0.253949 | 0.563819 | 0.618490 |
| Normalized anchor | 0.707914 | 0.256991 | 0.554949 | 0.608073 |
| Direct Tanimoto GP | 0.696516 | 0.251508 | 0.595496 | 0.714844 |
| Fingerprint RF | 0.731370 | 0.265614 | 0.582076 | 0.675781 |
| Smoothed Tanimoto-kNN | 0.692740 | 0.249653 | 0.569747 | 0.623698 |
| Nearest-hit ranking | — | — | 0.547217 | 0.674479 |

GP won the **two-repair selection**, including all four component-omission
sensitivity checks. It did not win every predictor metric: kNN had lower log
loss. Nearest-hit similarity is not an activity probability, so proper scores
are omitted. None of the 48 primary GP diagnostic cases used a numerical fallback.
All support-28 results and fit timings remain in the [diagnosis](../evidence/goal4r1-20261105-v1/predictor-diagnosis-v1.json).

GP pair-label log loss was 1.357336, versus 1.375623 for the exact product of its
own marginals. The old predictor gave 1.368687 versus 1.384235. These are dependent
pair diagnostics, aggregated at component level. They include shared-intercept/
prevalence uncertainty as well as chemical covariance, and do not isolate a
chemical mechanism or validate counterfactual information value. Conditional
scores derive from the same joint model and are not independent corroboration.

## Campaign discovery results

`H(T)` counts new source-positive labels delivered by the simulated deadline,
excluding initial labels, predictions and pending work. Costs/durations are
simulated; source positives retain FS-Mol potency-threshold semantics.

| Arm | Familiar-operation H(T) | Previously evaluated shifted-operation H(T) |
| --- | ---: | ---: |
| Original anchor Greedy | 6.0078 | 2.2109 |
| Original anchor dense planner | 6.1562 | 2.1562 |
| Normalized anchor Greedy | 5.8125 | 2.2500 |
| Normalized anchor dense planner | 5.6953 | 2.1484 |
| GP frozen-model Greedy | 6.6953 | 2.4297 |
| GP retrained Greedy | 6.9609 | 2.2578 |
| GP dense planner | 7.0547 | 2.1875 |
| Fingerprint RF | 6.7031 | 2.1875 |
| Tanimoto-kNN | 6.6719 | 2.0312 |
| Nearest-hit | 6.6719 | 2.3828 |
| Random | 4.2734 | 1.6406 |
| GP no-pending-information | 7.0625 | 2.2344 |
| GP timing-blind tail | 6.8047 | 2.3203 |

The no-WAIT arm has the same two H(T) means as the GP planner. All 32 arm/operation
cells, component values, compute costs and 36 paired contrasts are retained in
the [aggregate results](../evidence/goal4r1-20261105-v1/results-v1.json).

| Paired contrast in H(T) | Familiar mean | Descriptive 95% interval | Shifted mean | Descriptive 95% interval |
| --- | ---: | --- | ---: | --- |
| GP Greedy − original Greedy: predictor value | +0.953125 | [0.250000,2.062500] | +0.046875 | [-0.203125,0.515625] |
| GP planner − GP Greedy: incremental planning | +0.093750 | [-0.101563,0.335938] | -0.070313 | [-0.234375,0.023438] |
| Change in planning gain after GP repair: factorial interaction | -0.054688 | [-0.343750,0.140625] | -0.015625 | [-0.203125,0.171875] |

Intervals are descriptive 10,000-draw bootstraps over only four connected
components. They do not certify population coverage, significance, equivalence
or a prespecified material effect. Repetitions and many pairs do not create
additional independent families.

The GP planner made zero optional WAIT choices in its 192 main scientific
campaigns. The timing-blind ablation made 28 optional WAIT choices in familiar
operations. Removing pending-information gave higher point estimates in both
operating cells; timing-blind exceeded the planner under shifted conditions.
These findings weaken the intended acquisition mechanism. WAIT frequency itself
was never a success target.

## Interpretation and next decision

The familiar-condition Greedy predictor effect is promising, with substantial
component heterogeneity. Incremental planning is small/mixed, its point
interaction with the repaired predictor is negative in both cells, and shifted
frozen GP/nearest-hit controls exceed the planner. This supports the prespecified
stop rule for the current acquisition thesis; it does not establish that
all observed gains are conclusively explained or that every planner is useless.

Retain GP as a stronger development baseline. A new 4R2 method would need a new
decision principle, closest-work distinction and bounded approval. Reusing these
exposed operations/validation groups cannot supply fresh confirmation. Final
labels remain reserved. No automatic escalation to deeper lookahead, RL, new
utility or larger search was performed.

The [agentic R&D plugin direction](../04_business/AGENTIC_RD_PLUGIN_PROPOSAL_V1.md)
can be assessed on evidence quality, plan/replay correctness and workflow value
under its separate P1 contract. A connector or improved established GP alone
does not satisfy the intended journal contribution. No submission, business
pilot or real laboratory saving is established here.

## Preservation and verification scope

See [4R1 closeout](../06_execution/GOAL4R1_CLOSEOUT_20261105.md) for complete return,
resource accounting, exact cleanup and Git state. Frozen sources, original
private-input identities and historical negative results are preserved. Tests
were scoped to the research change; application/frontend/browser suites were
not rerun and the application was not changed. Linux environment bytes are
preservation evidence, not a Windows-runnable or fully hermetic environment.
