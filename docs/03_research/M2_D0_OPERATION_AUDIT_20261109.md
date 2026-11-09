# D0: operation semantics and identifiability audit

Date: 9 November 2026, Asia/Bangkok. Inspected base:
`bf59b103a789fa2832762abcdc6d5f7dc723466e`. Serial work; no independent reviewer.
Owner authorized applying the research recommendations to local implementation
and planning. This is not a release of molecular experiments or the conditional
96 CPU-hour grant. [Plan and next decision](../06_execution/M2_DIAGNOSTIC_PLAN_20261109.md).

## Findings supported by source

| Finding | Evidence and consequence |
| --- | --- |
| REUSE uses cached predictions | `State.execute` in `research/m2_costed_v2/engine.py` ranks the current `model.p` without calling update. R is separately random; forced REUSE with common G1 is cached greedy, not Random. |
| UPDATE is conditional retraining | It calls `model.update(observed)` only when stale observations exist. RF rebuilds a seeded 64-tree classifier and predicts the pool; neighbor recomputes delivered-label similarities. A no-staleness UPDATE is a no-op plus selection, not an independent fitting treatment. |
| PLAN includes UPDATE | A stale PLAN refits before planning. Therefore PLAN minus REUSE conflates refresh and planning. PLAN minus UPDATE is needed for incremental planning value. At one remaining query PLAN collapses to updated greedy. |
| Planning is a particular approximation | `Predictor.plan` scores hypothetical labels and a sum of the largest remaining probabilities. RF restricts candidates to a shortlist of at most eight; neighbor considers all eligible candidates. This is not a certified full ENS reproduction or a learned dynamics model. |
| Forced operation may never run | In `run`, RF one-class cold states set `forced=None` and choose COLD_UNIFORM. A forced operation can also lose feasibility. `worker.py` branch eligibility checks prefix CPU and snapshot budget, not actual execution of the forced operation. Thus assigned-operation support and executed-operation support differ. This is not hidden-label leakage or proof that M2's aggregate result is invalid. |
| One feature name is misleading | `State.features` computes `cached_top_mean` as the mean over all eligible cached scores. This is a confirmed naming mismatch, not demonstrated numerical corruption. Keep frozen feature order/model bytes unchanged. New instrumentation calls it eligible-score mean in prose. |
| Targets are terminal discoveries under a constraint | `worker.fit_artifacts` subtracts REUSE terminal hits from forced UPDATE/PLAN terminal hits; all use a common G1 continuation. `learning.fit_gate` fits two Ridge regressors. There is no separate scalar CPU penalty in the regression target, although real CPU exhaustion can reduce deliveries. CPU features/feasibility do not make this an explicit net monetary benefit target. |
| Training and deployed decision processes differ by construction | Supervision is one operation followed by G1. L makes repeated operation choices. This establishes a different continuation contract; it does not establish that this difference caused the negative M2 comparison. |
| State feature availability respects delivered information in source | Policy State contains public fingerprints/graphs, observed labels, cached scores and past prequential errors. Oracle labels are separately owned by the evaluator. Hypothetical planning uses proposed 0/1 labels, not the hidden realized label. This audit did not rerun a complete privacy/campaign audit. |

Cold starts, aliases and interrupted operations must remain in the assigned-state
denominator with their reasons. For causal attribution, separately report the
subset where a distinct operation executed. Do not silently replace unsupported
states or select snapshots where a positive effect happened.

## Accounting and replay limits

`worker.campaign` starts scientific Clock before dense fingerprints, public graph,
model work and inference. Imports, authenticated file parsing and deserialization
are startup; the worker/resource envelope accounts for them separately. Branches
carry the snapshot's prefix CPU into the same total cap and charge restoration
and subsequent work. These are source semantics, not fresh timing measurements.

`State.execute`'s operation EWMA includes refresh when PLAN is selected. It does
not provide separate fit, hypothesis-refit, ranking, gate-feature and reporting
timers. Delivery traces give cumulative CPU and requested/actual operation, not
complete fitted-cache histories or action propensities for all alternatives.
Prefix snapshots contain much more state, but only at prescribed locations.
Never infer exact alternative paths, terminal effects, or off-policy values from
ordinary logged trajectories alone. M2's explicitly executed paired branches are
valid for their original frozen question; they do not identify repeated-policy
or arbitrary new-snapshot effects. This round did not read their private outcomes.

Retained aggregate M2 findings remain unchanged: INCONCLUSIVE, L-G1=-0.225,
L-T=-0.425, L-E=+1.1625 in RF/cheap; six assays/four annotation components.
The closed 31.73/48 CPU-hour account is historical reservation accounting, not
measured total-host CPU and not reusable authority. No final-16 payload was read.

## Supported engineering improvement

Added `research/m2_diagnostics_v1/operations.py`, an outcome-free first-action
probe using the frozen `State.restore` and `State.execute`. It forks the same
observable snapshot, distinguishes UPDATE/PLAN cache changes, records whether
PLAN changes updated-greedy selection, preserves the prefix charge, and reports
unsupported/interrupted comparisons as null. It has no dataset loader, Oracle,
label delivery, gate fit, continuation, network, filesystem writer or CLI runner.
Clock production use fails closed without Linux SIGPROF. Injected test clocks
are explicitly labelled and cannot substantiate timing performance.

This is a bounded D1 instrumentation component, not a complete D1 campaign
evaluator. A Linux guarded continuation wrapper, source admission, output pins,
fresh reserve/settle ledger and full return/cleanup remain unimplemented. The
historical engine/predictor/learning modules are deliberately unchanged.

Constructed tests reproduce the cache semantics, terminal PLAN alias, cold-start
override, misleading feature name, copy isolation, CPU exhaustion and interrupted
contrast handling. Test execution and preservation are recorded separately in
[the evidence index](../evidence/m2-diagnostics-20261109-v1/README.md).

## Competing explanations, still hypotheses

1. One-step/G1-tail supervision may not predict value under repeated gate use.
2. Predictor calibration or ranking may limit useful refresh/planning headroom.
3. PLAN overhead or RF shortlist approximation may erase useful decisions.
4. Training targets may be too sparse/noisy or the horizon too short.

No label-free test here ranks those causes or establishes a method improvement.
The first next scientific question is whether any useful, context-dependent
UPDATE/PLAN headroom exists over cheap controls, not which larger policy to fit.
