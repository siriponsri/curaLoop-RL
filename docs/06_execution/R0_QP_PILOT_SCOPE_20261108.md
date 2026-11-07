# R0-QP: small ChEMBL 37 support-qualification pilot

**Direction approved; execution scope awaiting owner confirmation.**
Date: 8 November 2026, Asia/Bangkok. This is a new pilot proposal, not the old
R0-QC census, a release manifest or permission to reopen a closed ledger.
Basis: [Deep Research adoption](../03_research/DEEP_RESEARCH_ADOPTION_20261108.md).
Canonical machine-readable proposal:
[r0_qp_proposal_20261108_v1.json](../../research/configs/r0_qp_proposal_20261108_v1.json).

## Question and expected deliverable

Does a small prospectively selected population contain recorded, interpretable
same-compound support across Ki/Kd reference assays and auxiliary contexts,
after known protection, chemical identity, validity and source checks? Report
what remains unresolved after complete permitted metadata. Do not claim molecular
utility, biological independence or a qualified benchmark from support counts.

Deliver one pair-level support/context table, a complete target disposition
ledger, exact-stereo/parent/ambiguous identity counts, dependency/source warnings,
scope/resource receipts and an English owner readout. Include unsuccessful,
oversized and unresolved targets, not just candidates that survive.

## Prospective population and selection

1. Use the pinned ChEMBL 37 source only. Start from the existing 11,055-entry
   SINGLE PROTEIN target inventory; reconcile target identities before use.
   Within that inventory, form the metadata-only reference-capable list using
   the existence of a Ki/Kd binding assay and a distinct Ki/Kd/IC50 auxiliary
   assay; use endpoint-type existence only, not molecule counts or value flags.
   Report this catalog denominator and any missing eligibility metadata. Select
   at most **32 target entities**: three known development diagnostics
   (CHEMBL5966/FcRn, CHEMBL256/A3, CHEMBL264/H3) plus up to 29 candidates ranked by
   SHA256 of `CuraLoop-ChEMBL37-QP-v1-20261108|<target_chembl_id>`.
2. Candidate sampling uses only target/assay metadata, endpoint-type existence
   and existing protection/exposure records. Do not prioritize by potency, value
   availability, old support yield,
   hand-picked protein category or paper accessibility. Exclude known protected
   final targets/accessions/source lineages before ranking. Describe the rest as
   not-known-exposed candidates, not certified independent or clean final units.
3. Freeze the complete intent after the endpoint-existence catalog but before
   any new support-cardinality/structure/validity query.
   No post-failure refill, redraw or target replacement. An absent diagnostic
   remains absent. If the catalog cannot be authenticated, stop rather than
   constructing a convenient substitute frame.
4. Include whole eligible assay graphs for selected targets, at most **1,000
   assays / 250,000 topology rows / 25,000 source molecule IDs** in total.
   Reference tracks Ki and Kd stay separate; auxiliary tracks may be Ki/Kd/IC50.
   Reference candidates require binding type B, direct relationship D, confidence
   9, a single non-homologue protein accession and source-document traceability.
   Functional auxiliary contexts remain separate and cannot certify binding truth.
5. If a complete target exceeds remaining bounds, mark UNKNOWN_CAP and report
   its metadata denominator; do not analyze a favorable prefix. Pair tables must
   include all endpoint-compatible assay pairs within a completed target, or
   mark the target's pair search incomplete. No top-eight auxiliary heuristic,
   selected subset of pairs or pooling of assays into a reference procedure.

## Protection and chemical/source dependencies

Carry forward all old protected canonical identities/accessions/sources, exposed
assays, metadata frames, role labels and the 87-label development closure.
Reconcile CHEMBL8809 aliases and the four mixed-role source components. Preserve
old constraints even when their original identifier namespace is uncertain.

Resolve canonical/isomeric identity in a trusted layer before numeric validity
checks. Exclude exact and unresolved potential protected matches before those
checks; uncertain identity or source/family closure is UNKNOWN, never cleared
by an absent exact ChEMBL ID. No historical final outcome or per-cell validity
mask may be read, queried or emitted. No new final/validation role is assigned.

Record exact stereochemical identity separately from parent-normalized identity,
unspecified stereo and failed mappings. Parent-only matches are a diagnostic,
not admitted exact overlap. Do not mix salts/stereoisomers silently or count
repeated/deposited rows as independent measurements.

Normalize DOI/doc keys. Scope assay-group/deposition identifiers to their proven
source namespace; unresolved namespaces create conservative warnings/closures.
Report source-connected components and biological-family/homology annotations
on separate axes. Neither certifies independent biological families here.

## Requested trusted data access: counts, not activity magnitudes

This is a **blinded support-qualification** proposal. Calling all of it
metadata-only would conceal the extra validity access requested below.

- The planner may receive target/assay/source identifiers, endpoint type,
  unit/relation, procedural context and aggregate counts/reasons.
- The trusted evaluator may test whether a non-protected record has a finite,
  positive numeric `standard_value`, relation `=`, a recognized molar unit,
  an acceptable validity status and no known potential-duplicate flag. It must
  not transmit the number, pChEMBL, activity class/comment, rank, histogram,
  potency threshold or per-record validity mask to the planner or public output.
- Null/unknown validity or duplicate fields are explicit categories. In
  particular, a null validity comment means no recorded warning, not that a
  curator experimentally certified it. Quarantine known invalid/duplicate rows;
  preserve reason counts. Publish no strong/weak potency bins.
- Retain nominal, recorded-numeric, quality-filtered and unknown-source support
  as distinct counts. Non-null/positive numbers are not proof of genuine
  experiments or source-level measurement independence. Censored values are a
  separate diagnostic, not exact-reference support or inactive labels.
- Metadata projector must preserve allowed pH/technology/organism/construct,
  cell/tissue/variant and procedural facts. Outcome-bearing descriptions are
  quarantined without exposing their results. An incomplete/redacted metadata
  view cannot establish natural evidence uncertainty or justify a policy gain.

No activity magnitudes, final values, raw activity comments, training or policy
simulation are released. No numeric validity work starts until the owner confirms
this scope and a fresh budget/window.

## Readout rules: feasibility, not effect-size success

Report every completed pair's nominal reference/auxiliary support, exact-stereo
recorded-numeric intersection, parent-only matches, ambiguous/protected exclusions,
duplicates, censoring and source/context unknowns. Use no inherited 128/64/32
floor and do not introduce a new empirical-effect threshold.

For an engineering action-space diagnostic only, flag whether there are at least
two distinct reference choices and two shared exact-identity recorded cells in
distinct assays. This is a mathematical minimum to exercise a choice, not a
statistical/sample-size or publication criterion. Keep smaller pairs in the report.
No final panel size is selected in this pilot.

| Gate | Possible readout | Consequence |
| --- | --- | --- |
| Source/protection | PASS, STOP_INTEGRITY, UNKNOWN_PROTECTION | Unknowns withhold numeric checks for affected records; no new role clearance |
| Recorded support | Counts plus PASS_RECORDED_SUPPORT / FAIL_SUPPORT / UNKNOWN | Counts qualify storage support only; never label an unknown/imputed cell measured |
| Source/context | Metadata-complete / metadata-saturated / pending-source / unknown | Paper-only value requires later source-backed residual uncertainty |
| Isolation | Conservative source-component counts and unresolved links | Repeated assays or seeds cannot enlarge the unit count |
| Next step | CANDIDATES_FOR_DOMAIN_REVIEW or REVISE/STOP | Neither authorizes model training, a final set or an automatic pivot |

Multiple source-component candidates are necessary before proposing a broader
evaluation, but no number here proves adequate precision. Report the realized
unit count and unresolved links rather than claiming a powered experiment.
If all complete metadata resolves context, say so. A bounded low yield is a
dataset/sampling result, not falsification of an untested algorithm.

## Proposed resource grant and preservation

Fresh ceiling: **3 CPU-hours / 24 elapsed hours / at most two combined workers**:
one dr-train worker, 1 CPU-equivalent / 4 GiB; one local worker, 1 CPU / 1 GiB.
This includes failures, setup, return verification, cleanup and ordinary delivery.
No GPU, paid service, scientific HTTP, new paper intake or bulk download.

| Reservation | CPU seconds |
| --- | ---: |
| Source reuse/extraction, dependency checks, complete return/reread and exact cleanup | 7,200 |
| Protection/metadata/support qualification | 1,800 |
| Utilities, controls, failure records and English/main delivery | 1,800 |
| Total | 10,800 |

These are estimated ceilings, not measured runtimes or a guaranteed sufficient
budget. Set the new release/deadline only after confirmation. Unused old resources
cannot be borrowed. Stop on time/CPU/source/protection/storage bounds; no retry or
extension by resetting a ledger.

Reuse the existing archive, 5,764,252,857 bytes, SHA256
`33c203740555f96067710cdfc1c3c55d890660e5908ec5cbf5817492c290d281`.
The database pin remains 30,480,314,368 bytes, SHA256
`4be13df3b68e25dcd0bff44bf094033b5aebe98f415acdc8c1cdf380e0c15142`.
Verify actual source/environment and kernel CPU/memory enforcement before launch;
use only the existing configured chaw identity. No key/config/privilege change.

Fresh owned paths, only after release:
`.local/r0-qp-chembl-20261108-v1` and an explicitly recorded fresh matching remote
task/export pair. Never reuse any closed old remote root. Remote admission needs
80 GiB free (64 GiB task + 16 GiB reserve); local admission 38 GiB free (28 GiB
task + 10 GiB reserve). Complete return archive at most 16 GiB. Do not expand the
30.48 GB DB locally inside this cap or delete old data to create space.

Return and reread/hash every owned remote regular source/code/dependency/output
file and terminal export receipt before exact task/export cleanup and fresh
absence. Preserve originals if any return verification fails. All raw material
and per-record checks remain private. Public output is English aggregate evidence.

The pilot ends with an owner readout. Full qualification, domain/source review,
new final allocation, fitting, a curation pivot and publication remain separate
decisions. No live product integration or external communication is included.
