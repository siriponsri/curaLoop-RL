# M2 synthetic CPU profiling results

8 November 2026. **COMPLETE_12_SYNTHETIC_PROFILES; MOLECULAR_UTILITY_NOT_RUN.**
Base checkpoint: `6dbb20b7eb2ada42bc602012e9c02dafc3d3e789`. The owner approved
a synthetic-only profiling amendment, maximum one CPU-hour / eight elapsed hours,
within the cumulative 48-hour M2 grant. This investigation does not open biological
labels, train the learned gate or authorize molecular evaluation/M3.

## Completed scope

Twelve campaigns: RF predictor, N303 constructed bit vectors, B32 new queries,
initial n0 in {0,16}, G1/always-PLAN policies, repeats 0/1/2. Each campaign completed
32 queries; no censoring, failed profile or technical retry. Five constructed
checks additionally confirmed that the timing wrapper preserves exact deterministic
RF predictions, forwards the original fit return and restores original methods.

The RF/neighbor adapter and planner source file has the same SHA-256 as the prior
M2 preflight: `7a7403e5906dc0b74883f9d2eb35b50a438f13273d82cd2c9ddb25430ba722dc`.
RF remains 64 trees / depth 6 / min leaf 2 / sqrt features / bootstrap / one thread.
Planning remains the original at-most-eight-candidate, two-hypothetical-outcome,
full-remaining-budget greedy-tail approximation. No planner, tree count, candidate
set, seed or biological endpoint was weakened to fit a CPU cap.

All timed profiles ran on dr-train: Intel Xeon E5-2696 v3 @2.30 GHz, Python
3.12.3, starting core 69, enforced one-core-equivalent cgroup quota, 4 GiB memory,
zero swap and one-thread numerical libraries. NumPy 2.3.5, SciPy 1.17.0 and
scikit-learn 1.8.0 runtime files were authenticated from the prior verified private
return, with unused package tests/dataset fixtures omitted. No new download,
credential/configuration/privilege change or biological input was needed.

The matrix order and source/transport identities were frozen before profiling.
G1/P order alternates within repeat/n0 pairs on the same worker. Synthetic labels
and selection seeds retain the original recipe; they are not assay observations.

## Scientific CPU timing, excluding separately charged startup

| Policy | Completed campaigns | Min, seconds | Median, seconds | Max, seconds |
| --- | ---: | ---: | ---: | ---: |
| G1: refit then Greedy | 6 | 2.593 | 2.747 | 2.906 |
| P: refit then matched planning | 6 | 42.691 | 45.369 | 46.911 |

Process-startup CPU ranged **2.696-2.792 seconds**, median **2.738**. Whole-process
CPU was independently recorded and charged, so startup does not disappear from
the project cost. The new five-second startup/reporting allowance fit these
profiles; this is not a universal worst-case guarantee.

The median paired planning/Greedy scientific-CPU ratio was **16.263**. About
**91.99%** of planning CPU was recorded inside actual RF fitting calls, including
the hypothetical branches. Fit/predict counters are nested within update/planning
times and must not be added to them. All instrumentation/logging overhead remains
charged. Full per-repeat/init timings and provenance hashes are in the
[timing receipt](../evidence/m2-cpu-profile-20261108-v1/timing-summary-v1.json).

These measurements explain why the original proposed 30-second bound did not
admit the baseline. They do not show a planning discovery benefit, demonstrate a
learned gate, establish laboratory savings or imply that more computation is
always useful. No synthetic positive counts are used as method-efficacy evidence.

## Provisional caps and the remaining uncertainty

Applying the original 1.25 factor to the maximum completed RF N303/B32 times:

| Initial labels | Provisional Ccheap | Provisional Cplan |
| --- | ---: | ---: |
| 0 | 3.321769 | 55.249770 |
| 16 | 3.633101 | 58.639246 |

The original 96-configuration calibration grid still has **84 unchecked unique
contexts**, including N128, B16 and every neighbor-predictor context. Finish those
before fixing the actual molecular C values or reading biological labels. The
factor is a design allowance over three constructed repeats, not a statistical
runtime coverage bound. Chemical fingerprints and label histories can change
real-data timing; joint assay/CPU caps and partial-count reporting still apply.

## Recommended continuation and completion boundary

The [costed continuation proposal](../06_execution/M2_COSTED_CONTINUATION_PROPOSAL_20261108.md)
retains the original six development assays, two predictors, eight arms, five
paired evaluation seeds, all branches/ablations and the original effect/uncertainty
rules. It allocates different hard process reservations to cheap, RF planning and
neighbor planning contexts. Its conditional conservative upper bound is **47.7672
cumulative CPU-hours**, within 48, including the entire allowed profiling hour.

That budget proof requires remaining calibration to establish Ccheap <=5 seconds,
RF Cplan <=65 and neighbor Cplan <=25. The neighbor envelope is unmeasured and must
pass an explicit technical gate. A failure stops dependent work; it does not
justify truncating the full planner, dropping a predictor or changing assays.

The profiling step is complete. The scientific M2 gate training/evaluation is
still NOT_RUN. The next actor is the owner reviewing this complete revised matrix
before biological campaigns; M3 and final features/labels/presence remain closed.
Current profiling ledger, full return, exact cleanup, prior-state checks and delivery
receipts are linked from the [evidence index](../evidence/m2-cpu-profile-20261108-v1/README.md).
