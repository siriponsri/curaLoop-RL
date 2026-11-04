# Gaussian-surrogate development comparator: actual results v1

4 November 2026, Asia/Bangkok. **54/54 COMPLETE, 0 FAILED, 0 WARNINGS**.
The new pending-conditioned Gaussian comparator did not improve deadline hits
over its matched pending-blind Gaussian counterpart in this bounded pilot.
The [original 108-run results](NCATS_DEVELOPMENT_RESULTS_V1.md) and all their
negative comparisons remain unchanged. This amendment adds no untouched final
holdout, therapeutic-efficacy evidence or learned-controller evaluation.

## Observed comparison

Pending-conditioned minus blind GP-UCB H(12) was **zero in all nine heterogeneous
pairs**: 0 wins, 9 ties, 0 losses. Event traces nevertheless differed in **5/9**
of those pairs. All **9/9 common-delay pairs** matched exactly, satisfying the
prespecified negative control. Equality of nine small development hit counts
does not establish statistical equivalence or a population-wide null effect.

Mean newly delivered assay-active labels at T=12, each cell three seeds:

| Endpoint / duration | GP mean | GP UCB blind | GP UCB pending | Original LR Greedy, descriptive |
| --- | ---: | ---: | ---: | ---: |
| AhR / common 2 | 8.33 | 9.00 | 9.00 | 9.67 |
| AhR / heterogeneous 1,2,4 | 7.00 | 6.67 | 6.67 | 9.00 |
| PPAR-gamma / common 2 | 2.00 | 1.67 | 1.67 | 1.33 |
| PPAR-gamma / heterogeneous 1,2,4 | 2.33 | 2.33 | 2.33 | 2.00 |
| p53 / common 2 | 2.00 | 2.33 | 2.33 | 2.67 |
| p53 / heterogeneous 1,2,4 | 2.00 | 2.33 | 2.33 | 2.33 |

The new GP models are not uniformly better than the old LR control. Adding the
chosen exploration term also does not uniformly improve on GP mean. GP versus
LR changes the predictor as well as acquisition, so those columns do not isolate
pending awareness. Only the matched GP pair provides the within-model pending
diagnostic. No parameter was changed after inspecting the canary or complete grid.

## Method and scope

The [frozen amendment](NCATS_GAUSSIAN_PROTOCOL_V1.md) adapts the existing sklearn
1.8.0 GaussianProcessRegressor backend, with a feature-only binary Tanimoto Gram
matrix, unit amplitude, alpha=0.1, optimizer=None, normalize_y=False and kappa=1.
It conditions covariance on current pending locations while retaining the
observed-data posterior mean. No pending outcome or private duration enters the
selector. Binary Gaussian regression is an explicit approximation, not a
calibrated Bernoulli posterior. Gaussian means and optimistic scores are not
labelled probabilities. This is not a reproduction of GP-BUCB or a demonstration
of its regret guarantee.

The acquisition ranks a sum of marginal optimistic new-hit scores, rather than
best-value expected improvement after one positive. It is not an exact optimizer
of deadline utility. New simultaneous batch members do not condition one another;
both UCB arms share that limitation. Source/rights, labels, 600-compound pools,
uniform initial 24, seeds 0/1/2, budget 24, capacity 3, unit cost 1 and deadline 12
are unchanged from the original pilot. All three endpoints remain correlated,
exposed development resources.

Every new run's initial IDs, candidate schedule and full task-resource hash
matched its original LR counterpart. All public event metrics and decision-time
label/pending counts reconciled. All 54 snapshots reconstructed at runtime.
The third arm's variance reductions were active: **89 selected requests** had a
strictly lower conditioned standard deviation while pending work existed (post
hoc implementation diagnostic, tolerance 1e-12). Five changed heterogeneous
trajectories with tied hits confirm that the new term can affect decisions
without improving the chosen endpoint.

## Starts, fallback and resource costs

The PPAR-gamma seed-2 uniform start had zero actives. All six corresponding new
campaigns (three arms x two conditions) were retained, along with all zero new-hit
outcomes. Each GP arm used 24 explicitly logged one-class Random fallback
requests before both classes became available. Controller requests and controller
fallback are 0 / NOT_APPLICABLE_FIXED_ACQUISITION, distinct from these fallbacks.

| Method | Accepted requests | Selector fallback requests | Successful fits | Covariance prediction calls |
| --- | ---: | ---: | ---: | ---: |
| GP mean | 321 | 24 | 130 | 130 |
| GP UCB blind | 323 | 24 | 131 | 131 |
| GP UCB pending | 323 | 24 | 133 | 133 |

The included nine-run canary used 17.3427 cumulative run-wall seconds, projecting
104.0560 for 54, within the new amendment's frozen 300-second cap. The remaining
45 ran unchanged, skipping verified canary identities. Total **101.8956 run-wall
seconds**, **95.1563 process CPU seconds**, peak runner working set
**181,006,336 bytes (172.62 MiB)**. Windows 11/Python 3.12.10 used the freshly
installed isolated venv from the [reproduction](NCATS_REPRODUCTION_V1.md), with
captured BLAS/OpenMP pools each reporting one thread and one campaign at a time.

The fresh reproduction and new amendment together executed **162 campaigns**,
315.8262 cumulative run-wall / 290.1719 CPU seconds. They have separate explicit
300-second per-study caps; no earlier ledger was reset. Dependency installation,
data preparation, audit/report time and electricity/labor cost are separate.
No GPU job, paid API call or remote allocation was used. Simulated assay time
does not include measured policy latency and is not laboratory turnaround.

## Identity, evidence and verification

Implementation/protocol commit: `ce156ab1171f06031d858c249fc7677db269bd32`.
Config commit before first new assay-method run:
`a9d9c8f0747be3e2c7d8c41b42dc53efd049a40a`. Both execution phases recorded that
commit and a clean working tree at startup. Config canonical JSON SHA256 is
`408f78d6f3d7e5f6b3c9c092e8407a7cbfa0be66b8e1d54b5c647e10c56da752`;
named LF-normalized execution-source SHA256 is
`2aa92f296d5417ba56572030caa06e1194e34fda9a7804bd23891608b66dc80b`.
The freeze explicitly records that original LR results were already exposed and
new Gaussian assay outcomes had not been inspected. It does not preregister the
old pilot or freeze a final study.

[Frozen configuration](../../research/configs/ncats_gaussian_development_v1.json),
[freeze receipt](../evidence/ncats-gaussian-development-20261104-v1/freeze.json),
[all 54 raw public runs and ledger](../evidence/ncats-gaussian-development-20261104-v1/runs/),
[run CSV](../evidence/ncats-gaussian-development-20261104-v1/results/runs.csv),
[summary](../evidence/ncats-gaussian-development-20261104-v1/results/summary.csv),
[paired contrasts](../evidence/ncats-gaussian-development-20261104-v1/results/pending-pairs.csv)
and [audit/results JSON](../evidence/ncats-gaussian-development-20261104-v1/results/results.json)
retain statuses, raw identities, warnings, failures, costs, fits and hashes.
Full raw/derived pools, wheels, isolated environment/clone remain ignored.

Before freeze, eight constructed tests passed for kernel similarity/PSD,
conditional covariance versus directly augmented sklearn GP, independent fitted
state, one-class fallback, row order, common-delay equality and hidden-future-label
invariance. The final targeted suite also checks amendment failure retention,
verified skip and tamper rejection; exact counts/outputs are in the final
verification receipt. This is a single implementer's second-pass audit, not an
independent review. Full application/frontend/browser suites were not rerun.

## Interpretation and next acceptance gap

The original pending penalty had no positive heterogeneous pair and one loss;
the probabilistic adaptation now also has no positive pair under this allocation.
Keep that evidence rather than treating model sophistication as progress on H1.
The comparison adds a functioning, tested covariance-based control; it does not
establish value for pending-aware screening generally. Final H1/transfer,
calibration, known-hit sensitivity, alternative fixed parameter sensitivity,
within-batch conditioning and a genuine Bernoulli model remain open. Any further
development experiment needs a separate identity and prospective freeze.
Independent final task/family selection, an adequately supported material-effect
threshold and final resource allocation are unresolved scientific decisions.
Customer validation, push, publication and deployment remain NOT_RUN.
