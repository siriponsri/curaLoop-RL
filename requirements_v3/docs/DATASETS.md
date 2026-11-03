# Dataset plan, curation and license controls

## No proprietary data required

The starter must run with a committed tiny synthetic fixture for **software testing only**. The real benchmark is downloaded by the user or agent from authoritative primary sources with a recorded license and version. Do not commit huge original archives or mirror datasets without verifying redistribution rights.

## Primary: LIT-PCBA

Official current-looking pages (contents may differ by release):

- https://drugdesign.unistra.fr/LIT-PCBA/index.htm - lists 15 target sets; examples include `ESR_antago` (102 actives / 4,948 inactives on this page).
- https://drugdesign.unistra.fr/LIT-PCBA/ - a different index version with different per-target counts. **Resolve this release discrepancy before making a benchmark claim.**
- Primary dataset publication: Tran-Nguyen, Jacquemard & Rognan, *LIT-PCBA: An Unbiased Data Set for Machine Learning and Virtual Screening* (2020), DOI https://doi.org/10.1021/acs.jcim.0c00155.

**Why choose:** experimental active/inactive labels, reasonably small target subset for early testing, multiple targets for later evaluation, more realistic than arbitrary property-matched decoys. **Limitations:** target-dependent class prevalence, historical retrospective labels, assay artifacts, duplicate scaffolds and a potentially large full archive. First seek only selected target data.

**Never infer:** a molecule active in one target/assay implies clinical efficacy; the labels do not establish every type of activity for a molecule.

## Secondary

**TDC:** https://tdcommons.ai/ ; https://tdcommons.ai/benchmark/admet_group/overview/ . Has curated therapeutic datasets and scaffold-split benchmarks. Check *per-dataset* usage rights (software MIT license does not grant rights to each dataset). Do not combine unrelated assay endpoints as if a common repeated-measures experiment.

**OGB molecular tasks:** https://ogb.stanford.edu/docs/graphprop/ . `ogbg-molhiv` (41,127 graphs) and `ogbg-molpcba` (437,929 graphs, many tasks). Verify permissions, missing-label behavior and scaffold splits before including.

**PubChem BioAssay:** https://pubchem.ncbi.nlm.nih.gov/ ; useful to source traceable assay definitions and data IDs, not an automatic guarantee of compatible measurements.

**OpenADMET:** https://www.openadmet.org/datasetsmodels/ ; useful for future pharmacology-related decision support, but not a drop-in source of paired low/high fidelity outcomes for LIT-PCBA molecules.

## Required provenance table

For each dataset target include:

| Field | Rule |
|---|---|
| `dataset_name` | Stable human-readable name |
| `source_uri` | Primary source URL, not unofficial mirror when avoidable |
| `release_id` | Release/date/version explicitly obtained |
| `retrieved_on` | UTC date of original download |
| `file_sha256` | Checksums of raw files |
| `rights_statement` | Dataset-specific copyright/terms/redistribution status |
| `assay_id` | Exact assay identifier such as PubChem AID |
| `endpoint_definition` | What active/inactive means and units/thresholds |
| `preprocessing_sha256` | Reproducible script version / code SHA |
| `removed_invalid` | Count and reason |
| `removed_duplicate` | Count and conflict policy |
| `label_balance` | Count per task and partition |
| `split_manifest` | Exact split IDs and seed |
| `label_provenance` | Real experimental, inferred proxy or synthetic (must differ) |

## Preprocessing

1. Parse source types (e.g. SDF/CSV) with a dedicated adapter; fail clearly when fields are missing.
2. RDKit validation, molecular standardization policies documented: salts, stereochemistry, tautomer rules, canonical SMILES.
3. Deduplicate by stable structure and assay ID; contradictory recorded activity must be counted and handled transparently rather than resolved by hiding the conflict.
4. Map identifiers to an immutable candidate ID; attach the original record ID for traceability.
5. Fingerprints: RDKit Morgan radius 2 and 2048 bits or a preregistered alternative.
6. Partition policies by objective: prospective-like campaign candidate pool vs scaffold-disjoint prediction benchmark vs disjoint-target policy-transfer benchmark. These are not interchangeable.
7. Store the source count summary and all filtering decisions; enforce expected bounds in CI fixture tests.

## Release caution

LIT-PCBA website versions may show inconsistent counts. Fetch the exact dataset snapshot, do not silently switch between mirrors, and treat cross-release comparisons as different experiments unless normalized and reconciled. Store metadata, not copyrighted large raw data, in Git by default.
