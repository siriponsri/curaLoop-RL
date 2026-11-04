# Current-state audit

> Local continuation amendment: see [the foundation checkpoint](../06_execution/FOUNDATION_CHECKPOINT.md)
> for the new reference/registry and actual checks. The source-cutoff audit below
> remains the historical application baseline. New toy engineering does not
> establish multi-target or business results.

**Evidence cutoff:** 4 November 2026, Asia/Bangkok. **Source:** `2d287a170b39b0c07d02631ca027c2ba535c0df9`. This is a source and recorded-evidence review, not a rerun of the application benchmark or Windows test suites.

## Implemented behavior

The core package defines immutable public contracts, a private result store, a budget scheduler, a process-isolated built-in policy runner, reporting and validated restoration. The primary interface is React/TypeScript with FastAPI on loopback. SQLite stores public campaign revisions and comparison records. These controls provide local reproducibility and accidental-failure recovery; they do not provide enterprise authentication, tenant isolation or a malicious-code sandbox.

Three datasets are allowlisted: one historical HIV replay and two synthetic fixtures. Historical candidates contain canonical SMILES, scaffold IDs and Morgan features. No new dataset is installed by this documentation release. User-supplied compound libraries, live assay ingestion, customer accounts, an LLM assistant, multi-fidelity execution and operational lab integration are not implemented features.

## Models and learning

`policy_worker.py` fits a StandardScaler/LogisticRegression pipeline using revealed Boolean labels. Greedy ranks predicted activity; Uncertainty ranks closeness to 0.5. Predictions are uncalibrated. With fewer than two observed classes, predictive policies explicitly fall back to Random. The learned controllers load frozen synthetic-only tables and choose among Random, Greedy and Uncertainty. They do not train online in the UI.

The training reward is new delivered actives minus 0.01 times newly settled cost. Q-learning has gamma 0.95; the bandit estimates immediate sample-average return. The state key is a coarse combination of remaining budget, observed activity rate, label count, two-class availability and pending status. State coverage is a scientific limitation, not a UI defect.

## Preserved results

| Recorded result | Meaning |
| --- | --- |
| 50 HIV campaigns, 5 policies x 10 seeds | Within-assay initialization comparisons |
| Mean new hits: Random 0.7, Greedy 3.8, Uncertainty 0.9 | Exploratory historical-replay results |
| Q-learning and bandit each 3.8; fallback 300/300 each | No demonstrated learned transfer |
| Scaffold audit: 960 train / 240 test, 36 / 6 positives | Small, imbalanced predictor evaluation |
| AUROC 0.5562678; AP 0.0326585 | Weak ranking evidence on this held-out split |
| Preserved report: 136 Python and 18 frontend tests | Prior Windows software execution, not rerun in this package |

Raw values come from `docs/evidence/hiv-benchmark/summary.json`; exact artifacts remain in place. Historical verification reports retain their original environment, dates and NOT_RUN limitations.

## Research risks to resolve

Uniform cost and a common delay can leave acquisition order unchanged when no deadline is enforced. The existing budget curve can therefore miss a timing effect entirely. Treat this as a testable invariance hypothesis. Introduce candidate/assay duration variation only through a declared model that does not inspect hidden activity. Capacity and missingness are operational assumptions; measure sensitivity rather than presenting them as observed laboratory conditions.

A second risk is selecting a large method because the project name contains RL. Retain a benchmark/software route if a learned controller cannot improve on matched simpler policies. A third risk is target leakage through duplicated molecules, shared biological families or development reuse. Different random seeds do not resolve any of these.

## Commercial state

Customer interviews: NOT_RUN. External research-team installation: NOT_RUN. Paid pilots: NONE_RECORDED. Revenue, savings, willingness to pay and procurement readiness: NOT_VALIDATED. The business documents contain proposed experiments and illustrative economics, not market findings. No organizational endorsement, official GPO relationship or access to internal data is assumed.

## Documentation revision 2

The supplied literature has been incorporated into a full-text amendment and downstream specifications. All 28 source records now identify a PDF version, with one R05 supplement. R05 is reviewed as ChemRxiv v3. No additional assay data, application feature, trained controller, new scientific run or customer evidence is installed by this revision. The current-state findings above remain the implementation baseline.
