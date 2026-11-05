# Goal 4R1 execution contract

Owner approved 5 November 2026: **8 cumulative CPU-hours / 12 elapsed hours /
maximum four CPU workers**. This executes the [reviewed proposal](../03_research/GOAL4R_METHOD_PREDICTOR_PROPOSAL_V1.md).
Proposal statements saying execution was not yet authorized are historical.

Start: **2026-11-05 14:43:55 UTC** (21:43:55 Bangkok).
Deadline: **2026-11-06 02:43:55 UTC** (09:43:55 Bangkok).
Starting main: `6e1458326300a4042f805dac9e73b98f16180dbc`.

## Scope and ownership

Parent is sole writer. Methods, English/evidence and code-interface specialists
review read-only. New code/config/outputs use `research/redesign_v1/`,
`research/configs/goal4r1_protocol_v1.json`, `.local/goal4r1-20261105-v1/` and
`docs/evidence/goal4r1-20261105-v1/`. Old frozen code/data/results remain unchanged.
Do not interpret an executed diagnostic as a passed method-advance gate.

Six existing development assays only; no new data extraction or new validation
cohort. Former validation groups are exposed and excluded from selection. Final
outcomes, P1 implementation, 4R2/V2, Goal5, publication and external writes are
outside this approval. Existing private development payloads may be read by a
role/hash-checked evaluator; policies receive public features/known labels only.
No raw private rows are printed or committed.

## Fixed diagnostic choices before new-code evaluation

M128 for all joint predictors; binary Morgan1024; original anchor control plus
exactly two repairs. Normalized anchor divides only the 64 similarity columns
by8. Direct GP uses `K=4*ones+Tanimoto+1e-8*I`, logistic Bernoulli likelihood,
observed-coordinate whitened MAP/Laplace and correlated full-pool function draws.
Prior covariance and cross blocks use the same nugget. No kernel/prior tuning.
Reuse existing optimizer limits100/ftol1e-12/gtol1e-8/maxls30 and clipping1e-9.
Failure returns the declared prior with a recorded reason; never remove a case.

Supports16/28 are nested original hash-ranked initial IDs. The diagnostic query
set is the complement of the28-label support for both sizes, avoiding a moving
query population. Fixed pair selection uses public features/IDs only, maximum64
unique pairs; joint scores compare the exact product of same-model marginals.
Conditional scores are diagnostics derived from that joint model, not independent
confirmation. Uniform pre-fantasy column permutations are a finite-M stress test.
One fixed RF, smoothed Tanimoto-kNN and nearest-hit controls; nearest-hit is ranking
only. Definitions and source hashes are locked before D1/D2.

Select one of the two repairs by equal-component-macro16-support query log loss;
exact ties lower measured CPU then fixed variant ID. Original predictor is a
control, not a third selectable repair.28-support and old validation do not select.
Main campaign cross13arms*6assays*8seeds*4operations=2496; selected-repair
three ablations add576. Preserve starts, keyed durations, deadlines, unit costs,
public-only state, successful-submit-before-acceptance and sunk-label exclusion.
All canary/reexecution attempts count separately unless explicitly reused by
frozen case identity. No optional-WAIT target or outcome-selected schedules.

## Resource limits and stop rules

D0 cap3600CPU-seconds; D1 cap7200; D2 cap10800; D3 cap7200; global28800.
Include tests, failures, setup, reporting and preservation; state conservative
reserves where exact process accounting is unavailable. Every heavy worker has
one CPU affinity, one BLAS thread, memory/CPU/wall guards and resource receipts.
Do not launch concurrent workers whose reservations exceed the remaining phase
or global cap. Check the absolute deadline at every launch.

The owner subsequently directed CPU processing on dr-train directly. Scientific
constructed checks, predictor fitting and campaigns therefore run on dr-train;
local work prepares code and verifies returned artifacts. Choose worker count
from live RAM/CPU and measured runtime. Use a new
`/home/chaw/curaloop-rl/goal4r1-20261105-v1` root after live
ownership/allocation checks. Retrieve and reread/hash-verify every task file
before deleting only that owned task/export root. Do not recreate old roots.
No new credentials/config, GPU or paid service.

Stop and report if fixed controls cannot fit the budget, definitions cannot be
implemented faithfully, or correctness/role isolation fails. Research conclusions
may be STOP/REVISE/PROPOSE4R2; no new thesis or extra repair without consultation.
At completion publish English reports/evidence on main with a normal push and
give the owner a Thai decision summary. Scientific Goal4 remains NOT_PASSED and
the final-study design NOT_FROZEN unless separately justified later.
