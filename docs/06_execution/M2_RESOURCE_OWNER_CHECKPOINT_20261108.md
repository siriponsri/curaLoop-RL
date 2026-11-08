# M2 owner checkpoint: resource admission, not a method verdict

8 November 2026. **M2 INCOMPLETE_AT_RESOURCE_CHECKPOINT.** Molecular evaluation
and M3 remain NOT_RUN / NOT_RELEASED. This is the same M2 phase, not another M1
mechanism revision.

## What happened

The owner approved the [complete M2 plan](M2_EXPERIMENT_PLAN_20261108.md) at
`9e78f391e8e90398fe86097622753b38bfc1d744`. Its synthetic admission rule requires
the calibrated campaign CPU cap to be at most 30 seconds, computed as 1.25 times
the measured complete baseline time. This was an unmeasured proposed technical
bound; it was not the total 48 CPU-hour allowance.

Six-pool identity/protection and outcome-blind mask checks passed. All six training
pools retain at least 48 structures. No exact canonical structures span the four
annotation components; the historical duplicate rows are within components.
Twelve constructed predictor/planner checks passed on dr-train. Fresh cgroup CPU,
memory and swap proof was obtained. No biological labels were decoded or copied
to dr-train.

The first registered synthetic configuration was RF / 303 constructed molecules /
16 initial labels / B=32 / always PLAN / repeat 0. The order was frozen by technical
resource risk before synthetic results. Planning did not finish by the verified
24.0877 process-CPU-second lower bound. Applying the required 25% allowance gives
a cap lower bound of **30.1096 seconds**, above the permitted 30 seconds. The full
campaign duration is unknown. Neither a speedup nor a molecular-discovery result
can be inferred.

The initial timing attempt had a signal/process-clock granularity mismatch: its
recorded lower bound implied 29.9971 seconds, so its premature STOP inference was
invalid. That attempt and cost are retained. One technical timer repair verified
the actual process-clock threshold before raising the interrupt; the identical
synthetic scientific configuration then established the resource-fit stop. No
predictor, seed, planner, endpoint or dataset was changed.

Only **one unique synthetic configuration, two attempts, zero complete calibration
campaigns and zero molecular campaigns** were executed. All remaining dependent
work was stopped. The learned gate, supervision generation, tuning, main comparison
and ablations are NOT_RUN. This does not establish that the research strategy is
unsuccessful, that the server is unsuitable, or that 48 CPU-hours are insufficient.
The per-campaign reservation proposed in the plan did not admit this baseline.

See [execution evidence](../evidence/m2-selective-compute-20261108-v1/README.md)
and [results](../03_research/M2_PREFLIGHT_RESULTS_20261108.md) for exact receipts,
resource accounting and return/cleanup evidence.

## Recommended amendment for consideration, not execution

Approve a **synthetic-only RF profiling step inside M2**. Keep the total cumulative
48 CPU-hour cap, original 12 November 08:17:29Z deadline, dataset, RF specification,
planner, hypothesis and final protections unchanged. Reallocate one unused CPU-hour
from the main-comparison allocation to admission (main 17 -> 16 hours; synthetic
admission 1 -> 2 hours), without increasing the 48-hour total. This reallocation
and the new per-unit bound require owner approval; they are not made now.

| Item | Proposed bounded amendment |
| --- | --- |
| Scope | Constructed synthetic data only; no biological labels, fitting on real records or final data |
| Matrix | N=303, B=32, n0 in {0,16}, policies G1/P, repeats 0/1/2: 12 campaigns |
| Resources | At most 1 CPU-equivalent / 4 GiB on dr-train; local orchestration at most 1 CPU / 512 MiB |
| Per attempt | At most 180 scientific CPU-seconds plus five startup/reporting seconds; 240-second wall timeout |
| Profiling allowance | At most 1 additional CPU-hour from the reallocated admission bucket, including setup, failures, return, cleanup and delivery; at most 8 elapsed hours and never beyond the original M2 deadline |
| Retry limit | At most two technical retries total, within the same hour; no outcome/seed/parameter substitution |
| Private roots | Fresh `.local/m2-cpu-profile-20261108-v1` and `/home/chaw/curaloop-tasks/m2-cpu-profile-20261108-v1`, not created by this proposal |
| Output | Completed baseline CPU distributions or explicit censoring, measured startup/scoring/refit/plan breakdown and a revised costed M2 matrix for owner review |

Conservative reservation: 12 x 185 = 2,220 CPU-seconds, plus at most 370 seconds
for two retries, 240 setup/transport, 360 return/verification/cleanup and 410
analysis/delivery = **3,600 CPU-seconds**. These are maxima, not claimed runtime.
Each retry retains its cost and original failure. If setup cannot fit its assigned
reserve, or any profile hits 180 seconds, stop and report; do not weaken the
baseline or read molecular outcomes to choose a solution.

The profiling result must determine whether the original evaluation workload can
fit the remaining grant with honest per-unit reservations. Provide the revised
matrix and stage accounting before biological campaigns. Do not automatically
release all 4,260 intended units under a larger cap. Both total compute feasibility
and the original matched-control design must be retained or explicitly amended.

## Owner decision

The recommended next decision is approval of this bounded profiling amendment.
Its [machine-readable specification](../../research/configs/m2_profile_amendment_20261108_v1.json)
is disabled, with no release clock or created root.
Deferring research is also possible; no work is running while awaiting the owner.
No new biological data, additional model family, method revision, protected
evaluation, paid service, product claim or journal submission is requested.
