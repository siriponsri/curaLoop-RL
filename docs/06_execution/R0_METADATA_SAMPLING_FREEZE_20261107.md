# R0 metadata sampling freeze

Frozen before assay records were requested, 7 November 2026.
Owner approved switching the candidate source from ChEMBL 35 to ChEMBL 37.
The status response and release-37 README/schema/license were retrieved first.
Historical 35 evidence remains separate. Execution caps and deadline unchanged.

Frame: live ChEMBL 37 metadata at retrieval time, restricted to literature
source ID 1, direct single-protein assignment confidence 9, and assay category
B or F. This is a deliberately limited feasibility frame, not all ChEMBL and
not the eventual scientific population. It excludes many ambiguous target
assignments, so a lack of ambiguity cannot generalize to the whole database.

Select the first 25 stable assay IDs in lexicographic ascending order in each
category, using only assay/document/target IDs, category, confidence and source
ID. This is a deterministic convenience sample, not a random or representative
sample. A complete frame is unavailable within the record cap; no release-wide
hash/random claim is made. Freeze the returned 50 identities before obtaining
descriptions. Never replace missing, conflicting or quarantined records.

Then retrieve the fixed IDs' assay metadata once with field projection. Do not
query activity or full-text/SI endpoints. Free text stays in private raw artifacts;
only categorical summaries/dispositions enter the planning context. Conservative
screening flags possible quantitative outcomes and masks whole suspicious fields;
it is not an adjudicated semantic guarantee.

Choose at most 20 unique document IDs from these assays by SHA-256 ordering of
plan ID plus document ID, before requesting document metadata. Other documents
remain NOT_REVIEWED, not replaced. Target metadata is limited to these assays'
unique targets; supporting classification records share the 100-record ceiling.
Do not make a biological-family claim from broad target classes. Freeze future
queries from observed IDs; do not use outcome, hit frequency or model behavior.

Guardrails: exact allowed URL registry; zero activity requests; count every
attempt/byte and all excluded records. Before/after service status must still
identify ChEMBL 37. A version change stops admission. No reference truth,
measurement support or phase GO can be inferred from this sample alone.
