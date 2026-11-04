# Working manuscript

**Reviewed documentation version 2. Historical pilot plus proposed study; new multi-target results remain NOT_RUN.** This file is assembled from numbered chapters. Edit the chapters and rebuild before publication. R05 source-specific details refer to the inspected ChemRxiv v3.

## Title, abstract and keywords

**Manuscript state: WORKING_DRAFT_WITH_HISTORICAL_PILOT.** The new multi-target study is specified but unexecuted. The final-study title below is conditional on completing that study. Do not submit this draft as a completed multi-target experiment.

### Current working title

CuraLoop: An Auditable Molecular Screening Workbench, Historical Pilot and Protocol for Evaluation under Delayed Feedback

### Candidate final-study title

When Does Pending-Aware Selection Help? A Reproducible Study of Molecular Screening under Delayed Feedback and Resource Constraints

### Abstract

Molecular screening requires sequential decisions under limited budgets and incomplete assay feedback. We describe CuraLoop-RL, a local research workbench that separates public candidate information from unrevealed historical outcomes and records accepted requests, pending commitments and delivered results in an inspectable ledger. The existing pilot uses a frozen 1,200-molecule MoleculeNet HIV derivative, 48 preexisting labels, a 30-assay budget and ten paired initialization seeds. Recorded mean newly delivered actives were 0.7 for Random, 3.8 for Greedy and 0.9 for margin-based Uncertainty. Frozen Q-learning and contextual-bandit controllers each matched Greedy while using an unseen-state Greedy fallback for all 300 requests; this does not establish learned transfer. We specify a multi-target evaluation of pending-aware acquisition under heterogeneous simulated duration, limited capacity and deadlines, with matched predictors, independent comparisons and task-level uncertainty analysis. That evaluation has not yet been executed. The workbench and protocol support reproducible retrospective research; prospective assay utility, laboratory savings and operational Digital Twin fidelity remain unvalidated.

### Scientific contribution statement

The implemented contribution is an inspectable local replay workflow with explicit information and accounting boundaries. The proposed research contribution is a controlled evaluation of when pending work and operational timing change acquisition performance. Learned-controller superiority is a hypothesis and is not supported by the existing pilot.

### Keywords

Molecular screening; active learning; delayed feedback; asynchronous optimization; reinforcement learning; reproducibility; retrospective benchmark; research software.

## Introduction

Screening decisions determine which compounds receive scarce experimental attention. A predictive model may rank a large pool, but the next useful measurement also depends on what has already been tested, which experiments remain pending and which results can arrive before the decision horizon. The scientific question is therefore broader than discrimination on a static test set: it concerns the sequence of information acquisition under explicit resource constraints.

Public molecular benchmarks provide a basis for retrospective evaluation. MoleculeNet and TDC organize datasets and task definitions (R01-R02), while active-learning studies examine how models and acquisition choices guide exploration (R04-R05, R27). Learned acquisition and RL-driven screening have existing precedents (R07, R28). Parallel and delayed optimization also have substantial prior art (R10-R13). These developments require a precise contribution beyond introducing an iterative loop or naming a controller RL.

Retrospective replay is useful because it allows a policy to be evaluated using historical labels that remain hidden until requested. However, replay quality depends on the information boundary, initialization, task sampling, event semantics and endpoint definitions. A hidden label can leak through preprocessing or simulation assumptions even when it is absent from the nominal model input. A repeated random seed changes initialization variability but does not establish generalization across biological targets.

CuraLoop-RL provides a local workbench in which selection, pending work, delivery and accounting are recorded as public events. The current implementation combines fingerprint-based prediction, fixed acquisition policies and frozen synthetic-trained controllers. It supports historical and synthetic scenarios, independent matched comparisons and recoverable exports. These capabilities support reproducibility and inspection; their software correctness is separate from biological or operational validity.

The historical HIV pilot reveals an important limitation. Both learned controllers used Greedy fallback for every recorded request. Their equality with Greedy therefore cannot be interpreted as successful RL transfer. The result motivates a study in which actual learned decisions, relevant state coverage and held-out biological tasks are explicitly evaluated. The existing pilot is retained because it identifies a methodological failure that a polished interface might otherwise obscure.

This research programme asks when pending-aware acquisition changes confirmed historical hit discovery under a fixed simulated deadline and limited capacity. The comparison separates policy information from predictor quality and assesses whether heterogeneous durations create a decision problem that a common delay alone does not. It also asks whether adaptation transfers to tasks not used in controller development.

The present manuscript describes the implemented workbench, recorded pilot and a detailed study protocol. The proposed multi-target evaluation is unexecuted. Its eventual conclusions may support an adaptive method, identify conditions in which a fixed policy is sufficient or motivate a benchmark/software contribution centered on reproducible operational evaluation. None of these conclusions is predetermined by the project name.

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

Uncertainty and RL evaluation sources motivate precise score definitions, matched comparisons and interval estimates (R20–R24). The current uncalibrated logistic margin is not validated epistemic uncertainty. Fixed-FPR enrichment, top-ranked-fraction enrichment, acquired-set enrichment, predictor AUROC and discovery-versus-time area also need distinct names and denominators.

All 28 reference records now have an identified PDF; one supplement is attached to R05. R05 was reviewed as ChemRxiv v3, and its associated journal full text was not compared. The VDR description discrepancy and preprint MI minimization direction remain explicit reproduction/import questions. References resolve through [the register](../02_literature/REFERENCES.md) and `references.bib`. The targeted, AI-assisted review requires an exact-version and nearest-work refresh before submission.

## Materials and methods: implemented historical pilot

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

This documentation release reads existing artifacts and does not rerun or alter the pilot. Exact machine-readable settings, metrics and source identities remain in the original evidence folders. Software tests and browser verification are reported separately and do not validate chemical or operational performance.

## Proposed study: pending-aware screening

**Status: NOT_RUN.** The definitive implementation protocol is [Research protocol](../03_research/PROTOCOL.md), supported by data/split, scheduler, experiment and analysis specifications. This chapter describes planned work and is not a results section.

The primary study compares pending-aware and matched pending-blind acquisition on multiple eligible biological tasks under a fixed simulated deadline. Conditions vary duration heterogeneity and capacity while matching the candidate pool, initial knowledge, predictor and operational random realization. The primary endpoint is newly delivered active assay labels by the deadline. Time/budget discovery curves, active scaffold coverage, failure rates and computational overhead are secondary endpoints.

Task families are separated into controller development, validation and final evaluation. The engineering pilot is used to identify defects and estimate resources, not to establish the final generalization claim. Exact task roles, inclusion rules, primary contrast, material effect, repeats and stopping criteria are frozen before inspecting the final evaluation. Missingness is introduced as a separate sensitivity condition with a declared mechanism.

The baseline set includes Random, retrained Greedy, frozen-model Greedy, nearest-delivered-hit similarity, structural diversity, uncertainty with an explicit model, a simple exploration mixture and an asynchronous acquisition method matched to multi-hit retrieval. The final strong fixed policy is selected on development tasks only. A learned controller is evaluated only after its decisions can be audited. All fallback and infeasible-action counts remain visible. A method that always falls back is not treated as evidence for learned transfer.

The analysis estimates paired differences at the task level, with uncertainty that respects families/tasks and repeated seeds. Ablations remove pending and deadline information and separate predictor changes from policy changes. Tiny enumerated scenarios first establish that scheduling choices can affect the endpoint. Uniform-delay invariance is checked explicitly.

If the study finds no useful adaptive gain, the paper will report that result and identify the tested regimes. If the simulator cannot express a relevant decision tradeoff, the implementation must change before evaluating policies. If too few eligible tasks remain, the population and conclusion will be narrowed rather than inflated through extra seeds.

### Initialization, metrics and objective amendments

Primary starts are uniformly sampled without inspecting activity; zero-active starts remain eligible. A conditional-known-hit sensitivity follows a different initial-information distribution and is reported separately. The task registry preserves assay ID, functional phenotype, source release and eligibility attrition. LIT-PCBA's target ascertainment and unresolved description conflicts must be addressed before freezing tasks.

Report exact enrichment definitions and predictor-update cost. The simulator's assay clock and measured policy compute are separate unless a compute-aware scenario is explicitly defined. Best-observed-value EI is not automatically suitable for accumulating additional Boolean actives. [Baseline specification](../03_research/BASELINE_SPECIFICATION.md) and [metric concordance](../02_literature/METRIC_AND_INITIALIZATION_CONCORDANCE.md) govern the implementation amendment; neither is an executed result.

## Results: preserved historical evidence

**Evidence state: RECORDED_HISTORICAL, not newly executed in this package.** Source: `docs/evidence/hiv-benchmark/summary.json`. Each policy has ten paired initialization runs with a 30-assay budget. Initial labels are excluded from new hits.

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

### Results not yet available

Multi-target pending-aware comparisons, deadline-based effects, learned-controller transfer, new ablations, external reproduction and prospective customer value are NOT_RUN. The absence of these results is explicit. No expected improvement, invented confidence interval or simulated revenue is inserted into the manuscript.

## Discussion

The pilot shows that a local screening workflow can retain an inspectable relationship between a decision, the knowledge available when it was made and the outcome delivered later. This is useful infrastructure for experiments and explanation. It does not resolve whether the selection policy is biologically useful or whether the simulated operations represent a particular laboratory.

The clearest scientific observation is a transfer limitation: the two synthetic-trained tables were never used directly on the recorded HIV states. A trained checkpoint is therefore insufficient evidence that learned decisions occurred. Reporting fallback use is essential to avoid attributing baseline performance to a controller that did not operate as intended.

The next evaluation should establish whether operational conditions create meaningful choices. A common delay can increase simulated completion time without changing final compound selection. A fixed deadline and varying completion times can instead alter what is known before the next action. The proposed protocol isolates that distinction and requires comparison with established asynchronous methods.

A second issue is generalization. The current ten seeds explore initial-information variability within one assay. They do not demonstrate performance across target families. New data must be inspected for endpoint validity and structure overlap; adding a benchmark by name is not enough. Controller development and final tasks need separate roles, and the predictor audit must remain outside policy information.

The commercial implication is correspondingly limited. An auditable replay can help a team assess a decision workflow, but a retrospective advantage does not equal actual laboratory savings. A customer pilot should measure reproducibility, analyst effort and decision relevance before making claims about discovery outcomes. The installed local boundary may be attractive to some buyers, but that preference remains a hypothesis until customer evidence exists.

The paper route should follow the strongest supported result. Useful regime-specific findings can support a benchmark study even if a learned controller fails. A software contribution requires demonstrable utility and comparison with existing frameworks. A methods claim requires additional evidence that the proposed method, rather than a different predictor or favorable initialization, creates the improvement.

### Consequences of the additional full texts

The R05 preprint's known-active initialization and no-retrain/similarity controls show why favorable acquisition results cannot be attributed to controller adaptation without isolating initial knowledge and model updates. LIT-PCBA's ascertainment also limits the population to which a selected-task result can apply. These are design constraints for the proposed study, not new defects demonstrated in the preserved HIV pilot.

BayBE's documented backtesting, asynchronous support and campaign-stopping examples favor an interoperability assessment. A narrower evaluation/reporting layer can be useful if it solves an observed workflow problem. The software paper and pilot must demonstrate that utility; a feature list or another study's case-specific savings do not establish it.

## Limitations and threats to validity

The historical evidence concerns one custom HIV subset, not an official leaderboard split or multiple independent targets. The predictor audit has only six test actives. Its scores and the recorded discovery contrasts do not establish a generally reliable molecular classifier.

Controller training used synthetic tasks. All recorded HIV controller requests used fallback. Neither the current tables nor the UI demonstrate successful pharmaceutical RL transfer. A generalizing controller, stronger uncertainty model and pending-aware acquisition remain planned work.

Costs, duration, capacity and missingness are scenario assumptions. The simulator is not calibrated to a physical laboratory and has no live process link. Retrospective replay exposes historical labels through a scheduler; it does not synthesize compounds or repeat an assay. “Active” is endpoint-specific and does not imply efficacy, safety, potency, novelty or developability.

Data standardization, duplicate handling, initialization and target selection can bias results. A source dataset may contain redundancy even when commonly used. The proposed audit and final freeze reduce these risks but have not yet been executed. Model uncertainty, calibration and prospective deployment shift also require separate assessment.

The literature review is targeted and AI-assisted, with single-reviewer selection. All 28 source records have an identified PDF version, plus one supplement, but this does not imply exhaustive reading of every appendix, independent replication or systematic dual screening. R05 is inspected as ChemRxiv v3; the associated journal full text was not compared. Version-specific VDR wording and MI-direction questions remain unresolved pending exact data/code checks. The nearest-work search and source versions require an update before submission. No full technical reproduction of competing studies was performed.

No buyer interviews, external installations, paid pilots or measured business benefits are recorded. Commercial documents are hypotheses and draft offer materials. The current workstation application lacks enterprise multi-user and operational integration evidence. Software verification from earlier releases must not be represented as clinical or commercial validation.

LIT-PCBA's original target panel is ascertained partly through baseline screening performance. Any eligible subset can further restrict the population. Differences between uniform and known-hit starts, source metric definitions and model-update cost can alter comparisons. Simulated turnaround does not establish end-to-end laboratory time savings, especially when policy compute and real operational queues have not been measured.

## Conclusion

CuraLoop-RL provides a local historical-screening workbench with explicit separation of pending predictions and delivered assay evidence. Its preserved HIV pilot exposes a substantive limitation: synthetic-trained controllers matched Greedy through complete fallback, leaving learned transfer unestablished.

The proposed next study tests when pending-aware acquisition changes deadline-constrained discovery across biological tasks, using matched controls and reproducible evidence. Its outcomes may support, limit or reject an adaptive advantage. A completed multi-target evaluation and an auditable reproduction are needed before making that conclusion.

## Declarations and author review

**Draft state: author verification required before submission.** This file records known facts and unresolved author-supplied information. It does not assert that human review, institutional permission or a commercial agreement has already occurred.

### Authorship and affiliation

The project owner is Siripon Srihangpiboon according to the account context. Publication spelling, author order, affiliation, corresponding email and ORCID must be confirmed by the owner. No employer, hospital, university or GPO endorsement is inferred. Add coauthors only for qualifying actual contributions and with their agreement. AI systems are not listed as authors.

### Data and code availability

The public source repository is `https://github.com/siriponsri/curaLoop-RL`. The historical derivative and evidence artifacts are described by versioned manifests. New multi-target results are not yet available. No archival DOI has been assigned by this package. Downloaded reading-room PDFs retain third-party rights and are not part of the public code payload.

### Funding and competing interests

No project-specific external funding was supplied in this request. Confirm actual funding at submission. The owner intends to investigate commercial R&D pilots; disclose any financial interest, paid engagement or organizational relationship that exists at that time. An intention to sell is not a recorded sale or customer endorsement.

### Human/animal participants and data

The current scope uses public historical molecular assay data and no new participant or animal study. This is a factual scope statement, not an institutional ethics determination. A future prospective study, identifiable user study or customer dataset may need a different review and declaration. Do not copy “not applicable” into a changed study without checking its actual design.

### AI assistance

ChatGPT/Codex assistance was used to inspect source, discover and extract literature, organize documentation and draft the protocol/business/manuscript materials. The exact deployment/model-version log was not independently verified in this package. Before submission the human author must record the tools/versions available to them and review every claim, reference, calculation and generated change. Do not state that this review is complete until it is done.

The submission venue's current AI policy must be checked. JOSS currently requires disclosure and restricts AI use in author-editor/reviewer conversational interactions beyond translation. This package contains no sent submission correspondence. Any later editorial response must follow the applicable policy.
