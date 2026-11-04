# Evidence notes

Source-level extraction prepared from inspected primary material. These notes are original paraphrases. “Implication” is a project design decision, not a result claimed by the cited study. Read levels identify the inspected PDF versions. All 28 records now have a PDF, with one additional R05 supplement; journal-version comparison and numerical reproduction remain separate questions.

## R01: MoleculeNet: a benchmark for molecular machine learning

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1703.00564v3; journal/conference year is listed separately.

**Source contribution:** Standardized molecular datasets, features and evaluation choices.

**Limit:** A custom HIV replay is a derivative, not the official leaderboard split.

**Project implication:** Keep dataset/split hashes and distinguish campaign utility from prediction quality.

[Primary source](https://arxiv.org/abs/1703.00564). PDF status: PDF_VERIFIED.

## R02: Therapeutics Data Commons: Machine Learning Datasets and Tasks for Drug Discovery and Development

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 2102.09548v2; journal/conference year is listed separately.

**Source contribution:** Therapeutics task definitions, data access and evaluation resources.

**Limit:** Task collections have distinct endpoints and data terms.

**Project implication:** Use a task registry; retain assay semantics instead of merging heterogeneous labels.

[Primary source](https://arxiv.org/abs/2102.09548). PDF status: PDF_VERIFIED.

## R03: LIT-PCBA: An Unbiased Data Set for Machine Learning and Virtual Screening

**Evidence level:** FULL_TEXT_METHODS_RESULTS_AND_LIMITATIONS_INSPECTED. **Version:** HAL hal-03013622v1 author manuscript, 32 physical PDF pages including cover. Author correction: Célien Jacquemard.

**Source contribution:** Curated experimental active/inactive assay sets with artifact filtering and AVE train/validation splitting. The reported final set covers 15 target sets, with 7,844 unique actives and 407,381 unique inactives. These are paper totals, not local ingestion counts.

**Limit:** Targets are selected partly through baseline virtual-screening enrichment. AVE and near-chance nearest-neighbor validation do not guarantee that all later derivatives are free of identity or analog overlap. Original standardization uses named commercial tools; a replacement pipeline needs its own derivative identity.

**Project implication:** Preserve assay ID and functional phenotype, disclose target ascertainment, audit exact releases and group related endpoints. Separate EF at a fixed false-positive rate from EF at a ranked fraction or acquired-set size.

**Page evidence:** PDF pp. 7–12 (source/cleaning/metrics), 15 (assays and phenotypes), 19–24 (selection, AVE and counts), 25 (conclusions).

[Journal record](https://doi.org/10.1021/acs.jcim.0c00155); [inspected manuscript record](https://hal.science/hal-03013622v1). PDF status: PDF_VERIFIED. See [full-text amendment](FULL_TEXT_REVIEW_ADDENDUM.md).

## R04: Accelerating high-throughput virtual screening through molecular pool-based active learning

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 2012.07127v1; journal/conference year is listed separately.

**Source contribution:** Pool-based model-guided screening of docking libraries.

**Limit:** Docking-score retrieval is not wet-lab assay confirmation.

**Project implication:** Use a strong Greedy baseline and label computational versus assay endpoints.

[Primary source](https://arxiv.org/abs/2012.07127). PDF status: PDF_VERIFIED.

## R05: Traversing Chemical Space with Active Deep Learning: A Computational Framework for Low-data Drug Discovery

**Evidence level:** FULL_TEXT_METHODS_RESULTS_AND_LIMITATIONS_INSPECTED plus supplied supplement. **Version:** ChemRxiv v3, 23 February 2024, explicitly a preprint; 15 main PDF pages and seven supplementary pages. Associated journal full text was not inspected.

**Source contribution:** Three 100,000-compound screening pools, separate predictor audit sets, two model representations and six comparison arms. Starting sets contain a guaranteed known active. Similarity and frozen-model exploitation help isolate iterative learning from other effects. Campaign enrichment and predictive AUROC can favor different configurations.

**Limit:** Three selected tasks and ten initializations do not establish universal acquisition rankings. The batch sensitivity is ALDH1-specific and is not an equivalence result. Figure bands use SEM in the stated examples. The main text and supplement differ in describing VDR's phenotype; Eq. 8 minimizes its mutual-information score and needs exact-code interpretation before reproduction.

**Project implication:** Retain unconditional zero-hit starts in the primary study, add a separately labelled known-hit sensitivity, include no-retrain and similarity controls, and report model/update runtime. Do not silently equate the preprint's objective with maximum-BALD or transfer its headline gain to CuraLoop.

**Page evidence:** Main PDF pp. 4–6 (setup/arms/EF), 7–10 (results), 11–12 (initialization and methods); supplement pp. 1–2 (batch sensitivity and VDR caption), 5 (independent-test AUROC).

[Inspected preprint](https://doi.org/10.26434/chemrxiv-2023-wgl32-v3); [associated journal record](https://doi.org/10.1038/s43588-024-00697-2). PDF status: PDF_VERIFIED. See [version discrepancies](VERSION_DISCREPANCIES.md).

## R06: Sample efficient reinforcement learning with active learning for molecular design

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Public publisher/conference or institutional copy; see source metadata.

**Source contribution:** Active learning coupled to RL molecular generation for oracle efficiency.

**Limit:** Generation and expensive scoring differ from fixed-pool binary replay.

**Project implication:** Treat as related methodology, not a directly comparable result table.

[Primary source](https://doi.org/10.1039/D3SC04653B). PDF status: PDF_VERIFIED.

## R07: Reinforced Active Learning for Large-Scale Virtual Screening with Learnable Policy Model

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Public publisher/conference or institutional copy; see source metadata.

**Source contribution:** Learned RL policy for virtual-screening acquisition, with batch/runtime analyses.

**Limit:** Its task, model and budget protocol differ from the proposed study.

**Project implication:** Use as closest RL prior art and define a narrow operational comparison.

[Primary source](https://papers.neurips.cc/paper_files/paper/2025/hash/57ac7ccded0eaaec4ad6f05612289b79-Abstract-Conference.html). PDF status: PDF_VERIFIED.

## R08: ALF: An Active Learning Framework for Scientific Discovery

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 2609.31197v1; journal/conference year is listed separately.

**Source contribution:** Modular offline/online acquisition framework; inspected Appendix F notes synchronous assumptions.

**Limit:** A 2026 preprint and version-specific implementation, not a survey of all tools.

**Project implication:** Test an adapter and compare operational capabilities without broad novelty claims.

[Primary source](https://arxiv.org/abs/2609.31197). PDF status: PDF_VERIFIED.

## R09: PAL: Parallel active learning for machine-learned potentials

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 2412.00401v1; journal/conference year is listed separately.

**Source contribution:** Parallel active-learning modules coordinated through MPI.

**Limit:** Applications emphasize scientific model-building, including potentials.

**Project implication:** Acknowledge existing asynchronous orchestration and evaluate the smaller local workflow separately.

[Primary source](https://arxiv.org/abs/2412.00401). PDF status: PDF_VERIFIED.

## R10: Asynchronous Batch Bayesian Optimisation with Improved Local Penalisation

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Public publisher/conference or institutional copy; see source metadata.

**Source contribution:** Asynchronous BO using local penalization around busy evaluations.

**Limit:** Continuous optimization does not transfer to a binary pool without adaptation.

**Project implication:** Implement a faithful method or identify the finite-pool approximation explicitly.

[Primary source](https://proceedings.mlr.press/v97/alvi19a.html). PDF status: PDF_VERIFIED.

## R11: Batch Bayesian Optimization via Local Penalization

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1505.08052v4; journal/conference year is listed separately.

**Source contribution:** Batch acquisition via local penalization and a Lipschitz-based heuristic.

**Limit:** Assumptions and parameter choices matter for an adaptation.

**Project implication:** Separate within-batch redundancy control from learned strategy selection.

[Primary source](https://arxiv.org/abs/1505.08052). PDF status: PDF_VERIFIED.

## R12: Online Learning under Delayed Feedback

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1306.0686v2; journal/conference year is listed separately.

**Source contribution:** Theory and algorithms for online learning with delayed feedback.

**Limit:** Formal regret assumptions need not match a finite assay campaign.

**Project implication:** Motivate delay handling without borrowing an unproved regret guarantee.

[Primary source](https://arxiv.org/abs/1306.0686). PDF status: PDF_VERIFIED.

## R13: Parallelizing Exploration-Exploitation Tradeoffs in Gaussian Process Bandit Optimization

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Public publisher/conference or institutional copy; see source metadata.

**Source contribution:** GP-based batch/delayed-feedback selection with theoretical and empirical evaluation.

**Limit:** Gaussian-process assumptions differ from an uncalibrated classifier.

**Project implication:** Provide a meaningful parallel acquisition control and distinguish theory from replay evidence.

[Primary source](https://www.jmlr.org/papers/v15/desautels14a.html). PDF status: PDF_VERIFIED.

## R14: Multi-Fidelity Cost-Aware Bayesian Optimization

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 2211.02732v1; journal/conference year is listed separately.

**Source contribution:** Cost-aware optimization across fidelities and source biases.

**Limit:** Engineering examples are not proof of pharmaceutical assay fidelity.

**Project implication:** Keep multi-fidelity work optional until linked experimental measurements exist.

[Primary source](https://arxiv.org/abs/2211.02732). PDF status: PDF_VERIFIED.

## R15: Bayesian Optimization over Multiple Experimental Fidelities Accelerates Automated Discovery of Drug Molecules

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Public publisher/conference or institutional copy; see source metadata.

**Source contribution:** Multi-fidelity drug-discovery optimization with retrospective and prospective evidence.

**Limit:** Its docking, inhibition and dose-response outcomes are distinct measurements.

**Project implication:** Do not synthesize fidelity labels and call the result experimental validation.

[Primary source](https://doi.org/10.1021/acscentsci.4c01991). PDF status: PDF_VERIFIED.

## R16: BoTorch: A Framework for Efficient Monte-Carlo Bayesian Optimization

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1910.06403v3; journal/conference year is listed separately.

**Source contribution:** Monte-Carlo acquisition and optimization infrastructure.

**Limit:** A software framework alone does not establish assay utility.

**Project implication:** Prefer backend reuse where it preserves the information and scheduling contract.

[Primary source](https://arxiv.org/abs/1910.06403). PDF status: PDF_VERIFIED.

## R17: Analyzing Learned Molecular Representations for Property Prediction

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1904.01561v5; journal/conference year is listed separately.

**Source contribution:** Assessment of learned molecular representations for property prediction.

**Limit:** Prediction benchmarks do not automatically establish acquisition performance.

**Project implication:** Use matched representation/predictor ablations and retain fingerprint controls.

[Primary source](https://arxiv.org/abs/1904.01561). PDF status: PDF_VERIFIED.

## R18: A systematic study of key elements underlying molecular property prediction

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Public publisher/conference or institutional copy; see source metadata.

**Source contribution:** Systematic examination of dataset/model/metric/generalization choices.

**Limit:** Its evaluation settings must be matched to the intended chemical extrapolation.

**Project implication:** Audit label distributions and scaffold overlap; report both predictive and campaign endpoints.

[Primary source](https://doi.org/10.1038/s41467-023-41948-6). PDF status: PDF_VERIFIED.

## R19: Data Leakage and Redundancy in the LIT-PCBA Benchmark

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 2507.21404v2; journal/conference year is listed separately.

**Source contribution:** Preprint audit reporting leakage and redundancy in LIT-PCBA uses.

**Limit:** Findings depend on distributions, splits and similarity definitions.

**Project implication:** Reproduce a local identity/analog audit and preserve release-specific conclusions.

[Primary source](https://arxiv.org/abs/2507.21404). PDF status: PDF_VERIFIED.

## R20: Deep Reinforcement Learning at the Edge of the Statistical Precipice

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 2108.13264v4; journal/conference year is listed separately.

**Source contribution:** Interval estimates and aggregate evaluation methods for few-run RL.

**Limit:** The demonstrated benchmarks are not molecular assay tasks.

**Project implication:** Respect task hierarchy and report uncertainty instead of only mean performance.

[Primary source](https://arxiv.org/abs/2108.13264). PDF status: PDF_VERIFIED.

## R21: Deep Reinforcement Learning that Matters

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1709.06560v3; journal/conference year is listed separately.

**Source contribution:** Reproducibility and experimental-reporting concerns in deep RL.

**Limit:** Evidence concerns general RL evaluation rather than this chemical endpoint.

**Project implication:** Record hyperparameters, seeds and failures and compare under matched resources.

[Primary source](https://arxiv.org/abs/1709.06560). PDF status: PDF_VERIFIED.

## R22: Deep Bayesian Active Learning with Image Data

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Public publisher/conference or institutional copy; see source metadata.

**Source contribution:** Bayesian active learning with uncertainty-aware acquisition in image tasks.

**Limit:** Image-task gains do not validate molecular uncertainty.

**Project implication:** Label current margin sampling honestly and test uncertainty estimates on chemical data.

[Primary source](https://proceedings.mlr.press/v70/gal17a.html). PDF status: PDF_VERIFIED.

## R23: Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1612.01474v3; journal/conference year is listed separately.

**Source contribution:** Ensemble-based predictive uncertainty on classification/regression tasks.

**Limit:** Ensemble disagreement need not be calibrated on a new molecular task.

**Project implication:** Assess calibration and acquisition utility separately before making probabilistic claims.

[Primary source](https://arxiv.org/abs/1612.01474). PDF status: PDF_VERIFIED.

## R24: On Calibration of Modern Neural Networks

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1706.04599v2; journal/conference year is listed separately.

**Source contribution:** Calibration analysis and postprocessing for neural-network predictions.

**Limit:** The current surrogate is logistic regression, not the studied neural models.

**Project implication:** Avoid interpreting a predicted score as an established success probability.

[Primary source](https://arxiv.org/abs/1706.04599). PDF status: PDF_VERIFIED.

## R25: GuacaMol: Benchmarking Models for de Novo Molecular Design

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1811.09621v2; journal/conference year is listed separately.

**Source contribution:** Standardized evaluation for de novo molecular generation.

**Limit:** Generation is a different problem from selecting from a frozen pool.

**Project implication:** Keep generation outside the first study and use the source to define scope.

[Primary source](https://arxiv.org/abs/1811.09621). PDF status: PDF_VERIFIED.

## R26: BayBE: a Bayesian Back End for experimental planning in the low-to-no-data regime

**Evidence level:** FULL_TEXT_METHODS_RESULTS_AND_LIMITATIONS_INSPECTED. **Version:** RSC publisher article, Digital Discovery 2025, 4, 1991–2000; 11 PDF pages including issue cover. Manuscript software snapshot 0.12.2.

**Source contribution:** Practical BO software with chemical/custom categorical encodings, distributed asynchronous workflows, partial measurements and serialization. The paper evaluates campaign trajectories through backtesting and demonstrates encoding, related-task transfer and stopping examples.

**Limit:** Reaction-yield and housing examples do not validate binary multi-hit retrieval, biological controller transfer or customer savings for CuraLoop. A best-value EI stopping objective is not the same as maximizing additional Boolean hits. Current-release behavior requires a separately pinned integration test.

**Project implication:** Evaluate a local backend adapter before duplicating acquisition infrastructure. Preserve hidden-label and accounting boundaries. Differentiate the offer through scoped data-readiness, replay and reporting work; do not advertise generic asynchrony/backtesting as unique or borrow a percentage saving.

**Page evidence:** PDF pp. 3–4 (capabilities and backtesting), 5–6 (encoding examples), 7–8 (transfer and stopping), 9 (code/data snapshots).

[Primary source](https://doi.org/10.1039/D5DD00050E). PDF status: PDF_VERIFIED. See [full-text amendment](FULL_TEXT_REVIEW_ADDENDUM.md).

## R27: Query Matters: How Selection Strategies Influence Active Learning in Drug Discovery

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Public publisher/conference or institutional copy; see source metadata.

**Source contribution:** Query-strategy comparison in a BRD4 docking-based simulated DMTA workflow.

**Limit:** A focused chemical domain and proxy score limit direct biological extrapolation.

**Project implication:** Study when acquisition rankings change instead of declaring one universal winner.

[Primary source](https://doi.org/10.1021/acs.jcim.5c02504). PDF status: PDF_VERIFIED.

## R28: Deep Active Learning with Adaptive Acquisition

**Evidence level:** TARGETED_FULL_TEXT_INSPECTED. **Version:** Downloaded arXiv manuscript 1906.11471v1; journal/conference year is listed separately.

**Source contribution:** Reinforcement-trained adaptive acquisition in image datasets.

**Limit:** Adaptive acquisition predates CuraLoop and cross-domain transfer is unproven.

**Project implication:** Use as foundational prior art and compare adaptation against simpler fixed choices.

[Primary source](https://arxiv.org/abs/1906.11471). PDF status: PDF_VERIFIED.
