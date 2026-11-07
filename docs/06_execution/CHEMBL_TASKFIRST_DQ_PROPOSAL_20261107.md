# Proposed R0-DQ scope, permission and resource contract

Date:7November2026. **PROPOSAL_ONLY; EXECUTION_NOT_RELEASED; CLOCK_NOT_STARTED**.
The owner approved preparation of the [task-first dataset/benchmark plan](../03_research/CHEMBL_TASKFIRST_DATASET_BENCHMARK_PLAN_20261107.md),
not the activities or fresh resources below. Old R0/R0-R/R0-A1 ledgers stay closed.

## Recommended next package

**16 additional CPU-hours / 72 elapsed hours / at most2combined CPU workers**.
One heavy worker on the existing dr-train profile, at most1CPU-equivalent/4GiB;
one local worker at most1CPU/1GiB for tests, hashing and return verification.
Use enforced aggregate one-core quota plus initial leased affinity remotely;
do not require unavailable cpuset delegation or change privileges/configuration.
No GPU, paid API, paid paper, model fitting, live LLM campaign or team write.

Start an absolute72-hour clock at explicit execution release, before the first
admission check, recording release/deadline in UTC and Asia/Bangkok. Admission
work consumes that same clock/CPU allowance; failed checks remain charged. An unstarted or
expired old clock is never reset. No automatic extension, retry or second round.

| Allocation ceiling | CPU-hours |
| --- | ---: |
| Source acquisition verification/decompression/schema | 3 |
| Target/family/source frame and protection | 2 |
| Canonical identities and complete support graph | 5 |
| Development methods/context feasibility | 3 |
| Checks/full return/reread/scoped cleanup | 2 |
| Utilities/reporting allowance | 1 |
| Total increment | 16 |

These are conservative admission ceilings, not measured runtime estimates or
spend commitments. Reserve before jobs; include failures, transfer verification
and utilities, with at most the total16hours. Any later pilot/reference/final
campaign needs a new proposal rather than consuming an unstated balance.

## Data access that would need explicit approval

1. Acquire the exact private `chembl_37_sqlite.tar.gz` source archive, plus release
   checksum/schema/README/LICENSE metadata. Cap8GiBcompressed/32GiBunpacked DB.
   It contains numerical outcomes in plaintext at rest. No complete archive,
   raw source paper or full masked passage goes to public Git.
2. A restricted trusted qualifier may inspect only candidate records that first
   clear the frozen assay/target/protected-identity gates. It may check finite,
   positive/nonmissing values and exact relation/unit validity, but emit only
   IDs, eligibility booleans and support counts. No activity magnitudes, ranks,
   pChEMBL, compound classes or result-derived flags enter model context.
   Old protected final records are never queried for values. New reserved-final
   candidate values remain unexported; no R10 utility/ranking is calculated.
3. Read metadata for the bounded frame, complete its support graph and at most24
   development-source documents. Allow context identifiers and clearly methods-
   input numerical conditions, while masking activity/effect/dose-response
   outputs, rankings, results/tables/figures. This is broader than A1 identifier-
   only access and is a proposed permission, not a present release.

No schema checks or model tooling should expose a raw unrestricted SELECT path.
Validate the restricted projection and leakage guards on constructed fixtures
before scientific intake. Private/sealed here is a process/output contract,
not a claim of cryptographic isolation from the host owner.

## Bounded population and network

At most100target entities,2000selected assay metadata records,120candidate
bundles,1000000support rows and100000canonicalized molecules. Complete support
for a candidate is required; truncation is UNKNOWN, not a qualified panel.
Freeze the target/assay frame and rules first; build its complete outcome-free
identity topology; then freeze at most120candidate bundles before numeric-support
validation or source-reference interpretation. No potency/performance selection
or post-validation refill outside that candidate frame.

At most96scientific HTTP attempts:1bulk archive, up to7other release metadata,
56bibliographic/access/family metadata and32methods requests. No automatic
retries/mirrors/unknown redirects; one active source request at a time. Count
failed attempts and bytes. Bulk timeout at most6hours within the absolute phase
deadline; other metadata30seconds, methods60seconds. Nonbulk decoded cap512MiB,
metadata2MiB/file and methods8MiB/file. Reuse authenticated cached inputs where
appropriate. No stopped PubChem/UniProt/publisher/source request is retried.

Three previously purchase-only documents remain deferred; no new purchase or
substitution for those cases. New candidate-source availability is recorded for
the full frame. If an approved fresh source route fails, report it and request
lawful owner help when useful, keeping the same clock/caps; do not silently
change release or endpoint.

Future source-assistance target, **not a request to download now**:
`C:\Users\User\Desktop\myProject\curaloop-rl\research\raw_data\external-benchmarks\chembl-37-taskfirst\source\chembl_37_sqlite.tar.gz`.
Provider checksum/size/member validation remains mandatory even for owner copies.
Expected exact bytes/checksum are currently UNKNOWN, not inferred from5.4G.

## Storage, environment and remote return

Plan-time local C:free space was60749815808bytes, about56.6GiB, observed
7November. This is not a launch reservation. Remote capacity/authentication have
not been checked in this planning task.

Remote task cap64GiB: archive8 + DB32 + intermediates8 + export16. Require at
least80GiBfree at admission, including16GiBreserve. Local task cap28GiB: source
archive8 + full return archive16 + extracted evidence/code/derived data4. Require
at least38GiBfree, including10GiBreserve, and enforce the reserve before jobs.
Do not extract the full returned DB locally merely to verify it.

Use only the existing SSH profile/key; check host identity, live allocation,
memory/disk/quota enforcement and conflicts without configuration or privilege
changes. A failed admission is a reported blocker, not permission to weaken
limits. Default no more than one remote scientific job plus one local utility.

Fresh versioned local and remote owned roots only, never any closed root.
Before cleanup, return an archive containing **every current regular task file**,
including code, private outcomes/source SQLite and derived data, with relative
paths, sizes and SHA-256 manifest. Stream-decompress/hash every entry locally
without expanding the large DB; validate entry paths and complete file counts.
Preserve special-file/alias metadata and reject paths escaping the owned root.
Only after full return/reread and verified local persistence, delete the exact
checked remote task/export paths and verify absence. If return exceeds the16GiB
cap or verification fails, preserve remote files and consult the owner; never
delete data to make the return fit. Keep raw copyrighted sources private.

## Deliverables and stopping point

Return the versioned source/schema/terms manifest; candidate and exclusion frame;
family/source grouping and exposure ledger; complete support/attrition report;
candidate36-bundle4/2/12role reservation; eight-development-bundle context packet;
leakage/contract fixtures; code/environment/resources; full private return and
public typed report. Independent reference judgments are not invented.

Use G1-G5 in the dataset plan. All supported -> PASS_FOR_REFERENCE_REVIEW only.
Partial cohort -> PILOT_ONLY_REVISE. No natural decision relevance beyond complete
metadata -> STOP_CURRENT_ADAPTIVE_EVIDENCE_ROUTE. Missing truth/expert input ->
PENDING_DOMAIN_REVIEW. Integrity failure -> FAIL_INTEGRITY. No automatic new
intake, model fitting, R1/final evaluation, commercial-rights promotion or
publication follows any verdict. The owner reviews the achieved result first.

Later human reference-review workload is estimated separately in the dataset
plan; it is not part of CPU-hours or an authorization to contact/pay reviewers.
Paid services and the existingUSD300journal ceiling remain outside execution.
