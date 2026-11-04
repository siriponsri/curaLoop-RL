# Figure, table and supplement plan

## Figures

| Figure | Content | Evidence state |
| --- | --- | --- |
| F1 | Information/scheduler/ledger architecture | Existing code plus clearly marked planned extensions |
| F2 | Development attrition/overlap and candidate audit flow | Source tables available; independent-family final splits remain unassigned |
| F3 | Development discovery versus simulated time | Public event trajectories available for 108 original/54 Gaussian runs; publication figure not yet generated |
| F4 | Paired endpoint effects and uncertainty | Raw development pairs available; no independent-family population CI assigned |
| F5 | Duration/capacity regime map | Planned; identifies where rankings change |
| F6 | Learned decisions, fallback and compute overhead | Historical fallback exists; new transfer evaluation planned |

Keep the existing UI screenshot as a software illustration, labelled with its capture provenance. It is not an experimental result. Render exact scientific plots from tables using standard plotting tools; do not use image generation for result charts.

## Tables

T1 defines data, endpoints, rights and task roles, distinguishing exposed development from unassigned final candidates. T2 compares selectors, update schedules and matched information access. T3 reports the executed NCATS fixed-control and Gaussian development means/pairs; these tables are populated in the results chapter. T4 reports failures, cap exclusions, missingness and fallback. T5 covers future ablations only when executed. Keep the historical HIV table separate from the NCATS estimates and hypothetical sensitivity grid. None is an independent-family final-study table.

## Supplements

Provide complete protocol/configuration, data preparation and exclusions, source/split hashes, hyperparameter search, per-task/per-seed results, endpoint derivations, bootstrap settings, runtime/hardware, exact software release, source-to-figure mapping and reproduction instructions. Include protocol amendments and unsuccessful runs. Keep customer-private data outside the public supplement unless explicitly authorized and appropriate.

Every figure/table row needs an artifact ID, generating script, input table and completion status. A draft results shell may state NOT_RUN but must not contain plausible-looking invented means or error bars. Use vector graphics or high-resolution standard plots suitable for the chosen journal after the experiment is complete.

## Added reporting requirements after full-text review

Add a source-to-eligible-task flow with assay/family groupings; an initialization-regime table; a baseline selector/update-schedule table; and a metric-definition table. Show frozen-model and nearest-hit controls in campaign curves. Report measured fit/inference time separately from simulated assay time. Label every uncertainty band with its unit and construction. Do not import a paper's SEM band as a new-study confidence interval.

The supplement should include exact source versions, resolved/unresolved provenance questions, initialization IDs, no-active fallbacks, task overlap sensitivity and all baseline adaptation choices. Source figures are not reused in this package; proposed figures require generated study data and scripts.


## Available source-to-table map

| Manuscript material | Exact source | State |
| --- | --- | --- |
| HIV historical means/predictor audit | `docs/evidence/hiv-benchmark/summary.json` | Preserved historical values |
| NCATS six-method means and paired differences | `docs/evidence/ncats-development-20261104-v1/results/` | 108 executed development runs |
| Fresh-environment comparison | `docs/evidence/ncats-reproduction-20261104-v1/attempt.json` | 108 matched scientific artifacts; same host/implementer |
| Gaussian means/paired differences | `docs/evidence/ncats-gaussian-development-20261104-v1/results/` | 54 executed development runs |
| Candidate attrition/feature overlap | Initial, gene-expansion and HTS-panel evidence packets | Metadata/features only; rights/role gates open |
| Hierarchical precision/resource sensitivity | `docs/evidence/design-preparation-20261104-v1/simulation/` | 1,080 hypothetical effect rows; 288 resource rows |

Current manuscript tables are transcribed from these preserved artifacts and
checked against their reported values. Publication-quality result figures must
be generated from those data with a recorded script/version; a polished diagram
or UI screenshot is not a substitute. No new scientific figure is claimed by
this documentation revision.
