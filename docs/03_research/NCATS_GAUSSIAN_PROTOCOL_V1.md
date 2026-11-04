# NCATS Gaussian-surrogate development amendment v1

Prepared 4 November 2026, after exposure to the original 108-run pilot. Numerical
settings below precede any new Gaussian-control assay outcomes. This is a separate
bounded development experiment; preserve all original inputs/results and their
null/unfavorable comparisons. No final evaluation or new biological data is added.

## Existing-backend feasibility and method choice

The installed scikit-learn 1.8.0 backend already provides GaussianProcessRegressor
with fixed-kernel/no-optimizer fitting and predictive covariance. Its installed
signature and predict implementation were inspected. This is a small adapter to
that existing backend, not a new GP optimizer. BayBE, BoTorch and GPyTorch were
not installed in the inspected project environment. Installing a large stack is
unnecessary for this bounded covariance-conditioning diagnostic; no BayBE
compatibility or end-to-end integration is claimed.

[The official sklearn guide](https://scikit-learn.org/stable/modules/gaussian_process.html)
documents Gaussian mean/variance and alpha as diagonal noise/regularization. The
live stable guide identified version 1.9.1, whereas execution pins installed
1.8.0 and its code; the versioned 1.8 guide was inaccessible to the browsing tool.
[Desautels et al., JMLR 2014](https://www.jmlr.org/papers/volume15/desautels14a/desautels14a.pdf)
provides the GP-BUCB pending-location variance idea. This amendment changes its
objective/context and does not inherit its regret guarantees or reproduce the
original algorithm. The [NeurIPS 2023 Tanimoto paper](https://proceedings.neurips.cc/paper_files/paper/2023/hash/6a69d44b3386e50c06f7107ef4f29302-Abstract-Conference.html)
supports using fingerprint Tanimoto as a positive-definite molecular kernel.
No random-feature approximation from that paper is implemented.

## Fixed approximation and scores

Use public 1,024-bit binary Morgan features and kernel
`K(x,z) = intersection_bits / union_bits`, unit amplitude; two empty vectors have
similarity one. Precompute this immutable feature-only Gram matrix per campaign.
Use sklearn GaussianProcessRegressor with **alpha=0.1, optimizer=None,
normalize_y=False**, zero mean, float64 and random_state=seed. No length scale,
amplitude, noise or exploration parameter is fitted or selected from assay
outcomes. Refit only when revealed labels change. Gaussian regression on 0/1 is
an explicit approximation, not a calibrated Bernoulli model. Alpha is a fixed
modeling/regularization assumption, not measured assay noise.

Three arms use the same predictor and operational conditions:

1. `gp_mean`: rank posterior mean only.
2. `gp_ucb_blind`: rank `mu_observed + 1.0 * std_observed`.
3. `gp_ucb_pending`: preserve the observed-data mean, but use the standard
   deviation after conditioning covariance on current pending locations.

For eligible U and pending P, the third arm uses
`var_U_pending = diag(S_UU - S_UP (S_PP + 0.1 I)^-1 S_PU)`, where S is the
posterior covariance given revealed outcomes only. It receives no pending outcome
or private duration. This is a Gaussian variance-conditioning adaptation; there
are no sampled or actual pending labels. Clip only numerical negative variances
within 1e-8 of zero, reject larger errors, and leave means/scores unclipped.
Gaussian means/UCB scores are not reported as predicted probabilities.

Each decision takes the feasible top-k by its marginal score, with candidate-ID
tie-breaking. Thus it maximizes an additive optimistic score for multiple new
discoveries at that decision, rather than best-value expected improvement that
can saturate after one binary positive. It is an informative acquisition heuristic
for repeated hit accumulation, not an exact solution of deadline utility or
calibrated probability of multiple hits. There is **no within-batch conditioning**
on the new simultaneous choices. Both UCB arms share this limitation. A one-class
start retains the original declared Random fallback until both classes are
revealed; never discard those starts. The mean arm separates mean exploitation
from the chosen exploration term.

## Matched allocation and immutable freeze

Use the **same three development cohorts and exact hashes** as
`ncats_development_v1.json`: 600 each, uniform initial 24, seeds 0/1/2, budget 24,
capacity 3, T=12, unit cost 1 and candidate-keyed common-2 / heterogeneous-1,2,4
durations. The integer decision grid and atomic settlement semantics are unchanged.
No assay is imported, relabelled or promoted to a final holdout. These endpoints
and structures remain exposed/correlated. Source rights and all source/label
boundaries of [the original protocol](NCATS_DEVELOPMENT_PROTOCOL_V1.md) apply.

Allocation: **54 runs = three arms x three endpoints x three seeds x two timing
conditions**. A nine-run included canary uses seed0/heterogeneous. Proceed to the
remaining 45 only if all nine complete and the measured full-grid projection
fits the 300 cumulative run-wall-second cap. One campaign/numerical thread, CPU
only; no paid/GPU resources. Cap is checked between runs, soft by one run.
Preserve failures, warnings and uncertain interrupted attempts. Do not reset a
ledger, repeat failed identities or retune after the canary. Source preparation,
dependency installation and manuscript time are separate from run wall time.

Commit implementation/protocol before `python -m
research.development.gaussian_runner_v1 --freeze`. Commit the generated
`research/configs/ncats_gaussian_development_v1.json` and receipt before any new
method runs. Source identity includes the untouched original runner/selector/
scheduler and the two new Gaussian files. Later changes need a new version.
Run the module with `--phase canary`, then `--phase all` only after feasibility.

## Analysis, controls and remaining limits

Primary development diagnostic: descriptive paired `gp_ucb_pending - gp_ucb_blind`
H(12), per endpoint/seed/condition. Common-delay event histories must match for
all nine pairs; any mismatch blocks interpretation. Report the mean arm, raw
paired values, new-hit/time-area/scaffold metrics, delivered/accepted/pending/
spent/reserved counts, fits, covariance calls, fallback reasons/shares, measured
wall/CPU/peak memory, source and configuration identities, warnings and failures.
Reconcile public journals, decision-time information and exact matched starts/
schedule hashes. Retain zero hits and all negative comparisons.

Existing LR/control results may be linked descriptively after exact initial/
schedule matching. A GP-versus-LR difference confounds predictor and acquisition;
it does not isolate pending awareness. The genuine pending contrast is within
this matched GP pair. Do not pool three correlated endpoints into a population
CI or treat seeds as new targets. No final H1 inference, calibration, learned
transfer, therapeutic efficacy, prospective savings or commercial validation is
established. Fixed kappa/noise and the Gaussian binary approximation require
future sensitivity/validation, under a new identity. Conditional-known-hit
sensitivity, a Bernoulli posterior and full BayBE integration remain NOT_RUN.
