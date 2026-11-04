# Claim ledger

Use this ledger to reconcile the manuscript, README, presentation, pilot report and sales copy. A statement may advance only when the linked evidence supports its exact population, endpoint and version.

| ID | Statement | Status | Evidence / next evidence |
| --- | --- | --- | --- |
| C01 | Local retrospective screening UI and engine are implemented | IMPLEMENTED; prior verification retained | Source and `docs/RELEASE_VERIFICATION.md` |
| C02 | Historical HIV labels and structures are used | RECORDED | `src/curaloop/resources/hiv_manifest.json` |
| C03 | Pending results are excluded from policy observations | IMPLEMENTED; regression-sensitive | Engine/oracle/worker contracts and prior tests |
| C04 | Recorded Greedy mean new hits exceed Random on the HIV subset | HISTORICAL_EXPLORATORY | `docs/evidence/hiv-benchmark/summary.json` |
| C05 | Current RL transfers usefully to HIV | NOT_DEMONSTRATED | Both controllers used 300/300 fallback requests |
| C06 | Pending-aware selection improves held-out-target deadline discovery | HYPOTHESIS | New frozen multi-target experiment required |
| C07 | Proposed simulator models a particular lab's operations | NOT_VALIDATED | Measured timestamps, capacity and cost data needed |
| C08 | Product reduces actual laboratory spending or elapsed project time | NOT_VALIDATED | Prospective or carefully controlled historical customer evaluation |
| C09 | Teams will pay for installation/support | BUSINESS_HYPOTHESIS | Buyer interviews, committed pilot and payment evidence |
| C10 | Software is an operational Digital Twin | NOT_ESTABLISHED | Physical process linkage and independent validation absent |
| C11 | Clinical efficacy, GMP suitability or regulatory qualification | OUTSIDE_CURRENT_EVIDENCE | Separate intended-use and validation programme |
| C12 | New documentation/review package was checked | PACKAGE_AUDIT | `docs/07_audit/PACKAGE_AUDIT.md` |
| C13 | Integer-time deadline/accounting reference passes constructed diagnostics | ENGINEERING_TOY_EVIDENCE_ONLY | `docs/03_research/INTEGER_REFERENCE.md`; 648 fixtures / 3,888 ordering checks; does not promote C06 |
| C14 | Known HIV registry identity and declared gate checks execute | REGRESSION_RESOURCE_ONLY | `research/manifests/task_registry.json`; no additional assay or independent new rights/phenotype audit |

## Language rules

Use “historical assay active” for replay outcomes, “predicted score” for model output, “simulated cost/time” for scenario units and “proposed” for unimplemented functionality. “Confirmed hit” always needs a context: it means delivered assay-label evidence inside a particular replay, not validated therapeutic efficacy. Name a chemical or target population whenever reporting generalization.

The literature may report advantages of another method. Such values remain that study's result and must never be transferred into CuraLoop's product metrics. A paid pilot does not itself establish improved discovery. A software test does not establish predictor quality. A favorable point estimate without uncertainty is incomplete evidence.

## Promotion record

For each change of status record: claim ID, previous wording, new wording, run/artifact identity, exact endpoint, population, reviewer and date. A single-author project can perform an explicit second-pass audit without inventing an independent reviewer. Missing evidence leaves the claim at its prior status while implementation continues.

## Literature-derived claim boundaries

The version-2 review supports statements about inspected source versions and planned controls. It does not support “all journal versions reproduced,” “unbiased for all targets,” “VDR labels corrected,” “BayBE savings achieved,” or “new asynchronous backend implemented.” R05's known-active start, R03's target ascertainment and R26's case-specific objective must remain visible whenever their results inform a comparison. The discrepancy register records uncertainty rather than declaring source errors.
