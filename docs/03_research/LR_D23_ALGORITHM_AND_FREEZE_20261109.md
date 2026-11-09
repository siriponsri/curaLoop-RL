# LR-D23: algorithm and analysis contract

Status: implementation/admission, before new molecular outcomes. This document
operationalizes the owner-approved plan at `36f3812`; it does not replace its
limits or activate M3. The fresh release is recorded in
`research/manifests/lr_d23_release_20261109_v1.json`.

## Method question and closest work

The candidate tests behavior-conditioned terminal-discovery supervision for a
small residual UPDATE/REUSE decision under a measured compute budget. Gk2 is the
incumbent; a standardized Ridge(alpha=1) estimates terminal UPDATE-minus-REUSE
hits and overrides only beyond +/-0.25. Features use delivered observations and
cached predictions; feature extraction/inference consumes the campaign clock.
The deadband is a heuristic, without a cumulative safety guarantee.

Regol et al., *Cost-Aware Model Retraining under Limited Information*, ICML2025,
study accumulated test loss and retraining cost over an incoming dataset stream.
Their uncertainty-aware performance forecast supports retrain/skip decisions.
The selected methods also discuss the dependence of later data on past choices.
Their objective, stream and forecast do not establish a terminal active-search
policy guarantee for this experiment. Primary source:
https://proceedings.mlr.press/v267/regol25a.html.

Jiang et al., *Efficient Nonmyopic Active Search*, ICML2017, already establish
finite-budget discovery and nonmyopic selection as prior work. Primary source:
https://proceedings.mlr.press/v70/jiang17d.html. The proposed distinction here is
the measured compute/refresh decision and two-round behavior-conditioned targets,
not the invention of active search or a claim of a novel RL algorithm. This is a
defensible empirical method question; novelty and journal sufficiency remain
unproven. No theorem or published improvement is transferred to this candidate.

Reading boundary: the official Regol PDF was acquired and all36 pages extracted;
only the first six physical pages were read in this run, including the objective
and selected methods. Page5 was rendered and inspected. The private download
receipt records its SHA-256. This is selected-method reading, not a full-paper
or exhaustive literature review.

## Exact learning procedure

For each of four outer annotation components g, exclude g from state generation,
targets, standardization and fitting. Round0 uses Gk2 prefixes and Gk2 tails;
fit v0 from paired terminal hit differences. Round1 generates its own prefixes
using that fold's v0 and uses the same frozen v0 continuation after either forced
operation. Fit v1 using only round1 targets. The outer fold's no-history variant
keeps features0,1,3,4; its Gk2 incumbent still has history. It is a feature ablation,
not a completely memoryless policy. No third round or alternate candidate.

All training is RF/B32/Cref, n0=0/16, seeds81001/81013/81029, snapshots8/16/24.
Supported targets require both forced operations actually executed from the same
authenticated state/core. An infeasible/cold pair stays in assigned counts and
does not become a misleading executed-operation target. Minimum support remains
30 states and two training components per fold. Equal component training weights
and training-only scaling apply. Deployment v1 is one approximate improvement
step beyond its v0 continuation, without a policy-improvement guarantee.

## Frozen reporting and gate details

Evaluation seeds82003/82013/82037/82051/82067 are matched across arms and n0.
Means average contexts within assay, assays within component, then components
equally. CPU savings are ratios of these means. Joint-seed percentile intervals
enumerate all5^5 resamples; they are conditional intervals, not biological CIs.
The approved G1/Gk2/component/frontier thresholds remain unchanged.

To make the approved attribution requirement executable before outcomes, use a
conservative sufficiency rule: full v1 must show the same approved usefulness
preference against no-history v1 (>=1 hit with CPU<=1.1x, or >=20% CPU saving with
loss<=0.25); v0 must not mean-point dominate v1; and at least one delivered learned
override must occur in every component. Weak attribution is INCONCLUSIVE, never
repaired by dropping an ablation. This rule supports a development decision only.
It does not prove causal biological generalization or calibrated safety.

Profile 16 complete synthetic G1 contexts plus eight constructed mechanism/guard
checks on each of cores69/70/71: 72 admission contexts, not72 full campaigns.
Cref=1.25 times maximum complete synthetic G1 CPU over pool sizes128/303 and cores,
separately by predictor/n0/B; RF<=5s, neighbor<=1s. Preserve all failed checks and
stop/re-cost before molecular outcomes if admission fails.

Freeze the code, this contract, exact matrices, data hashes, analysis and seed
assignments before first molecular outcome. Authenticated private prefixes,
caches, traces, artifacts and results must return before exact owned cleanup.
No final16 feature, label or presence access. D3 starts only after all D2 gates;
independent handoff and paper results insert are required even on early stop.

## Pool-frame correction and engineering notes

The historical D1 report/proposal incorrectly described M2's training mask as a
different compound population. A fresh identifier-only comparison found that it
retained every member of each six-pool assay. Counts168/270/303/248/129/167 match
exactly. See `docs/evidence/lr-d23-20261109-v1/pool-frame-erratum-v1.json`.
The old files/results remain immutable. Seed, intervention/state-history and
estimand differences still prohibit arbitrary cross-experiment pairing. The
new experiment remains the same six already exposed pools, not new independence.

One constructed test initially failed because its Windows-only signal stub had
the wrong method signature; the stub was repaired and all17 targeted tests
passed. No molecular run occurred. Two earlier local utility jobs briefly
overlapped while both were pinned to CPU0; this respected one CPU-equivalent but
did not respect intended utility-process serialization. No molecular worker was
active. Subsequent local jobs are serialized; do not claim perfect scheduling.
