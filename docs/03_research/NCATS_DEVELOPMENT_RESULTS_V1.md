# NCATS development pilot v1: measured results

Date: 4 November 2026, Asia/Bangkok. State: **108/108 COMPLETE, 0 FAILED**.
This local CPU pilot executed six fixed controls on three correlated Tox21
development endpoints. It did not establish a benefit from the pending penalty.
Nothing was pushed, deployed or submitted. The existing application and historical
evidence remain separate.

## Main result

With heterogeneous synthetic durations, pending-penalty minus retrained Greedy
H(12) was **0 in eight pairs and -2 in one pair**, with no positive pair. The
assay-wise mean differences were AhR -0.67, PPAR-gamma 0, and p53 0 new delivered
active labels. The penalty changed public event traces in 7/9 heterogeneous
pairs, so equality of hit counts usually did not mean identical decisions.

All **9/9 common-delay pairs had exactly identical public event histories**,
passing the prespecified negative control. Neither result establishes equivalence
or a population effect: there are only three repeated seeds per endpoint, from
one panel, and all chemistry pools are exposed development resources.

Mean new delivered assay actives at T=12, each cell three seeds:

| Endpoint / duration | Random | Frozen Greedy | Retrained Greedy | Nearest-hit | Diversity | Pending penalty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AhR / common 2 | 1.00 | 8.33 | 9.67 | 10.33 | 1.00 | 9.67 |
| AhR / heterogeneous 1,2,4 | 1.33 | 8.00 | 9.00 | 8.33 | 1.00 | 8.33 |
| PPAR-gamma / common 2 | 0.67 | 1.67 | 1.33 | 2.00 | 0.00 | 1.33 |
| PPAR-gamma / heterogeneous 1,2,4 | 0.67 | 1.67 | 2.00 | 1.67 | 0.00 | 2.00 |
| p53 / common 2 | 0.67 | 2.33 | 2.67 | 1.33 | 1.00 | 2.67 |
| p53 / heterogeneous 1,2,4 | 0.67 | 2.33 | 2.33 | 1.67 | 1.00 | 2.33 |

These rounded descriptive means are not a leaderboard or a superiority test.
Nearest-hit is competitive on AhR; retraining is not uniformly better than the
frozen model. The existing final-study claim C06 remains HYPOTHESIS.

## What actually ran

The [frozen protocol](NCATS_DEVELOPMENT_PROTOCOL_V1.md) specifies 600 compounds per
endpoint, 24 uniformly sampled initial labels, seeds 0/1/2, unit cost 1, budget
24, capacity 3 and deadline 12. All methods receive the same initial labels,
candidate-keyed schedule, cost quotes and decision opportunities within each
assay/seed/condition. They retain independent fitted state. Initial labels are
sunk knowledge and excluded from new hits. Simultaneous deliveries are atomic;
outcomes due at the deadline count, while no requests start at the deadline.

The 18-run canary was included in the 108, not repeated. It completed in 34.67
cumulative run-wall seconds and projected 208.02 seconds for 108. Its saved
feasibility receipt authorized unchanged continuation under the frozen 300-second
cap. Resume verified existing byte hashes and ran the remaining 90. No coefficient,
seed, pool, predictor or scenario was retuned after observing those results.

The frozen model is StandardScaler -> LogisticRegression (C=1, liblinear,
max_iter=500); fit data contain only revealed labels. Pending penalty is predicted
activity minus 0.2 times maximum Tanimoto to currently pending locations. All
methods exclude already requested candidates; that common feasibility control
is not the treatment. The penalty does not diversify within a simultaneously
submitted batch. It is an explicitly named finite-pool heuristic, not a
reproduction of a probabilistic asynchronous method.

## Source, attrition and exposure

Training exports came directly from the [NCATS challenge](https://tripod.nih.gov/tox21/challenge/data.jsp),
which defines 1=active and 0=inactive and links AIDs 743122 (AhR), 743140
(PPAR-gamma) and 720552 (p53). These are pathway/toxicology activity endpoints;
positive is not a therapeutic benefit. Provider public-domain evidence, source
selection limits and the deferred LIT-PCBA candidate are recorded in the protocol.

| Endpoint | Raw rows | Unique eligible | Invalid rows | Conflicting-label rows excluded | Consistent duplicate rows collapsed | Subset active / 600 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AhR | 8,169 | 6,670 | 2 | 92 in 44 groups | 1,405 | 59 |
| PPAR-gamma | 8,184 | 6,591 | 2 | 30 in 14 groups | 1,561 | 18 |
| p53 | 8,634 | 6,909 | 2 | 42 in 20 groups | 1,681 | 31 |

Exact-canonical duplicate groups with conflicting labels were wholly excluded,
not majority-voted. No missing/unexpected raw labels were observed in these
files; the code excludes/rejects them rather than inferring inactivity. Cohort
membership was selected by structure/identity hash without activity in ranking.

The subsets share 52 AhR/PPAR-gamma, 52 AhR/p53 and 36 PPAR-gamma/p53 exact
structures. Shared nonempty scaffold counts are 65, 68 and 61. Against HIV there
are zero exact-canonical matches, but one AhR query has nearest Tanimoto 0.8.
This is an overlap audit, not proof of independent biological tasks or absence
of every analog relationship. HIV labels never enter the new campaign models.

Raw and full derived inputs remain ignored under
`research/raw_data/ncats-development-20261104/`. Source receipts and the
[preparation audit](../evidence/ncats-development-20261104-v1/preparation-audit.json)
retain hashes, identifiers, exclusions and RDKit version. None of these resources
can be described as untouched final holdouts after this development exposure.

## Zero-active starts and fallback behavior

Initial active counts by seed 0/1/2 were AhR **1/3/1**, PPAR-gamma **1/2/0**,
and p53 **1/4/1**. The zero-active PPAR-gamma seed was retained in both conditions
for all six methods: 12/108 runs, one of nine distinct assay/seed starts.

| Fixed method | Accepted requests across 18 runs | Selector Random fallback requests | Successful predictor fits |
| --- | ---: | ---: | ---: |
| Random | 315 | 0 (Random is the declared policy) | 0 |
| Frozen Greedy | 322 | 36 | 16 |
| Retrained Greedy | 331 | 24 | 133 |
| Nearest-hit | 325 | 24 | 0 |
| Diversity | 309 | 0 | 0 |
| Pending penalty | 328 | 24 | 130 |

Frozen Greedy retained initial-one-class Random fallback throughout both affected
campaigns, even after active results arrived. Dynamic predictive policies could
fit only after a second class was delivered. Nearest-hit used a logged fallback
until an active reference existed. These are selector/model fallbacks. All
learned-controller requests and controller-fallback requests are **0 / N/A**:
no RL controller was evaluated in this pilot. This does not revise the preserved
HIV controller result of complete Greedy fallback.

## Accounting and failure analysis

The audit reconciled every completed journal, accepted request and decision's
revealed-label counts. All 108 runtime snapshots reconstructed exactly. Across
all runs, delivered counts ranged 11-21, reserved units 0-3, uncommitted units
2-12 and total accepted exposure 12-22. The budget is a cap, not a promise of
24 completed assays. Every common-delay run delivered 18; heterogeneous realized
turnaround and refill trajectories changed throughput. No missingness was
configured or observed; handling missing outcomes in this real-data grid is NOT_RUN.

The unfavorable AhR seed-1 heterogeneous pair first diverged at simulated time
1, with identical prior labels and two pending locations. Greedy selected
`ncats-dc485e1612fe2bc8e7b80f2f` (probability 0.995303); the penalty selected
`ncats-2e6f304996d388df574d1a00` (probability 0.992559, adjusted score 0.966918).
At T, Greedy had 12 hits / 18 deliveries / 2 pending; penalty had 10 hits /
15 deliveries / 0 pending. Both found six distinct nonempty active scaffolds.
This post hoc trace describes the observed difference, not an isolated causal
explanation or a validated rule for selecting a better coefficient. The frozen
coefficient remains unchanged and the unfavorable outputs are retained.

## Actual resources and verification

Environment: Windows 11, Python 3.12.10, NumPy 2.3.5, scikit-learn 1.8.0,
RDKit 2026.9.1, threadpoolctl 3.6.0. One campaign at a time; captured OpenBLAS
and OpenMP pools each report one thread. The host exposed 12 logical CPUs;
this pilot did not reserve the whole host.

- Cumulative run-wall time: **219.4677 seconds**, including per-run construction,
  journal restoration and artifact serialization; CPU time **196.8594 seconds**.
- Highest runner process peak working set across both phases: **224,002,048 bytes**
  (213.63 MiB). Separate cohort preparation: **14.9937 seconds**.
- No paid API calls, GPU jobs or remote host allocation. Electricity, analyst
  labor, source-research time and a currency bill were not measured. These CPU
  timings do not advance simulated assay time or establish laboratory savings.
- **0 actual run failures, 0 captured warnings**. Constructed failure tests check
  preservation of warning/traceback/resource metadata and prevent silent retries.
- **61 targeted tests PASS**: 19 development tests and 42 scheduler/registry/
  preservation-guard tests. Pre-freeze subset: 59 PASS. Ruff passes original and
  new Python paths. Full application/frontend/browser suites were NOT_RUN here.
- Strict 191-file historical-byte preservation PASS. Package/link/source checks
  are recorded separately; they are not a fresh clinical or model validation.
- Second-pass execution audit PASS: 108 identities and hashes, all 18 matched
  assay/seed/condition cells, budget reconciliation, public information counts
  and byte-identical evidence copies. Performed by the implementer, not an
  independent reviewer.

## Exact identities and reproducibility

| Identity | Value |
| --- | --- |
| Implementation commit before freeze | `a79707754d34e2d43fed4f9e1bac908f91dc0def` |
| Config freeze commit before first real method run | `4091e209fed78d04d48b13ef8ad719257302f684` |
| Material results commit | `efc8bcce623029cc49919c98c997eb025b459dcd` |
| Frozen at UTC | `2026-11-04T08:32:45.114256+00:00` |
| Config SHA256 (canonical JSON) | `8d1d7b0450074a78d54fedbe9ec96579845de08589103324a729947a6b567be2` |
| Execution source SHA256 (named LF-normalized source mapping) | `41dce53850a58caee1c0dda2e32cf7f1f47ab948b4ea632d219eb01f9fc31437` |

Both phases recorded the freeze commit and a clean working tree at process
startup. Audit/analysis documentation added afterward does not change execution
source identity. The config, source/cohort receipts and all 108 raw **public**
run JSONs plus ledger are in [the evidence packet](../evidence/ncats-development-20261104-v1/).
Exact run bytes are protected against Git newline conversion by packet-local
attributes; [execution-audit.json](../evidence/ncats-development-20261104-v1/execution-audit.json)
contains their SHA256 values.
The [committed-byte receipt](../evidence/ncats-development-20261104-v1/commit-identity.json)
also verifies all 110 raw run/ledger/canary artifacts directly from that results
commit. A packet-local CR-at-EOL check rule preserves captured Windows bytes
while keeping trailing-space checks enabled.

[36-cell summary CSV](../evidence/ncats-development-20261104-v1/results/summary.csv),
[108-run CSV](../evidence/ncats-development-20261104-v1/results/runs.csv),
[18 paired contrasts](../evidence/ncats-development-20261104-v1/results/pending-pairs.csv),
[complete analysis JSON](../evidence/ncats-development-20261104-v1/results/results.json),
[frozen config](../../research/configs/ncats_development_v1.json) and
[task registry](../../research/manifests/ncats_development_tasks_v1.json).

For a fresh local reproduction, fetch the pinned public sources, prepare cohorts
and use the **existing committed frozen config** with the runner commands in the
protocol. Do not refreeze or overwrite existing inputs/evidence. If upstream
bytes differ, the preparation rejects them; preserve the original local files
and create an explicit new source version rather than changing expected hashes.
Saved completed/failed attempts are hash-checked and skipped, while uncertain
interrupted attempts require a new explicit identity. Analysis and audit never
call the selectors or rerun campaigns.

## Remaining acceptance gaps

A genuine objective-matched probabilistic asynchronous comparator, ensemble
uncertainty, known-hit sensitivity, compute-aware assay-clock treatment and
controller training/transfer are NOT_RUN. There is no separate predictor audit
set or calibration claim. A final study needs independent task/family assignment,
the stronger comparator, a prespecified material-effect threshold and a frozen
confirmatory allocation. The present null/unfavorable finding is a reason to
reassess the heuristic on development evidence, not to tune a final holdout or
promote C06. External reproduction, commercial discovery, customer installation,
remote GPU use, push and publication remain outside this executed milestone.
