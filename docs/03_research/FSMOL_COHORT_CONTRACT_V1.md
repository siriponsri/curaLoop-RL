# FS-Mol feature-only cohort contract

5 November 2026. **FROZEN AND EXECUTED; FAIL_FAMILY_QUOTAS.**
The first attempt produced2development/2validation/7finalgroups. Preserve this
contract/config/output; [revision options](../06_execution/GOAL3_COHORT_REVISION_OPTIONS_20261105.md)
are proposed, not silently applied.
The owner chose biological-family separation with exact chemical overlap
removal, reporting scaffolds and near analogues as limitations. This does not
claim chemical out-of-distribution evaluation.

## Units, provenance and family boundary

Use only the pinned 5,135-task source manifest. Keep source train/valid/test as
provenance, not evaluation authority. The inspected paper's text total5,120
conflicts with its role counts and released5,135; the exact pinned release is
the operational population. The extra21,930 physical training files are unused.
FS-Mol source potency-derived binary positives are preserved, not renamed HTS
hits, binding confirmation or clinical efficacy.

Registry v3 maps direct confidence9, single-protein ChEMBL37 annotations to
reviewed UniProt2026_04 protein families and pinned InterPro110.0 entry types.
It accepts2,884assays and excludes2,251 of the5,135source tasks. Nine assays
with unresolved bifunctional scope are excluded. Literal broad-family ancestry
and shared typed family/homologous-superfamily annotations define conservative
connected components; generic domain/site/repeat identities do not create edges.

There are139components:40development,34validation,65final candidates. The largest
component contains87broad names/1,845assays and is development-only. Do not call
these139independent evolutionary families. The guarantee concerns shared
exported InterPro identities, rather than complete ontology, phylogeny or
statistical independence. The selected held-out biological groups and attrition
must be listed individually. Role/rank hashes are fixed without assay outcomes.
Exposed p53/PPARG/AHR and schema-canary PPI-component anchors quarantine their
complete connected groups to development, including conservative generic
InterPro-overlap exposure screening. CHEMBL1614128 is permanently nonfinal.

## Frozen feature eligibility and finite reserves

The [configuration](../../research/configs/goal3_feature_preparation_v1.json)
targets4development,2validation and12final groups, with1–2assays per group.
Inspect at most8,6and32families respectively, in existing family-rank order;
within each inspect at most the first8assays in existing assay-rank order.
Parse every fixed reserve pool before cross-role purge, so later eligibility
cannot silently change which collision pool was used. Collision support
includes ALL valid projected canonical structures, including
within-assay duplicates and feature-ineligible assays. Abort if any reserved
pool cannot be projected completely under its safety limits.
Select first eligible assays/families, retaining every failed attempt. No labels, class balance,
model-fit behavior or method results influence admission. A quota failure is
a reported gate failure, not permission to reseed or add unranked replacements.

Trusted preparation reads row-oriented bytes but projects only SMILES and
Assay_ID. Outcomes and provided features never leave the row parser. Exceptions
emit task identifiers and fixed reason codes, without raw row values or parsing
tracebacks. Enforce line, expanded/member/total byte, row, wall, memory and output
caps before expensive work. Unsafe identity/integrity violations abort the run.

Use RDKit2026.09.1 canonical isomeric SMILES with no salt/charge/tautomer edits.
Remove all rows belonging to repeated within-assay canonical structures without
reading/comparing their labels. Remove exact matches against all previously
retrieved NCATS source structures and HIV1200. Remove any canonical structure
shared across reserved roles from every role. Keep within-role overlaps and
report them. Require128surviving unique structures, retain at most600 by the
fixed structure hash, and recompute nonchiral radius2/1024-bit Morgan features.

Report exact cross-role overlap after purge, nearest-fingerprint Tanimoto>=0.8,
and nonempty Murcko-scaffold overlap; report acyclic molecules separately.
These audits characterize residual chemical dependence, not a new exclusion
chosen from downstream results. Family analysis weights are equal; average
assays/seeds within families. Seeds and assays are not extra family units.

## Access and stage boundary

Freeze selected IDs, membership/order, source/member hashes, source code,
dependency versions, exclusion ledger and preparation config before semantic
development outcome use. Record trusted parsing as physical outcome-byte
access with no emitted values, not a claim that no outcome bytes were read.
Final outcomes remain in the original ignored archive and are not prepared for
Goal4. Development/validation label material requires a separate frozen evaluator
projection and the Goal3 readiness gate. Any degenerate labels later discovered
remain visible and cannot trigger replacement. Final quality/evaluation remains
unrun until a separately authorized Goal5.
