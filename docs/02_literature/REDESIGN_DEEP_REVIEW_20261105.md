# Predictor, planning and agentic R&D: related-work review

5 November 2026. **RESEARCH REVIEW; NO NEW EXPERIMENTS.**

## Decision supported by this review

Recommend a bounded diagnostic stage before another acquisition architecture.
The research opportunity is to determine **which chemical relationships make
delayed information useful for discovering actives before a deadline**, and
whether that value transfers across annotation groups and operating conditions.
An agentic plugin could make this capability usable from literature search through
an executable study plan and a replayable report. Neither contribution is established.

The [scientific proposal](../03_research/GOAL4R_METHOD_PREDICTOR_PROPOSAL_V1.md)
and [plugin proposal](../04_business/AGENTIC_RD_PLUGIN_PROPOSAL_V1.md) separate
the experimental question from the product workflow. A better predictor, a new
connector or an LLM orchestrator alone does not establish a new research method.

## Search and access record

This is a focused deep related-work investigation, not a systematic review or
an exhaustive novelty certificate. Search date: 5 November 2026. The root agent
and three read-only reviewers inspected primary publications, versioned arXiv
records, official code and existing project source reviews. Searches covered
few-shot molecular prediction, Tanimoto uncertainty, nonmyopic positive search,
asynchronous scheduling, learned acquisition, and tool-using scientific agents.
Citation following connected ENS to batch ENS/ANS, FS-Mol to ADKF and the
embedding benchmark, and chemical agents to literature-agent evaluation.

The Consensus Deep tool was attempted once after the owner explicitly requested
deep research. It returned a free-usage quota error; **no research run started**.
It was not retried and no service was purchased. alphaXiv discovery and raw
PDF-page queries, primary web sources and independent reviews supplied the
review instead. Generated discovery descriptions were leads, not evidence of
methods or results.

Access labels below mean: **TEXT** = targeted method/experiment/full-text sections
inspected, not every page; **PARTIAL** = primary indexed text or earlier project
review with a stated current access limit; **RECORD** = abstract/metadata only.
Publication and preprint versions are distinguished. No reading-room PDFs,
compound rows or copyrighted full texts are added to public Git. These source
IDs are local to this review and do not alter the frozen R01–R28 catalogue.

## Evidence matrix: predictors and uncertainty

| ID and primary source | Evidence and access | Consequence for CuraLoop |
| --- | --- | --- |
| S01: [FS-Mol, NeurIPS Datasets and Benchmarks 2021](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/file/8d3bba7425e7c98c50f52ca1b52d3735-Paper-round2.pdf) | TEXT: few-shot bioactivity tasks; single-task RF/kNN and cross-task learned baselines. Its support/query prediction benchmark is not an asynchronous campaign benchmark. | Keep RF/kNN as serious controls. Our custom component split and H(T) evaluation are adaptations, not the official benchmark protocol. |
| S02: [ADKF-IFT, v5, 17 February 2023 / ICLR 2023](https://arxiv.org/html/2205.02708v5) | TEXT: task-adapted GP with meta-learned features; Appendix D includes a single-task Tanimoto GP. Reported meta-test timing used an RTX 2080 Ti. | A Tanimoto GP is established, not our novelty. GPU timing does not establish CPU feasibility. Its fingerprint/descriptor controls differ from our binary Morgan1024 control. |
| S03: [FlowMO, v2, 14 October 2020](https://arxiv.org/abs/2010.01118v2) | RECORD plus [official code](https://github.com/henrymoss/FlowMO): molecular GP prediction and uncertainty on small data. | Motivation for a cheap kernel baseline, not evidence that our Bernoulli GP or campaign will improve. |
| S04: [Tanimoto Random Features, NeurIPS 2023 / v2](https://arxiv.org/html/2306.14809v2) | TEXT: scalable Tanimoto approximations, molecular regression and optimization. | Do not call an anchor-feature product kernel a direct Tanimoto kernel. At our small pool sizes, benchmark a direct kernel before introducing a new approximation. |
| S05: [Quantifying the Hardness of Bioactivity Prediction Tasks for Transfer Learning, JCIM 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11134514/) | PARTIAL: primary article text/metadata accessed; subsequent PMC requests returned a browser challenge. Studies task difficulty and transfer on FS-Mol. | Report assay/component heterogeneity. A pooled average can hide a method that only helps easy related tasks. No new complete full-text certification is claimed. |
| S06: [Evaluating uncertainty-based active learning, Journal of Cheminformatics 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10633997/) | PARTIAL: primary indexed method/results sections; direct open subsequently challenged. Regression/UQ and prediction-oriented AL differ from hit accumulation. | Calibration, uncertainty ranking and downstream utility are separate. Do not infer useful acquisition or joint chemical dependence from one reliability plot. |
| S07: [Benchmarking Pretrained Molecular Embedding Models, v5, 3 November 2026](https://arxiv.org/html/2508.06199v5) | TEXT: current version compares 28 models on 25 classification datasets; external scaffold-CV tests do not establish definite CheMeleon superiority over ECFP. Documents CLAMP benchmark-label overlap and retraining. | Audit training exposure before using a checkpoint. Retain fingerprint controls. AUROC gains do not establish H(T) gains. Version 4 reported a different model count and headline comparison; do not reuse its summary. |
| S08: [When Molecular Similarity Works: Property Cliffs Reveal Hidden Errors, v1, 17 May 2026](https://arxiv.org/html/2605.17265v1) | TEXT: regression diagnostics on quantum/physicochemical properties. CliffSplit uses ground-truth property differences to construct splits. | Similarity can conceal local failure. Diagnose this on development only; do not construct outcome-selected cliff splits in the reserved final panel. This is adjacent evidence, not a binary acquisition result. |

The [official FS-Mol release](https://github.com/microsoft/FS-Mol) provides
pretrained models using its original roles. Our rebuilt final panel includes
original-source training assays. **Inference:** importing those checkpoints could
contaminate our new holdout. Exact training-assay/compound provenance is required;
a different filename or new split does not remove exposure.

For classification, a GP prior with Bernoulli observations requires approximate
inference; Gaussian regression on Boolean values is a different model.
[Rasmussen and Williams, Chapter 3](https://gaussianprocess.org/gpml/chapters/RW3.pdf)
supplies the classification reference. Neither Laplace approximation nor a finite
posterior mixture certifies biological calibration.

## Evidence matrix: planning and closest algorithms

| ID and primary source | Established overlap and access | Design consequence |
| --- | --- | --- |
| S09: [Efficient Nonmyopic Active Search, ICML 2017](https://proceedings.mlr.press/v70/jiang17d.html) | RECORD refreshed; existing project PDF review retained. Whole-budget positive-discovery utility and an exploitation-tail approximation already exist. | Budget awareness and exploration/exploitation are not new. Match the binary cumulative-hit objective. |
| S10: [Efficient nonmyopic batch active search, NeurIPS 2018](https://proceedings.neurips.cc/paper/2018/file/a7aeed74714116f3b292a982238f83d2-Paper.pdf) | TEXT: optimal batch formulation, fictional-label approximations, parallelization cost and aggressive pruning. | Batch information and pruning already exist. Our old bounds cannot become novel merely through an event-time wrapper. |
| S11: [Azimi et al., NeurIPS 2011](https://proceedings.neurips.cc/paper_files/paper/2011/file/3a066bda8c96b9478bb0512f0a43028c-Paper.pdf) | TEXT: concurrent experiments, IID stochastic durations, query/time budgets, elapsed pending time and potentially empty dispatch; real-valued best-function objective. | Waiting and joint when/which scheduling are established. Preserve the difference between its optimization objective/CPE schedule and our multi-hit adaptations. |
| S12: [ANS, v1, 23 May 2024](https://arxiv.org/html/2405.15031v1) | TEXT: synthetic imitation of ENS and transfer to real search problems. Experiments start with one known positive and one negative; drug examples include BindingDB positives plus ZINC negatives. | A learned cheap search policy is not new. Keep uniform starts, including zero-hit starts; do not equate artificial negative pools or synthetic functions with measured inactive assays. |
| S13: [Nonmyopic Multiclass Active Search with Diminishing Returns, AISTATS 2023](https://arxiv.org/abs/2202.03593) | TEXT via raw PDF pages: diverse-class utility, including a substructure-grouped photoswitch example. | Diverse discovery is substantive but already studied. Adding a scaffold reward would change our endpoint and requires a separately approved scientific question. |
| S14: [Nonmyopic Multifidelity Active Search, ICML 2021](https://proceedings.mlr.press/v139/nguyen21f/nguyen21f.pdf) | TEXT reviewed by methods specialist: cheap/noisy feedback supports expensive positive discovery; an asynchronous extension is discussed. | Multi-fidelity plus pending work alone cannot be our contribution. Actual paired outcomes and missingness masks are needed. |
| S15: [Neural Nonmyopic BO in Dynamic Cost Settings, v1, 10 January 2026](https://arxiv.org/html/2601.06505v1) | TEXT: history-dependent costs and H-entropy lookahead for real-valued optimization. Protein experiment uses a learned semi-synthetic fluorescence oracle. | Neural long-horizon cost-aware planning is occupied. That experiment is not wet-lab evidence or an objective-matched multi-hit comparator. |
| S16: [Cost-Aware Diffusion Active Search, v1, 23 February 2026](https://arxiv.org/html/2602.19538v1) | TEXT: amortized lookahead, asynchronous multi-agent sensing, travel/sensing costs and recovery rewards on spatial grids. Timing compares diffusion on GPU with a CPU comparator. | Cost-aware asynchronous learned search is not new. Do not import its speed figure into a CPU-only molecular argument. |
| S17: [Interpretable Meta-Learning for Multi-Objective Chemical Search, v1, June 2026](https://arxiv.org/html/2606.20497v1) | TEXT, targeted sections: transferable lightweight surrogates and adaptive confidence for multiobjective chemical search. | A transferable surrogate plus an adaptive confidence term is insufficient novelty; endpoint and acquisition differences must be explicit. |
| S18: [MICRO, v1, September 2026](https://arxiv.org/html/2609.26025v1) | TEXT, targeted sections: cheap/strong feedback, confirmed-discovery utility and impact-clustered rollout for severe-error discovery. | Confirmation-aware rollout has precedent outside chemistry. A molecular application still needs a distinct principle and suitable paired data. |
| S19: [Queue-Scheduled Multi-Fidelity BO with Anomaly Resolution, 2026](https://www.mdpi.com/2504-4990/8/9/268) | PARTIAL: primary indexed full-text sections inspected; subsequent direct access returned 429. Includes queue overhead, verification/escalation and laboratory deployment; fixed triggering remains competitive in its ablation. | Queue integration and verification are not an untouched gap. Compare useful decisions with a simple fixed rule instead of assuming adaptation helps. |

A later multi-fidelity route remains possible, but is not selected here.
[MF-PCBA's official repository](https://github.com/davidbuterez/mf-pcba) is a
relevant source lead; primary indexed text describes defaults where confirmatory
values are missing. Untested/missing/censored outcomes cannot become verified
negatives. This dataset and real assay durations are **not cleared inputs** to
the proposed next experiment.

## Evidence matrix: agentic plugin and evaluation

| ID and primary source | Established overlap and access | Product/research consequence |
| --- | --- | --- |
| S20: [ChemCrow, Nature Machine Intelligence 2024](https://www.nature.com/articles/s42256-024-00832-8) | PARTIAL journal indexed text; TEXT of [early v2 preprint](https://arxiv.org/html/2304.05376v2). Tool-using chemical agents and expert evaluation already exist. Early preprint lists 13 tools; journal article lists 18. | Do not mix versions or claim the first chemistry agent. Evaluate scientific correctness and supported actions, rather than report fluency or tool count. |
| S21: [Coscientist, Nature 2023](https://www.nature.com/articles/s41586-023-06792-0) | PARTIAL: primary indexed article sections; direct page returned an identity-provider redirect. Combines search, documentation, computation and experimental automation. | A search-to-lab loop is established prior art. CuraLoop presently has retrospective simulation, not comparable physical execution. |
| S22: [PaperQA2, v2, 26 September 2024](https://arxiv.org/html/2409.13740v2) | TEXT via raw PDF pages: retrieval, synthesis, contradiction detection and human citation assessment. | Literature search and cited answers are not our novelty. Audit each scientific claim against the actual supporting passage; unanswered or conflicting evidence must survive report generation. |
| S23: [FIRE-Bench, ICML 2026](https://proceedings.mlr.press/v306/wang26d.html) | RECORD: evaluates rediscovery against documented findings rather than only generated-paper quality. Full paper was not inspected in this pass. | Motivation for independently checkable workflow tasks, not evidence that our agent works. Use fixture-based correctness and independent source audits. |

The [official MCP introduction](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)
describes a standard interface between AI applications and external tools/data.
**Inference:** MCP is a useful interoperability option for the plugin, not a new
scientific method, universal connector guarantee or current repository feature.

## Synthesis: what survives the challenge

**Supported:** strong fingerprint predictors deserve priority; chemical joint
uncertainty needs explicit evaluation; acquisition, model and compute effects
need separate controls. Existing work already covers learning to search,
nonmyopia, waiting, pruning, cost awareness and chemical agents.

**Plausible but unproven:** more faithful chemical dependence may make some
pending labels useful before a deadline. An evidence-linked plugin may reduce
the effort required to turn a literature question into a reproducible R&D study.
These require different experiments and different success criteria.

**Not supported:** a foundation model will fix the result; no WAIT means a bug;
adding RL establishes novelty; a connector establishes business demand; a
simulated timing improvement establishes laboratory savings.

The [Goal4 evidence](../03_research/GOAL4_RESULTS_V1.md) already rejects the
current screening-speed claim on its timing panel. It does not identify the
cause of modest discovery effects. The next experiment should discriminate
predictor weakness, dependence error and limited planning opportunity before
increasing horizon or training a new controller.

For [JCAMD](https://link.springer.com/journal/10822/aims-and-scope), appropriate
retrospective validation can support a novel computational strategy; experimental
validation is prioritized. **Our inference:** a useful new decision principle
with independent retrospective evidence is a more defensible route than adding
agent features to the current mixed result. Submission readiness remains
unestablished. The subscription route does not relax this scientific requirement.

## Remaining gaps and status

Novelty of the exact future algorithm: **NOT_ESTABLISHED**. Full replication of
the cited baselines: **NOT_RUN**. New predictor, plugin, fresh validation cohort
and business pilot: **NOT_RUN**. Complete automated Deep-tool synthesis:
**BLOCKED_BY_QUOTA**, with the manual primary-source review above completed.
No new labels, campaigns, remote jobs, paid actions or team-tool writes occurred.

Before implementation, pin exact baseline versions and finish any full-text/code
access needed for the selected comparator. Preserve negative evidence and ask
the owner before a new bounded experiment or material scope change.
