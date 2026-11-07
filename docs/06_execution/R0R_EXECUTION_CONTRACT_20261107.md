# R0-R reference-feasibility execution contract

Owner approval: 7 November 2026, explicit approval of the proposed R0-R before
considering another phase. Base: ff5d33509e972fd812298d5f99f9c68ed23126c6.
Release: 2026-11-07T06:16:25Z (13:16:25 Asia/Bangkok).
Absolute end: 2026-11-07T14:16:25Z (21:16:25 Asia/Bangkok).

This is a fresh bounded revision within R0, not an extension/reset of closed R0,
A3 or LR-BC ledgers. No P1/R1 release is implied. Parent remains sole writer.

## Bounds and actions

- One local processing worker, one CPU equivalent, at most 1 GiB. Reserve 600 of
  3600 CPU seconds for setup/protection/validation/source review/report utilities;
  reserve 60 per network worker before admission. At most 48 requests means at
  most 3480 conservative seconds under this schedule. Retain failures/charges.
- Fresh private root `.local/r0r-chembl-20261107-v1/`; no old-root recreation.
  One request at a time, at least 1 second apart, at most 30 seconds each. No
  automatic retry, mirror or unknown redirect. 32 MiB total decoded response
  bodies; metadata responses at most 2 MiB and methods XML/PDF at most 4 MiB.
  Retain a 64 MiB new working-storage ceiling. Include failed attempts/bytes.
- Use ChEMBL 37 with status before/after and local byte hashes; do not combine
  source releases or claim an atomic full-release snapshot.
- Select up to 12 assays from the already metadata-exposed 50, using an outcome-
  blind balanced B/F hash rule and distinct documents where feasible. Apply
  verified frozen protein/family protection first. Unknown target/family matches
  remain quarantined; do not refill after post-freeze failures.
- For each selected assay, request at most 20 records with an exact projection
  of activity_id, assay/document/molecule IDs, standard_type and standard_units;
  at most 240 total. Exclude values, pChEMBL, activity comments/classes, quality
  flags and result-derived filtering. Stable activity-ID ordering is a bounded
  convenience sample, not exhaustive measurement support.
  Observed adapter amendment: the activity service adds the original string
  `type` and `units` aliases despite the six-field projection. Those two fields
  are within the approved readout/unit metadata scope and may be retained after
  schema/type validation. No numeric value fields are allowed. The two earlier
  rejected cases remain STOP/excluded, without retry or replacement.
- Retrieve at most 240 distinct molecular identity records (structure/IDs only)
  for exact canonical overlap checks using the previously pinned RDKit policy.
  Do not admit an identity if the required canonicalization cannot be reproduced.
- At most 12 accessible methods extracts, only for selected source documents.
  Discover access via source metadata without abstracts/results. A trusted
  parser may consume a legally accessible article stream to isolate methods,
  discard other sections and mask numbers/result statements BEFORE agent view.
  Do not persist/emit unmasked full article bodies, tables, figures, results or
  activity values. Record transit bytes/exposure limitations. If a trustworthy
  section boundary cannot be determined, quarantine rather than infer methods.
  Owner-supplied PDFs use operator-triggered local intake after notification,
  not folder polling. Reserve 20 CPU seconds per file in addition to existing
  charges, check the fixed DOI in front matter and the source-byte/size limits,
  and mask before any agent view. Six local files plus the maximum 48 network
  reservations and 600 utility seconds fit the unchanged 3600-second ceiling.

## Scientific question and analysis freeze

Does an admissible source-methods passage resolve a context/endpoint compatibility
decision left unresolved by the already available typed metadata? Separate:
metadata incompleteness, actual ambiguity, source resolution and a decision
change. A field fill is not automatically a decision improvement. This round
does not test compound ranking, confirmed hits, policy reward or lab savings.

Record metadata-only eligibility for a declared endpoint cell: same target and
organism, same endpoint type, compatible stated units and a compatible assay
system. Keep Ki/KD/IC50/EC50 separate. Unknown applicability remains UNKNOWN,
not negative. Construct a fixed case question before retrieving its methods;
retain ties/unresolved cases. Cases that are already decided by metadata are
controls, not failures to discard. Actual assay/paper/family counts must remain
visible; repeated assays do not create independent families.

Source-supported draft judgments and masked references are to be presented to
the owner. No independent adjudicator is designated by this approval. Therefore
references stay PENDING_OWNER_REVIEW; the parent cannot call its own labels
independent gold. A positive feasibility result would only justify a later
frozen development comparison against complete upfront resolution and strong
same-predictor acquisition. No method superiority or paper readiness follows.

## Protections and stop conditions

Verify existing cached label-free protection inputs and pinned family registry;
do not inspect outcome arrays or alter frozen roles. Molecules failing exact
identity protection are excluded before scientific admission. All new selected
identities are development/reference exposed, never untouched final cases.
Reuse the existing local pinned environment if available; no global environment
or SSH configuration changes. Old PubChem/UniProt/source STOPs remain in force.

No final outcomes, numeric activity values, model fitting, paid services/GPU,
remote processing, real team writes, deployment or journal action. Consult the
owner on material rights/population/endpoint/access changes or increased bounds;
continue independent authorized preparation. End with an honest readout and
reference review packet; no automatic next phase. Evidence will be exported to
`docs/evidence/r0r-chembl-20261107-v1/`, with private raw inputs kept local.
