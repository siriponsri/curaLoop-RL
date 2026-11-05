# Goal 4: development selection and crossed validation

5 November 2026. **FROZEN BEFORE NEW SEMANTIC OUTCOMES.**
Authorized by Plan A after Goal3 revision A readiness. Source checkpoint:
`27aa3593d69d17122a40304ac82698ad6a7e6b95`. Finish within the original window
ending 6 November 05:37:04 Bangkok, 40 cumulative Goal4 CPU-hours, at most four
one-thread workers; no GPU/paid compute/final-family outcomes.

## Question and population

Test whether conditional event-time fixed-list recourse improves deadline
discovery and whether valid finite-mixture screening saves policy computation
against efficient vectorized dense evaluation. A null or unfavorable result is
a valid challenge result, not permission for a fourth candidate or new thesis.
Use the frozen feature-v2 cohort: six development assays/four annotation groups,
two validation assays/two groups. Final16assays/12groups remain sealed. Retain
all source/chemical/rights/independence limits from the dataset card.

The pinned [FS-Mol source decoder](https://github.com/microsoft/FS-Mol/blob/92aa95daba3f43863227e65be85a07b4a2ee754f/fs_mol/data/fsmol_task.py#L117)
uses `bool(float(Property))`. Our trusted projection preserves finite binary
numeric values, including numeric strings, and aborts globally on unexpected
nonbinary/malformed values. It never uses string truthiness or silently drops
such a row/task. This source/schema check precedes new outcome access.

## Frozen campaign choices

Use all128–600retained structures per admitted assay, public Morgan features,
unit costs, new-request budget12 and16initial labels sampled uniformly without
looking at outcomes. Initial labels are sunk knowledge; zero-hit and one-class
starts stay eligible. Explicit study seeds are101,211,307,401,503,601,701,809.
The initial subset is identical across methods, M and operations for each task/
seed. Candidate-keyed positive IID durations use task ID, candidate ID, seed and
operation ID, never outcomes, a private resource hash or dispatch order. No
missingness is introduced. Simulated time units are not laboratory measurements.

| Operation | Role | Assay capacity | Duration law | Deadline |
| --- | --- | ---: | --- | ---: |
| sequential | Familiar |1| D=1with probability1 |12|
| async_mixed | Familiar |2| D=1or4with probability1/2each |8|
| async_longtail | Held-out |2| D=1with1/2;3with1/4;9with1/4 |7|
| single_shift | Held-out |1| D=2or5with probability1/2each |9|

Assay capacity is distinct from host CPU workers. These operations deliberately
test count-limited, deadline-limited and changed-duration conditions; they are
not inferred from real lab timestamps. Held-out-operation utility is not released
or used until M selection is frozen.

## Candidate, controls and measurement

Exactly three configurations of the reviewed architecture: M32/M64/M128, with
all other model/selector/cap/fallback choices unchanged. Fourteen arms at each M:
Random, nearest-hit, frozen Greedy, retrained Greedy, parameter TS, fingerprint
RF128, count-ENS proxy, completion-first CPE adaptation, MC16greedy rollout,
event-dense, event-screened, no-WAIT, no-anticipated-pending-information and
timing-blind-tail. Comparator adaptations and finite-model limits follow
METHOD_REDESIGN_PLAN_A_V1.md. No learned RL controller is trained or claimed.

The primary metric H(T) counts only new source-positive labels delivered by T,
excluding starts/predictions/pending/missing. Settle all due-at-T results atomically,
advance to T after early budget exhaustion, and retain reservations for jobs
unfinished at T. Report accepted/delivered/missing/pending/spent/reserved and
time-discovery area separately. Simulator decision latency is negligible;
measured compute does not imply end-to-end laboratory time savings.

Only public Observation reaches PolicySession. Record acceptance only after
Campaign.submit succeeds. Separate one campaign per process at any instant;
clear queue caches at setup. Count setup plus every decision, fit, bound, queue,
fallback and scoring cost in policy wall/CPU time; whole-run/worker CPU is also
recorded. Keep complete label-containing traces and private outcomes ignored.

## Canary, allocation and selection

Before scaling, run all14arms/all3M/both familiar operations on the development
assay with the largest feature pool (task-ID tie break), seed101:84campaigns.
Keep timing and unfavorable results. No validation/final/held-out-operation run
belongs to the canary. Forecast the full allocation with a conservative factor3
on the largest observed per-arm familiar-operation cost, checking both CPU and
remaining wall budget and available host capacity. Choose the largest feasible
seed prefix from8or4; if neither fits with mandatory controls, consult the owner.
Freeze the allocation before the main batch. No outcome-based removal of an arm.

Development selection uses all six assays/both familiar operations/all14arms/
all3M and the chosen seed prefix. Select M using the largest mean H(T) of
event-screened, averaging seeds and operations within assays, assays within
groups, then groups equally. Exact ties choose smaller M. No timing or validation
result changes this rule. Report the compute/discovery tradeoff and whether any
candidate improves on controls; selecting an M is not a superiority claim.

Freeze the selected M and input/result identities before validation access or
held-out-operation utility. Then run selected-M/all14arms in the crossed design:
development versus validation groups, familiar versus held-out operations. Reuse
the completed selected-M development/familiar batch only as that cell, without
counting its runs twice. No replacement for degenerate or unfavorable tasks.

## Computation challenge, uncertainty and reexecution

On the largest development assay, seed101, both familiar operations and selected
M, independently rerun event-dense and event-screened five times, alternating
method order. Require identical complete public-decision-state sequences and
scientific actions/accounting before calling a timing ratio matched. Include
setup and cold per-campaign caches; report each repetition and fallback shares.

After selection and crossed evaluation, report initial-model Brier/log-loss and
five-bin reliability summaries on remaining historical labels for each task/seed,
as trusted evaluator-only diagnostics. They do not feed selection and do not
establish calibration throughout an adaptive campaign.

Primary contrasts are screened minus dense, Greedy, nearest-hit, CPE and rollout;
retain all controls/ablations and per-group values. Report paired effects with
empirical ranges and descriptive group-bootstrap95%intervals (10,000 draws,
seed20261105), averaging nested assays/seeds first. Only four development and two
validation groups exist; intervals do not certify independent-family population
coverage, confirmatory significance, clinical relevance or equivalence. Do not
pool sources or make an unapproved material-effect threshold.

Reexecute first lexicographic development and validation assays, seed101, all
four operations/all14arms at selected M in fresh worker processes. Compare
deterministic action/event/accounting signatures, separating timing. This is
same-project computational reexecution, not external scientific replication.

## Stop and delivery

Before new semantic outcome use, require reviewed evaluator/runner, meaningful
constructed leakage/accounting tests, pinned source/config/environment and a
freeze receipt. Before validation require a selection freeze. Preserve failures,
all job receipts and ledger. Stop at the first stage/global CPU/wall cap. Any
remote work uses a new verified owned task root and return-before-delete checks.
Deliver full English results, uncertainty/limits, source/input identities and
Thai status, normal main push, then stop for joint Goal4review. No Goal5execution.
