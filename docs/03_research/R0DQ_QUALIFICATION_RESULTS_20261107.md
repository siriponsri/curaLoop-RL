# R0-DQ: real support found, full benchmark not qualified

Date: 7 November 2026. Phase: **COMPLETE_AWAITING_OWNER_DECISION**.
Scientific readout: **PILOT_ONLY_REVISE**. The ledger closed at
2026-11-07T11:56:56Z (18:56:56 Bangkok), within the original 72-hour window.
Read the [machine-readable readout](../evidence/chembl-taskfirst-dq-20261107-v1/qualification-summary-v2.json)
and [handoff](../../HANDOFF.md). No next phase is released.

The owner released the [R0-DQ contract](../06_execution/R0DQ_EXECUTION_CONTRACT_20261107.md)
with 16 additional CPU-hours, 72 elapsed hours and at most two combined CPU
workers. This audit preserves the proposed Ki/Kd reference tracks, 128-compound
panels, auxiliary support floors and historical protections. It does not open
old final outcomes, fit a model or authorize the next phase.

## What is now verified

The fixed [ChEMBL 37 release](https://doi.org/10.6019/CHEMBL.database.37) official SQLite archive was received in one request:
5,764,252,857 bytes. Its SHA-256 agrees with the official checksum:
`33c203740555f96067710cdfc1c3c55d890660e5908ec5cbf5817492c290d281`.
The archive contains `chembl_37/chembl_37_sqlite/chembl_37.db` and a short
installation note. The extracted DB is 30,480,314,368 bytes; its locally computed
SHA-256 is `4be13df3b68e25dcd0bff44bf094033b5aebe98f415acdc8c1cdf380e0c15142`.
Schema checks passed. The task-scoped offline environment uses Python 3.12,
RDKit 2026.09.1, Numpy 2.3.5 and SQLite 3.45.1.

The database LICENSE/README/schema snapshots were authenticated and retained.
Calculated proprietary properties were not used. Database attribution and
paper-specific rights are separate; commercial redistribution clearance was
not established.

The inherited protected index contains 4,723 canonical structures. An additional
10,151 known exposed structures were authenticated from the existing NCATS/HIV
identity projections and 13 label-free development/validation feature files.
These are separate, potentially overlapping sets, not an additive unique total.
Historical numerical outcomes were not parsed by that identity projection.
The incidental planning exposure CHEMBL8809 was resolved as a molecule ID.

## Achieved scope

| Measure | Actual result | Full-design target |
| --- | ---: | ---: |
| Frozen target entities | 8 | At most 100 |
| Frozen assays, all with complete topology | 121 | At most 2,000 |
| Outcome-free topology records | 8,231 | At most 1,000,000 |
| Distinct source molecule IDs | 5,549 | At most 100,000 |
| Source molecule IDs excluded for protected exact identity | 2 | Exclude every known match |
| Frozen candidate bundles | 2 | At most 120 |
| Finite-panel support candidates | 2 | 36 bundles |
| Candidate development / validation / final groups | 1 / 0 / 0 | 4 / 2 / 12 |
| Candidate development / validation / final bundles | 2 / 0 / 0 | 8 / 4 / 24 |
| Independently certified biological families | 0 | Review still required |

The restricted validator checked 738 protection-cleared activity IDs; all 738
passed the declared exact/positive/finite/unit test. It emitted support booleans
and counts, without magnitudes, rankings, pChEMBL or utility. Eleven topology
rows were removed through protected/unresolved-identity handling, and 295 were
outside exact-relation/recognized-unit support. Multiple records for an admitted
edge use the lowest admissible activity ID. Missingness is not inactivity.

| Development diagnostic | Reference type | Fixed panel | Shared auxiliary compounds |
| --- | --- | ---: | ---: |
| Human adenosine A3 annotation, CHEMBL256 | Ki | 128 | 72 |
| Human histamine H3 annotation, CHEMBL264 | Ki | 128 | 64 |

Each candidate has one auxiliary context candidate and meets the 128/64/32
numerical-support floors after pruning. **Neither is yet a source-verified
reference task**: construct identity, context distinctness and source-to-assay
mapping remain unresolved. Both belong to one historically development-exposed
typed group. Two bundles do not create two independent groups.

The status token PILOT_ONLY_REVISE sets an upper bound on this evidence. It does
not declare a scientifically qualified pilot or imply the two candidates are
reference gold.

## Why the broad benchmark did not qualify

The 100-target, 2,000-assay, 1-million-row, 100,000-molecule and 120-candidate caps
were not binding. The bottleneck is the admitted population and task definition,
with the following recorded release-catalog diagnostics:

| Diagnostic | Count | Unit / interpretation |
| --- | ---: | --- |
| Unknown or ambiguous family mapping | 10,008 | Target entities outside the inherited exact-accession taxonomy |
| No qualifying nominal reference/auxiliary catalog | 980 | Mapped targets failing the predeclared ID-support criteria |
| Known protected family/accession | 42 | Excluded targets |
| Multiple components | 1 | Excluded target |
| No primary-document DOI | 9,422 | Assays excluded by the source requirement |
| Prior/protected assay | 37 | Assays excluded before the new frame |

These are **partial catalog diagnostics with different units**, not a complete
mutually exclusive flow over all ChEMBL targets. Complete admitted-frame topology
and both frozen candidate dispositions are retained privately. No truncated
assay prefix was promoted to a complete task.

The reused taxonomy is authenticated, but it was built for an earlier FS-Mol
frame rather than all ChEMBL proteins. Its surviving group merges 87 broad
annotations and already has a development role. It is unsuitable as evidence of
twelve independent biological families. This audit does not establish that
ChEMBL as a whole lacks suitable tasks; it establishes that this **predeclared
mapping and task construction** did not yield the intended cohort. More CPU
without changing those choices will not create missing biological split units.

## Context and source feasibility

The two development bundles involve four assays and four primary documents.
Europe PMC exact-DOI metadata and independent, abstract-free OpenAlex location
metadata provided no confirmed open full-text route for any of them. No methods
body was read; no paper was purchased or substituted. This does not prove that
lawful access is universally unavailable.

| Document | DOI | Current evidence |
| --- | --- | --- |
| CHEMBL1154073 | [10.1016/j.bmc.2009.05.038](https://doi.org/10.1016/j.bmc.2009.05.038) | No confirmed open route in the two checked metadata services |
| CHEMBL1821550 | [10.1016/j.bmcl.2011.07.006](https://doi.org/10.1016/j.bmcl.2011.07.006) | Same limitation |
| CHEMBL1145284 | [10.1021/jm049662f](https://doi.org/10.1021/jm049662f) | Same limitation |
| CHEMBL1155513 | [10.1016/j.bmcl.2010.04.045](https://doi.org/10.1016/j.bmcl.2010.04.045) | Same limitation |

ChEMBL metadata already identifies a CHO/NECA context for one A3 assay and
different named radiotracers for the H3 pair. These metadata-visible differences
cannot be credited as paper-only contribution. All four variant fields are null
and parameter lists empty. A null variant does not certify wild type or establish
construct equivalence. Known radiotracer isotope identifiers were restored in a
versioned projection repair; omitted identifiers were not called natural
uncertainty.

The requested eight bundles/four development groups, two source-linked
decision-sensitive factors across two groups and two clear-context controls were
not established. Parent review is not independent domain adjudication. With no
source methods, this is not negative evidence against the general adaptive-
evidence hypothesis and does not justify stopping that research route as futile.

## Engineering issues and retained evidence

1. A constructed SQLite fixture initially waited on a backup of an uncommitted
   transaction. The failed wall-limit receipt remains; the committed fixture
   passed the repaired checks.
2. A local integration fixture initially lacked RDKit on the global import path.
   The existing compatible Windows package tree was used in a new bounded run;
   no global installation was made.
3. The first remote dependency job failed before opening SQLite because a newly
   extracted import path was not found in that process. A fresh read-only import
   diagnosis passed. The versioned repair authenticated all existing dependency
   bytes and invalidated import caches; its extraction/schema check passed.
4. The first metadata frame used the internal target-type spelling while SQLite
   stores `SINGLE PROTEIN`. Its empty result is retained as an implementation
   representation failure, not scientific yield. The adapter normalizes only
   that spelling; research eligibility is unchanged.
5. A query-plan check showed endpoint-wide scans repeated for each target. The
   owned metadata job was stopped. A versioned implementation scans eligible
   assay metadata once and uses the existing assay index; it froze the actual
   frame in about 9 CPU seconds. Earlier reservations remain charged.

The final constructed integration fixture tests the real SQLite-shaped adapter,
frame/candidate ordering, protected-identity handling, missingness and support
floors. Projection and lineage fixtures also pass. These checks establish
implementation behavior, not clinical benefit, model efficacy, reference truth
or independent biological grouping.

## Decision and journal implications

| Gate | Final status |
| --- | --- |
| G1 source | PASS: pinned archive, schema and source/attribution record; commercial clearance unestablished |
| G2 protection | PASS for implemented known-identity gates; family/source certification remains pending |
| G3 structural scope | FAIL: 2 development candidates in 1 unit, against 36 bundles/18 units |
| G4 evidence relevance | NOT_ESTABLISHED: 0 source methods, no independently supported incremental facts or controls |
| G5 integrity/return | PASS: real artifact checks, complete return/reread and fresh scoped absence |

Twelve real derived-artifact invariants passed, including the actual freeze hash
chain, old assay/protein/family exclusions, blocked identities outside the value
allowlist, boolean-only outputs and panel support. The source DB was not opened
by that final checker. The [acceptance record](../evidence/chembl-taskfirst-dq-20261107-v1/qualification-acceptance-v1.json)
does not certify reference truth or efficacy.

The complete private return has 1,777 regular task files, 36,533,325,290 bytes
before compression and an archive of 11,070,386,037 bytes. Every entry was
stream-hashed locally; 14,687,964 bytes of usable code/input/derived evidence
were extracted. The full source DB remains inside the archive. After local
verification, both exact owned remote task/export paths were deleted on
7 November and a separate fresh absence check passed. See the
[return proof](../evidence/chembl-taskfirst-dq-20261107-v1/complete-return-verified-v1.json)
and [absence proof](../evidence/chembl-taskfirst-dq-20261107-v1/fresh-absence-v1.json).

Conservative retained accounting is **32,910/57,600 seconds, 9.14/16 CPU-hours**,
including failures and a 3,600-second utility reserve. This is reserved/retained
budget, not a claim of 9.14 hours of measured CPU execution. Measured times are
receipt scoped and are not a complete host profiler. Source/frame/support/
context/closeout reservations are 10,260/7,200/3,600/1,050/7,200 seconds.
The source ledger records 10 scientific HTTP attempts, one bulk request,
17,288 nonbulk decoded bytes, no new source STOP and no retries. Old ledgers and
STOPs are unchanged. Unused allowance does not authorize another phase.

The first closeout collector looked for the export receipt inside the task
snapshot although its terminal capsule is separate. A reporting-only v2
reconciliation associated that already verified receipt, preserving v1 and the
closed ledger snapshot. No job was rerun and no scientific count, reservation
or clock changed. All ledger jobs are terminal. Latest
[resource receipts](../evidence/chembl-taskfirst-dq-20261107-v1/resource-receipts-v2.json).

Cross-role scaffold/Tanimoto analysis is not applicable with empty validation
and final roles. There is no chemical-OOD or pretraining-contamination claim.

The phase has made progress beyond the earlier one-molecule subset: it found
real panels with 128 molecular alternatives and complete auxiliary support.
It has not produced the proposed 36-task/18-group benchmark, untouched validation
or final roles, independently adjudicated references, a tested joint planner,
an effect estimate or novelty evidence. Publication readiness remains
**NOT_READY**. The product's molecular-research claims also remain unvalidated.

The recommended next owner decision is a **metadata/design revision within R0**,
before R1: broaden independently reviewable family coverage and assess whether
source-verified procedure groups can support the reference task unit. Retain
Ki/Kd separation and the molecular-choice floors; do not lower them merely to
raise counts. Any pooling must be justified by procedure/source identity before
values, with every historical protection preserved. This is a proposal direction,
not execution authority or a promise that twelve final families will qualify.

The four papers may help adjudicate these two diagnostics if the owner has lawful
access. They will not by themselves repair the missing validation/final groups.
No purchase or next phase follows automatically. The owner reviews the achieved
readout and the next concrete scope, budget and gates first.
