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
| C15 | Three public NCATS development endpoints have source/cohort identities and overlap/attrition audits | DEVELOPMENT_RESOURCES_ONLY | `research/manifests/ncats_development_tasks_v1.json`; [source/protocol](../03_research/NCATS_DEVELOPMENT_PROTOCOL_V1.md) |
| C16 | Six fixed controls executed on the frozen 108-run NCATS development allocation | MEASURED_DEVELOPMENT_ONLY | [Results](../03_research/NCATS_DEVELOPMENT_RESULTS_V1.md); 108 complete, 0 failed; pending penalty 0 wins / 8 ties / 1 loss under heterogeneous delay; C06 remains HYPOTHESIS |
| C17 | Frozen pilot reproduces in a clean venv and separate local checkout | SAME_IMPLEMENTER_SAME_HOST_REPRODUCTION | [108 exact scientific comparisons](../03_research/NCATS_REPRODUCTION_V1.md); not independent scientific review or new biological repetitions |
| C18 | Gaussian covariance-based development comparator executed | MEASURED_DEVELOPMENT_ONLY | [54 completed runs](../03_research/NCATS_GAUSSIAN_RESULTS_V1.md); pending versus blind tied H(12) in all nine heterogeneous pairs; C06 stays HYPOTHESIS |
| C19 | Broader candidate source/structure audit executed without new compound outcomes | PREPARATORY_OPEN_GATES | [Audit](../03_research/CANDIDATE_ASSAY_AUDIT_V1.md); 24 original source audits, 1 bounded gene-search candidate, 17 new/3 reused panel audits and 3 cap exclusions; zero final-ready tasks, no certified family independence |
| C20 | Hierarchical precision/resource sensitivity executed | HYPOTHETICAL_MODEL_ONLY | [1,080 sensitivity rows](../03_research/DESIGN_SENSITIVITY_V1.md); assumed variances/effects, not measured final power, assay savings or equivalence |
| C21 | Existing owner-supplied SSH IP profile authenticates | READ_ONLY_CONNECTION_ONLY | `docs/evidence/design-preparation-20261104-v1/dr-train-ip-profile-test.json`; hostname dr-train returned, no resource reservation or remote study |
| C22 | Active English documentation and manuscript reflect executed development evidence | DOCUMENTATION_RECONCILED | [Language/manuscript audit](../07_audit/LANGUAGE_AND_MANUSCRIPT_AUDIT.md); independent agent cross-review, not human author approval or new biological replication |
| C23 | Current journal routes and a USD 300 budget were assessed | PUBLICATION_PREPARATION_ONLY | [Shortlist](../01_paper/JOURNAL_TARGETS_20261104.md); conditional no-APC subscription route, unresolved scientific/venue/author gates; no submission, payment or acceptance |
| C24 | A higher-upside content-aware dispatch/wait planner and its validation programme are selected | PROTOTYPE_EVALUATED_ADVANCE_NOT_ESTABLISHED | [Goal4 results](../03_research/GOAL4_RESULTS_V1.md); finite-mixture planning implemented and challenged; screening slower and no optional WAIT; no learned RL controller or new-theorem claim |
| C25 | Four constructed dispatch/wait expectations and development-log diagnostics were checked | ANALYTICAL_AND_POST_HOC_ONLY | [Goal 1 packet](../evidence/goal-01-contribution-20261104/); 162 existing run hashes, 72 matched-arm runs/36 pairs; no new assay campaign or final outcome |
| C26 | A finite-world dispatch/wait planner and scenario relaxation execute | DEVELOPMENT_PROTOTYPE_ONLY | [Goal 2 protocol/results](../03_research/GOAL_02_RESULTS_V1.md); exact tiny-model checks, finite-model/shortlist guarantee only; no new theorem or biological certificate |
| C27 | A new paper-backed Tox21 development benchmark ran on dr-train | EXECUTED_DEVELOPMENT_EVIDENCE | 180 completed/0 failed runs, 18 matched groups, 36 exact pruning pairs; real historical labels, simulated operations; one CPU, no final roles |
| C28 | The Goal 2 content relaxation improves computation or discovery | NOT_SUPPORTED_BY_EXECUTED_CHALLENGE | 13/458 actions pruned; policy time +24.3%, whole-run time +2.26%; no planner WAIT; rollout mean hit difference vs nearest-hit -1.722, observed range [-6,+1] |
| C29 | FS-Mol is acquired and ready for a family-transfer study | SCOPED_COHORT_PREPARED_AND_DEV_VALIDATION_EVALUATED | [Dataset card](../03_research/FSMOL_DATASET_CARD_V2.md); owner-approved A reached 4/2/12 annotation components, 6/2/16 assays; source/chemical limits explicit; final outcomes reserved |
| C30 | Goal 4 real-data development/validation challenge executed | EXECUTED_BOUNDED_CHALLENGE | [Closeout](../06_execution/PLAN_A_CLOSEOUT_20261105.md); 6,488 campaigns + 64 calibration diagnostics; 43 evaluator checks locally/Linux; 112/112 reexecution and 448 main dense/screened signature matches |
| C31 | New screening improves computation and broad deadline discovery | NOT_SUPPORTED_AS_A_BROAD_ADVANCE | [Results](../03_research/GOAL4_RESULTS_V1.md); matched median policy time +32.2% on one development assay; mixed effects/two validation groups; no optional WAIT in the selected-M128 planner panel; C06 remains a broader hypothesis |

## Language rules

Use “historical assay active” for replay outcomes, “predicted score” for model output, “simulated cost/time” for scenario units and “proposed” for unimplemented functionality. “Confirmed hit” always needs a context: it means delivered assay-label evidence inside a particular replay, not validated therapeutic efficacy. Name a chemical or target population whenever reporting generalization.

The literature may report advantages of another method. Such values remain that study's result and must never be transferred into CuraLoop's product metrics. A paid pilot does not itself establish improved discovery. A software test does not establish predictor quality. A favorable point estimate without uncertainty is incomplete evidence.

## Promotion record

For each change of status record: claim ID, previous wording, new wording, run/artifact identity, exact endpoint, population, reviewer and date. A single-author project can perform an explicit second-pass audit without inventing an independent reviewer. Missing evidence leaves the claim at its prior status while implementation continues.

## Literature-derived claim boundaries

The version-2 review supports statements about inspected source versions and planned controls. It does not support “all journal versions reproduced,” “unbiased for all targets,” “VDR labels corrected,” “BayBE savings achieved,” or “new asynchronous backend implemented.” R05's known-active start, R03's target ascertainment and R26's case-specific objective must remain visible whenever their results inform a comparison. The discrepancy register records uncertainty rather than declaring source errors.
