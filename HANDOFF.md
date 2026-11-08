# Handoff: method-first design and constructed reference

Date: 8 November 2026, Asia/Bangkok. Base:
`1950b74d12f33eb08dc0b8a0fabf0ec0dbb7ad7a` on main. Parent sole writer.
Owner authorized method design/implementation and correction of old material.

## Current result

M0 COMPLETE_FOR_OWNER_REVIEW. Candidate: computation-bounded baseline-relative
rollout under predictive-model ambiguity. Novelty HOLD_PRIOR_ART_OVERLAP.
Molecular adapter/benefit, new product integration and final study NOT_RUN.
The publication goal is a method evaluated on existing benchmarks, not a new
benchmark paper. The exact report and unfavorable prior results remain retained.

Read [design](docs/03_research/METHOD_FIRST_DESIGN_20261108.md),
[closest work](docs/02_literature/METHOD_FIRST_CLOSEST_WORK_20261108.md),
[scope/supersession](docs/06_execution/METHOD_FIRST_CHECKPOINT_20261108.md),
[current status](research/configs/method_first_status_20261108_v1.json) and
[evidence](docs/evidence/method-first-20261108-v1/README.md).

## Implementation and evidence

New isolated module: `research/method_first_v1/rollout.py`.
Tests: `tests/research/test_method_first_v1.py`.
Completed checks: 20 constructed cases/parameterized checks in final v3 XML.
They cover independent enumeration, completed-score interruption, caching,
observation conditioning, ambiguity fallback and a misspecified-model failure.
The prototype has no dataset loader/network/oracle/application-state access.

One toy expectation changes from 1.1 to 1.3; this is not molecular evidence.
Another rejects nominal optimism and returns Greedy. Cached/uncached horizon-3
outputs match with 15/17 expanded states; there is no wall-clock speedup claim.
The typed nominal control never reports a robust lower-gain certificate.
No application runtime suite/browser/build was rerun because no product runtime
changed. Independent semantic/scientific review remains NOT_RUN.

## Old material corrected

Current GOAL/PLAN/START_HERE/README and manuscript framing now point to the method
design. Historical results and numbered results/declaration chapters are retained.
Old Deep Research adoption and QP/QC proposals carry supersession notices.
The old QP configuration remains byte-identical as a historical proposal; the
current status configuration overrides it to DEFERRED_METHOD_FIRST_NOT_RELEASED.
The previous QP confirmation question is no longer the next owner decision.
Old document creation hashes refer to commit `1950b74`, not newly edited notices.

## Data and resource boundary

No new scientific budget, clock, root or release was created. Ordinary local
constructed unit/mechanism checks are inside the owner's implementation request.
No SSH, raw DB/archive/assay-row/presence access, final outcome, model fitting,
molecular campaign or new split was used. No GPU/paid service or external/team
write. No benchmark-publication pivot or journal submission is authorized.

Keep `.local/r0-chembl-20261107-v1`, `.local/r0r-chembl-20261107-v1`,
`.local/r0a1-chembl-20261107-v1`, `.local/chembl-taskfirst-dq-20261107-v1`,
`.local/chembl-taskfirst-dqr-20261107-v1` and `.local/r0-design-review-20261107-v1`
ledgers CLOSED. Their hashes are checked against the inventory pins and recorded
in new delivery validation. Preserve every old STOP, reservation, protection
union, source namespace uncertainty and exposed/protected task role.

The [previous detailed handoff](https://github.com/siriponsri/curaLoop-RL/blob/1950b74d12f33eb08dc0b8a0fabf0ec0dbb7ad7a/HANDOFF.md)
and phase details remain in Git and the linked old execution readouts.
Do not recreate old remote roots or turn historical absence
proofs into a fresh live host check. No remote host was probed in this task.

## Next actor and discriminating task

Owner reviews the concrete candidate and novelty HOLD. A later bounded M1 task
should audit the reduction to robust baseline regret and test a credible/scalable
predictive-scenario adapter against matched cached robust rollout on exposed
development data. Its data/compute budget/window must be specified before running.
QP32/QC500 are not required or automatically restarted. If only established robust
improvement plus caching remains, report insufficient method novelty and return
to the owner; do not relabel it a new algorithm or substitute a benchmark paper.

Normal English main delivery/push is standing-authorized. Final delivery SHA and
remote equality are checked through Git; delivery evidence pins the exact new
source, tests and documents. The working tree must be clean at final handoff.
