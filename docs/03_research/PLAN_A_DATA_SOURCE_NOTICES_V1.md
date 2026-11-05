# Plan A data provenance and notices

5 November 2026. This page covers the bounded research/audit use. Project
software licensing does not replace upstream dataset or annotation terms.
Raw assays, structures, labels and protein-annotation tables remain ignored.
The public evidence packet contains task identities/hashes and original
aggregate audits, with the source attribution below.

| Source | Identity and attribution | Notice / boundary |
| --- | --- | --- |
| FS-Mol | Stanley et al., *FS-Mol: A Few-Shot Learning Dataset of Molecules*, NeurIPS Datasets and Benchmarks2021; [paper](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/8d3bba7425e7c98c50f52ca1b52d3735-Abstract-round2.html); [Figshare16941100.v1](https://doi.org/10.6084/m9.figshare.16941100.v1); repository commit92aa95daba3f43863227e65be85a07b4a2ee754f | Repository datasets CC BY-SA3.0; Figshare CC BY4.0. Preserve both notices and the discrepancy. Software MIT does not cover these data. Local reproduction/adaptation supported; no uniform row-redistribution grant asserted. |
| ChEMBL | Original FS-Mol measurements: ChEMBL27. Current target/assay annotations: ChEMBL37 (2026-05-01), separate from the original release; [resource](https://www.ebi.ac.uk/chembl/) | CC BY-SA3.0 source notice. Current curation is not an exact reproduction of original ChEMBL27 target assignments. Raw activity endpoints were not queried. |
| UniProt | Reviewed protein-family exports, release2026_04; [resource](https://www.uniprot.org/), [license](https://www.uniprot.org/help/license) | CC BY4.0 data notice; keep source accessions/version and attribution. Family annotations are evidence for the declared split, not complete evolutionary-independence certification. |
| InterPro | Pinned release110.0, official [entry.list](https://ftp.ebi.ac.uk/pub/databases/interpro/releases/110.0/entry.list); [resource paper2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11701551/); [data license](https://interpro-documentation.readthedocs.io/en/latest/license.html) | InterPro data CC0. Entry types distinguish family/homologous-superfamily edges from domain/site/repeat annotations. Cached API and bulk listing agree for153checked types. |
| Prior exposed references | All three previously retrieved NCATS Tox21 source structure files and the existing HIV1200 resource | Used only for structure-exposure purge. Existing source notices/manifests remain applicable; this use does not assert a new data license. |

The derivative preparation changes are explicit: new annotation-connected role
blocks, hash-ranked finite reserves, canonical isomeric RDKit structures,
outcome-independent duplicate removal, exact prior/cross-role purge,
hash-ranked128–600structure cohorts and recomputed Morgan/scaffold features.
Source potency-derived phenotype labels are unchanged. These custom cohorts
are a new retrospective protocol, rather than the official FS-Mol leaderboard
split or evidence of sparse HTS, therapeutic efficacy or prospective laboratory
savings. Full raw/annotation redistribution remains a separate rights review.
