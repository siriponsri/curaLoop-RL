# Working manuscript

**Executed development studies plus proposed final study.** This English working draft reports the preserved HIV pilot, 108 NCATS development runs, 108 fresh-environment scientific reproductions and 54 Gaussian amendment runs. The independent-family final evaluation remains NOT_FROZEN / NOT_RUN. It is not a submission-ready final-study report. R05 source-specific details refer to the inspected ChemRxiv v3.

This file is assembled from the numbered chapters; edit those chapters and rebuild before publication.


## Title, abstract and keywords

**Manuscript state: WORKING_DRAFT_WITH_EXECUTED_DEVELOPMENT_STUDIES.** The
historical HIV pilot, NCATS development campaigns, fresh-environment reproduction
and Gaussian amendment are available. The broader held-out-family study remains
unfrozen and unexecuted. This is not a submission-ready final-study report.

### Current working title

CuraLoop: An Auditable Molecular Screening Workbench with Reproducible Development Studies under Delayed Feedback

### Candidate final-study title

When Does Pending-Aware Selection Help? A Reproducible Study of Molecular Screening under Delayed Feedback and Resource Constraints

The final-study title is conditional on completing the independent-family study;
it does not imply that a benefit has been demonstrated.

### Abstract

Molecular screening combines candidate selection with limited resources and
delayed assay feedback. CuraLoop-RL separates public candidate information from
unrevealed historical labels and records accepted requests, pending commitments
and delivered outcomes in an auditable ledger. Its preserved 1,200-compound HIV
pilot shows a transfer limitation: two synthetic-trained controllers each used
Greedy fallback for all 300 requests. We then executed a frozen 108-run CPU
development study on three correlated NCATS Tox21 endpoints, using six fixed
controls, three paired initialization seeds and two simulated-duration conditions.
Under heterogeneous duration, a pending-similarity penalty tied retrained Greedy
in eight of nine pairs and lost two delivered active labels in one pair; all
nine common-delay pairs had identical public event histories. A clean virtual
environment and separate checkout reproduced all 108 scientific artifacts on the
same host. A separately frozen 54-run Gaussian-surrogate amendment tied its
matched pending-blind comparator in all nine heterogeneous pairs despite five
changed histories. These bounded development results neither establish an
independent-target population effect nor demonstrate equivalence or learned
transfer. Outcome-sealed source/structure audits and hypothetical hierarchical
precision/resource simulations prepare a broader family-level estimation study,
whose rights, endpoint, task-role and analysis gates remain open. The workbench
supports reproducible retrospective research; prospective assay utility,
laboratory savings and operational Digital Twin fidelity remain unvalidated.

### Scientific contribution statement

The implemented contribution is an inspectable local replay workflow with tested
information/accounting boundaries, versioned development controls and retained
null/unfavorable comparisons. Same-implementer fresh-environment reproduction
supports reproducibility of those campaigns. Independent-family generalization,
practical utility and successful learned adaptation remain research questions.

### Keywords

Molecular screening; active learning; delayed feedback; asynchronous acquisition;
reproducibility; research software.

## Introduction

Screening decisions determine which compounds receive scarce experimental attention. A predictive model may rank a large pool, but the next useful measurement also depends on what has already been tested, which experiments remain pending and which results can arrive before the decision horizon. The scientific question is therefore broader than discrimination on a static test set: it concerns the sequence of information acquisition under explicit resource constraints.

Public molecular benchmarks provide a basis for retrospective evaluation. MoleculeNet and TDC organize datasets and task definitions (R01-R02), while active-learning studies examine how models and acquisition choices guide exploration (R04-R05, R27). Learned acquisition and RL-driven screening have existing precedents (R07, R28). Parallel and delayed optimization also have substantial prior art (R10-R13). These developments require a precise contribution beyond introducing an iterative loop or naming a controller RL.

Retrospective replay is useful because it allows a policy to be evaluated using historical labels that remain hidden until requested. However, replay quality depends on the information boundary, initialization, task sampling, event semantics and endpoint definitions. A hidden label can leak through preprocessing or simulation assumptions even when it is absent from the nominal model input. A repeated random seed changes initialization variability but does not establish generalization across biological targets.

CuraLoop-RL provides a local workbench in which selection, pending work, delivery and accounting are recorded as public events. The current implementation combines fingerprint-based prediction, fixed acquisition policies and frozen synthetic-trained controllers. It supports historical and synthetic scenarios, independent matched comparisons and recoverable exports. These capabilities support reproducibility and inspection; their software correctness is separate from biological or operational validity.

The historical HIV pilot reveals an important limitation. Both learned controllers used Greedy fallback for every recorded request. Their equality with Greedy therefore cannot be interpreted as successful RL transfer. The result motivates a study in which actual learned decisions, relevant state coverage and held-out biological tasks are explicitly evaluated. The existing pilot is retained because it identifies a methodological failure that a polished interface might otherwise obscure.

This research programme asks when pending-aware acquisition changes confirmed historical hit discovery under a fixed simulated deadline and limited capacity. The comparison separates policy information from predictor quality and assesses whether heterogeneous durations create a decision problem that a common delay alone does not. It also asks whether adaptation transfers to tasks not used in controller development.

The present manuscript describes the implemented workbench, preserved HIV pilot and newly executed NCATS development studies. The 108-run fixed-control pilot and separate 54-run Gaussian amendment retain null and unfavorable pending-aware comparisons; a fresh environment and separate local checkout reproduce the original scientific artifacts. These three correlated development endpoints do not constitute an independent-family final study. Source/structure audits and hypothetical hierarchical sensitivity calculations prepare that broader estimation design while preserving its open rights, endpoint and split gates. The evidence can support a bounded software/development contribution; no adaptive advantage is predetermined by the project name.

## Related work

The review connects molecular acquisition, learned policies, asynchronous optimization and scientific software. Its complete synthesis is in [Critical review](../02_literature/CRITICAL_REVIEW.md); the [full-text amendment](../02_literature/FULL_TEXT_REVIEW_ADDENDUM.md) identifies newly inspected versions and page-level evidence. This section is a manuscript bridge, not a second independent review.

### Molecular acquisition and low-data controls

MolPAL studies surrogate-guided selection in large docking pools (R04). The inspected ChemRxiv v3 low-data study uses three experimental assay-derived pools and compares model representations, acquisition and initial information (R05). It includes similarity and frozen-model exploitation controls and conditions its initial sets on a known active. Its acquisition utility and predictor discrimination are not interchangeable. SimDMTA studies query strategies in a focused BRD4 docking workflow (R27). These differences in outcome, initialization and budget prevent direct reuse of reported gains as a CuraLoop result or a universal ranking.

The resulting design requires Random, nearest-hit similarity, frozen-model Greedy and retrained Greedy, followed by explicit uncertainty and asynchronous controls. Such controls can distinguish iterative learning from a favorable initial ranking or a change of model. Zero-hit starts remain in the primary population; known-hit starts form a separately labelled sensitivity.

### Learned acquisition and operational constraints

RL-assisted generation and GLARE provide related and direct learned-selection precedents respectively (R06–R07), while R28 supplies earlier adaptive-acquisition methodology. Generation rewards and fixed-pool historical assay labels are different endpoints. Delayed feedback, batch interaction and asynchronous completion are established topics in online learning and Bayesian optimization (R10–R13). A new contribution must therefore be a specific controlled finding about tasks and operational assumptions, with actual learned decisions and fallback shares exposed.

ALF, PAL, BoTorch and BayBE provide relevant software and optimization precedents (R08–R09, R16, R26). BayBE's publisher article explicitly describes backtesting, asynchronous workflows, partial measurements and serialization; its examples include representation, related-task transfer and campaign stopping. Those capabilities rule out generic asynchrony or a reusable acquisition API as unique claims. They do not establish that a reaction-yield stopping objective is suitable for accumulating many Boolean hits. Exact versions and objective matching matter in an adaptation.

### Data and evaluation boundaries

MoleculeNet and TDC supply task/evaluation foundations (R01–R02). LIT-PCBA's curation and AVE splitting offer a valuable assay-based resource, but the target panel is selected partly through baseline virtual-screening enrichment (R03). Representation, overlap and benchmark analyses further motivate release-specific audits (R17–R19). Related endpoints must be grouped when assessing controller transfer, and seeds remain within-task repetitions.

Uncertainty and RL evaluation sources motivate precise score definitions, matched comparisons and interval estimates (R20–R24). The historical uncalibrated logistic margin is not validated epistemic uncertainty. The separate development Gaussian adapter supplies an explicit covariance-based uncertainty score, but Gaussian regression on Boolean labels is not a calibrated Bernoulli posterior and does not inherit a published asynchronous method's guarantees. Fixed-FPR enrichment, top-ranked-fraction enrichment, acquired-set enrichment, predictor AUROC and discovery-versus-time area also need distinct names and denominators.

All 28 reference records now have an identified PDF; one supplement is attached to R05. R05 was reviewed as ChemRxiv v3, and its associated journal full text was not compared. The VDR description discrepancy and preprint MI minimization direction remain explicit reproduction/import questions. References resolve through [the register](../02_literature/REFERENCES.md) and `references.bib`. The targeted, AI-assisted review requires an exact-version and nearest-work refresh before submission.

## Materials and methods: historical and development studies

### Dataset and initialization

The pilot uses the frozen `curaloop-hiv-1.0.0` derivative described in the resource manifest. The downloaded DeepChem HIV source contained 41,127 rows; seven invalid SMILES were removed under the documented preparation procedure. A label-blind random sample of 1,200 valid rows was retained. Canonical SMILES, Morgan radius-2 fingerprints with 1,024 bits and nonchiral Murcko scaffold identifiers were derived with RDKit. Historical CA/CM labels were mapped to active and CI to inactive.

Each campaign began with 48 uniformly sampled labelled compounds, selected without inspecting activity. These labels were preexisting sunk information, excluded from new-hit counts and campaign cost. Ten seeds, 0-9, were paired across five independent policies. The candidate pool, initial labels and scenario constraints were common within a seed; results were not shared between policies.

### Predictors and policies

Greedy and margin-based Uncertainty used `StandardScaler -> LogisticRegression`, with liblinear, C=1 and a maximum of 500 iterations. Only initial and subsequently delivered Boolean labels were used for fitting. A one-class observed set caused a labelled Random fallback. Predicted probabilities were uncalibrated. Greedy selected high predicted activity; Uncertainty used proximity to 0.5 as a margin score.

Frozen tabular Q-learning and contextual-bandit controllers selected among Random, Greedy and Uncertainty. Each controller had been trained on 160 synthetic episodes using seeds 10000-10159. The reward was newly delivered active hits minus 0.01 times newly settled assay cost. Their state lookup and explicit unseen-state Greedy fallback were retained during HIV evaluation. No HIV label was used for controller training.

### Scheduler and metrics

The recorded scenario used budget 30, unit assay cost, concurrent capacity 5 and a common delay of two simulated steps, with no jitter or missing outcomes. Accepted requests reserved cost once. Delivered outcomes settled cost once. Only unique newly delivered active results counted as new hits; seed labels, predictions and pending outcomes were excluded. The budget identity was spent plus reserved plus remaining equals total.

The recorded AUC-DB is the left-step integral of cumulative delivered hits against settled cost, carried to the configured budget and normalized by budget times the maximum affordable assay count. It is not AUROC or average precision. The historical comparisons summarize within-assay seed variation and include exploratory paired-bootstrap contrasts against Random.

### Separate predictor audit

A custom whole-scaffold hash split at seed 42 produced 960 training and 240 test molecules, containing 36 and six actives respectively and no shared Murcko scaffold. Scaling and fitting used training rows only. The evaluator's labels and fitted model were never passed to campaign policies. This is not an official MoleculeNet/TDC leaderboard reproduction.

### Evidence preservation

The historical HIV artifacts are retained unchanged. The separate NCATS studies below have new execution identities, frozen configurations and public run packets. Their versioned research modules are separate from the production UI and do not make the research configs supported inputs to the application CLI. This manuscript revision reads those completed artifacts; it does not rerun campaigns or retroactively preregister results. Software tests and browser verification are separate from chemical or operational validation.


### NCATS fixed-control development study

The [development protocol](../03_research/NCATS_DEVELOPMENT_PROTOCOL_V1.md)
was frozen at commit `4091e209fed78d04d48b13ef8ad719257302f684` before the
108 method runs. NCATS training exports identify AhR AID 743122, PPAR-gamma AID
743140 and p53 AID 720552, with CSV active=1/inactive=0. They are historical
pathway/toxicology endpoints, not therapeutic-efficacy labels. Canonical
duplicate groups with conflicting labels were excluded in full. Invalid rows
were excluded and consistent duplicates collapsed. Fixed structure/identity
hash ranking selected 600 compounds per endpoint without activity in the rank.
Raw/export/cohort hashes and attrition are retained in the development packet.
The cohorts overlap chemically and belong to one source panel; they are
explicitly exposed development resources rather than independent final tasks.

Each endpoint used seeds 0/1/2, 24 uniformly sampled initial labels, unit assay
cost, budget 24, concurrent capacity 3 and simulated deadline T=12. Conditions
used common duration 2 or heterogeneous durations 1/2/4 from a candidate-keyed
schedule. Initial labels and operational realizations were matched across
methods while fitted policy states remained independent. Initial labels are
sunk knowledge and excluded from newly delivered hits. All outcomes due at T
are processed atomically and count; no new request starts at T. No missingness
was configured. Zero-active starts were retained with declared fallbacks.

The six methods were Random, frozen Greedy, retrained Greedy, nearest-delivered-
hit similarity, structural diversity and a matched pending-similarity penalty.
Predictive controls use StandardScaler and liblinear logistic regression with
C=1 and max_iter=500. The penalty subtracts 0.2 times maximum Morgan/Tanimoto
similarity to the current pending set from predicted activity. Excluding already
requested candidates is shared by every arm and is not the treatment. Newly
chosen simultaneous batch members do not diversify one another. This is a
finite-pool heuristic, not a reproduction of a probabilistic asynchronous method.
The included canary and complete grid used the same frozen settings; resume
verified identities instead of repeating completed campaigns.

### Fresh-environment reproduction

A separate detached local clone of `d57838d41b30d956c7fd72ac502c1765653fd087`
and a new venv with system-site packages disabled regenerated the three cohort
hashes from pinned source bytes. Seven exact-version wheels were installed
offline; pip check and recorded distribution-path checks passed. The frozen
108-run grid was then reproduced and compared for scientific metrics, event
histories, initialization, schedules, selected scores and non-timing counters.
Runtime and environment metadata were compared separately. The implementer,
base Python interpreter and Windows host were shared. This tests fresh-
environment reproducibility, not independent scientific review or a second
biological sample. The [reproduction report](../03_research/NCATS_REPRODUCTION_V1.md)
retains setup/driver limitations and exact command logs.

### Gaussian-surrogate development amendment

The [Gaussian protocol](../03_research/NCATS_GAUSSIAN_PROTOCOL_V1.md) was frozen
at `a9d9c8f0747be3e2c7d8c41b42dc53efd049a40a` after the logistic pilot was
exposed and before any new Gaussian method runs. Three fixed arms, GP mean,
pending-blind GP-UCB and pending-conditioned GP-UCB, used the same three pools,
starts, seeds and operational conditions, giving 54 new campaigns. The sklearn
1.8.0 GaussianProcessRegressor uses a unit binary-Tanimoto kernel, alpha=0.1,
optimizer=None, normalize_y=False and kappa=1. Pending locations condition the
covariance while the observed-label posterior mean remains unchanged; no actual
pending outcome enters acquisition.

Gaussian regression on Boolean labels is an approximation. Its means/scores
are not labelled calibrated probabilities, and the adapter is not a GP-BUCB
reproduction. Acquisition uses marginal optimistic multi-hit scores rather than
plain best-value expected improvement. Simultaneous new batch members do not
condition one another. One-class Random fallback remains explicit. The matched
Gaussian pair isolates its declared pending term; comparison against logistic
Greedy also changes the predictor and cannot isolate pending awareness.

### Preparatory audit and hierarchical sensitivity

The [candidate audit](../03_research/CANDIDATE_ASSAY_AUDIT_V1.md) requests only
assay metadata, unfiltered membership and structures. No new candidate compound
outcome values are requested. Exact response hashes, versions, access errors,
feature-sample rules, overlap counts and unresolved data grants are retained.
Raw source AIDs are not a reproduction of prepared LIT-PCBA or DeepChem data.

The [design sensitivity](../03_research/DESIGN_SENSITIVITY_V1.md) simulates
family, task and paired-repeat variation under explicitly hypothetical profiles,
with 216 cells, 10,000 replicates per cell and five effect values. Its 1,080
reported rows are assumptions-driven planning outputs, not observed assay
effects or calibrated final-study power. Repeated seeds do not increase the
number of independent families. The owner's current direction is 12+ families
and effect estimates with uncertainty, without a confirmatory material-effect
threshold. No final allocation or outcome access is created by this preparation.

## Proposed final study: pending-aware screening

**Final-study status: NOT_FROZEN / NOT_RUN.** The [research protocol](../03_research/PROTOCOL.md), [candidate audit](../03_research/CANDIDATE_ASSAY_AUDIT_V1.md) and [estimation sensitivity](../03_research/DESIGN_SENSITIVITY_V1.md) distinguish this future independent-family study from the completed NCATS development campaigns reported in Chapter 5. No final compound outcome values were inspected during preparation.

The primary study compares pending-aware and matched pending-blind acquisition on multiple eligible biological tasks under a fixed simulated deadline. Conditions vary duration heterogeneity and capacity while matching the candidate pool, initial knowledge, predictor and operational random realization. The primary endpoint is newly delivered active assay labels by the deadline. Time/budget discovery curves, active scaffold coverage, failure rates and computational overhead are secondary endpoints.

Task families are separated into controller development, validation and final evaluation. The engineering pilot is used to identify defects and estimate resources, not to establish the final generalization claim. The owner selected 12+ biological families and effect estimates with uncertainty, without a confirmatory material-effect threshold. Exact roles, eligibility, primary contrast, family weighting, interval procedure, repeats, failure/stopping rules and a numeric CPU cap must be frozen before final outcome access. Missingness is introduced as a separate sensitivity condition with a declared mechanism.

The baseline set includes Random, retrained Greedy, frozen-model Greedy, nearest-delivered-hit similarity, structural diversity, uncertainty with an explicit model, a simple exploration mixture and an asynchronous acquisition method matched to multi-hit retrieval. The final strong fixed policy is selected on development tasks only. A learned controller is evaluated only after its decisions can be audited. All fallback and infeasible-action counts remain visible. A method that always falls back is not treated as evidence for learned transfer.

The current estimation proposal averages paired repeats within tasks and tasks within families, then weights families equally, with uncertainty that respects that hierarchy. It requires adjudicated families and cannot infer independent units from a convenient group count. Ablations remove pending and deadline information and separate predictor changes from policy changes. Tiny enumerated scenarios first establish that scheduling choices can affect the endpoint. Uniform-delay invariance is checked explicitly.

If the study finds no useful adaptive gain, the paper will report that result and identify the tested regimes. If the simulator cannot express a relevant decision tradeoff, the implementation must change before evaluating policies. If too few eligible tasks remain, the population and conclusion will be narrowed rather than inflated through extra seeds.

### Initialization, metrics and objective amendments

Primary starts are uniformly sampled without inspecting activity; zero-active starts remain eligible. A conditional-known-hit sensitivity follows a different initial-information distribution and is reported separately. The task registry preserves assay ID, functional phenotype, source release and eligibility attrition. LIT-PCBA's target ascertainment and unresolved description conflicts must be addressed before freezing tasks.

Report exact enrichment definitions and predictor-update cost. The simulator's assay clock and measured policy compute are separate unless a compute-aware scenario is explicitly defined. Best-observed-value EI is not automatically suitable for accumulating additional Boolean actives. [Baseline specification](../03_research/BASELINE_SPECIFICATION.md) and [metric concordance](../02_literature/METRIC_AND_INITIALIZATION_CONCORDANCE.md) govern the design. Six inexpensive controls and the Gaussian adapter have development execution evidence; a calibrated Bernoulli model, fixed mixture, within-batch conditioning and learned transfer remain open. These documents do not freeze a final comparison catalogue.


### Eligibility dependencies

Twenty completed/reused panel feature audits span 17 provisional planning
groups, including 14 human-annotated groups; quarantining mixed-endpoint CYP2C9
leaves 13. These are not certified independent families. Three additional panel
structure audits stopped at the prespecified payload cap. The earlier source
census and bounded gene search offer additional candidates, but exact file
rights, endpoint semantics, full-pool/cross-group chemical overlap and source
dependence remain unresolved. No final-ready task or validation/final role has
been assigned. Further attrition must be reported rather than repaired by
opening outcomes or relabelling related tasks. Development HIV/AhR/PPAR-gamma/
p53 resources cannot become untouched final holdouts.

## Results: historical pilot and executed development studies

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

### Separate predictor audit

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

### NCATS fixed-control development results

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

### Fresh-environment reproduction

The [reproduction](../03_research/NCATS_REPRODUCTION_V1.md) regenerated all
three cohort hashes and matched all 108 scientific artifacts in a separate
checkout and clean offline-installed venv. All campaigns completed without
failure; environment/timing/raw-file differences were retained separately.
Run-wall time was 213.93 seconds, CPU 195.02 seconds and peak runner memory
172.51 MiB. The same host and implementer performed the reproduction. It adds
environment reproducibility evidence, not new biological repetitions or
independent external review.

### Gaussian-surrogate development results

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

### Outcome-sealed preparation and hypothetical sensitivity

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

### Results not yet available

Independent-family final evaluation, learned-controller transfer, calibrated
Bernoulli uncertainty, within-batch conditioning, known-hit sensitivity,
independent external reproduction and prospective customer value remain
unavailable. The broader final protocol is not frozen. No invented confidence
interval, favorable task replacement or simulated revenue fills these gaps.

## Discussion

The pilot shows that a local screening workflow can retain an inspectable relationship between a decision, the knowledge available when it was made and the outcome delivered later. This is useful infrastructure for experiments and explanation. It does not resolve whether the selection policy is biologically useful or whether the simulated operations represent a particular laboratory.

The clearest scientific observation is a transfer limitation: the two synthetic-trained tables were never used directly on the recorded HIV states. A trained checkpoint is therefore insufficient evidence that learned decisions occurred. Reporting fallback use is essential to avoid attributing baseline performance to a controller that did not operate as intended.

The development studies make the operational distinction observable without demonstrating an advantage. Both matched pending pairs preserved identical common-delay histories, whereas heterogeneous durations changed many histories. The heuristic nevertheless produced no positive hit pair and one loss, while the Gaussian pair tied all nine heterogeneous hit counts. Changing decisions or adding a covariance model is therefore insufficient evidence of useful discovery gains. These limited null/unfavorable findings should guide a separately frozen broader study rather than a search for favorable replacements in final data.

Generalization remains unresolved. The HIV seeds explore initialization within one assay. The NCATS studies add three endpoint-specific development pools with only three seeds each, substantial shared chemistry and a common source panel. Neither their count nor the 108 reproduced runs creates independent target families. Metadata/structure audits now expose candidate scope and overlap, but exact-file rights, phenotype mapping, whole-pool dependence and task roles remain open. New benchmark names and provisional family labels are not substitutes for those checks.

The commercial implication is correspondingly limited. An auditable replay can help a team assess a decision workflow, but a retrospective advantage does not equal actual laboratory savings. A customer pilot should measure reproducibility, analyst effort and decision relevance before making claims about discovery outcomes. The installed local boundary may be attractive to some buyers, but that preference remains a hypothesis until customer evidence exists.

The paper route should follow the strongest supported result. Useful regime-specific findings can support a benchmark study even if a learned controller fails. A software contribution requires demonstrable utility and comparison with existing frameworks. A methods claim requires additional evidence that the proposed method, rather than a different predictor or favorable initialization, creates the improvement.

### Consequences of the additional full texts

The R05 preprint's known-active initialization and no-retrain/similarity controls show why favorable acquisition results cannot be attributed to controller adaptation without isolating initial knowledge and model updates. LIT-PCBA's ascertainment also limits the population to which a selected-task result can apply. These are design constraints for the proposed study, not new defects demonstrated in the preserved HIV pilot.

BayBE's documented backtesting, asynchronous support and campaign-stopping examples favor an interoperability assessment. A narrower evaluation/reporting layer can be useful if it solves an observed workflow problem. The software paper and pilot must demonstrate that utility; a feature list or another study's case-specific savings do not establish it.


### Reproducibility and uncertainty

The separate clean venv/checkout reproduced scientific trajectories and cohort
hashes while retaining different timing/environment identities. That is useful
engineering evidence; because the implementer and host were shared, it does not
constitute independent scientific validation. The Gaussian adapter is an
explicit approximation with no inherited regret or probability-calibration claim.

The three exposed endpoints cannot identify between-source/family variation.
All-zero Gaussian contrasts do not justify a zero-variance prior or equivalence.
The hypothetical hierarchical grid makes that uncertainty visible: additional
seeds cannot remove a family component. Current direction is estimation with
uncertainty and no confirmatory practical margin. Any later statement of
practically meaningful superiority would require a different justified design
and claim, rather than a post hoc margin selected from these outcomes.

## Limitations and threats to validity

The historical HIV evidence concerns one custom subset, not an official leaderboard split. Its predictor audit has only six test actives and does not establish a generally reliable molecular classifier. The new NCATS development studies concern three correlated, chemically overlapping endpoints from one source panel, with only three paired seeds per endpoint. They are not untouched independent-family final tests. Reproducing 108 campaigns does not add biological replication.

Controller training used synthetic tasks and all recorded HIV controller requests used fallback. No learned controller was evaluated in the NCATS studies. Neither the checkpoints, fixed-control results nor UI establish pharmaceutical RL transfer. Pending-similarity and Gaussian covariance controls were implemented and executed, but a generalizing controller, calibrated Bernoulli uncertainty, within-batch conditioning and known-hit sensitivity remain open. The Gaussian adapter is a binary-regression approximation, not a calibrated posterior or a reproduction of published asynchronous theory.

Costs, duration, capacity and missingness are scenario assumptions. The simulator is not calibrated to a physical laboratory and has no live process link. Retrospective replay exposes historical labels through a scheduler; it does not synthesize compounds or repeat an assay. “Active” is endpoint-specific and does not imply efficacy, safety, potency, novelty or developability.

Data standardization, duplicates, initialization and task selection can bias results. Development attrition/overlap audits and outcome-sealed candidate samples have been executed, but a 200-structure sample cannot clear a complete feature pool or certify family independence. Source identity is pinned per received response rather than as an atomic historical prepared release. Some metadata/endpoint/rights conflicts remain unresolved, and no final-ready role has been assigned. The preserved gene search includes HTTP 404 membership errors; the panel includes three payload-cap exclusions and RDKit warnings. Final freezing and full-pool/cross-group dependence checks remain incomplete.

The literature review is targeted and AI-assisted, with single-reviewer selection. All 28 source records have an identified PDF version, plus one supplement, but this does not imply exhaustive reading of every appendix, independent replication or systematic dual screening. R05 is inspected as ChemRxiv v3; the associated journal full text was not compared. Version-specific VDR wording and MI-direction questions remain unresolved pending exact data/code checks. The nearest-work search and source versions require an update before submission. No full technical reproduction of competing studies was performed.

No buyer interviews, external installations, paid pilots or measured business benefits are recorded. Commercial documents are hypotheses and draft offer materials. The current workstation application lacks enterprise multi-user and operational integration evidence. Software verification from earlier releases must not be represented as clinical or commercial validation.

LIT-PCBA's original target panel is ascertained partly through baseline screening performance. Any eligible subset can further restrict the population. Differences between uniform and known-hit starts, source metric definitions and model-update cost can alter comparisons. Simulated turnaround does not establish end-to-end laboratory time savings, especially when policy compute and real operational queues have not been measured.


The 108-run reproduction used the same implementer, host and base interpreter;
there was no independent external scientific reproduction. Measured CPU/wall
costs apply to the recorded 600-compound development pools and methods. Forecasts
for remote hardware, larger pools and additional methods are assumptions.
Hypothetical hierarchical simulations use continuous unbounded differences and
assumed variance profiles, not calibrated assay-count distributions or empirical
population variance. No final power, coverage, equivalence or practically
meaningful-superiority guarantee follows from them. No final outcome file was
opened during candidate preparation.

## Conclusion

CuraLoop-RL provides a local historical-screening workbench with explicit
separation of pending predictions and delivered assay evidence. Its preserved
HIV pilot exposes complete controller fallback rather than successful learned
transfer. The frozen NCATS development pilot and Gaussian amendment add tested
deadline-based comparisons on three correlated endpoints: the similarity penalty
had eight ties and one loss under heterogeneous duration, while the Gaussian
pair tied all nine comparisons. No positive pending-aware hit pair was observed
in these bounded allocations, and tied counts do not establish equivalence.

A separate clean environment and checkout reproduced the original 108 scientific
artifacts on the same host. This supports engineering reproducibility, with its
same-implementer limitations explicit. Source/structure audits and hypothetical
hierarchical sensitivity prepare a broader family-level estimation design while
keeping final outcomes sealed. Independent-family effects, learned transfer,
practical laboratory utility and commercial benefit remain unestablished. The
next scientific step is source/endpoint/dependence closure and a frozen analysis,
not a claim that implementation complexity or publication preparation proves an
adaptive advantage.

## Declarations and author review

**Draft state: author verification required before submission.** This file records known facts and unresolved author-supplied information. It does not assert that human review, institutional permission or a commercial agreement has already occurred.

### Authorship and affiliation

The owner supplied the following publication details on 4 November 2026: **Siripon Srihangpiboon**; **King Mongkut's Institute of Technology Ladkrabang**; corresponding email **srihangpiboon.siri@gmail.com**; ORCID **0009-0001-0611-5568**. These are owner-provided declarations, not an independent verification of affiliation, institutional permission or endorsement. The author must confirm the exact affiliation presentation and all submission declarations. Add coauthors only for qualifying actual contributions and with their agreement. AI systems are not authors.

### Data and code availability

The source repository is [CuraLoop-RL](https://github.com/siriponsri/curaLoop-RL). Versioned manifests and public packets identify the historical derivative, 108 NCATS development campaigns, their 108 fresh-environment reproductions and the 54-run Gaussian amendment. The independent-family final study remains unexecuted. Full raw/derived candidate sources, cached wheels and reading-room PDFs are outside the public Git payload; exact identities, rights limits and retrieval/preparation instructions are documented. Do not imply that software MIT terms license all third-party assay files. No archival DOI is assigned by this manuscript, and no outcome file is redistributed without its applicable grant.

### Funding and competing interests

No project-specific external funding was supplied in this request. Confirm actual funding at submission. The owner intends to investigate commercial R&D pilots; disclose any financial interest, paid engagement or organizational relationship that exists at that time. An intention to sell is not a recorded sale or customer endorsement.

### Human/animal participants and data

The current scope uses public historical molecular assay data and no new participant or animal study. This is a factual scope statement, not an institutional ethics determination. A future prospective study, identifiable user study or customer dataset may need a different review and declaration. Do not copy “not applicable” into a changed study without checking its actual design.

### AI assistance

ChatGPT/Codex assistance was used for source inspection, code generation/refactoring, test development, experiment execution and analysis tooling, literature discovery/extraction, documentation and protocol/business/manuscript drafting. The exact deployment/model-version log was not independently verified in this package. Before submission the human author must record the tools/versions available to them and review every claim, reference, calculation and generated change. Do not state that this review is complete until it is done.

The selected venue's current AI policy must govern the manuscript, disclosure and any editorial communication. This draft contains no sent submission correspondence and does not assert completed human validation. The owner supplied a publication-fee ceiling of USD 300; this is a budget constraint, not a paid invoice, waiver approval or permission to submit inconsistent declarations.
