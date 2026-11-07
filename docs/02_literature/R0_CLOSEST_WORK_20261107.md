# R0 closest-work and source ledger

Reviewed: 7 November 2026. Purpose: discriminate a contribution/data direction,
not certify exhaustive novelty. Bounded discovery used alphaXiv and SciSpace as
leads, web search, primary publisher/author pages and a Hugging Face dataset card.
Duplicate records are not independent studies. Primary links below support
statements; inaccessible files do not count as inspected. Repository evidence
is linked separately. No benchmark task/gold files or new activity rows loaded.

## Claim/evidence matrix

| ID | Primary source and inspected scope | Supported statement | Consequence / limit |
| --- | --- | --- | --- |
| S01 | Javdani et al., [Near Optimal Bayesian Active Learning for Decision Making](https://proceedings.mlr.press/v33/javdani14.html), AISTATS 2014; publisher abstract | Decision-region resolution is an established alternative to generic uncertainty reduction | Adaptive evidence purchase alone is not novel; no theorem was transferred to the proposed problem |
| S02 | Nguyen et al., [Nonmyopic Multifidelity Active Search](https://proceedings.mlr.press/v139/nguyen21f.html), ICML 2021; publisher abstract and PDF excerpts | Active search can use a cheaper surrogate alongside a faithful expensive oracle | A cheap/expensive feedback loop is occupied territory; our missing records cannot become faithful oracle observations |
| S03 | Papadatos et al., [Activity, assay and target data curation and quality in the ChEMBL database](https://link.springer.com/article/10.1007/s10822-015-9860-5), JCAMD 2015; abstract and curation sections | ChEMBL standardizes measurements and flags ambiguity, duplicates and possible errors | Normalization and flagging are prior art; flags are not automatic truth |
| S04 | Smit et al., [Integrating artificial intelligence and manual curation to enhance bioassay annotations in ChEMBL](https://link.springer.com/article/10.1186/s13321-026-01165-x), 12 February 2026; updated abstract, scientific contribution and schema sections | AI/manual annotation extracts assay methods and categories; assay parameters may be shared across activities | Assay-context extraction is already a contribution elsewhere; measure downstream decision value instead |
| S05 | [Correction to S04](https://doi.org/10.1186/s13321-026-01181-x), 27 March 2026; notice identity linked on publisher page | Original article has a published correction | Correction body inaccessible through browsing; do not assume its contents; qualification must reconcile it |
| S06 | Fan and Barzilay, [AssayMatch](https://arxiv.org/abs/2511.16087), v1, 2025 preprint; abstract | Assay-description embeddings are trained to select compatible training assays for an unlabeled test set | Assay-specific training-data selection is occupied territory; no full reproduction reviewed |
| S07 | [PCAM](https://link.springer.com/article/10.1186/s13321-026-01316-0), 2026; publisher abstract and author repository README | Assay-aware prediction/uncertainty is evaluated with random, scaffold and assay-held-out splits on a GPCR benchmark | A model with assay text is not novel by itself; target counts are not independent family counts; model-layer comparator only |
| S08 | [Papyrus](https://link.springer.com/article/10.1186/s13321-022-00672-x), published 6 January 2023; construction sections and [version 05.5 file metadata](https://zenodo.org/records/7019874) | Curated multi-source bioactivity data; Papyrus++ filters selected discordant potency measurements | Useful prediction reference; filtering could erase the natural disagreements needed here (our inference). Original assay/document traceability and version rights require audit |
| S09 | [Jev for Scientific Decisions](https://arxiv.org/abs/2609.24965), v5, revised 2 November 2026, preprint; targeted PDF passages on setup, semantics and limitations | Prepared semantic choices feed trusted computations and separately scored scientific claims | Semantics plus trusted code is not novel. Curated exposed cases are not a retrieval/policy benchmark; paper examples reviewed here are development exposure |
| S10 | [Held-out evidence resolves follow-up measurement decisions in biological screens](https://arxiv.org/abs/2607.27651), v3, revised 1 September 2026, preprint; targeted PDF passages on qualification and limitations | Follow-up rules are qualified against held-out measured outcomes, including abstention/fallback; source reports no selective measurement-saving rule authorized | Useful counterevidence against presumed savings; not a verified downloadable dataset, rights grant or independent validation of our proposal |
| S11 | [ChEMBL official downloads](https://chembl.gitbook.io/chembl-interface-documentation/downloads) and [general FAQ](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/general-questions); metadata | Versioned releases and distinct assay/document identifiers are documented; ChEMBL 35 has a listed release DOI | Propose one fixed release, not an unversioned API mixture. Release archive/README and DOI resolution failed through browsing; no checksum/schema pin established |
| S12 | [ChEMBL licensing post](https://chembl.github.io/chembl-licensing/), historical official notice | States CC Attribution-ShareAlike 3.0 for database content | Historical notice is a starting point; selected release, upstream article access and intended redistribution/model use still require an itemized terms assessment |
| S13 | [LAB-Bench card](https://huggingface.co/datasets/futurehouse/lab-bench/blob/main/README.md) via Hugging Face card-only read and [paper](https://arxiv.org/abs/2407.10362) identity from card | Card lists LitQA2/DbQA, CC BY-SA 4.0, public questions under a train split and a retained private test fraction | Public split name does not make tasks safe for development then final reuse. Card only inspected; paper full text and question/gold files NOT_READ |
| S14 | [JCAMD aims/scope](https://link.springer.com/journal/10822/aims-and-scope), current primary page | Prioritizes experimental validation; suitable retrospective validation can support novel computational strategies | Proposed molecular decision method is a plausible scope fit, not a readiness or acceptance judgment |

## Retained repository counterevidence

- [4R1 results](../03_research/GOAL4R1_RESULTS_V1.md): repaired prediction improved
  some development results, while incremental planning was small/mixed across
  only four connected components. Same-predictor comparisons remain essential.
- [A3 qualification](../03_research/GOAL4R2A3_QUALIFICATION_V1.md) and
  [B closeout decision](../06_execution/B_POTENTIAL_DECISION_LRBC_20261106.md):
  the selected primary canary had zero complete tuples; intake stopped on an
  HTTP 504. Unrequested pairs remain unknown. A stopped service is not an oracle.
- [FS-Mol card](../03_research/FSMOL_DATASET_CARD_V2.md): original reserved
  final outcomes and label-free identity protections remain unchanged.
- Existing cached-metadata workflow ties on authored cases establish neither
  model efficacy nor broad agent superiority. Current question text is a label;
  connectors cannot be assumed to implement an evaluated research agent.

## Access/exposure register

Inspected material consists of source metadata, abstracts, targeted method/PDF
passages, paper figures/examples returned with those passages, official docs,
repository READMEs and the LAB-Bench card. These are now review exposure, not a
fresh held-out source collection. Public paper examples can contain outcomes;
they were not loaded as project assay-row cohorts, and cannot be silently reused
as fresh evaluation examples. No claim is made that all model pretraining is
uncontaminated. No ChEMBL/Papyrus archive, activity API, LAB-Bench task files,
old protected final labels or stopped PubChem request was accessed.

Tool access failures: ChEMBL release directory/README, direct release DOI,
acknowledgements endpoint, Zenodo API metadata, and correction DOI body were
inaccessible through browsing. The Papyrus version page itself was readable.
These failures do not authorize a service retry, mirror or download and are
not evidence that the underlying datasets are unavailable to the owner.

## Synthesis and next discriminating test

Evidence gathering, assay curation, assay-aware modeling and semantic provenance
already exist separately. A shared-context joint decision rule is a candidate
gap, not a proven gap. First test for natural, adjudicable uncertainty and a
nontrivial distinction from existing decision-region policies. Then compare
against resolving everything cheaply upfront. If that baseline removes the
advantage, stop this adaptive-evidence thesis rather than raising artificial
verification costs. See [the decision brief](../03_research/R0_CONTRIBUTION_DATA_PROPOSAL_20261107.md).

Status: READY_FOR_REVIEW. Independent review NOT_RUN.
