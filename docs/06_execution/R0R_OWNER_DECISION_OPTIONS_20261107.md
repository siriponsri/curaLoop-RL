# Owner decisions after the R0-R three-paper subset

Date: 7 November 2026. Inspected main: `54eaed07b2a9dd38d01e1377060ebc06b5b227fb`.
Status: **READY_FOR_OWNER_DECISION; PROPOSAL ONLY; R0-A1 NOT_RELEASED**.
This document records options, not a new compute clock, data permission or phase
transition. Existing source/protection ledgers remain unchanged.

## Evidence and decisions already made

The [subset report](../03_research/R0R_OWNER_SUBSET_RESULTS_20261107.md),
[reference packet](../03_research/R0R_REFERENCE_REVIEW_V2_20261107.md) and
[current aggregate](../evidence/r0r-chembl-20261107-v1/interim-summary-v6.json)
support the following current state:

- Three owner-supplied main papers are processed. Together with earlier S1,
  document methods cover 9/12 frozen cases, but only 7/10 admitted cases and
  26/86 admitted metadata records. A document-level link is not an exact
  assay-to-procedure mapping.
- All 17 null-unit records come from a deferred paper. They remain unresolved;
  this proposal does not promise to resolve them.
- The three admitted ghrelin-target cases each contain one projected record.
  Those sampled records alone do not establish a useful molecular choice panel.
  Resolving construct names is therefore insufficient for scientific GO.
- All case-specific reference mappings remain unadjudicated. There is no
  demonstrated molecular decision gain, independent gold or journal readiness.
- The masking removed useful digits in cell/receptor/construct identifiers.
  This is a potential extraction limitation, not proof that the underlying
  science contains useful uncertainty or that selective evidence has value.

Already settled: retain ChEMBL37 as the core candidate; retain the approved
shared-context evidence/measurement research direction as a hypothesis; use
only the supplied three new articles; defer the other three without purchase;
keep old final outcomes closed and require an owner decision before advancing.
These decisions are not being asked again. The owner is not being asked to
certify unfamiliar assay science merely to unlock work.

## Decision map

| Ticket | Decision owner | Options | Recommendation and consequence |
| --- | --- | --- | --- |
| R0-D6 | Project owner | Permit narrowly controlled protocol/entity identifiers from existing inputs, or retain blanket numeral masking | Permit only identifiers under R0-A1 below. This may resolve extraction-induced ambiguity; it releases no numerical activities or results. Retaining blanket masking preserves the present limit and may leave exact mapping infeasible. |
| R0-D7 | Project owner | A: one last bounded feasibility audit within R0; B: prepare a revised research question now; C: prepare a product-first plan while molecular-paper work is paused | A is recommended because it tests the current bottleneck using existing files before any expansion/training. B/C are legitimate pivots but require a separate concrete design; selecting either does not launch an unbounded implementation. |
| R0-D8 | Project owner, later domain reviewer | After reference feasibility: nominate a qualified reviewer; explicitly retain author-only exploratory references; or stop the reference-dependent study | Defer this choice until A1 produces a usable packet. Qualified review is needed for an independently adjudicated reference claim. Neither owner approval nor another automated check establishes scientific gold. No reviewer contact/payment is authorized here. |
| R0-D5 | Project owner | Later: continue, revise or stop R0, then separately release any P1/R1 | Not ready for phase-advance approval today. A1 results must separate reference feasibility, action relevance, panel support and unresolved novelty. |

Ready frontier: R0-D6 + R0-D7. Dependency: those decisions -> R0-A1 if chosen ->
owner readout -> R0-D8 / remaining data-and-method decisions -> R0-D5.
No later node starts automatically.

## Recommended package A: R0-A1

Purpose: determine whether the present data can support a source-grounded,
decision-relevant reference problem, or whether the current thesis needs revision.
This is a final bounded feasibility round in R0, not R1 or a method benchmark.
It preserves the intended joint evidence/measurement contribution. It does not
silently replace that contribution with an annotation benchmark or a connector.

### Proposed access and resource contract

- Fresh cap: **1 CPU-hour / 8 elapsed hours**, including 600 utility CPU seconds;
  one local worker, at most 1 CPU / 1 GiB. No SSH, GPU or paid service. These are
  ceilings, not measured predictions or additions to any old ledger.
- Clock starts only at an explicit owner release of this package. Fresh owned
  root/version then; do not alter old roots, frozen snapshots or reservations.
- Zero network/source requests. Use only existing cached metadata, admitted
  outcome-free record identities, the three supplied main PDFs and existing
  masked S1 evidence. Supplements stay quarantined; unavailable papers stay
  unavailable. No re-retrieval of S1 or stopped HTTP sources.
- Read only the original twelve frozen case roles. Cached metadata has fifty
  assay records, including structured cell/organism/tissue/subcellular/format
  fields and description fields. Only selected-case fields/spans can enter the
  new projection; do not display complete original descriptions.
- Allow source-located **entity identifiers only**, such as cell-line names,
  receptor subtype suffixes, wild-type/mutant names and mutation positions, in
  otherwise masked methods and selected-case metadata. These numbers are part
  of identifiers. Biological organism/system and stated endpoint/unit metadata
  remain allowed. Do not unmask general numerical protocol conditions, activity
  values, effect sizes, dose-response results, compound rankings, tables,
  figures, results sections or protected final outcomes.
- Use a trusted allowlist/filter before model view. Ambiguous number roles or
  uncertain section boundaries remain quarantined. Previously quarantined
  outcome-bearing descriptions are not released wholesale. Check explicit
  positive/negative leakage fixtures before using the revised extraction.
- Keep source/derivation locations and hashes, retain every rejected span and
  failure disposition without publishing raw passages. Read at most 32 MiB in
  aggregate, 4 MiB per source file and 64 MiB new working storage. Scientific
  input files are read-only. No new activity projections, molecules or outcomes.
- One audit round only. Report the result even if the subset remains inadequate;
  no automatic second round, source expansion, model fitting or P1/R1.

### Work and reviewable deliverables

1. **Reference feasibility.** Produce a twelve-row matrix showing metadata-only
   context, source-supported candidate context, source location, exact mapping
   status and reason for UNRESOLVED/unavailable/rejected cases. Preserve the
   denominator and distinguish extraction-induced uncertainty from natural
   scientific ambiguity. New draft judgments are not independent gold.
2. **Decision relevance.** Apply the same permitted complete metadata to a
   competent baseline before using paper evidence. Determine whether a cited
   context fact could change a declared compatibility/transfer eligibility
   decision that metadata alone leaves open. Record clear-context controls and
   unchanged decisions. A candidate eligibility change is not a demonstrated
   compound-shortlist or planner improvement.
3. **Support feasibility.** Audit only admitted row/molecule/context identities
   to determine whether candidate decisions have more than one molecular
   alternative and relevant shared support. This is a necessary structural
   check, not proof of nonmissing activity values, adequate sample size or
   statistical power. Flag where a later bounded outcome-support qualification
   or an owner-approved population change would be required.
4. **Contribution readout.** State which part, if any, goes beyond complete
   upfront metadata resolution. Retain the existing closest-work/reduction
   concerns. Do not claim a new algorithm from a dependency graph or an LLM.
   Prepare the next decision with its exact remaining population, endpoint,
   reference, rights and method questions rather than launching it.

Final artifacts: revised extraction/access audit; twelve-case comparison matrix;
candidate context-to-decision dependency examples or explicit absence of them;
support/attrition table; resource/failure ledger; English readout and handoff.
Normal main documentation/code delivery remains authorized; external publication
or tool-team writes do not.

### Resolution test and stop rule

Return **REFERENCE_FEASIBLE_FOR_REVIEW**, **REVISE**, or
**INFEASIBLE_IN_CURRENT_SUBSET**, with reasons. This is a feasibility verdict,
not a confirmatory effect threshold or a scientific phase GO.

A favorable feasibility recommendation requires a traceable candidate reference,
natural decision sensitivity beyond complete allowed metadata, and plausible
nondegenerate identity support for later testing. A single example is at most
an existence signal, never sufficient independent scope, algorithm novelty or
publication evidence. Independent reference review and actual outcome support
remain later gates even after a favorable audit.

If richer allowed metadata already resolves every case, or source evidence only
fills descriptive fields, report that the adaptive-evidence rationale is not
supported by this slice. If the problem remains masked/unavailable or the panel
is too sparse, distinguish that from a negative scientific result. Recommend a
bounded redesign/expansion decision; do not manufacture ambiguity or refill the
sample to obtain a positive result.

## Alternatives B and C

**B: prepare a revised research question before more reference work.** Advantage:
avoids another local audit if the owner no longer prioritizes the current
shared-context thesis. Cost: the primary contribution, endpoint and comparison
must be reconsidered; no replacement is yet qualified. A benchmark-only route
would need an explicit contribution/venue rationale and independent references.
This option authorizes preparing a proposal, not new data or experiment intake.

**C: prepare a product-first plan and pause molecular-method publication work.**
Advantage: can focus the existing Evidence Workspace/Decision Workbench on a
reviewable source-to-report workflow. Cost: it does not repair the scientific
method gap or establish demand, customer savings or journal readiness. A later
plan must specify a real workflow, correctness/benefit comparator and intended
users; deployment, team writes and customer contact need their own authority.
This option also authorizes proposal preparation only.

No option buys the three missing papers, silently imputes the seventeen units,
opens old final outcomes, or claims commercial data clearance. None guarantees
closing R0 or producing a publishable result.

## Evidence and handoff

PASS: current Git checkpoint/clean main inspected; current aggregate and review
packet read; cached metadata schema inspected without emitting descriptions;
all twelve roles and the sparse ghrelin-case counts reconciled. This was planning
only: no new source retrieval, unmasking, activity intake or scientific execution.
Independent scientific review NOT_RUN.

Recommended owner response: approve **A / R0-A1 with the above identifier-only
access and 1 CPU-hour / 8-hour / local-one-CPU limits**, or select proposal B/C.
If a qualified reviewer is already available, the owner may name that role later;
no reviewer or purchase is required to make today's feasibility-audit decision.
