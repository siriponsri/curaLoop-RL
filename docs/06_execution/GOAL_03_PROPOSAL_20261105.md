# Proposed Goal 3: real benchmark readiness and a stronger method decision

5 November 2026, Asia/Bangkok. **PROPOSED / READY_FOR_OWNER_REVIEW.**
This document is a proposal, not authorization to extract data, inspect new
labels, launch compute, train a model or run the final study. Goal 3 has not
started. The owner requested a proposal after supplying the FS-Mol archive.

## Destination

Deliver an auditable real-data benchmark and a falsifiable method specification
for testing transfer across biological families and operating conditions.
The research ambition is efficient molecular discovery on unfamiliar targets,
with a planner that values pending information and accounts for decision cost.
Goal 3 should determine whether the next implementation is justified; it does
not claim that data curation alone establishes a high-impact contribution.

## Verified starting point

- [Goal 2](../03_research/GOAL_02_RESULTS_V1.md) completed 180 development runs.
  Its content relaxation preserved decisions but increased policy time by
  24.3%. It did not demonstrate a discovery advantage or select WAIT on the
  real-data panel. These negative results remain immutable.
- The owner-supplied FS-Mol archive passed [byte verification](../evidence/fs-mol-receipt-20261105-v1/README.md).
  Members remain unopened and labels uninspected. A matching archive is not
  a cleared scientific split or a complete dataset-rights review.
- The existing [source assessment](../03_research/GOAL_02_DATASET_ACQUISITION_V1.md)
  identifies FS-Mol as a potency-threshold transfer complement, not sparse HTS.
  License notices, task-count discrepancies, family identity and overlap need
  release-specific resolution. Existing Tox21 development tasks stay exposed.

## Proposed work and dependency order

| Ticket | Work | Deliverable and resolution test |
| --- | --- | --- |
| G3-01 | Inspect archive headers safely, validate paths and index source files. Reconcile paper, release, assay/target identity and license notices. Preserve the original tar. | Data-source register with exact paper/version/hash/permission/endpoint fields and explicit unresolved entries; no silent count or phenotype corrections. |
| G3-02 | Map targets to a declared biological-family hierarchy using documented identifiers. Audit canonical structure, duplicate and near-neighbor overlap with development data. Select roles from source/metadata/features before evaluating outcomes. | Family/source register, eligibility/exclusion ledger and reproducible grouping rule. Aim for at least 12 evaluable held-out families, with development families separate; actual available counts must be reported, not manufactured from assay IDs. |
| G3-03 | Specify development, validation and final roles and held-out operational conditions. Retain source splits as provenance while auditing whether they meet CuraLoop's stronger requirements. | Versioned split manifest and access ledger; source family and molecule overlap quantified; no final labels sent to agents or policies during design. |
| G3-04 | Review the Goal 2 failure and select one stronger, literature-challenged model/planning approach for Goal 4. | Method decision stating objective, belief/uncertainty semantics, root-action scope, bound assumptions, strongest comparators, compute accounting, ablations and falsification criteria. No claim that a generic inequality is new. |
| G3-05 | Audit the combined package independently and assess its relevance to JCAMD. | English readiness report with PASS/FAIL/UNRESOLVED by gate, exact counts, journal evidence gaps and a concrete recommendation for Goal 4. |

G3-01 is the ready frontier after owner approval. G3-02/03 depend on source and
identity closure. G3-04 can proceed alongside metadata/feature audits; its
empirical evaluation belongs to Goal 4. No favorable campaign result may decide
which families or operational regimes enter the final panel.

## Data roles, labels and realistic scope

Use two clearly separated evidence tracks if their gates close:

1. FS-Mol supports assay/target transfer using its published potency-derived
   binary labels. Resolve the paper/release discrepancy and preserve the actual
   label definition. Do not reinterpret its positives as sparse HTS hit calls.
2. A paper-backed sparse experimental-screening source, such as a permitted
   prepared LIT-PCBA release or a properly cleared assay panel, is a complement.
   The choice depends on source rights and endpoint evidence, not method wins.
   Tox21's three exposed development tasks cannot become untouched tests.

Report effects separately by source and endpoint definition; do not pool raw
positive counts across different meanings/prevalences as one discovery claim.
Family count is a design target, not a claim of statistical independence.
Repeated seeds do not create more families. Costs/durations remain simulated
unless genuine operational measurements with their own provenance are obtained.

Before parsing assay rows, freeze an access plan: source metadata and structures
may support role assignment; semantic inspection of labels is limited to
declared development tasks. Trusted preparation must isolate any label bytes
encountered while parsing row-oriented files, suppress their display/export,
record access and keep final labels sealed from agents/selection code. Any
unavoidable human/agent exposure changes the recorded role and must not be
called untouched afterward. Final execution remains a later goal.

If a required source cannot be obtained, give the owner its official URL,
exact file/version and ignored destination path; continue independent work.
Do not substitute synthetic labels or a more favorable biological task.

## Stronger method decision

The leading option to investigate is a conditional hypothesis-mixture belief
with a content-sensitive recourse calculation. It could avoid the artificial
information from a small fixed set of fully sampled label worlds and avoid
rescoring the whole pool for every fantasy branch. This is a hypothesis for
design/review, not an implemented improvement or a demonstrated cause of the
Goal 2 failure. Select or reject it after the closest-work comparison.

Mandatory challenges include ordinary unpruned rollout, Azimi2011-style
scheduling, ENS/ANS active search, analytical Greedy, frozen-model selection,
nearest-hit and a cheap content-aware WAIT rule. State which are objective-
matched adaptations and which theory does not carry over. Goal 4 must measure
both discovery and total decision cost, with identical predictors/beliefs where
needed to isolate acquisition changes. Existing standard relaxations, policy
switching and posterior-distance inequalities are not novelty by themselves.

No fitting, benchmark campaign or broad hyperparameter search is included in
Goal 3. The method contract must explain the proposed computational advance
and a test capable of rejecting it before a large evaluation is justified.

## Proposed resource ceiling after approval

- Existing local machine and owner-authorized dr-train only, after live
  allocation/job checks. Parent is the sole repository writer; read-only
  subagents own source/data review, method/closest-work review and English/
  journal review. No shared-file concurrent edits or other-job changes.
- At most 2 CPU workers, one thread each; 8 cumulative CPU-hours across data
  preparation/audits, measured separately from human/agent planning time.
  Stop when that cap is reached and report the exact checkpoint.
- At most 4 GiB RAM per worker, 8 GiB total, and 16 GiB additional scratch/output
  disk above the retained archive. Check available disk before writes. Stream
  or selectively extract; validate archive paths, reject links/path traversal
  and cap expanded bytes/member counts before extraction.
- At most 200 MB of additional official metadata/feature downloads, excluding
  the already received archive. Another large dataset requires an explicit
  acquisition record and a revised bounded allocation or owner download.
- No GPU, paid resources, dependency upgrades, key/config changes, editorial
  outreach, journal submission or final-study execution.

These are proposed engineering ceilings, not measured runtime estimates or
an approved final-study budget. Stop on invalid archive paths, uncertain source
rights, final-label exposure, resource exhaustion or inconsistent identities;
retain the evidence and continue work that does not depend on the blocked item.

## Acceptance and handoff

The deliverables are an English dataset card, source/family registry, feature-
overlap report, split/access manifests, method decision and readiness report.
Every admitted task needs a paper-backed source, exact release identity,
permitted-use evidence, endpoint definition and auditable exclusion history.

Recommend **READY_FOR_GOAL4** only if the data gates close, the intended
held-out family scope is supported and one falsifiable stronger method contract
survives the closest-work review. Otherwise report **REVISE_DATA**,
**REVISE_METHOD** or both, with exact missing inputs. A completed audit must not
be mislabeled as a benchmark-ready dataset or successful algorithm.

No confirmatory material-effect threshold is introduced. Future effect and
uncertainty analysis must respect family/source dependence and operational
transfer. Stop after the Goal 3 report; Goals 4–6 require their own direction.

## Journal rationale and current evidence

Inference: a useful method that transfers across molecular families and
operational shifts, supported by well-designed retrospective evidence, is a
more credible JCAMD contribution than more assay IDs or an isolated bound.
The [current JCAMD scope](https://link.springer.com/journal/10822/aims-and-scope),
checked 5 November, allows proper retrospective validation for novel methods
or innovative computational strategies and prioritizes experimental evidence.
This proposal does not establish acceptance or relax that standard.

The [FS-Mol paper](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/8d3bba7425e7c98c50f52ca1b52d3735-Abstract-round2.html)
is recorded in the existing source review. Its page timed out during this
proposal's refresh; no new full-text inspection is claimed. The pinned
[repository data license](https://raw.githubusercontent.com/microsoft/FS-Mol/92aa95daba3f43863227e65be85a07b4a2ee754f/LICENSE)
was read again; it distinguishes dataset CC BY-SA 3.0 from software MIT. The
archive's different notice remains an open release-specific item.

Proposal preparation used read-only repository/source checks. It did not open
the archive or start any Goal 3 task. **Next actor: owner, to approve or revise
this bounded contract.**
