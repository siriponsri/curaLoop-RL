# Results: historical pilot and executed development studies

The first two sections retain the historical HIV result exactly. Subsequent sections report the separately executed NCATS development studies and preparation artifacts. They do not supply untouched final-study results.

**HIV evidence state: RECORDED_HISTORICAL.** Source: `docs/evidence/hiv-benchmark/summary.json`. Each policy has ten paired initialization runs with a 30-assay budget. Initial labels are excluded from new hits.

| Policy | Mean new active hits | Sample SD | Range | Controller fallback |
| --- | ---: | ---: | --- | --- |
| Random | 0.7 | 0.9487 | 0-3 | Not applicable |
| Greedy | 3.8 | 3.2592 | 0-9 | Not applicable |
| Uncertainty | 0.9 | 1.1972 | 0-3 | Not applicable |
| Q-learning | 3.8 | 3.2592 | 0-9 | 300/300 requests |
| Contextual bandit | 3.8 | 3.2592 | 0-9 | 300/300 requests |

The recorded exploratory Greedy-minus-Random mean paired difference is 3.1 hits, with a deterministic paired-bootstrap 95% percentile interval of 1.5 to 4.8. The Uncertainty-minus-Random difference is 0.2, with interval -0.8 to 1.0. These intervals reflect initialization variation within one assay. They are not uncertainty estimates across independent biological targets, and multiple contrasts were exploratory.

Both learned controllers invoked the explicit unseen-state Greedy fallback for every accepted request. Their identical aggregate outcomes therefore do not demonstrate transfer of the learned tables. The recorded evaluation supports a statement about the fallback execution path and the tested Greedy baseline, not superiority of Q-learning or bandits.

## Separate predictor audit

| Quantity | Recorded value |
| --- | ---: |
| Training / test molecules | 960 / 240 |
| Training / test actives | 36 / 6 |
| Shared Murcko scaffolds | 0 |
| AUROC | 0.5562678063 |
| Average precision | 0.0326585013 |
| Brier score | 0.0440829783 |
| Test prevalence | 0.025 |

The predictor result is weak on this small imbalanced test set. Campaign acquisition and static discrimination address different questions, so the recorded Greedy discovery result should be read alongside this limitation. The audit model was not used by the acquisition policies.

## NCATS fixed-control development results

**108/108 campaigns completed, zero failures and zero captured run warnings.**
The [frozen pilot results](../03_research/NCATS_DEVELOPMENT_RESULTS_V1.md)
cover AhR, PPAR-gamma and p53, three seeds each, six fixed methods and two
duration conditions. Each descriptive mean below is based on three runs, not
three independent target families.

| Endpoint / duration | Random | Frozen Greedy | Retrained Greedy | Nearest-hit | Diversity | Pending penalty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AhR / common 2 | 1.00 | 8.33 | 9.67 | 10.33 | 1.00 | 9.67 |
| AhR / heterogeneous 1,2,4 | 1.33 | 8.00 | 9.00 | 8.33 | 1.00 | 8.33 |
| PPAR-gamma / common 2 | 0.67 | 1.67 | 1.33 | 2.00 | 0.00 | 1.33 |
| PPAR-gamma / heterogeneous 1,2,4 | 0.67 | 1.67 | 2.00 | 1.67 | 0.00 | 2.00 |
| p53 / common 2 | 0.67 | 2.33 | 2.67 | 1.33 | 1.00 | 2.67 |
| p53 / heterogeneous 1,2,4 | 0.67 | 2.33 | 2.33 | 1.67 | 1.00 | 2.33 |

Values are newly delivered historical assay-active labels at T=12. Under
heterogeneous duration, pending-penalty minus retrained Greedy was zero in
eight pairs and -2 in one AhR pair: 0 wins, 8 ties, 1 loss. Endpoint means of
that contrast were -0.67, 0 and 0. Event traces changed in 7/9 heterogeneous
pairs. All 9/9 common-delay pairs had exactly identical public histories. The
unfavorable result is retained; trace differences do not establish useful gains.

The 600-compound pools contained 59/18/31 actives respectively. The three pools
shared 52/52/36 exact canonical structures pairwise. A zero-active PPAR-gamma
seed was retained in both conditions for all six methods, giving 12/108
campaigns with zero initial actives. No learned controller was evaluated;
fixed-selector/model fallbacks are distinct from HIV controller fallback.

The small, correlated, exposed endpoints do not support a population-level
confidence interval or equivalence claim. Cumulative run-wall time was 219.47
seconds, process CPU 196.86 seconds and peak runner memory 213.63 MiB on the
recorded single-threaded Windows configuration. These are compute measurements,
not simulated assay duration or laboratory savings.

## Fresh-environment reproduction

The [reproduction](../03_research/NCATS_REPRODUCTION_V1.md) regenerated all
three cohort hashes and matched all 108 scientific artifacts in a separate
checkout and clean offline-installed venv. All campaigns completed without
failure; environment/timing/raw-file differences were retained separately.
Run-wall time was 213.93 seconds, CPU 195.02 seconds and peak runner memory
172.51 MiB. The same host and implementer performed the reproduction. It adds
environment reproducibility evidence, not new biological repetitions or
independent external review.

## Gaussian-surrogate development results

**54/54 campaigns completed, zero failures and zero captured run warnings.**
The separately frozen [Gaussian amendment](../03_research/NCATS_GAUSSIAN_RESULTS_V1.md)
used three fixed arms on the same exposed pools, initializations and schedules.

| Endpoint / duration | GP mean | GP UCB blind | GP UCB pending |
| --- | ---: | ---: | ---: |
| AhR / common 2 | 8.33 | 9.00 | 9.00 |
| AhR / heterogeneous 1,2,4 | 7.00 | 6.67 | 6.67 |
| PPAR-gamma / common 2 | 2.00 | 1.67 | 1.67 |
| PPAR-gamma / heterogeneous 1,2,4 | 2.33 | 2.33 | 2.33 |
| p53 / common 2 | 2.00 | 2.33 | 2.33 |
| p53 / heterogeneous 1,2,4 | 2.00 | 2.33 | 2.33 |

Pending-conditioned minus pending-blind GP-UCB tied H(12) in all nine
heterogeneous pairs, with five changed histories. All nine common-delay pairs
matched exactly. A post hoc implementation diagnostic counted 89 selected
requests with strictly reduced pending-conditioned standard deviation. This
shows that covariance conditioning was active; it does not establish improved
discovery. Every arm retained 24 one-class Random fallback requests. Six
zero-active-start campaigns were retained. No learned controller was run.

The amendment consumed 101.90 cumulative run-wall seconds, 95.16 seconds CPU
and 172.62 MiB peak runner memory. Gaussian-on-binary uncertainty and lack of
within-batch conditioning remain explicit limitations. Comparison to logistic
Greedy also changes predictor family and is descriptive, not an isolated test
of pending awareness. No equivalence conclusion follows from tied hit counts.

## Outcome-sealed preparation and hypothetical sensitivity

The [candidate audit](../03_research/CANDIDATE_ASSAY_AUDIT_V1.md) completed
24 initial source feature audits. A bounded 16-gene search found one HSP90
feature candidate and retained 23 HTTP 404 membership attempts. All 128 pinned
PCBA identifier descriptions were inspected; of 23 preselected panel structure
audits, 17 were new, three reused existing audits and three stopped at the
payload cap. The 20 completed/reused panel audits span 17 provisional groups,
not certified independent families. File rights, endpoint mappings and full
feature-pool dependence remain open. Final-ready task count is zero.

The [sensitivity simulation](../03_research/DESIGN_SENSITIVITY_V1.md) retained
1,080 hypothetical rows from 216 cells with 10,000 replicates per cell, plus
288 resource rows. In the assumed middle Gaussian profile, median 95% interval
halfwidth is 0.710 hits for 12 families, one task/family and 20 paired repeats,
compared with 0.599 hits for 16 families. These are model assumptions, not
observed final-study effects or guaranteed precision. No new candidate outcome
values were requested and no confirmatory material-effect margin was selected.

## Results not yet available

Independent-family final evaluation, learned-controller transfer, calibrated
Bernoulli uncertainty, within-batch conditioning, known-hit sensitivity,
independent external reproduction and prospective customer value remain
unavailable. The broader final protocol is not frozen. No invented confidence
interval, favorable task replacement or simulated revenue fills these gaps.
