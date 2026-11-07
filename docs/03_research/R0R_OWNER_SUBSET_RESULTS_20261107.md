# R0-R: results from the owner's three supplied articles

Date: 7 November 2026. Base checkpoint: `351814ceb6fa8d07b5051aa53ec2da74b66c9f56`.
Status: **OWNER_SUBSET_PROCESSING_COMPLETE; REFERENCE_REVIEW_PENDING; SCIENTIFIC REVISE**.
The owner instructed using only three of the six requested articles because the
others require purchase. All three supplied main articles were processed. Two
related supplements were inspected but supply no admitted methods reference.
No further download or purchase is requested for this subset.

## Observed coverage

| Evidence | Result | Interpretation |
| --- | --- | --- |
| Owner inputs | 3 main PDFs + 2 supplements, 5,793,019 bytes | Three articles, not five independent papers |
| Main-article identity | All 3 fixed DOIs verified in front matter; all 5 source hashes reread | Identity checks, not publisher authentication or reuse permission |
| New masked methods | 16 retained blocks across the 3 main articles | Parent-readable procedural context; not independently adjudicated |
| Total source availability | 4/7 documents, including the earlier S1 source | Access-limited development sample |
| Frozen cases with document methods | 9/12 | Includes 2 cases whose metadata projections were rejected |
| Admitted cases with document methods | 7/10 | Document coverage does not establish exact assay-to-procedure mapping |
| Admitted records with document methods | 26/86, representing 20 distinct molecules | Record identities, not observed numerical outcomes |
| Remaining source-unavailable cases | 3/12, one from each deferred document | Retained as unavailable, never negative or replaced |
| Null standard units | All 17 remain unresolved | Their source is CHEMBL1136971, outside the supplied subset |
| Independent reference judgments | NOT_RUN | All source-supported interpretations remain parent drafts |
| Verified molecular decision improvement | NOT_ESTABLISHED | No policy, ranking, activity or final-outcome evaluation |

The unchanged full frame is twelve assays, seven documents and three frozen
annotation components. It is not twelve independent biological families. Source
availability covers 75% of cases but only about 30% of admitted records; reporting
case coverage alone would hide this imbalance. No access-based population refill
or complete-case success rate is used.

## What each supplied article contributes

**S2: perforin-related cytolysis**, CHEMBL1140224,
[10.1021/jm801063n](https://doi.org/10.1021/jm801063n).
The retained Experimental Section passages on physical PDF page 10 describe
lysis and cytotoxicity procedures using erythrocyte and nucleated-cell systems,
including controls and concentration-series measurements. This supports a
document-level cytolysis context for the sampled Inhibition/% readout. It does
not identify which retained procedure belongs to CHEMBL1000319. A database B
category alone must not be treated as proof of a direct affinity endpoint.
Do not convert percentage inhibition into Ki, IC50 or an activity threshold.

**S3: EBP and receptor binding**, CHEMBL1140235,
[10.1021/jm800965b](https://doi.org/10.1021/jm800965b).
Physical PDF pages 7-8 describe radioligand-binding procedures, cell culture and
a separate MTT cell-growth assay. This establishes that multiple assay systems
occur in the same document. It does not justify assigning one system to every
record from that document. Numeric masking obscures receptor suffixes and some
cell identifiers, so exact case mapping remains unresolved. CHEMBL1000140 stays
projection-rejected; methods availability does not repair its absent metadata.

**S4: ghrelin receptor systems**, CHEMBL1156448,
[10.1074/jbc.M609796200](https://doi.org/10.1074/jbc.M609796200).
Physical PDF page 3 describes receptor constructs/mutations, transfected cells,
phosphatidylinositol turnover, an SRE reporter and competition binding. Several
systems can therefore share a target label. Exact construct, pathway and
assay-specific procedure mapping remain unresolved for the four frozen cases.
Shared target and IC50/nM metadata do not establish interchangeability. The
separate rejected case CHEMBL1001324 remains excluded from admitted-record counts.

The [current review packet](R0R_REFERENCE_REVIEW_V2_20261107.md) retains S1 and
all twelve case dispositions, source locations and review questions. These
paragraphs are concise paraphrases of masked methods, not source quotations,
confirmed reference labels or discoveries of database errors.

## Supplements and extraction limits

Both supplements match most or all distinctive tokens of their corresponding
bibliographic title and the owner supplied their associations. Neither contains
the expected DOI in the first two pages. Association status is therefore
OWNER_LINKED_TITLE_MATCHED_NOT_PUBLISHER_AUTHENTICATED. No publisher verification
or commercial reuse right is inferred.

- CHEMBL1140224 supplement: an explicit Experimental Section occurs on physical
  PDF page 18, but no block meets the conservative biological-method criteria.
  Status QUARANTINE_NO_ADMISSIBLE_METHODS.
- CHEMBL1140235 supplement: no admitted explicit methods boundary was found.
  Status QUARANTINE_UNVERIFIED_PDF_SECTION_BOUNDARIES.

These are extractor dispositions, not proof that the supplements contain no
useful information. They do not add two articles or two reference sources.

The trusted reader consumes full PDFs in memory, selects explicit methods
boundaries, drops result/table/figure and nonprocedural blocks, and masks decimal
numerals before any model view. Only masked methods were presented to the
assistant. A native PDF reading order and a keyword filter do not guarantee
perfect semantic separation or complete extraction. Numerical masking also
removes useful construct/protocol identifiers. No unmasked page was rendered to
the assistant, and no independent visual/semantic methods audit was performed.
The retained text is suitable for a cautious draft, not self-certified gold.

Owner-supplied full PDFs remain in the ignored owner-methods input directory.
Parser-generated unmasked full-text files were not saved. Neither PDFs nor full
masked passages are included in public Git. Paper copyright and commercial data
rights remain separate from ChEMBL metadata terms.

## Retained resource failure and bounded repair

The first independent job for CHEMBL1140235 exhausted its 20-second CPU ceiling
before producing a masked output; the receipt reports 20.078125 process CPU
seconds, including monitor granularity. The initial successful independent PDF
job used 19.84375 seconds. The evidence is consistent with substantial library
startup cost; it is not a controlled import-time profile.

A fresh single-process batch imported the existing PDF library once under an
OS-enforced one-CPU/512-MiB/60-CPU-second guard, then monitored each file at its
unchanged 20-second CPU and 60-second wall ceilings. It processed only previously
unattempted remaining files. A separate controlled local-processing repair then
read the identical hash-verified CHEMBL1140235 bytes with the warmed reader. The
failed job and its 20-second reservation remain visible and charged. This was
local processing within the approved three-paper scope, not a retry of the
publisher/repository HTTP STOPs. The repair output passed DOI and masking checks.
No package installation, system change, new download or new resource grant was
used. Exact executed script hashes are archived with the receipts.

## Verification and accounting

Fourteen owner-subset checks passed: fixed case/question retention, exact safe
projection fields/counts, old R0 artifact hashes, original R0-R response hashes,
all supplied-file hashes, main DOIs/masked outputs, numeral masking, five masking
fixtures, supplement quarantine, failure/charge retention, unchanged deadline
and no new HTTP/source replacement. This is engineering/provenance evidence;
independent scientific adjudication remains NOT_RUN. Runtime application tests
were not rerun because the UI, engine and scientific transition logic did not
change.

The ledger retains 41 HTTP attempts, 36 PASS and 5 STOP. This subset added zero
HTTP requests. Total charged decoded/read bytes are 13,076,188/33,554,432,
including metadata preview, local reads and the retained failed read. Distinct
owner-file bytes are 5,793,019; do not confuse repeated reads with new articles.
Conservative charge is 3,200/3,600 CPU seconds, including the existing 600-second
utility allocation, original 41 network reservations, metadata preview and six
20-second local processing reservations. It is not measured total CPU use.
Partial enclosing-process receipts total 103.046875 CPU seconds at the subset
checkpoint; overlapping file-phase receipts are excluded from that sum.

The 154 private files / 1,133,634 bytes were reread and hashed at the subset
checkpoint; the five owner inputs were separately reread. All 76 closed R0
private artifact hashes remain unchanged. A final documentation audit may add
a later receipt/index; use the latest index named by the evidence README.

The original window remains 06:16:25Z-14:16:25Z on 7 November 2026, ending
21:16:25 Bangkok. Unused time/resources do not release additional source intake
or a next phase. No unattended worker remains active after closeout.

## Research decision and next actor

The supplied subset establishes that bounded methods extraction can add useful
procedure-level context. It has not established an assay-specific decision
change, independent reference benchmark, adaptive-planner advantage or commercial
savings. Journal readiness is **NOT_READY**; the scientific gate remains
**REVISE_PENDING_REFERENCE_REVIEW**.

Next is the owner's review of the source-linked drafts: agree, revise or retain
UNRESOLVED for the procedure mapping and endpoint compatibility. Owner agreement
is a documented review, not automatically independent domain-expert gold. The
three purchase-only documents stay deferred. No more files are required from
the owner to complete this subset's processing.

After that review, prepare a concrete decision on whether the unresolved mapping
problem supports a bounded adjudication study or needs a research redesign.
Present its population, endpoint, closest baselines and budget for an owner
decision before any P1/R1 or new phase. Do not fit models, evaluate final outcomes
or claim that a methods field fill demonstrates planning value.

Evidence: [current evidence index](../evidence/r0r-chembl-20261107-v1/README.md),
[source manifest](../evidence/r0r-chembl-20261107-v1/owner-source-manifest-v1.json),
[case candidates](../evidence/r0r-chembl-20261107-v1/reference-candidates-v2.json),
[subset checks](../evidence/r0r-chembl-20261107-v1/owner-subset-checks-v1.json).
