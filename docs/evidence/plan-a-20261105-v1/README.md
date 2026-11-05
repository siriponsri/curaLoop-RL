# Plan A execution evidence

Latest 5 November revision: the owner approved A. The
[new result](feature-cohort-v2-result.json), [chemical audit](chemical-audit-v2.json),
[readback](revision-a-feature-readback-v2.json), [independent review](revision-a-postrun-review-v2.json)
and [English review](revision-a-english-review-v2.json) support scoped Goal3
readiness at 4/2/12 annotation-connected groups, with 6/2/16 assays. See the
[dataset card](../../03_research/FSMOL_DATASET_CARD_V2.md) and
[updated budget](revision-a-budget-v2.json). The first failed cohort remains
intact. Goal4 proceeds to evaluator/protocol freeze; final outcomes stay reserved.
The earlier pending-decision descriptions below are historical.

5 November 2026. **Goal3 IN_PROGRESS / first cohort FAIL / Goal4 NOT_RUN.**
Owner authorization covers Goals3–4,48CPU-hours/24hours/maximum4CPUs, with
verified task-local remote retrieval followed by deletion. The
[execution contract](../../06_execution/PLAN_A_EXECUTION_CONTRACT_20261105.md)
sets exact caps, authority and the stopping boundary before Goal5.

| Evidence | Result and scope |
| --- | --- |
| [Source metadata audit](source-metadata-audit-v1.json) | All5,135default tasks present among27,065physical files;21,930extra training files unused; paper/source count discrepancy retained |
| [Independent family/preparer review](family-and-preparation-review.json) | PASS scoped shared-exported-annotation boundary and exact preparer;139connected components, not139independent evolutionary families |
| [Local research rights](source-rights-local-use-v1.json) | PASS nonpublic processing; preserve CC notices; row-level redistribution unresolved |
| [Owner family direction](owner-family-direction.json), [chemical direction](owner-chemical-direction.json) | New biological-family split; exact chemical purge; no chemical OOD claim |
| [Feature freeze](feature-preparation-freeze-v1.json) | Exact reviewed sources/config frozen before new assay-member parsing |
| [Executed cohort](feature-cohort-v1-result.json), [chemical audit](chemical-audit-v1.json) | FAIL4/2/12quota; actual2/2/7groups,3/2/8assays; no semantic outcome use |
| [Preparation tests](preparation-tests-v1.txt), [JUnit](preparation-tests-v1.xml) | PASS27tests: safe headers/remote preservation, exact queue enumeration, outcome noninterference and chemical purge regressions |
| [Fresh combined119tests](constructed-all-v1-tests.txt), [source/environment identity](constructed-all-v1-identity.json), [resource receipt](constructed-all-v1-resources.json) | PASS119constructed planner/adapter/data/preservation tests; exact sources unchanged; not molecular efficacy, novelty or full-app-suite evidence |
| [Access ledger](access-ledger.json) | Retains aggregate metadata exposure and trusted physical parsing; no agent-visible compound/final outcomes |
| [Budget after first cohort](budget-after-features-v1.json) | About50recordedCPU seconds plus7,200-second conservative overhead charge; metadata123,663,827bytes charged including unknown-usage reserves, below200MB |
| [Delegated accounting limitation](delegated-metadata-accounting.json) | Exact delegated request count/bytes UNKNOWN; conservative80MBreservation, not measured usage |
| [Old Goal2 return inventory](goal2-return-manifest.json), [local verification](goal2-return-local-verification.json), [remote deletion](goal2-remote-cleanup.txt) | PASS382files,4,882,614bytes returned and checked before deletion; original remote root absent |
| [PlanA return inventory](plan-a-return-manifest-v1.json), [enhanced local proof](plan-a-return-local-verification-v2.json), [both-root cleanup](plan-a-remote-cleanup-v1.txt), [fresh absence check](remote-absence-v1.json) | PASS8files/1,564,567bytes returned/verified, then task/export removed; all three scoped task roots checked absent |
| [Current budget](budget-after-constructed-v1.json) |68.46875recorded CPU seconds plus7,200-second conservative unmetered-overhead charge; no new real-data campaign |

The failed cohort is retained under the ignored source cache. The public packet
contains task IDs/hashes and aggregate audits, without structures or labels.
See [source notices](../../03_research/PLAN_A_DATA_SOURCE_NOTICES_V1.md).
[Revision options](../../06_execution/GOAL3_COHORT_REVISION_OPTIONS_20261105.md)
await owner selection; do not silently expand the frozen reserve. Remote
preservation/cleanup for this checkpoint is complete. No new real campaign,
trained controller, held-out result, external replication, journal submission
or algorithm advantage is established by these preparation checks.
Read the [self-contained checkpoint](../../06_execution/PLAN_A_CHECKPOINT_20261105.md)
for actual work, limits, remaining steps and the current owner decision.

The generic package check's `source_commit` identifies its historical protected
catalogue, and its `not_run` fields describe that checker alone. Live main-push
verification is a separate operation. Constructed-test success does not replace
the failed dataset gate or a real-data experiment.
