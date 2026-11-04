# Figure, table and supplement plan

## Figures

| Figure | Content | Evidence state |
| --- | --- | --- |
| F1 | Information/scheduler/ledger architecture | Existing code plus clearly marked planned extensions |
| F2 | Task registry, family splits and overlap audit | Planned; use actual audited counts only |
| F3 | Discovery versus simulated time under the primary scenario | Planned; no illustrative curve presented as a result |
| F4 | Paired task effects and intervals | Planned; task-level denominators visible |
| F5 | Duration/capacity regime map | Planned; identifies where rankings change |
| F6 | Learned decisions, fallback and compute overhead | Historical fallback exists; new transfer evaluation planned |

Keep the existing UI screenshot as a software illustration, labelled with its capture provenance. It is not an experimental result. Render exact scientific plots from tables using standard plotting tools; do not use image generation for result charts.

## Tables

T1 defines data, endpoints, rights and task roles. T2 compares policies and matched information access. T3 reports primary and secondary results. T4 reports failures, missingness and fallback. T5 summarizes ablations. A separate historical-pilot table may retain the existing HIV values without combining them with new estimates.

## Supplements

Provide complete protocol/configuration, data preparation and exclusions, source/split hashes, hyperparameter search, per-task/per-seed results, endpoint derivations, bootstrap settings, runtime/hardware, exact software release, source-to-figure mapping and reproduction instructions. Include protocol amendments and unsuccessful runs. Keep customer-private data outside the public supplement unless explicitly authorized and appropriate.

Every figure/table row needs an artifact ID, generating script, input table and completion status. A draft results shell may state NOT_RUN but must not contain plausible-looking invented means or error bars. Use vector graphics or high-resolution standard plots suitable for the chosen journal after the experiment is complete.

## Added reporting requirements after full-text review

Add a source-to-eligible-task flow with assay/family groupings; an initialization-regime table; a baseline selector/update-schedule table; and a metric-definition table. Show frozen-model and nearest-hit controls in campaign curves. Report measured fit/inference time separately from simulated assay time. Label every uncertainty band with its unit and construction. Do not import a paper's SEM band as a new-study confidence interval.

The supplement should include exact source versions, resolved/unresolved provenance questions, initialization IDs, no-active fallbacks, task overlap sensitivity and all baseline adaptation choices. Source figures are not reused in this package; proposed figures require generated study data and scripts.
