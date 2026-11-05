# CuraLoop FS-Mol cohort: revision A dataset card

5 November 2026. **Feature preparation and scoped readiness PASS.**
No Goal 4 campaign or final-family evaluation is established by this card.

## Intended research use and source

Retrospective finite-pool molecular discovery with simulated assay durations,
unit costs and deadlines. Evaluate conditional event-time planning on development
and validation tasks; reserve final-family outcomes for a separately authorized
study. FS-Mol's potency-derived binary labels retain their source meaning. They
are not prospective experimental discoveries, sparse HTS hit calls, therapeutic
efficacy or clinical evidence. No measured laboratory latency/cost is available.

Source: [Stanley et al., FS-Mol, NeurIPS Datasets and Benchmarks 2021](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/8d3bba7425e7c98c50f52ca1b52d3735-Abstract-round2.html).
Pinned upstream commit: `92aa95daba3f43863227e65be85a07b4a2ee754f`.
Archive SHA256: `528a9c4e8d74c4287acda79536eecbf91418d6d0ac2c55918b270d78c2333ebc`.
The exact default release has 5,135 tasks; the paper text's 5,120 discrepancy is
retained. The 21,930 extra physical training files are outside this population.
Original train/valid/test roles remain provenance, not our evaluation roles.

## Population, grouping and attrition

Registry v3 accepts 2,884 of 5,135 source tasks, excluding 2,251 with its complete
metadata-only reason ledger. Direct confidence-9 single-protein target annotations
use ChEMBL37, reviewed UniProt2026_04 and pinned InterPro110.0. These current
annotations do not certify exact identity with source ChEMBL27 curation.

Shared broad-family ancestry and typed exported family/homologous-superfamily
identities are merged transitively. The result is 139 annotation-connected
components assigned 40/34/65 to development/validation/final. These are not 139
independently certified evolutionary families. The largest component joins
87 broad names and 1,845 assays; its complete component stays in development.
Previously exposed target/component anchors are quarantined to development.
The guarantee covers exported identities, not complete phylogeny or ontology.

The first frozen reserve failed at 2/2/7 groups and remains intact. Owner-approved
revision A expands to all already assigned components, with the same first eight
hash-ranked assays per component, no outcome-driven replacements and unchanged
128-structure minimum. Every one of 457 fixed assays contributes complete
pre-deduplication collision support before eligibility and selection.

| Selected role | Annotation-connected groups | Assays | Structure rows | Unique structures |
| --- | ---: | ---: | ---: | ---: |
| Development | 4 | 6 | 1,285 | 1,107 |
| Validation | 2 | 2 | 330 | 330 |
| Final, outcomes reserved | 12 | 16 | 5,015 | 4,416 |

Development groups: globin; MIT/TFE; tumor necrosis factor; the quarantined
87-name connected component. Validation: dihydrofolate reductase; isocitrate/
isopropylmalate dehydrogenases. Final component labels: TIM17/TIM22/TIM23;
pyruvate kinase; transthyretin; inositol monophosphatase; the connected transporter
component; GPCR2; sirtuin/TPP; bZIP; cytidine/deoxycytidylate deaminase;
carnitine/choline acetyltransferase; BCL-2; dUTPase. Composite labels denote
conservative connected groups, not biological equivalence of their members.
Exact IDs, complete names, source roles and hashes are in the
[selected-task manifest](../evidence/plan-a-20261105-v1/feature-cohort-v2-result.json).

## Structure processing and residual dependence

RDKit 2026.09.1 canonical isomeric SMILES retain salts, charges, tautomers and
isotopes. Remove every repeated within-assay canonical structure without reading
its label. Purge exact matches against all previously acquired NCATS structures
and HIV1200, and purge all cross-role exact canonical matches from every role
using the complete fixed reserve. Select at most two eligible assays per group,
128–600 structures per assay by the original outcome-independent hash rank.
Recompute nonchiral Morgan radius2/1024-bit features and nonempty Murcko scaffolds.

Exact canonical overlap is zero across roles and prior exposure references.
Development/final still share 63 scaffolds, and four directed queries each way
have nearest Tanimoto at least 0.8. Prior-reference nonchiral fingerprint similarity
can reach 1.0 despite different isomeric canonical identities. There is **no
chemical OOD claim**. Within-role overlaps remain, and unique counts differ from
assay rows. Average assays/seeds within groups and weight groups equally;
assays and seeds do not create independent biological units. Two validation
groups give weak evidence for generalization to a wider family population.

## Label access, rights and reproducibility

Trusted row parsing physically decoded source rows but positively projected
only SMILES/Assay_ID; no semantic compound-outcome use, prevalence export or
final-label preparation occurred. All 457 attempts and structure-based exclusion
counts are retained. Later label loading needs a separately frozen role-checked
private evaluator. Degenerate labels cannot trigger replacement.

Scoped nonpublic research processing passed the
[rights review](../evidence/plan-a-20261105-v1/source-rights-local-use-v1.json).
Preserve the dataset CC BY-SA 3.0 notice, Figshare CC BY 4.0 discrepancy, upstream
ChEMBL provenance and protein-annotation notices. Raw rows, structures, outcome
vectors and derived row files remain ignored; public evidence contains permitted
IDs/hashes and original aggregates. Software MIT does not override dataset terms.
See [source notices](PLAN_A_DATA_SOURCE_NOTICES_V1.md).

Frozen configuration SHA256:
`e07917dd3af9e76ca9f4f8d2b784deaf2af61f4eabfc9156deff7d8f42446fe4`.
Ignored full manifest SHA256:
`66ddda3ae98fe317f8c26e0fe6443ac40f0522a84b7e8d683eeec9012a726006`.
[Freeze](../evidence/plan-a-20261105-v1/feature-preparation-freeze-v2.json),
[chemical audit](../evidence/plan-a-20261105-v1/chemical-audit-v2.json) and
[artifact readback](../evidence/plan-a-20261105-v1/revision-a-feature-readback-v2.json)
identify the inputs and resulting artifacts. Fifteen metadata/constructed checks
passed before freezing. Preparation used 120.484375 CPU seconds/210.688 wall seconds,
one low-priority CPU, one BLAS thread and a 1 GiB memory limit; 7,321,889 output bytes
were recorded before the final receipt write. No new download or remote run.

## Claims remaining untested

Predictor calibration, discovery advantage, computational advantage, learned RL
behavior, novelty, operational realism and journal readiness are not established.
This is a custom, restricted family-component split of FS-Mol; its campaign
metrics are not directly comparable to the original few-shot benchmark scores.
