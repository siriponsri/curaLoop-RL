# M2 preflight results: data ready, CPU admission not passed

8 November 2026. **INCOMPLETE_AT_RESOURCE_CHECKPOINT; MOLECULAR_UTILITY_NOT_RUN.**
Release baseline: `9e78f391e8e90398fe86097622753b38bfc1d744`. Owner-authorized
48 CPU-hours / 96 elapsed hours / maximum four combined workers. The original
LR-M12 M1 negative result is preserved. This is a technical M2 checkpoint, not
another molecular-method verdict.

## Observed results

| Check | Result | Interpretation |
| --- | --- | --- |
| Six prepared development input/feature identities | PASS | Expected hashes matched before label decoding; only six allowed feature sidecars were decoded |
| Protected identity metadata | PASS | No protected canonical/assay/component conflict; protected payloads not decoded |
| Global training-only canonical mask | PASS | Zero cross-component canonical structures; all original training/evaluation rows retained |
| Distinct canonical structures | 1,107 across 1,285 task rows | Repetition is within annotation components; no new biological-family certification |
| Minimum 48 rows per training pool | PASS, range 129-303 | Six development pools remain feasible for the proposed 16+32 allocation |
| Constructed predictor/planner checks | PASS, 12/12 | Engineering properties on constructed data only; no controller utility result |
| Remote resource proof | PASS on recorded receive/bootstrap/calibration jobs | One CPU-equivalent quota, initial core 69, 4 GiB memory cap, no swap, fixed wall limits; no credential/config/privilege changes |
| Synthetic CPU admission | STOP_RESOURCE_FIT | Required full-baseline cap exceeds the proposed 30 CPU-second campaign ceiling |
| Molecular evaluation, learned gate and final evaluation | NOT_RUN | Zero biological-label decode, gate fit, biological continuation or evaluation campaign |

The six pool row counts are 168,303,248,270,167,129, matching the approved
allowlist. Four annotation-connected components remain the outer holdout units.
The broad quarantined component is not relabeled as a certified biological family.

## Exact synthetic timing evidence

Configuration: RF 64 trees / depth 6 / min leaf 2 / sqrt feature subsampling /
bootstrap / no class weights / one thread; 303 constructed bit vectors; 16
constructed initial labels; 32 new queries; always the matched ENS-inspired
planner; repeat 0. Python 3.12.3 on dr-train; retained offline NumPy 2.3.5,
SciPy 1.17.0 and scikit-learn 1.8.0 dependencies were hash-authenticated.

The predeclared calibration order placed the most resource-demanding RF case
first, independently of biological outcomes. One unique configuration was
attempted twice; neither campaign completed. Ninety-five other intended unique
calibration configurations were not run after the stop. No molecular data was
present on the remote task root.

- Original attempt `calibration-000`: signal interruption at recorded 23.997707119
  process seconds yielded a cap lower bound 29.997133899. Its immediate failure
  inference was invalid because the bound was below 30. Preserve its raw receipt
  and full 31-second reservation; exclude it as admission evidence.
- Technical repair: verify actual process-clock elapsed time above 24.05 before
  interrupting. The same data generator, predictor, planner, seed and endpoint
  remained unchanged; this was not a new scientific mechanism.
- Repaired attempt `calibration-000-r1`: full campaign still incomplete at
  **24.087672592 CPU-seconds**, implying **30.109590740 CPU-seconds** with the
  plan's required factor 1.25. Whole-process CPU was **26.913984235 seconds**,
  within its 31-second reservation. The signal-time bound is a censored observation,
  not an exact finished-campaign duration or estimated total runtime.

Whole-process minus timed scientific CPU was approximately 2.8263 seconds in the
repaired attempt. This also exceeds the original nominal one-second startup/
serialization assumption, although the actual whole-process attempt stayed below
31 seconds. A future profiling amendment proposes five startup/reporting seconds;
that allowance remains a proposed bound to check, not an established worst case.

Because a required calibrated cap is above 30 seconds, the approved protocol
requires stopping dependent molecular work before altering this limit. Ccheap,
the full Cplan, predictor quality, gate behavior, effect sizes and discovery/CPU
frontiers are unmeasured. No significance, speedup, efficiency, noninferiority,
therapeutic efficacy or practical-effect claim follows.

## What is implemented and what remains

Implemented in isolated `research/m2_v1/`: authenticated outcome-blind admission,
training-mask derivation, frozen RF/neighbor adapters, matched hypothetical
planning, deterministic synthetic generator, constructed checks and bounded
synthetic calibration with a retained technical timer repair. Fresh reservation,
remote cgroup launch and complete-return controllers are separate from production.

The operation-benefit regressors, training continuations, grouped gate fitting,
threshold/Exp3/Gk tuning, eight-arm molecular comparison, ablations, B=16 transfer,
uncertainty analysis and reproduction of molecular findings remain **NOT_RUN**.
No production UI or Python screening policy was changed. The method contribution
remains a hypothesis, and publication readiness is not established.

## Accounting, preservation and owner action

Exact conservative reservations, measured guarded-process CPU, old-ledger pins
and complete-return/exact-cleanup receipts are collected in the
[evidence directory](../evidence/m2-selective-compute-20261108-v1/README.md).
Reservations are charged without refund, including the invalid timing attempt.
Measured worker CPU excludes unmeasured utilities; the conservative ledger includes
explicit utility envelopes. Neither quantity may be presented as total measured
CPU for all activity.

The 48 CPU-hour total was not exhausted. The obstacle is the per-campaign
30-second admission rule proposed without measured RF campaign timing. Do not
conclude that dr-train lacks capacity or that the complete M2 matrix necessarily
fits/fails the overall grant.

Recommended next decision: [bounded synthetic-only profiling amendment](../06_execution/M2_RESOURCE_OWNER_CHECKPOINT_20261108.md),
then a realistically costed matrix for owner review. No molecular continuation,
new data intake, hidden final outcome or automatic M3 is authorized while waiting.
