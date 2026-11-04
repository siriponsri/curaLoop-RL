# Related Papers | Prioritized, Rights-Aware Reading List

**Important:** This ZIP does **not** contain original publisher/article PDF binaries. Previous pack had 25 *references*, not 25 downloaded PDFs. This version preserves a 25-entry bibliography (`papers_manifest.json`) and provides a smaller prioritized set, status of source checks, and safe reading instructions. 'Open access' is not identical to permission to repackage without attribution, and data licensing is separate from article licensing.

## Must read before claiming RL/Digital Twin novelty

| Order | ID | Work | Why it matters | Reference verification in this audit |
|---|---|---|---|---|
| 1 | P01 | Chen et al., **Reinforced Active Learning for Large-Scale Virtual Screening with Learnable Policy Model** (GLARE), NeurIPS 2025. https://papers.neurips.cc/paper_files/paper/2025/hash/57ac7ccded0eaaec4ad6f05612289b79-Abstract-Conference.html | Direct competing RL selection policy for virtual screening | **SOURCE-CHECKED:** official NeurIPS metadata & abstract |
| 2 | P02 | Williams et al., **Query Matters: How Selection Strategies Influence Active Learning in Drug Discovery** (SimDMTA), J Chem Inf Model 2026, DOI 10.1021/acs.jcim.5c02504. https://pmc.ncbi.nlm.nih.gov/articles/PMC13014458/ | Closed-loop DMTA simulator, uncertainty vs greedy sampling | **SOURCE-CHECKED:** PMC/publisher metadata; article CC BY on PMC page; PDF still not downloaded |
| 3 | P03 | McDonald et al., **Bayesian Optimization over Multiple Experimental Fidelities Accelerates Automated Discovery of Drug Molecules**, ACS Cent Sci 2025, DOI 10.1021/acscentsci.4c01991. https://pmc.ncbi.nlm.nih.gov/articles/PMC11869128/ | Real multi-fidelity, cost-aware decision making | **SOURCE-CHECKED:** ACS, PubMed and PMC; do not equate synthetic fidelities with actual assays |
| 4 | P08 | Loeffler et al., **REINVENT 4: Modern AI-driven generative molecule design**, J Cheminform 2024, DOI 10.1186/s13321-024-00812-5. https://pmc.ncbi.nlm.nih.gov/articles/PMC10882833/ | Shows molecule generation/RL is mature prior art, not a necessary first milestone | **SOURCE-CHECKED:** publisher/PubMed |
| 5 | P11 | Tran-Nguyen & Rognan, **Benchmarking Data Sets from PubChem BioAssay Data: Current Scenario and Room for Improvement**, Int J Mol Sci 2020, DOI 10.3390/ijms21124380. https://pmc.ncbi.nlm.nih.gov/articles/PMC7352161/ | Data bias and virtual-screening benchmarking pitfalls | **SOURCE-CHECKED:** PMC page |
| 6 | P16 | Klähn et al., **Generative Active Learning for Molecular Design with REINVENT: Balancing Binding Affinity and Synthetic Accessibility**, J Chem Theory Comput 2026, DOI 10.1021/acs.jctc.6c01017. https://pmc.ncbi.nlm.nih.gov/articles/PMC13602925/ | Current approach combining GAL and tractability; scope alternative | **SOURCE-CHECKED:** ACS/PubMed/PMC |
| 7 | P23 | Tran-Nguyen et al., **LIT-PCBA: An Unbiased Data Set for Machine Learning and Virtual Screening**, J Chem Inf Model 2020, DOI 10.1021/acs.jcim.0c00155. https://pubmed.ncbi.nlm.nih.gov/32282202/ | Source dataset, assay-specific limitations | **SOURCE-CHECKED:** PubMed/publisher; full article may not be OA |

## Digital Twin framing (must read)

- National Academies, **Foundational Research Gaps and Future Directions for Digital Twins** (2024), DOI 10.17226/26894. https://www.ncbi.nlm.nih.gov/books/NBK605515/ ; https://www.nationalacademies.org/read/26894 . Defines coupling with a physical counterpart and dynamically updated bidirectional information. **SOURCE-CHECKED**; publication rights retain National Academies copyright; **not included as PDF**.
- NIST, **Definitions and State of the Art**: https://www.nist.gov/digital-twins/definitions-and-state-art . Emphasizes that definitions vary; status depends on operational update/validation. **SOURCE-CHECKED**.
- P05, **Drug Development Digital Twins for Drug Discovery, Testing and Repurposing**, https://pmc.ncbi.nlm.nih.gov/articles/PMC9351294/ — in catalog, metadata not independently verified this pass due to access/captcha. Read original before citing detailed claims.

## Secondary paper catalog: verification limits

The full 25-entry JSON includes literature across RL, active learning, digital twins, uncertainty, synthetic accessibility and virtual screening. In this audit **only the above seven source entries** were independently checked against primary or indexed records, while the remaining entries are **CATALOGUED-UNVERIFIED** for this round. Links may become unavailable; a listed PMCID is not proof of OA article reuse rights. Do not claim all 25 are 'verified articles' or 'included PDFs'.

## Access originals safely (for your own reading)

- Follow article/DOI/PMC URLs. Use the publisher's or PMC's official PDF link where available and keep article citation, license, date and provenance alongside the download.
- The optional `scripts/fetch_oa_papers.py` downloader can attempt OA PMC files **only in an internet-enabled workspace**, subject to manual retraction, license and article identity review. Its offline helper tests do not prove that source papers were downloaded. Keep locally downloaded PDFs out of a public Git repository by default.
- `papers/pdf/` is gitignored when implemented. If Work finds a closed-access article, record a `LINK_ONLY` status and move on; do not bypass access controls.

## What is NOT appropriate to claim

- That RL for virtual screening is unprecedented (GLARE exists).
- That a DMTA simulator is equivalent to a real dynamic Digital Twin (SimDMTA is simulation; digital twins require additional operational evidence).
- That all real assay prices, costs or measured delays were present in LIT-PCBA.
- That a personal project has been certified for drug, patient, laboratory or GMP workflows.
