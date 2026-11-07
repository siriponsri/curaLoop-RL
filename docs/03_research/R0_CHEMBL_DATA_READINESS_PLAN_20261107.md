# R0 ChEMBL data-readiness plan

Date: 7 November 2026. Base main:
66e6387fa17d7e2f8e4d7e97613c2f974f982d06.
Status: **PLAN_READY_FOR_REVIEW**. Metadata sample intake: **NOT_RUN**.
Owner decision: ChEMBL is the primary source for the approved contribution
direction. This is an R0 plan, not release of a new phase, dataset certification,
final outcome access or a novel-method claim.

## Objective and decision to support

Determine whether a fixed ChEMBL source can support a source-linked benchmark
of shared assay-context verification and molecular selection. Produce an honest
GO / REVISE / NO_GO recommendation with remaining unknowns. A metadata-only pass
means that bounded development qualification can be proposed; it cannot establish
complete observed outcomes, molecular overlap control or policy value.

The approved direction is recorded in the [contribution proposal](R0_CONTRIBUTION_DATA_PROPOSAL_20261107.md).
The owner remains a decision maker before the next phase and before material
changes to the endpoint, population, release, access rights or resources.

## Verified source facts and consequences

Official [download documentation](https://chembl.gitbook.io/chembl-interface-documentation/downloads)
lists ChEMBL 35 with a release DOI and currently lists release 37. Keep 35 as
the proposed historical reference; do not call it latest or silently upgrade.

The [official FAQ](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/general-questions)
states that the API/interface reflect the current release and cannot extract
older versions. Consequently, live API data cannot certify a release-35 cohort.
A source-pinned historical metadata export or controlled release extraction is
required. The same FAQ describes database licensing and additional constraints
on certain calculated properties. Release, provider content and intended uses
must be assessed separately; no commercial-rights clearance is asserted here.

[Service documentation](https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services)
distinguishes assay details from activity values and documents field projection.
Projection is a useful minimization mechanism, not proof that returned free text
contains no outcome. These docs were read; no assay/activity endpoint was called.

The [assay FAQ](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/chembl-data-questions)
distinguishes binding from functional assays and describes confidence in target
assignment. A high target-confidence score does not certify endpoint equivalence,
biological-family independence or comparability of all measurements.

## Proposed first execution envelope

These are proposed new bounds, **not an approved compute/intake grant**. Prior
LR-BC accounting and deadlines remain unchanged. Ordinary preparation of this
plan does not create a new reservation or claim zero computer use.

| Resource or access | Proposed ceiling |
| --- | --- |
| Processing | One local worker, at most one CPU equivalent, 1 GiB memory; no SSH/GPU/model training |
| Execution accounting | 30 CPU-minutes total, including validation; 4 hours elapsed from an explicitly recorded release time |
| Metadata sample | At most 50 unique assay records and 20 unique document metadata records from one verified release |
| Supporting records | At most 100 target/lineage metadata records; count and byte caps still apply |
| Source access | At most 32 attempts total, serialized; at least one second between attempts, 30-second request deadline; no automatic retry/fallback |
| Payload | At most 16 MiB decoded responses in total, 2 MiB per response; 64 MiB new working storage |
| Activity and evaluation access | Zero activity records, values, benchmark questions/gold or protected final outcomes |
| External actions | Zero paid API/model calls, team writes, deployments or journal actions |

Request, response, timeout and decoded-byte caps must be enforced before an
executable run. Retain failed attempts and partial bytes. HTTP errors, rights
ambiguity, unknown redirects, an unsupported schema or any cap failure stop the
affected source; do not silently retry another endpoint or mirror. If a metadata
export is local, source-request use may be zero, but its provenance and bytes
still count. The limits are feasibility limits, not statistically powered sizes.

## Ordered work and gates

| Step | Work | Inspectable output | Gate |
| --- | --- | --- | --- |
| M0: version/access/rights | Verify fixed release, exact artifact identity, schema and outcome-free metadata route; enumerate intended research/publication/product uses | Source registry, access/rights matrix, URL/file hashes and version evidence | Stop before sample intake if a release-pinned route cannot be verified |
| M1: metadata contract | Map required fields to the actual pinned schema; validate missingness, ID joins, duplicate handling and outcome-exposure controls | Field map and contract validation report | No assumed field mapping; no activity table access |
| M2: fixed feasibility sample | Freeze an outcome-blind candidate frame and bounded sampling rule, then inspect up to 50 assays and 20 document metadata records | Selection manifest, complete dispositions and metadata coverage | Count all attempts/exclusions; no result-driven replacement |
| M3: dependence and context review | Inspect target/document lineage, recorded endpoint descriptions and candidate ambiguity sources; separate natural absence from actual inconsistency | Dependency map, context evidence register and uncertainty report | No automatic claim of gold truth or 12 independent families |
| M4: owner readout | Present GO / REVISE / NO_GO for further qualification, proposed endpoint/population, gaps and next bounded budget | R0 readiness report and decision ticket updates | Owner chooses next work; no automatic phase transition |

### M0 source-route decision

Preferred route: a metadata-only export whose identifiers, fields and release
match an official immutable release. If obtaining it requires the complete
database archive, do not download it under this slice: that archive contains
activity data and exceeds the proposed envelope. Present artifact URL, size,
checksum availability, target path and a separate storage/extraction contract.
Ask the owner to assist with download only after the concrete access failure
and required artifact are identified. An unavailable route is not a reason to
substitute current-release API responses.

Metadata source availability may make a newer release preferable. Such a change
requires a documented owner decision before sampling. Never mix releases in one
record or use later annotations without preserving their separate provenance.

### M2 sampling without an outcome filter

First record the accessible metadata universe, its scope and ordering. If a
verified release-wide metadata frame is available within the envelope, stratify
by its fixed target-classification hierarchy and broad assay context, then rank
IDs deterministically using SHA-256 of plan ID, release and assay ID. Assign
quotas before reading individual descriptions. Record the classification level
and unknown/overlapping groups. Do not choose a group because it is a known
example of bad data or because any activity value looks favorable.

If only a partial or convenience frame is available, label it as such; do not
call the sample representative of ChEMBL. Freeze its IDs before inspecting
descriptions. Exceeding a record/lineage cap or needing another frame produces
REVISE, not an unrecorded expansion. Rejected/quarantined records retain their
slots. The 20-document ceiling may leave some assays unreviewable; report that
denominator rather than replacing those assays.

The owner's 12+ independently verified biological-family ambition remains a
later cohort criterion. This small sample does not certify it. Target classes,
targets and annotation-connected components are different counting units.

## Minimal metadata contract

These are canonical output fields, not claims about exact source column names.
Confirm source mappings in M1 before admitting rows. Required means that a value
or an explicit unknown reason is present; it does not allow fabricated values.

| Record | Required canonical fields | Not admitted in this slice |
| --- | --- | --- |
| Source | release ID, artifact/URL, retrieval UTC, SHA-256, source schema version, projection, terms reference and scope | Unversioned replacement, secrets, an assumed checksum |
| Assay | stable assay ID, document/target IDs or unknown reasons, assay category, target-assignment confidence, organism/context, evidence reference | Activity values/classes, pChEMBL, compound hit lists or ranking |
| Document | stable document ID, DOI or unknown reason, title/year, methods-access status, source reference | Full article/SI/results tables or unreviewed attachments |
| Target/lineage | stable target/component IDs, relationship type, source version, classification path and evidence | Unverified biological-family certification |
| Context review | field being reviewed, claim, source location, uncertainty status, reviewer identity/role and exposure disposition | A flag treated as ground truth; a made-up endpoint/unit |
| Disposition | ADMIT / QUARANTINE / REJECT, reason, first-seen order and counts | Silent deletion/replacement or a corrected source row overwriting the original |

Null reasons include NOT_REPORTED, NOT_MAPPED, INACCESSIBLE, CONFLICTING and
NOT_REVIEWED. None means zero, inactive, false or a negative outcome. Keep
endpoint types and units as stated; Ki, KD, IC50 and EC50 remain separate.
An endpoint mentioned in an assay description is a candidate interpretation,
not a verified activity-record type or proof of measured support.

Example fixtures for later validation use fictional IDs, not new scientific
records: an assay with a missing DOI and NOT_REPORTED is structurally valid;
an assay with an unversioned source is rejected; two differing payloads with the
same release/ID are quarantined as a conflict; a payload containing an activity
value is quarantined and excluded from agent context. These are contract
examples, not tests that have already passed against ChEMBL.

Duplicate identity is source release plus entity type plus stable ID. An exact
payload duplicate reuses the first immutable record and is counted. A changed
payload is a new exposure/conflict record, never an overwrite. Output schema v1
is additive: preserve original inputs and write new derived records. No existing
benchmark, frozen manifest or database schema is migrated. Rollback consists of
withdrawing the new candidate report, preserving its audit, and using the prior
checkpoint; raw scientific history is not erased.

## Outcome and leakage protections

Metadata is not inherently outcome-free. Free text and document titles may
mention potency or outcomes. Automated screening can reduce exposure but cannot
guarantee semantic cleanliness. Screen before text reaches the planning agent;
quarantine the entire suspicious record and retain only hashes/disposition in
normal reports. Record accidental exposure honestly, then keep the affected
case out of a future untouched set. Do not label an imperfect filter a guarantee.

No full paper/SI intake occurs in this slice. Resolving natural uncertainty from
methods will need a later bounded evidence-access plan with result masking and
reference adjudication. If one person reads a reference outcome, their case is
exposed for method development; software labels cannot undo that exposure.

Use existing label-free protection/exposure artifacts identified through the
[A3 qualification record](GOAL4R2A3_QUALIFICATION_V1.md). Verify their exact paths,
hashes, coverage and completeness before use. Do not reconstruct them by opening
outcome arrays. This metadata slice cannot certify exact compound overlap or
measurement support: the required outcome-free molecule/assay crosswalk is not
yet admitted. Unresolved mapping remains UNKNOWN and blocks final admission.

No policy replay, thresholds, synthetic corruption, assay-outcome peeking or
model selection is allowed during metadata sampling. Protected final outcomes
remain closed for the entire R0 work described here.

## Readiness decision rules

| Dimension | Metadata-stage PASS requires | Remains unknown after a metadata pass |
| --- | --- | --- |
| Source integrity | Fixed release/bytes, reproducible schema and working metadata route | Full measured-panel coverage |
| Use permission | Itemized sources/terms and intended research/publication uses with no unresolved blocker for this slice | A blanket right to redistribute raw articles or commercial property calculations |
| Joinability | Stable assay/document/target mapping with every missing/conflicting case recorded | Complete molecule/measurement linkage |
| Scientific context | Inspectable fields and plausible natural uncertainties, with explicit unresolved cases | Independently adjudicated truth, resolution yield and adaptive decision value |
| Independence | Document/target relationships and actual counting unit documented | A sufficiently large, independently verified 12-family final cohort |
| Leakage control | Exposure/disposition register and exclusion policy; no undeclared outcome use | Absence of public-model pretraining contamination |

GO_METADATA means a bounded development-qualification proposal can be prepared.
REVISE means the evidence is incomplete or a material design/access choice is
needed. NO_GO_CURRENT_ROUTE means a demonstrated blocker defeats this route.
An inaccessible file alone does not establish that ChEMBL itself is unusable.
Use PASS / FAIL / BLOCKED / NOT_RUN per check; missing evidence never passes.
Do not invent numeric success thresholds after seeing the sample. The first
slice reports counts/ranges and limitations, not confirmatory significance.

## Deliverables and remaining decisions

The later execution should return: source/terms registry; schema map; immutable
selection and exposure manifests; metadata dispositions and denominators;
lineage/context review; resource/request ledger; and one owner-facing readiness
report. Each output must state the exact source, date, code revision and scope.

| Decision | Current state | Next resolution |
| --- | --- | --- |
| R0-D1 contribution direction / ChEMBL primary | APPROVED by owner | Retain; no new cohort or release approval implied |
| R0-D2 readiness execution contract | PLAN_READY_FOR_REVIEW | Release concrete bounds and verify M0 prerequisites before intake |
| R0-D3 source/rights/metadata feasibility | NOT_RUN beyond official-document review | Execute M0-M3 within released bounds |
| R0-D4 endpoint/population and bounded development evidence/outcome qualification | NOT_RELEASED | Owner decision after M4, still within R0 if chosen; final outcomes remain closed |
| R0-D5 R0 closeout / next phase | NOT_RELEASED | Owner reviews achieved evidence and chooses next phase explicitly |

Source documentation review PASS; local document/manifest consistency checks are
recorded in the execution checkpoint. Metadata sample validation, scientific
adjudication and independent review are NOT_RUN. The parent prepared the plan
serially. Planning is complete; data readiness and method novelty are not.
