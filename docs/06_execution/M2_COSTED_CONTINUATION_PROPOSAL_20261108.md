# Costed M2 continuation: preserve the experiment, repair the resource envelope

8 November 2026. **PROPOSED_NOT_RELEASED.** This is the next owner decision after
the approved synthetic profiling step. No molecular campaign or label decoding
is released by this proposal. M3 remains NOT_RELEASED.

## Recommendation

Continue the original M2 study with **the same six development assays, two
predictors, eight arms, five paired evaluation seeds and all declared ablations**.
Replace the unmeasured uniform 31-second process reservation with bounds matched
to predictor and CPU regime. Keep the cumulative **48 CPU-hour ceiling**, the
original **12 November 2026 08:17:29Z deadline** and maximum four combined workers.
No reduction in the always-plan algorithm or discovery endpoint is proposed.

The [12 completed RF profiles](../evidence/m2-cpu-profile-20261108-v1/timing-summary-v1.json)
show Greedy at 2.59-2.91 scientific CPU-seconds and planning at 42.69-46.91, with
startup at 2.70-2.79. The original 30-second admission bound did not fit planning;
the one-second startup assumption was also too small. Every profile completed
32 queries inside the newly approved 180+5-second limit. About 92% of planning's
scientific CPU was recorded inside RF fitting, including hypothetical refits.
Nested fit time is part of total time, not an extra charge.

These are constructed-data timings on the admitted dr-train hardware, not a
molecular speedup/utility finding or a runtime coverage guarantee. Three repeats,
N303 and B32 do not characterize all remaining contexts. The original predictor
and planner source hash is unchanged.

## 1. Complete technical calibration before biological labels

The original calibration grid contains 96 unique configurations. Twelve RF
N303/B32 configurations are now complete; **84 remain**, including N128, B16 and
the neighbor predictor. Run those before biological-label decoding. Use the same
seed recipe, source code, declared profiles and matched timing rules. Pair policy
orders within the same worker and record hardware/load and all failures.

Derive Ccheap/Cplan from full reference maxima multiplied by 1.25, per predictor,
n0 and B, over both pool sizes and three repeats as in the original plan. Current
N303/B32 provisional RF values are:

| Initial labels | Ccheap, CPU-seconds | Cplan, CPU-seconds |
| --- | ---: | ---: |
| 0 | 3.322 | 55.250 |
| 16 | 3.633 | 58.639 |

These are not the final M2 caps until the 84 remaining technical configurations
are checked. The neighbor predictor has **not** been timed in this profiling step.

For the proposed budget proof, require derived Ccheap <=5 seconds in each context,
RF Cplan <=65, and neighbor Cplan <=25. Prefix generation gets at most 15
scientific seconds. Add five process-startup/reporting seconds per isolated unit.
These are prospective admission envelopes, not measured neighbor performance.

**If a required complete reference implies a cap above its envelope, stop dependent
work and report.** Do not truncate planning, lower tree counts/shortlist size,
discard slow seeds, substitute assays or choose a scientific budget using molecular
outcomes. Do not silently drop the second predictor. The remaining calibration
is necessary to test whether this conditional budget proof applies.

## 2. Requested execution scope after technical admission

After owner approval of this proposal and successful technical admission:

1. Implement and verify the operation selector and fixed/threshold/Exp3 controls
   under synthetic sentinel information boundaries. Freshly authenticate the six
   allowlisted inputs and original protection metadata before decoding labels.
2. Use only the original development-label/counterfactual authority: grouped gate
   fitting, G1/mixed prefixes, forced operation continuations, training-only control
   selection and frozen outer development evaluation. No new input pool or split.
3. Run the full main matrix and original no-history/no-UPDATE/no-PLAN ablations,
   RF B16 transfer and bounded reproduction checks. Keep the unsuccessful results.
4. Analyze per-component effects, paired seed variability, actual assays acquired,
   offline/online/startup CPU, decisions, fallbacks and censoring. Return all scoped
   code/data/artifacts, verify complete local reread, delete exact remote task/export
   paths and stop for the owner's M3 decision.

The [original plan](M2_EXPERIMENT_PLAN_20261108.md) remains authoritative for
predictors, operations, eight arms, training targets, seed/fold separation, primary
endpoint, uncertainty and potential criteria. This proposal changes resource
admission/reservations, not those scientific choices. Five startup seconds are
charged to the total grant; the original definition of scientific C still counts
preparation, fits, scoring, gate inference, planning and fallbacks. Report complete
process costs as well; imports and offline training must not disappear from cost.

## 3. Remaining workload and conservative CPU proof

Process reservations at the admission envelopes are **10 seconds for cheap-regime
units, 70 for RF high-regime units, 30 for neighbor high-regime units and 20 for
prefix generation**. Use smaller derived caps when the frozen calibration supports
them, with the same allowance for every matched arm. An individual hard guard and
the stage/total ledger both bind. No free recommendations after scientific C is
exhausted; partial work and actual acquired counts remain in the report.

| Remaining work | Units | Worst reserved CPU-seconds | CPU-hours |
| --- | ---: | ---: | ---: |
| Remaining synthetic calibration | 84 | 2,400 | 0.667 |
| Development prefixes | 48 | 960 | 0.267 |
| Forced continuations | 1,152 | 34,560 | 9.600 |
| Gk/threshold tuning | 576 | 17,280 | 4.800 |
| Main eight-arm comparison | 1,920 | 57,600 | 16.000 |
| RF ablations | 180 | 1,800 | 0.500 |
| RF B16 transfer | 288 | 11,520 | 3.200 |
| **Remaining intended units** | **4,248** | **126,120** | **35.033** |

The [machine-readable calculation](../../research/configs/m2_costed_continuation_20261108_v2.json)
lists each predictor/regime cell, not just a mean-time extrapolation. For example,
main RF uses 480 cheap x10 +480 high x70 =38,400 seconds; neighbor uses 480 cheap
x10 +480 high x30 =19,200. These sum to the already amended 16-hour main bucket.
Branch states remain correlated training examples, not independent research units.

Allow the following remaining stage ceilings, including their non-unit work:

| Remaining stage | CPU-seconds | CPU-hours |
| --- | ---: | ---: |
| Engineering and information/resource guards | 12,690 | 3.525 |
| Remaining synthetic calibration and utilities | 2,700 | 0.750 |
| Prefixes, targets and grouped gate fits | 39,600 | 11.000 |
| Control tuning and aggregation | 18,000 | 5.000 |
| Main comparisons | 57,600 | 16.000 |
| Ablations, transfer and aggregation | 16,200 | 4.500 |
| Analysis, return/cleanup, retries and delivery | 17,460 | 4.850 |
| **Remaining grant upper bound** | **164,250** | **45.625** |

This retains the original stage ceilings after the approved transfer of one
CPU-hour from main comparison to synthetic admission. Old M2 retained 4,112
seconds; the entire current profiling allowance is conservatively bounded at
3,600 even if its actual reservations are smaller.

The profiling ledger's internal setup/return/analysis costs all belong to that
one-hour admission suballocation; they are not charged a second time to the other
original stage ceilings. The closed old M2 reservations were 1,710 setup, 62
synthetic admission and 2,340 analysis/return/delivery seconds. The cumulative
bound is:

`4,112 + 3,600 + 164,250 = 171,962 <= 172,800 seconds`.

There are **838 seconds of headroom** even using that full profiling allowance.
The 17,460-second final-stage ceiling includes up to **138 remaining technical
retries x70 =9,660 seconds**, leaving 7,800 for analysis, full return/cleanup and
delivery. Failed work stays charged. This is a conditional worst-reservation proof,
not a prediction of measured total CPU or a promise every attempted unit succeeds.

Of the original 4,400-attempt maximum, two retained censored/invalid preflight
attempts and 12 completed profiles have occurred. Remaining maximum: **4,386
attempts**, comprising 4,248 intended and at most 138 additional attempts, all
subject to the tighter stage/total/time ceilings. Setup/check utilities are
separately reserved, not mislabeled as molecular repetitions.

## 4. Placement, decision and unchanged claims

Use local at most one CPU / 512 MiB for independent engineering and analysis,
and dr-train up to three workers each one CPU-equivalent / 4 GiB, maximum four
combined. All timed molecular comparisons remain on dr-train; pair on the same
worker with randomized policy order. Require fresh kernel proof, fixed code/data
pins, one-thread libraries and absolute deadline enforcement. Use fresh task roots
named in the eventual execution release; do not recreate closed profile/M2 roots.
No key/config/privilege change, paid service, GPU, live team write or submission.

Technical completion, exploratory potential and publication readiness remain
separate. The original RF Ccheap potential rule and all unfavorable comparisons
are retained. Four annotation components are not certified independent biological
families; seed intervals are conditional on this cohort. The method's molecular
benefit remains unmeasured and final features/labels/presence stay closed.

**Owner decision requested:** approve this complete costed continuation or amend
it before biological campaigns. No work beyond the synthetic profiling release
has begun. A positive timing outcome does not automatically authorize molecular
evaluation or M3.
