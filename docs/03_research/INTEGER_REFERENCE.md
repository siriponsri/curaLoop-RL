# Integer-time research reference v1

Status: **IMPLEMENTED_AND_TOY_VALIDATED**, separate from the legacy application.
Version: `curaloop.research.integer-events.v1`.
Source: [event_time.py](../../research/event_time.py).
This is an engineering reference, not a new historical study or a production
replacement. The full development/final study protocol remains NOT_FROZEN.

## Observation and resource contract

Policies receive the immutable `Observation` only: public feature vectors and
cost quotes, delivered initial/new results, missing IDs, pending IDs, clock,
capacity, uncommitted budget and remaining horizon. They receive neither the
Task/oracle nor its outcome table, realized future durations or resource hash.
The trusted Task owns the fixture outcomes and durations. Built-in separation is
an information contract, not protection against a hostile local source owner.

Snapshots contain resource identity, scenario, public action history, events and
derived metrics. They do not serialize the private outcome table. Restoration
requires an explicitly supplied resource with the same hash; it replays actions
and compares the entire reconstructed snapshot. A snapshot is an evaluator/recovery
artifact, not an additional policy input. No missing resource is invented.

## Timing and accounting

- Time is a nonnegative integer. Accepted costs are positive integers; durations
  may be zero. The budget identity is `budget = spent + reserved + uncommitted`.
- Validate the whole submitted batch before mutating state. Reject unknown,
  seeded, used, pending, unaffordable or excess-capacity requests atomically.
- Reserve full cost once on acceptance. Delivered and missing outcomes settle
  exactly once. Missing outcomes never become inactive labels.
- Settle every completion at a timestamp before returning a new observation.
  Request IDs determine log order, not an opportunity to act between simultaneous
  outcomes. A zero-duration submitted batch is accepted completely, then settled.
- Accept new actions only **before** the deadline. Process completions due
  **at or before** the deadline. Keep later work pending with its reservation;
  do not refund it, reveal it or count it in `H(T)`.
- `wait()` advances to the next event or deadline. With no pending work, or at
  the deadline, it returns false. It cannot create an unbounded zero-time loop.
- Public-event reconciliation computes new delivered hits, seed hits, missing
  outcomes, accepted/spent/reserved exposure and the left-step time-discovery
  integral. A hit delivered exactly at T counts in H(T), with no point mass in
  the integral. Diagnostic wall time is recorded separately from simulated time;
  per-model fit/inference profiling belongs to the future baseline work.

`keyed_duration` uses `(task_id, scenario_seed, candidate_id, assay_type)` with
SHA256 and a declared duration set. It takes no outcome or request-order input.
These durations are synthetic assumptions. This reference does not install a
biological task importer, learned model, uniform sampler or asynchronous backend.

## Actual checks and their limits

Current evidence: [toy diagnostics](../evidence/reviewed-v2-integration-20261104/toy-validation-final.json)
and [42-test report](../evidence/reviewed-v2-integration-20261104/foundation-tests-final.xml).

The suite checks early-label invariance, exact-deadline simultaneous delivery,
missing settlement, seeds, zero-duration behavior, rejected batches, changed
resources, tampered snapshots and pending restoration. A separate mathematical
serial reference covers 648 constructed fixtures and all six candidate orderings
per fixture, 3,888 checks. The enumeration is evaluator-only and does not provide
future labels to a policy.

For a static selection order without a deadline, common durations 0/1/4 preserve
selected IDs `a,b` and two synthetic hits while elapsed time changes to 0/2/8.
This is a bounded regression property, not a theorem about all adaptive policies.
For an intentionally constructed heterogeneous fixture with deadline 2,
slow-first delivers zero with one cost unit still reserved; fast-first delivers
two. The independent enumeration upper bound is two. These hand-built outcomes
show that the reference can express a tradeoff; they do not test empirical H1,
pending-aware superiority, controller transfer or a laboratory benefit.

The first test run retained one failure caused by a test's platform-dependent
filename ordering assumption. The assertion now checks the intended file set;
dependency/private-output exclusion remains enforced. The original failed XML
is retained. A later direct `pytest` collection check found that repository-only
modules were absent from that entry point's import path. A scoped test bootstrap
now makes both invocation styles equivalent; direct execution passed all 42 new
tests and full collection found 178 tests. Collection is not full execution.
Scheduler cases passed in the initial run; final combined tests passed.
