# Goal 2 results: a valid prototype, without a useful computational advantage

4 November 2026. **The bounded implementation and real-data challenge are
complete. The candidate's computational contribution failed this test.**
It should not be promoted as the high-impact method or as journal-ready evidence.
The broader research ambition remains open; Goals 3–6 have not started.

## What was implemented and executed

A separate development planner can dispatch a partial batch or wait for the
next delivery, values hypothetical joint label information, and uses a
content/time/capacity relaxation to prune root actions. It shares the existing
trusted scheduler without changing the application, old studies or final roles.
An exact nonanticipative small-state reference tests its bound semantics.

The [frozen protocol](GOAL_02_REAL_DATA_PROTOCOL_V1.md) used **real historical
Tox21 assay labels**: 600-compound derivatives for AhR, PPAR-gamma and p53,
supported by the [original challenge paper](https://doi.org/10.3389/fenvs.2015.00085).
These exposed, correlated toxicology/pathway endpoints are development data.
Costs, capacity, deadline and durations are simulated; no new laboratory assay
or therapeutic-efficacy validation occurred. This is a delivered-hit benchmark
adaptation, not a reproduction of Tox21's classification leaderboard.

All **180 frozen runs completed, with zero failed runs**: three endpoints,
three uniform-start seeds, two timing conditions and ten controls. The canary's
ten runs are included, not additional. Two matched groups had zero active
initial labels and were retained. One pre-freeze local smoke is separately
disclosed with a partial record; it is not part of the 180-run ledger or
independent evidence.

## Results and effect estimates

Each cell is mean new assay-active labels delivered by deadline, across nine
task/seed campaigns per condition. It excludes initial labels and pending work.

| Method | Common duration | Heterogeneous duration |
| --- | ---: | ---: |
| Random | 0.333 | 0.222 |
| Frozen empirical-model Greedy | 0.444 | 0.444 |
| Updated empirical-model Greedy | 1.111 | 0.111 |
| Analytical posterior-mean Greedy | 0.889 | 0.778 |
| Nearest-hit | 2.444 | 2.000 |
| Cheap pending-cluster WAIT | 1.111 | 0.222 |
| Azimi2011-inspired CPE rollout | 1.111 | 0.667 |
| Unpruned hit rollout | 0.444 | 0.556 |
| Cardinality-pruned hit rollout | 0.444 | 0.556 |
| Content-pruned hit rollout | 0.444 | 0.556 |

The planning/pruning trio produced identical complete snapshots and selected
actions in all 18 matched groups: **36 exact pair checks passed**. Compared with
analytical posterior-mean Greedy, rollout had 4 wins, 8 ties and 6 losses across
the two conditions; its mean paired effect was -0.333 delivered hits. Compared
with nearest-hit, it had 1 win, 8 ties and 9 losses, with mean effect -1.722 and
observed paired range [-6, +1]. Nearest-hit is the strongest control in this
small panel; these results do not support a discovery advantage for this planner.

The primary matched-computation comparison is also unfavorable:

| Measure, summed across 18 matched campaigns | Unpruned | Cardinality-pruned | Content-pruned |
| --- | ---: | ---: | ---: |
| Root actions considered | 458 | 458 | 458 |
| Actions pruned | 0 | 0 | 13 |
| Continuation nodes evaluated | 14,196 | 14,196 | 14,144 |
| Policy time including model/bounds, seconds | 2.6687 | 2.7243 | 3.3168 |
| Complete run time including feature preparation, seconds | 16.4098 | 16.4365 | 16.7802 |

The content bound was tighter than cardinality for all 458 audited actions and
enclosed every corresponding unpruned rollout value, including the pruned
actions. It pruned only 13/458 actions (2.84%), reduced nodes by 0.37%, and added
24.3% to measured policy time (2.26% to complete run time). Its mean reported
finite-model shortlist gap was 2.962 hits, range [0.5, 6.25]. Tighter bounds alone
did not make this implementation useful. These are one-pass fixed-order timing
measurements, not repeated hardware benchmark confidence intervals.

Neither rollout nor its pruned variants selected WAIT on these real-data runs;
each made two partial-dispatch decisions. The cheap WAIT rule waited seven
times in heterogeneous runs, without an overall advantage. The exact constructed
tests demonstrate that waiting can be selected under informative beliefs, but
that mechanism was not demonstrated by the planner on this development panel.

## Uncertainty and claim limits

The [paired effects](../evidence/goal-02-real-data-20261104-v1/final/paired-effects.csv)
and [per-run metrics](../evidence/goal-02-real-data-20261104-v1/final/metrics.csv)
retain every endpoint/seed/condition, including negative differences. Paired
ranges describe observed variation, not confidence intervals. Three exposed
correlated endpoints do not support a confidence interval for independent
biological-family performance. No confirmatory effect threshold, equivalence
claim or favorable subset was selected.

The simple cluster Beta model is uncalibrated. Sixteen sampled full label worlds
can become artificially informative after hypothetical observations; root
shortlisting can omit useful experiments. Bounds are exact only relative to
that finite decision model, not its sampling error, all omitted root actions,
the true assay distribution or whole-campaign regret. Random, nearest-hit and
analytical Greedy timing also includes avoidable common wrapper overhead; only
the planning trio is the matched computational comparison. No trained/RL
controller exists in this prototype; learned-action share is not applicable.
Nearest-hit's no-hit fallback is recorded in per-run metrics. ENS/ANS, a strong
trained molecular predictor, larger posterior support and independent-family
transfer remain untested. The failure concerns this implementation, not a proof
that all content-aware planning is ineffective.

Finite full-world sampling can also introduce accidental label-duration
correlations even when the underlying generative law makes them independent.
This is a possible approximation error, not an isolated explanation of the
observed failure. A stable hypothesis-mixture model is a future option.

## Compute, integrity and verification

Existing SSH IP profile authenticated to **dr-train** with strict host checking.
Live preflight found 72 allowed logical CPUs, about 115 GiB available memory and
other active services. A single nice-19 process was pinned to CPU 71, with a
1 GiB virtual-memory limit, one-thread environment and a process lock. No GPU,
paid service, dependency installation, key/config changes or other-job changes.
The limited lock-path inspection does not establish the absence of all host
locks; no GPU resource was requested.

- **PASS:** 180 run/attempt pairs; 151.20 run-wall seconds, 151.10 CPU seconds;
  152.81 seconds across phase receipts including driver overhead; maximum RSS
  55.89 MiB. This is measured compute, separate from simulated assay time.
- **PASS:** event-to-metric reconstruction, cost conservation, restoration,
  matched initial labels and operational realizations, 36 pruning pair checks,
  and 458 offline upper-bound checks.
- **PASS:** 107 targeted research tests, including nine new exact/model/privacy
  cases. The randomized tiny oracle covers 48 prespecified four-world states;
  XOR complementary choices and an omitted-root-action example are explicit.
- **PASS:** 191 protected application files and hashes of 162 original
  development run files remain unchanged. Package/source/link checks and final
  independent review are recorded in the evidence receipt.
- **NOT_RUN:** new all-application/browser suites, model calibration/controller training,
  independent reproduction, held-out family/operational study and submission.
  Earlier application timing failures remain in their original delivery record.

Raw scientific outputs are retained at
`.local/goal2-real-data-20261104-v1/final/output` and
`/home/chaw/curaloop-rl/goal2-20261104-v1/output` on dr-train. The
[public run ledger](../evidence/goal-02-real-data-20261104-v1/final/run-ledger.json)
pins every raw run and attempt. Downloaded result archive SHA256:
`c238ae02dddd65fe35c1f5d13e6dad7e6ed68c7baafd76389f3a2eb08630c4f0`.
The [source-only archive](../evidence/goal-02-real-data-20261104-v1/execution-source.zip)
preserves exact frozen bytes, including pre-existing scheduler line endings,
without assay rows. It permits source restoration on another OS; cohort hashes
must still match the pinned preparation. This was remote execution by the same
implementer, not independent reproduction.

## Dataset acquisition and journal decision

[FS-Mol](GOAL_02_DATASET_ACQUISITION_V1.md) offers a paper-backed external
assay-transfer benchmark with explicit data-license notices, but its official
4.87 GB archive returned HTTP 403. The owner has been asked to place `fsmol.tar`
at the exact ignored path in that record. Size/MD5/SHA256 verification is ready;
no archive member or external label has been opened. Its potency-threshold
labels, source split, chemical overlap and conflicting release license notices
must remain distinct from sparse screening hits. LIT-PCBA is a relevant sparse
screening complement, with prepared-file rights/endpoint gates still open.

The [JCAMD scope](https://link.springer.com/journal/10822/aims-and-scope) allows
proper retrospective validation for novel methods/innovative computational
strategies, while prioritizing experimental validation. This prototype supplies
engineering feasibility and a useful failed candidate; it does not yet supply
the novelty and benefit needed for that route. Subscription/no-APC selection
does not relax scientific standards.

The justified next goal is to close real benchmark provenance, labels, overlap,
independent family/operational splits and a stronger model/comparator contract
before further scale-up. A sharper hypothesis-mixture recourse bound is a
research option, not an implemented advance or an automatic new experiment.
Report this Goal 2 result to the owner before beginning later goals.
