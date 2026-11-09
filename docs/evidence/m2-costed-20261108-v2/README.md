# Costed M2 evidence

**Complete technical closeout: PASS. Scientific decision: INCONCLUSIVE.**
Read the [full results](../../03_research/M2_COSTED_RESULTS_20261108.md) and
[owner checkpoint](../../06_execution/M2_OWNER_CHECKPOINT_20261108.md).

## Scope and measured result

Six exposed FS-Mol assays / 1,285 rows / four annotation components. All 4,164
biological units completed:48 prefixes,1,152 forced continuations,576 tuning,
1,920 main,180 RF ablations and288 RF B16 transfer. The fresh release also
completed84 synthetic contexts; twelve previous profiles bring synthetic
admission to96 unique contexts. The six additional booked-but-not-dispatched
failures remain charged; their identical-context retries and absence proofs were
rechecked. Recovered bookings are not extra biological replications.

Primary RF/Ccheap/B32 mean differences in new binary positives:

| Contrast | Mean difference | Conditional95% seed interval |
| --- | ---: | --- |
| L-G1 | -0.225 | [-0.650,0.275] |
| L-T | -0.425 | [-0.900,0.050] |
| L-E | +1.1625 | [-0.075,2.300] |

Only 1/4 components favors L over G1. History attribution is positive
(L-no_history +1.2875), but the predeclared promising-signal rule was not met.
Intervals condition on this fixed, previously exposed cohort; they do not sample
a biological-family population. All initial positives are excluded. No clinical,
chemical-OOD, lab-savings, production-policy or publication-readiness claim.

## Aggregate data and figures

- [Complete aggregate JSON](aggregate-results-v1.json)
- [All 32 predictor/regime/policy mean rows](main-summary-v1.csv)
- [All 32 discovery curves, 33 budgets each](discovery-curves-v1.csv)
- [Plotted values](figure-data-v1.json) and [visual QA](figure-qa-v1.json)
- Primary: [PNG](primary-discovery-v1.png), [SVG](primary-discovery-v1.svg), [PDF](primary-discovery-v1.pdf)
- Curves1: [PNG](rf-cheap-discovery-curves-1-v1.png), [SVG](rf-cheap-discovery-curves-1-v1.svg), [PDF](rf-cheap-discovery-curves-1-v1.pdf)
- Curves2: [PNG](rf-cheap-discovery-curves-2-v1.png), [SVG](rf-cheap-discovery-curves-2-v1.svg), [PDF](rf-cheap-discovery-curves-2-v1.pdf)

Figures retain zero/assigned-budget axes and all eight arms. Curve intervals are
pointwise. Final 178 mm exports passed font/dimension/text-bound checks; the three
PNG previews and three grayscale previews were visually inspected. No physical
print or human scientific approval is claimed.

## Admission, resources and preservation

- [Outcome-blind technical admission and exact caps](technical-admission-v1.json)
- [Constructed engine/analysis/pairing/transport checks](constructed-checks-v1.json)
- [Telemetry-only Windows lock checks](telemetry-io-checks-v4.json)
- [CPU reservation accounting](cpu-accounting-v1.json):114,225 / 172,800 seconds,
  or31.729 / 48 CPU-hours; retained reservations are not total-host measured CPU.
- [Old-history and source preservation](old-history-unchanged-v1.json)
- [Complete private return and independent reread](complete-return-verified-v1.json):
  27,454 task files / 260,658,750 bytes, plus seven export files.
- [Exact deletion](scoped-delete-v1.json) and [fresh absence](fresh-absence-v1.json)

All remote task code, dependencies, inputs, outputs and traces were returned.
Private archive SHA256:
`678f5a2fd2af96091d7adc2fdb3d6d1e138ca02794cc1351010b50ff1f6e2040`.
Exact task `/home/chaw/curaloop-tasks/m2-costed-20261108-v2` and its
`-export-v1` sibling were deleted only after full verification. Never recreate
closed roots or borrow their unused allowances.

Raw structures, fingerprints, labels, gates and individual histories remain
outside public Git in `.local/m2-costed-20261108-v2/`, including complete source
projections, permits, freezes, environment files and the full returned runtime.
Scientific code is `research/m2_costed_v2/`; the original predictor/planner in
`research/m2_v1/models.py` is unchanged. These artifacts support inspection and
reconstruction; no independent full-study reexecution is claimed.

The old [interim snapshot](interim-status-20261109.json) is historical. Final
outcomes remain closed. The conditional 96h / 120h M3/P1/J1 grant was not activated;
see the [disposition](../../../research/manifests/conditional_m3_p1_j1_disposition_20261109_v1.json).
