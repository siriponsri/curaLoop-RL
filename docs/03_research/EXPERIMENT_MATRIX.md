# Experiment matrix and ablations

All cells below are planned. Choose a small development grid before a larger final study; do not run a full Cartesian product without a runtime estimate.

| Experiment | Controlled comparison | Question | Required artifact |
| --- | --- | --- | --- |
| E00 | Existing engine on exact frozen HIV config | Does the implementation preserve the historical reference? | Original/new identities and reconciliation |
| E01 | Delay 0 vs common delay, no deadline | Is final selection invariant where expected? | Selected-ID equality and event-time differences |
| E02 | Synchronous barrier vs asynchronous refill | Does waiting for the slowest assay waste useful capacity? | Deadline curves and occupancy |
| E03 | Pending-blind vs pending-aware, matched predictor | Does knowledge of pending work improve discovery? | Primary paired contrast |
| E04 | Constant vs heterogeneous durations | Does operational variability change the E03 effect? | Interaction plot across tasks |
| E05 | Fixed strategies vs trained controller | Does learned adaptation transfer to held-out tasks? | Performance plus learned/fallback shares |
| E06 | Same acquisition, LR vs RF/ensemble | Is a gain actually caused by the predictor? | Factorial subset, calibration and runtime |
| E07 | Complete vs missing outcomes | How sensitive are conclusions to attrition? | Mechanism-specific metrics and missingness counts |
| E08 | One-class initialization retained | Does the method operate under realistic scarce positives? | Fallback histories and all-seed results |
| E09 | Identity/scaffold/near-duplicate audit | Does redundancy change the result? | Split overlap and sensitivity tables |

## Proposed development values

Begin with three development tasks, five seeds, budget fractions of 1% and 5% subject to an explicit minimum feasible pool, capacities 1 and 5, and a short/long duration condition. These are engineering probes, not a final inferential design. Preserve uniformly sampled initial labels even if all are inactive. If every run yields zero hits, examine prevalence, budget and initialization feasibility without selecting only favorable seeds.

## Final study reduction

The final protocol should designate one primary scenario and a limited sensitivity grid. A practical first configuration is 8 policies x 10 tasks x 20 seeds x 4 scenarios = 6,400 runs, plus a separately budgeted training/ablation allowance. That arithmetic is a planning example, not completed work or an established power calculation. Benchmark 10 representative runs to estimate runtime before scheduling it. If task eligibility or resources reduce scope, record the smaller population before final evaluation.

## Ablation interpretation

Remove pending summaries, deadline summaries and adaptation separately. Reuse the same predictor, training allocation and feature representation. Compare state-only changes against a controller of comparable capacity, since a larger model may benefit from added parameters rather than the intended information. Report whether a controller actually chooses different actions in matched conditions; identical actions cannot explain a claimed decision mechanism.

Store outputs under immutable experiment IDs outside the legacy evidence folder. Later reruns add a new ID with a parent/replicate relation. They do not overwrite an unfavorable run or change the definition of an endpoint mid-study.

## Additional controls required after full-text review

| Experiment | Matched comparison | Required interpretation |
| --- | --- | --- |
| E10 | Frozen-model vs retrained Greedy, same predictor and starts | Isolate value of newly revealed labels and record compute overhead |
| E11 | Nearest-delivered-hit similarity vs model-guided selection | Retain simple low-data control and log no-active fallback |
| E12 | Uniform vs conditional-known-hit initialization | Separate unconditional scarcity from known-hit campaigns; no cross-regime seed pooling |
| E13 | Fixed vs variable batch sizes under matched opportunities | Target-specific sensitivity, including compute; no assumed universal small-batch benefit |
| E14 | Local framework adapter vs native acquisition contract | Test objective, privacy, feasibility, version and accounting compatibility |

The earlier 6,400-run calculation is an illustrative planning subset, not a complete allocation for this expanded catalogue. Count every chosen arm, initialization regime and sensitivity cell before freezing compute. Reduce optional cells rather than omitting mandatory controls silently.
