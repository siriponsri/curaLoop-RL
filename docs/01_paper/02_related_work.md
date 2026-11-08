# Related work

The current method-first review is
[the focused primary-source matrix](../02_literature/METHOD_FIRST_CLOSEST_WORK_20261108.md).
It records strong robust-improvement/rollout overlap and novelty HOLD. The
historical molecular/asynchronous/software review below remains background,
not proof of a new method gap or a fresh reproduction.

The review connects molecular acquisition, learned policies, asynchronous optimization and scientific software. Its complete synthesis is in [Critical review](../02_literature/CRITICAL_REVIEW.md); the [full-text amendment](../02_literature/FULL_TEXT_REVIEW_ADDENDUM.md) identifies newly inspected versions and page-level evidence. This section is a manuscript bridge, not a second independent review.

## Molecular acquisition and low-data controls

MolPAL studies surrogate-guided selection in large docking pools (R04). The inspected ChemRxiv v3 low-data study uses three experimental assay-derived pools and compares model representations, acquisition and initial information (R05). It includes similarity and frozen-model exploitation controls and conditions its initial sets on a known active. Its acquisition utility and predictor discrimination are not interchangeable. SimDMTA studies query strategies in a focused BRD4 docking workflow (R27). These differences in outcome, initialization and budget prevent direct reuse of reported gains as a CuraLoop result or a universal ranking.

The resulting design requires Random, nearest-hit similarity, frozen-model Greedy and retrained Greedy, followed by explicit uncertainty and asynchronous controls. Such controls can distinguish iterative learning from a favorable initial ranking or a change of model. Zero-hit starts remain in the primary population; known-hit starts form a separately labelled sensitivity.

## Learned acquisition and operational constraints

RL-assisted generation and GLARE provide related and direct learned-selection precedents respectively (R06–R07), while R28 supplies earlier adaptive-acquisition methodology. Generation rewards and fixed-pool historical assay labels are different endpoints. Delayed feedback, batch interaction and asynchronous completion are established topics in online learning and Bayesian optimization (R10–R13). A new contribution must therefore be a specific controlled finding about tasks and operational assumptions, with actual learned decisions and fallback shares exposed.

ALF, PAL, BoTorch and BayBE provide relevant software and optimization precedents (R08–R09, R16, R26). BayBE's publisher article explicitly describes backtesting, asynchronous workflows, partial measurements and serialization; its examples include representation, related-task transfer and campaign stopping. Those capabilities rule out generic asynchrony or a reusable acquisition API as unique claims. They do not establish that a reaction-yield stopping objective is suitable for accumulating many Boolean hits. Exact versions and objective matching matter in an adaptation.

## Data and evaluation boundaries

MoleculeNet and TDC supply task/evaluation foundations (R01–R02). LIT-PCBA's curation and AVE splitting offer a valuable assay-based resource, but the target panel is selected partly through baseline virtual-screening enrichment (R03). Representation, overlap and benchmark analyses further motivate release-specific audits (R17–R19). Related endpoints must be grouped when assessing controller transfer, and seeds remain within-task repetitions.

Uncertainty and RL evaluation sources motivate precise score definitions, matched comparisons and interval estimates (R20–R24). The historical uncalibrated logistic margin is not validated epistemic uncertainty. The separate development Gaussian adapter supplies an explicit covariance-based uncertainty score, but Gaussian regression on Boolean labels is not a calibrated Bernoulli posterior and does not inherit a published asynchronous method's guarantees. Fixed-FPR enrichment, top-ranked-fraction enrichment, acquired-set enrichment, predictor AUROC and discovery-versus-time area also need distinct names and denominators.

All 28 reference records now have an identified PDF; one supplement is attached to R05. R05 was reviewed as ChemRxiv v3, and its associated journal full text was not compared. The VDR description discrepancy and preprint MI minimization direction remain explicit reproduction/import questions. References resolve through [the register](../02_literature/REFERENCES.md) and `references.bib`. The targeted, AI-assisted review requires an exact-version and nearest-work refresh before submission.
