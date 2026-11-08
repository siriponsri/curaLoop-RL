# Four-screen product checkpoint

8 November 2026. **COMPLETE_PRODUCT_CHECKPOINT. RESEARCH_REMAINS_PAUSED.**

Owner scope: [four-screen brief](FOUR_SCREEN_DASHBOARD_BRIEF_20261108.md).
The existing React application and Python engine are retained. The official
[shadcn Dashboard](https://ui.shadcn.com/blocks/dashboard) informed the navigation,
metric cards, chart panels and table hierarchy. No full starter, authentication,
fictional accounts, template scores or new production controller was imported.

## Delivered behavior

1. **Discovery Overview:** actual pool size, simulated budget, newly confirmed
   hits, delivered assays, cost/discovery curve, public RDKit molecule preview
   with pagination/zoom, campaign context and next-action links.
2. **Digital Twin Simulation Lab:** prominent Retrospective Simulator scope;
   inspectable Compound Selection -> Assay Queue -> Result Delivery -> Model
   Update stages using current public engine state. Inspection does not advance
   time. Select/advance controls operate the engine. A preselection upper bound
   shows quantity/cost; latest-delivery feedback separates active/inactive/missing
   counts. Model status belongs to the last recorded selection, not a fabricated
   automatic training event.
3. **Benchmark Arena:** Random, Greedy, uncertainty-based active learning and
   existing RL implementations; current independent single-seed results include
   confirmed hits per spent simulated unit. A zero denominator is unavailable.
   Preserved ten-seed HIV evidence separately shows mean/SD/range and its own
   budget/capacity/delay. No single-seed variance, confidence interval or RL
   advantage is invented. Learned fallback remains disclosed. These four display
   groups are not a claim that Greedy is outside active-learning methodology.
4. **Compound Explorer:** searchable, filtered, paginated semantic table by
   default, optional grid, real public 2D structures and record details with
   selection/delivery history. Eligible/pending rows remain Unrevealed. A narrow
   screen has an explicit horizontal-scroll cue and a grid alternative.

EN/TH preserves the current campaign and canonical API values. Graphite/Copper,
short functional transitions and reduced motion are retained. Existing Scenario,
Evidence/recovery and Presentation tools remain available. C Workspace is separate
and unchanged by this implementation.

## Current verification

| Check | Current result and practical scope |
| --- | --- |
| Frontend tests | **PASS: 23/23**, including persistence/recovery regressions, language preservation, stage inspection without an action, and a deliberately inconsistent pending fixture that must still hide its activity |
| Type check and production build | **PASS**, current source builds; packaged `frontend/dist` updated |
| Frontend lint and three Python utilities | **PASS** |
| Actual engine/browser workflow | **PASS**, fresh disposable local campaign, selection -> pending -> delivery, null pending labels, four actual policy reports; [receipt](../evidence/four-screen-dashboard-20261108-v1/engine-browser-check.json) |
| Final screen capture | **PASS**, desktop 1440 x 1000 / mobile 390 x 844, EN/TH, no page overflow or uncaught page errors; [gallery](../evidence/four-screen-dashboard-20261108-v1/README.md) |
| Served production build | **PASS**, all four routes through FastAPI at port 8000, mobile dialog navigation, stage inspection, latest delivery, reduced-motion preference; [receipt](../evidence/four-screen-dashboard-20261108-v1/production-check.json) |
| English manual | **PASS**, six pages rendered with Poppler and visually checked; [guide](../manual/CuraLoop-RL-Dashboard-Guide-EN-v3.pdf), linked from README |

Browser QA used `.local/product-four-screens-20261108-v1/qa.sqlite3`; owner
campaign storage and closed scientific ledgers were not used. Zero new hits in
the displayed example are retained. This is product validation, not an efficacy
experiment or a new scientific phase. A source fingerprint and actual public
comparison metrics are in the [delivery receipt](../evidence/four-screen-dashboard-20261108-v1/delivery-check.json).

## Independent review and corrections

Isolated visual reviewer `/root/dashboard_visual_review` inspected actual desktop
and mobile captures, without source/history. Its inspected v3 was rated 8/10;
this subjective screenshot review is not a user study. It identified loading-only
captures, ambiguous inspected-stage highlighting, mobile table affordance,
low mobile process placement and missing recorded-cost context. Corrections:
wait for settled content/charts/images, label stage inspection explicitly, show
scroll guidance, move the flow before KPIs, strengthen simulator scope, add the
recorded scenario and condense the strategy introduction. Final replacements
were visually checked by the parent; no independent rescore is claimed.

Isolated UX reviewer `/root/dashboard_ux_walkthrough` used the live app without
source/design history and inferred its own main path. It completed overview ->
lab -> select -> two advances -> delivered-result inspection on desktop/mobile,
and observed clear skip-link/focus behavior. Two nonblocking refinements were
implemented: quantity/cost preview and latest-delivery counts. The final
production browser check verifies their presentation and inspection behavior.
Its private screenshots are in the owner's `Drug Discovery/dashboard-ux-review-20261108`
folder. Concurrent QA initially caused stale-action rejections; a subsequent
uncontended sequence completed without errors. That observation is not classified
as a reproduced product freshness defect.

Not evaluated: representative-user outcomes, screen-reader certification,
physical-device touch behavior, live laboratory integration, validated digital
twin behavior, pharmaceutical benefit or new research-method superiority.

## Research and literature remain separate

M1's NO-GO and M2's NOT_RUN status are preserved; no protected final outcomes,
new dataset cohort, SSH work, training, external-team write or deployment occurred.
The owner-requested literature downloads produced 25 exact verified PDFs outside
Git, with three main papers and one supplement still unavailable. See
[download status](../02_literature/LITERATURE_DOWNLOAD_STATUS_20261108.md) and
[positioning review](../02_literature/POSITIONING_REVIEW_20261108.md). Downloaded,
read and independently reproduced remain distinct evidence states.
