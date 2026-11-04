# Review method and evidence limits

## Scope

This is a targeted critical scoping review prepared on 4 November 2026. It supports research design and product positioning for CuraLoop-RL. It is not an exhaustive systematic review, a PRISMA-compliant search, a meta-analysis or a guarantee that every relevant paper has been found.

Searches covered molecular active learning, reinforced acquisition, low-data screening, asynchronous/parallel Bayesian optimization, delayed feedback, multi-fidelity costs, scientific software, molecular benchmark leakage and uncertainty in RL evaluation. Primary sources were prioritized: publisher/conference pages, arXiv manuscripts, institutional repositories, author datasets and official project documentation. Search results and secondary summaries were discovery aids; they did not substitute for inspecting available primary text.

## Search families and examples

| Family | Representative query used |
| --- | --- |
| Screening | `drug discovery active learning reinforcement learning acquisition function selection benchmark` |
| Operational constraints | `asynchronous active learning virtual screening delayed feedback assay scheduling reinforcement learning` |
| Closest methods | Exact-title lookups for GLARE, MolPAL, ALF, BayBE and Query Matters |
| Delayed optimization | `Online Learning under Delayed Feedback`; `Asynchronous Batch Bayesian Optimisation with Improved Local Penalisation` |
| Data integrity | `Data Leakage and Redundancy in the LIT-PCBA Benchmark`; molecular property prediction evaluation |
| Publication | Official JOSS and Journal of Cheminformatics submission guidance |

The search was iterative and citation-led. Search engines did not expose a stable total denominator, so no fabricated search-hit count or screening funnel is reported. The included catalogue is a purposeful set of 28 sources, not an estimate of the size of the literature.

## Inclusion and extraction

Include sources that inform at least one design decision: assay/task definition, acquisition, adaptive control, pending work, objective/cost, uncertainty, evaluation or reusable software. Include foundational nonchemical papers only when the transfer is explicitly methodological. Keep de novo generation distinct from fixed-pool screening. Identify preprints and manuscript versions separately from journal versions.

For each source record title, year, canonical URL, retrieved version, PDF status, pages, SHA256 where downloaded, evidence-read level, contribution, limitation and a project implication. The extraction matrix and notes contain original paraphrases, not copied abstracts. The review inspected opening sections and targeted methods/results/discussion passages in accessible full texts; it does not claim independent reproduction of their numerical results.

## Availability and rights

The version-2 reading room contains 28 identified main PDFs and one R05 supplement, totaling 29 copies and 731 physical PDF pages. The first release had 25 PDFs and three abstract/metadata-only records. The owner subsequently supplied R03 (HAL author manuscript), R05 (ChemRxiv v3), its matching-title supplement and R26 (publisher article). Their substantive methods, results and limitations were inspected, and 15 selected pages were visually checked. All supplied files were copied unchanged and hashed.

PDF availability does not imply that the latest journal version was read. R05 remains a reviewed preprint; the associated journal full text was not compared. Page-level evidence and unresolved source discrepancies are recorded in [the full-text amendment](FULL_TEXT_REVIEW_ADDENDUM.md) and [version register](VERSION_DISCREPANCIES.md). No paywall or access restriction was bypassed. PMC records for four sources were checked through the official current metadata route and reported no retraction; this is not a comprehensive retraction audit of all 28 sources.

Reading-room copies are outside the repository payload. The public repository includes citations, metadata and review text. Public availability does not automatically establish unrestricted redistribution or commercial reuse. The register's per-source rights field is deliberately conservative.

## Limitations and update rule

A single AI-assisted reviewer prepared the review. There was no independent dual screening or formal risk-of-bias scoring. Recent preprints can change, and repository capabilities can evolve after the cutoff. Before submission, refresh the closest prior-art search, check the exact versions used for comparisons and verify all factual statements against the cited primary pages or PDFs. Preserve amendments rather than replacing the search history silently.

## Amendment trace

Version 2 updates the register, BibTeX, extraction matrix, evidence notes, critical synthesis and their downstream protocol/manuscript/product/business references. It does not change the purposeful 28-study inclusion set, invent a systematic-search denominator or imply independent dual review. The additional supplement is attached to R05. The original source documents remain archived; the earlier package remains a separate deliverable.
