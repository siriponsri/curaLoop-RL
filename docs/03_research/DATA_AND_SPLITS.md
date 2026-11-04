# Data and split plan

## Current frozen resource

The existing HIV resource is a 1,200-row label-blind sample of the downloaded DeepChem HIV CSV. The manifest records 41,127 source rows, seven invalid SMILES removed and 41,120 valid unique rows under the existing canonicalization rules. Features are Morgan radius-2 fingerprints with 1,024 bits; Murcko scaffold IDs are available. The underlying historical semantics map CA/CM to active and CI to inactive. Initial labels are uniformly sampled without outcome stratification. Preserve all resource bytes and the original preparation script.

## Candidate sources

| Source | Intended use | Current package state |
| --- | --- | --- |
| Existing MoleculeNet HIV derivative | Regression and historical comparison | BUNDLED_UNCHANGED |
| LIT-PCBA assay tasks | Potential multi-target historical study | SOURCE_IDENTIFIED; NOT_INGESTED; file-level terms and audit required |
| TDC HTS collections | Potential alternative task collection | SOURCE_IDENTIFIED; task-level eligibility and terms required |
| Zenodo 13337372 | Reproduction material for R05 | SOURCE_IDENTIFIED; approximately 21.6 GB advertised; not downloaded |

The Zenodo record is not a lightweight dataset download. Inspect metadata and file contents selectively before committing to a 21.6 GB acquisition. Do not assume a paper's license covers every redistributed raw dataset. A manifest can link a source and describe processing even when raw redistribution has not been established.

## Ingestion procedure

Record canonical source URL, access date, version, raw SHA256, endpoint name, assay identifier, species/context where supplied, label mapping, feature code version and applicable terms. Validate schema before preprocessing. Count invalid structures, salts/fragments, canonical collisions, conflicting labels, duplicates within and across tasks and missing outcomes. Preserve original identifiers and an exclusion table. Never infer “inactive” from an absent measurement.

Use a versioned standardization policy. The initial historical policy did not strip salts, normalize tautomers or remove stereochemistry. A new policy may be appropriate but creates a new derivative. Report sensitivity to standardization when it changes collisions or labels. Subsampling must be specified before method evaluation; sampling by outcome prevalence changes the discovery problem and requires a separately labelled scenario.

## Leakage and redundancy

Use exact canonical keys and fingerprint-similarity summaries to audit overlap. Group closely related targets and shared endpoints. Inspect overlap with controller-development pools even if targets differ. R19 is an arXiv audit reporting problems in particular LIT-PCBA uses; it motivates a version-specific local check, not an assumption that all distributions or all previous studies are invalid. Preserve the audited release and thresholds so a reader can reproduce the same conclusion.

## Three distinct partitions

1. **Controller partition:** task/family-level development, validation and final-test roles. This determines transfer claims.
2. **Campaign partition:** initial revealed set and candidate pool within a task. This determines retrospective acquisition.
3. **Predictor audit partition:** train/test structures, preferably scaffold-disjoint where that answers the stated generalization question. The audit model and labels never enter the campaign policy.

Keep these IDs in separate manifests. A campaign pool can legitimately be acquired over time; a held-out predictor test set cannot be used for acquisition tuning. Do not call an unseen random seed an unseen target.

## Eligibility and power

Minimum positives, pool size, endpoint clarity and available capacity are feasibility criteria set during development. If tasks with scarce positives are excluded, disclose the resulting restricted population. Select the final number of tasks and repeats using pilot variance, runtime and the material effect the study can detect. Do not claim a universal minimum of 10 seeds or 15 targets establishes statistical power.

Store the final public registry under `research/manifests/`, with raw datasets outside Git unless redistribution is explicit. Keep row IDs, hashes and split assignments sufficient to reconstruct the exact pool. No new dataset download is implied by these templates.

## LIT-PCBA source-specific requirements from full-text inspection

The HAL manuscript reports 15 selected target sets and AVE splitting; these are candidate source tasks, not imported datasets. Target selection includes a baseline-enrichment requirement. Preserve an eligibility flow from source assays to the final registry and state the resulting population. Treat ESR1 agonist/antagonist endpoints as related biological units for role assignment. Do not treat each assay label or seed as an independent target family.

Retain PubChem AID, source identifiers, phenotype, measured endpoint/threshold and release version. For VDR, R03 and the R05 main text describe antagonism while the supplied R05 supplement calls its hits agonists. Verify the exact data and assay mapping before allowing the task into a frozen registry. An inconsistent description is not permission to invert Boolean outcomes.

The original source preparation uses commercial tools and specific filtering rules. Import a permitted prepared release and audit it, or declare a new preprocessing derivative. RDKit standardization alone does not reproduce all original Corina/Filter/Pipeline Pilot steps. Report original-paper totals separately from raw-file, cleaned-pool and task-eligible counts.

Both uniform and conditional-known-hit starts must have explicit distribution identities. The primary uniform regime may produce one-class sets. A conditional sensitivity draws one prior active and the remaining labels uniformly, with all initial labels excluded from new-hit counts; it answers a different question. Never let source prevalence or held-out predictor labels become a hidden selection feature.
