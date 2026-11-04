# Full-text review amendment — version 2

Prepared 4 November 2026. This amendment replaces the abstract-only treatment of R03, R05 and R26 in the first package. Three owner-supplied main PDFs and one supplement were inspected, with text extraction and selected visual checks. All page references below are physical PDF page numbers, including repository or issue covers. The inspected files are identified by SHA256 in [the manifest](literature_manifest.json).

## Executive assessment

The additional evidence strengthens the benchmark/software direction and raises the standard for any new algorithm claim. Low-data molecular active learning, operational backtesting and asynchronous experimental planning already have substantial support. CuraLoop needs a controlled finding about its stated assay population and operational conditions, rather than an assertion that an iterative loop or RL label is novel. Its current HIV result remains a single-task historical demonstration in which both learned tables fell back completely to Greedy.

The principal changes are concrete: add frozen-model and nearest-hit similarity controls; separate zero-hit starts from known-hit starts; define enrichment metrics without ambiguous names; disclose LIT-PCBA's ascertainment and release-specific overlap risks; resolve phenotype/version discrepancies before importing tasks; and test whether an existing acquisition backend can support the required replay contract. No new scientific experiments or customer validation were performed by this review.

## R03 — LIT-PCBA

### Inspected version and bibliographic correction

The supplied 32-page file is the HAL author manuscript, identifier `hal-03013622v1`, with a repository cover. The cover identifies Viet-Khoa Tran-Nguyen, **Célien Jacquemard** and Didier Rognan, and associates the manuscript with JCIM 2020, volume 60, pages 4263–4273, DOI `10.1021/acs.jcim.0c00155`. The first package's expansion of Jacquemard's given name was incorrect and has been corrected in the active register, BibTeX and manifests. The HAL submission date is an archive date; it is not the journal publication year.

### What the dataset construction supports

The paper documents a substantial attempt to make screening evaluation more realistic than decoy-only collections. It uses PubChem dose-response assays, retains experimentally labelled inactives, removes inconclusive results and screens for several classes of assay artifact. Source selection requires a suitable protein structure and a template ligand with a matching functional phenotype. The cleaning pipeline includes restrictions on elements, physicochemical properties and conversion/normalization success; active-specific filtering uses dose-response slope, frequency of hits and counterscreen evidence (PDF pp. 7–12, 15–18).

These features support using well-described historical assay labels. They do not imply that all retained compounds have independently validated therapeutic efficacy or that a binary activity label is a universally comparable measure of direct binding. An inhibitor, agonist and antagonist label has a different biological meaning. Each imported task must preserve its assay identity, outcome mapping and context.

### Ascertainment and residual bias

The construction is a selected benchmark, not a random sample of targets. The reported workflow starts from 149 dose-response assays, processes 21 suitable sets and retains 15 after requiring at least one of three baseline virtual-screening methods to achieve enrichment above two (PDF pp. 12–21). This can restrict the population to tasks with detectable signal for those methods. An observed advantage on that population cannot automatically be generalized to every target or to assays screened out during construction.

The AVE procedure uses ECFP4 distances and an approximately 3:1 training/validation allocation. Thirteen sets were handled without deleting compounds at that stage; ALDH1 and VDR were reduced by 25% to complete the search while preserving hit rate. The final paper reports 7,844 unique actives and 407,381 unique inactives across 15 target sets (PDF pp. 22–24). These are source-paper totals, not counts of a locally ingested task registry. No LIT-PCBA data files were installed in this documentation release.

Near-chance one-nearest-neighbor validation supports the authors' stated debiasing assessment under their representation and split. It is not a proof that every later release, alternate standardization, learned representation or task combination is free of leakage. R19's later audit should be addressed through exact-file and structure-overlap checks, rather than used to dismiss the original construction or ignored because the title says “unbiased.”

### Metrics and reproducibility consequences

The manuscript defines its `EF1%` at a constant **1% false-positive rate** (PDF p. 10). That is distinct from an enrichment factor among the top 1% of a ranked library and from cumulative acquisition enrichment. The revised protocol assigns each definition its own name and denominator. Source-paper enrichment numbers must not enter a CuraLoop comparison table without matching that definition.

The original preparation uses specific commercial tools, including Pipeline Pilot, Corina and Filter. A new RDKit-only standardization produces a documented derivative; it is not automatically a reproduction of that pipeline. For a solo, public-data-first project, importing a permitted prepared release and auditing its identity is a more tractable first scope than recreating all original 3D preparation and docking procedures.

### Required project actions

Register the exact release, assay ID and endpoint; preserve raw identifiers and exclusion reasons; audit duplicates and analog overlap before assigning task roles; group related target endpoints such as ESR1 agonism/antagonism; and disclose eligibility attrition. If the final study uses only a subset with enough positives, state that narrower population. Do not use the original 15-target count as a statistical power argument.

## R05 — low-data active deep learning and supplied supplement

### Version boundary

Although the uploaded filename uses the journal title, the PDF itself is **ChemRxiv v3, posted 23 February 2024**, DOI `10.26434/chemrxiv-2023-wgl32-v3`. Its cover explicitly identifies it as a preprint. The related journal DOI `10.1038/s43588-024-00697-2` is retained as an associated record. The journal full text was not supplied, inspected or compared, so conclusions in this review are attributed to the preprint. The seven-page supplement carries the matching preprint title; no independent journal-supplement identity is asserted.

### Experimental design and what it actually tests

The preprint studies PKM2, ALDH1 and VDR with 100,000-compound screening libraries and separate 20,000-compound predictor test sets. Its main setup starts with 64 known labels, acquires 64 compounds per cycle and screens to a stated 1,000-compound budget. Ten different initial sets are used. ECFP-based multilayer perceptrons and graph-convolutional models share an MLP component; uncertainty uses ten anchored models (PDF pp. 4–5, 11–12).

Initialization is consequential: each starting set begins with a randomly selected **known active**, with the remaining molecules sampled uniformly (PDF p. 11). It is therefore conditional on an initial hit. It does not establish performance for a campaign that begins with no active labels. CuraLoop's primary design retains uniform starts, including one-class starts; a separately labelled known-hit sensitivity study can help explain the effect of this conditioning. The label used to guarantee the start must be treated as prior knowledge and excluded from new-hit counts.

The six reported comparison arms are similarity to previously discovered hits, exploitation with retraining, exploration, mutual-information-based acquisition, exploitation without retraining and Random. The Methods describe five acquisition functions because the frozen-model arm changes retraining rather than the selection formula. The revised baseline catalogue keeps these two levels separate instead of treating six arms as six distinct mathematical objectives.

### Findings that matter for CuraLoop

In the tested settings, exploitative and mutual-information-based selection retrieve more assay actives than the alternatives, while fingerprint-based models often retrieve more hits than the graph models. Similarity search is a meaningful low-data control, especially early in a campaign. The study's predictive-discrimination results and acquisition-enrichment results do not always favor the same configuration (main PDF pp. 6–10; supplement p. 5). These findings motivate matched-predictor acquisition comparisons and separate reporting of predictor quality and campaign utility. They do not establish a universal method ranking across targets, initialization regimes or delayed experiments.

The supplement compares acquisition sizes 16, 32 and 64 **on ALDH1**, without finding a statistically significant performance difference in that tested range (supplement p. 1). This is a bounded sensitivity result, not evidence of equivalence across batch sizes, targets or compute budgets. Its shaded bands in several figures are standard errors across ten experiments. They must not be relabelled as standard deviations or confidence intervals, nor interpreted as uncertainty across an extensive biological target population.

### Discrepancies that require explicit resolution

The main preprint's Table 1 and target description call VDR antagonism, consistent with R03's assay table. Supplementary Figure 2 calls its VDR hits agonists (main PDF p. 4; supplement p. 2; R03 PDF p. 15). This is an inconsistency in descriptions, not proof that the underlying labels are inverted. The project must verify the exact assay/release and label mapping before import; it must not choose a biological direction from the filename or silently repair the source text.

The preprint's Eq. 8 explicitly uses an **argmin** for its mutual-information score (PDF p. 12). Standard maximum-information acquisition must not be assumed to be the identical method. A reproduction would need the exact code commit, score implementation and optimization direction checked against the reviewed version. This package records the issue without asserting that it is a typographical error or that a later journal version fixes it. A new implementation must specify its own uncertainty formula and direction unambiguously.

### Feasibility for a solo project

The authors report roughly 8,000 hours of compute on a server with Xeon CPUs and A100 GPUs (PDF p. 12). The manuscript does not make those hours a required budget for every smaller derivative study, and they should not be relabelled as a precise GPU-hour bill. CuraLoop should first use small development pools and inexpensive fingerprint controls, measure runtime and freeze a feasible final scope. Full reproduction of a deep-model sweep is optional and must have its own compute estimate.

## R26 — BayBE

### Inspected version and feature evidence

The supplied RSC PDF is the published article in Digital Discovery 2025, volume 4, pages 1991–2000, DOI `10.1039/D5DD00050E`, with an issue-cover page. It was published 6 May 2025 and identifies the manuscript's software snapshot as **0.12.2** (PDF pp. 2, 9). The article explicitly lists distributed asynchronous workflows, partial measurements, serialization, active learning, bandit optimization, chemical/custom encodings and transfer learning (PDF p. 3). These are documented capabilities of that source, not a fresh certification of every current release.

### Evidence and its limits

BayBE evaluates complete optimization trajectories through historical backtesting rather than relying only on predictive scores. Its examples include chemical reaction-condition optimization and a nonchemical custom-encoding example, followed by related-task transfer and a stopping rule. For example, the reaction encoding comparison reaches a selected yield threshold earlier with chemical descriptors than with one-hot encoding (PDF pp. 4–6). This shows why representation choices can have practical effects in those cases; it does not supply a validated savings percentage for CuraLoop, for binary hit accumulation or for a specific customer's laboratory.

The transfer example constructs related tasks from different reaction temperatures and models inter-task covariance. It is not evidence that a synthetic-trained controller transfers to unrelated biological endpoints. The stopping example removes reaction outcomes above a chosen yield and uses a specified expected-improvement criterion (PDF pp. 7–8). Its thresholds cannot be copied directly to a Boolean assay task whose goal is to retrieve multiple actives. Best-value improvement can saturate after one positive, even though hit accumulation remains valuable.

These demonstrations are useful methodological precedents, not head-to-head evaluations against the proposed CuraLoop study. Differences in endpoint, objective, representation and data availability need to be controlled or explicitly labelled in any adaptation. A paper snapshot should be used for a reproduction; a current release may be used for an integration if its version, dependencies and tested behavior are separately recorded.

### Product and research consequences

Backtesting, asynchronous operation, serialization and a generic optimization loop cannot be CuraLoop's unique selling claims. Before building more acquisition infrastructure, run a small local adapter feasibility task using only public features and delivered labels. Evaluate whether the backend can preserve capacity, cost commitments, pending privacy and immutable run provenance. A useful integration might strengthen the pilot and provide a credible comparator. It remains planned until code exists and passes the information-boundary checks.

The commercial offer should sell a bounded service that a buyer can assess: data-readiness work, a matched replay design, a report with assumptions and uncertainty, and an operator handover. Measure analyst effort, reproducibility and decision relevance. Do not transfer another paper's “50%” example to pricing, customer ROI or a promised discovery rate. If an existing framework already solves the buyer's entire problem, integration/support or a narrower report may be the appropriate offer.

## Resulting decisions and remaining work

| Evidence issue | Revised decision | Release artifact |
| --- | --- | --- |
| Former abstract-only access | Inspect and identify supplied versions | Manifest, evidence notes, reference register |
| LIT-PCBA ascertainment and AVE scope | Audit exact releases; restrict population claims | Data/split plan and task schema |
| Ambiguous enrichment names | Separate FPR, ranked-fraction and acquired-set metrics | Metric/initialization concordance |
| Known-active starts in R05 | Retain zero-hit starts; add labelled sensitivity | Protocol and experiment matrix |
| Retraining and similarity effects | Add explicit controls and runtime accounting | Baseline specification |
| VDR description and MI direction | Record unresolved provenance questions before reproduction | Version-discrepancy register |
| BayBE workflow overlap | Test integration first; narrow sales claims | Competition and pilot documents |
| No new study outcomes | Preserve historical evidence and NOT_RUN status | Manuscript, claim ledger and audit |

This review does not establish publication acceptance, algorithmic superiority or commercial demand. It supplies a more defensible research specification and a bounded pilot proposition. The next engineering slice remains data identity, scheduler validation and matched baselines, followed by a measured development pilot and a final protocol freeze.
