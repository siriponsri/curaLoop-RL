# Synthetic Budget, Delay, Batch and Reward Specification

## Units and accounting

`cost_units` are **dimensionless scenario units**. They are never monetary baht or actual laboratory consumable prices. Scenario defaults: `assay_cost=1 unit/request`, `budget=30 units`, `batch_capacity=5`, `delay_steps=2`, `initial_labels=12 historical visible examples` at **no incremental campaign cost** (must explicitly label them as sunk prior information). If changing budget to include initial labels, charge all policies equally and record the rule.

Define `spent = sum(cost of committed accepted requests)` and `reserved = sum(cost of pending accepted requests)`, depending on chosen ledger semantics. In preferred semantics, `spent` is charged on **request acceptance** including pending requests, so `budget_remaining = B0 - sum(accepted costs)`; there is no separate double subtraction of reserved. If tracking reserved and paid fields, reconcile all fields and document when reservation converts to spending. A request that fails validation must change neither ledger nor truth visibility.

## Events

`request_accepted -> result_pending -> result_delivered` (or `result_missing`). Requests have unique `request_id`, `compound_id`, `assay_id`, selected `policy`, `scenario_id`, `requested_at_step`, `due_at_step`, `cost_units`, and immutable `event_id`. Delivery at `step >= due_at_step` reveals the label to the *same* policy run only. One result is counted once. A missing assay response is **not** automatically negative.

## Randomness

Separate seeded streams for fixture/truth, policy tie-breaking, delay/noise, and any predictor. Fix randomness per named stream, not one global RNG mutated by UI callbacks. Repeated clicks must not silently advance random state unless the action was accepted. Reproducible runs record RNG seed and library versions; CPU determinism can depend on BLAS/library versions.

## Synthetic stress scenarios

- Batch capacity: 1, 5, 10
- Delay: 0, 2, 5 simulated steps
- Budget: 15, 30, 60 units
- Cost: constant 1 or synthetic heterogeneous costs 1–3 (clearly labelled)
- Missing results: 0%, 5%, 15% with distinct flags
- Noise: simulated assay classification flips 0%, 2%, 10%, tracked separately from historical truth
- Shift: feature/scaffold/target regime changes controlled by documented rule

Use these as educational *what-if* scenarios only. Do not call them GPO laboratory distributions or calibrated assay uncertainty.

## What charts mean

`confirmed_hits` = number of active labels **delivered by current step**, not predicted positives. Cost curves use accepted and charged requests. `hit_recall` can be calculated in a historical fully labelled *evaluation context* but must not become a policy-visible input. `time_to_k_hits` is simulated and may be undefined if k not reached. Reports include all denominators, seeds and run source flags.
