> Documentation update, 4 November 2026: [current programme](03_research/PROTOCOL.md) and [documentation map](README.md). The detailed record below is retained from the inspected POC checkpoint. New research and commercial capabilities are specifications until implemented; prior test counts are historical execution, not new checks.

# Evaluation protocol actually used

Historical dataset: label-blind 1200-molecule MoleculeNet HIV subset from a frozen source CSV hash. Common initial 48 labeled molecules selected uniformly without consulting labels; preexisting sunk cost. Seeds 0–9 are paired across Random, Greedy, Uncertainty, frozen Q-learning and frozen contextual bandit. Cost=1, B=30, concurrent capacity=5, delay=2, no jitter/missing in the primary benchmark. No tuning on these results is claimed; results are exploratory engineering evidence on one assay.

## Event-derived endpoints

- New confirmed active hits: sum of unique `RESULT_DELIVERED` active labels. Initial seed labels, predictions, pending requests and missing outcomes are excluded.
- Delivered assays counts observed Boolean results; missing outcomes settle cost separately and are not inactive labels.
- Budget: accepted requests reserve once; delivered/missing outcomes settle once; total = spent + reserved + remaining.
- AUC-DB: left-step integral of cumulative delivered hits against settled cost, carried flat to configured B after termination, normalized by `B * floor(B / assay_cost)`. This is not AUROC or AP. Partial snapshots are incomplete campaign evidence.
- Hit rate: confirmed hits / delivered Boolean assays; null if no delivered assays.
- Learned-controller usage: count selected assay requests routed through a controller and count those using explicit unseen-state Greedy fallback. A trained checkpoint is not proof that its learned table was used on an out-of-distribution state.

## Uncertainty in comparisons

Report mean, sample SD, min/max across seeds. Exploratory contrasts against Random use the same per-seed initial data, with 2000 deterministic paired-bootstrap resamples and percentile intervals. These measure initialization variability within one assay, not independent biological targets. Multiple contrasts are exploratory; no corrected significance, cross-target SOTA or real savings claim is made.

## Separate predictor audit

Custom whole-scaffold hash split with seed 42: 960 train / 240 test, 36 / 6 actives, no shared Murcko scaffold. StandardScaler and logistic classifier fit training rows only. AUROC, average precision and Brier reported when both classes occur. The evaluator's labels and model never enter policy observations. The split/subset differs from official MoleculeNet/TDC benchmark splits, so numbers are not directly comparable to paper tables.

## Training / test separation

Q-learning and contextual bandit train on synthetic_linear/shift only, 160 episodes each, training seeds 10000–10159. Frozen JSON checkpoints record actual returns/values/counts and a checksum. Evaluation on HIV is an out-of-distribution engineering test. In this release historical states invoke Greedy fallback; equal outcomes to Greedy do not establish learned transfer. Training-seed nonoverlap is not a substitute for validation across multiple biological target families.

## What is not measured

Real laboratory costs or timing, model calibration suitable for drug discovery, molecular novelty/potency/ADMET, prospective biological utility, actual synthesis, economic savings, physical process fidelity, live Digital Twin behavior or GMP suitability.


## English/persistence release boundary (v0.3)

No datasets, assay labels, seed-selection rules, rewards, controller training or
evaluation protocols were changed. New Windows/API/browser tests verify software
behavior and recovery, not biological performance. Public snapshot restoration
uses the existing reconstruction path. Pending experiments remain unrevealed and
unsettled until their simulated due event; restart itself does not advance time.

Recorded v0.1 benchmark files retain their original bytes. Newly executed UI
comparisons have separate saved reports and source identities. Each controller's
actual learned/fallback request counts must be read from that run, including the
possibility of zero learned actions. POC completion does not resolve the recorded
300/300 historical fallback limitation or demonstrate useful RL transfer.
