# New local-agent proposal: review and scope decision

Status: **REVIEWED; SCOPE AMENDMENT NOT APPROVED**. 13 November 2026.
The owner's current request resumes LR-DC2 and asks to read the attached
proposal first. It does not explicitly adopt all instructions in that document.
The attachment itself is marked PROPOSAL_FOR_OWNER_REVIEW. Its original bytes
are retained privately with a source hash in the resume-review manifest.

## Current authority and clock

Resume began at the first trusted clock:13 November2026 11:51:07 UTC,
18:51:07 Bangkok. The effective deadline is20 November2026 11:51:07 UTC,
18:51:07 Bangkok, following the earlier explicit owner clock amendment.
There is no automatic clock extension while scope is discussed.
The unchanged total caps are64 CPU-hours and24 allocated GPU-hours.
Pre-pause retained CPU allocation remains2,430 seconds (0.675 hours), leaving
63.325 CPU-hours of unreserved allowance. No GPU allocation/model call occurred.
This allocation is not a claim of actual measured CPU consumption.

The new ledger state is RESUMED_REVIEW_PENDING_SCOPE_DECISION. It deliberately
fails the research runner's ACTIVE-state gate. The original release, original
clock/pause receipts, all prior bookings and historical results remain intact.
No changed study, model download, SSH/GPU run, archive extraction or evaluation
was performed during this proposal review.

## What the attachment changes

| Decision | Approved LR-DC2 proposal | New attachment | Review recommendation |
| --- | --- | --- | --- |
| Product demonstration | Contract library plus existing workbench integration | One real local compound-table/RDKit/export workflow, approximately2-3 adapters | Prefer the concrete end-to-end workflow; its engineering acceptance is separate from method efficacy |
| Mechanism | Question-conditioned contracts and targeted repair | Requirement-to-artifact/version bindings; invalidation after edits; targeted repair | A sharper hypothesis, but persistent state and invalidation are not automatically novel |
| Main comparator | C minus generic self-debugging T, with other controls | Proposed mechanism minus checklist seeing the same obligations and public check results | Prefer the stronger matched checklist comparison for attribution |
| Models/matrix | Two fixed model families,8 development/32 locked tasks,816 model missions | One primary model; tasks/seeds/matrix determined from eligible evidence and feasibility before freeze | Sensible for solo scope, but a material change requiring owner adoption |
| Decision thresholds | Proposed+10pp signal, positive model-specific directions and clustered interval | Complete faithful evaluation without treating a positive effect as the delivery condition | Separate positive efficacy evidence from complete negative/inconclusive delivery; never rewrite old thresholds/results |
| Fallback after feasibility failure | Stop/report first failed gate; no substitution | Potential bounded software study/pilot | Specify that fallback's scope in the amendment; not automatic permission to search for another benchmark |
| Resources |64 CPUh/24 GPUh, existing Typhoon plus approved Qwen download, protected sources closed | Retains accounting but requires an explicit new scope/resource amendment | Retain remaining caps; no paid provider or new model search without approval |

Recommended candidate contribution: determine whether a version-bound evidence
ledger improves native scientific-task success over a checklist with the same
obligations, observations, model and budgets. An obsolete file check must not
certify a changed artifact. A targeted invalidation/repair ablation can test that
specific mechanism. The claim remains conditional; it may overlap prior work
or have no useful natural error opportunity.

## Evidence and literature verification

This is a targeted source check, not a full related-work review or novelty PASS.

- [ContractBench v2](https://arxiv.org/abs/2605.17281): abstract and source identity
  inspected. It studies temporal validity and byte integrity of tool observations
  with programmatic evaluation. It is related counterevidence to a generic
  contract novelty claim, not identical evidence for arbitrary scientific
  requirement completeness. Its acceptance statement is the arXiv authors'
  metadata, not a separately verified proceedings record.
- [StateM](https://arxiv.org/abs/2608.15089): abstract/source identity inspected.
  Durable states, checked transitions and recoverable procedures already appear
  there. No native reproduction or transfer of reported score gains is claimed.
- [ToolUniverse interaction protocol](https://zitniklab.hms.harvard.edu/ToolUniverse/en/guide/interaction_protocol.html):
  official schema/local-Python/MCP sections inspected. Reuse/compatibility should
  be assessed before duplicating scientific tool interfaces; the page does not
  establish CuraLoop integration or runtime performance.
- NeuDiff Agent PMC13440046: direct access returned a browser access-check page.
  Its detailed method claims in the attachment are **not verified this turn**.
  Do not cite the attachment alone as a verified method comparison.

## Exposure and scientific boundaries

The attachment reports that an earlier assistant context received a public
BBBC002 cell-counting demonstration with reference code. Record this as
**reported exposure**, not independently reconstructed exposure in this review.
The exact task ID and connected source/data lineage remain unmapped. Until
resolved, treat BBBC002-related tasks as exposed/development or exclude them
from a locked cohort. Do not claim the whole benchmark is contaminated or that
the current reviewer has inspected archive gold. No public project-demo page
was opened during this review to avoid unnecessary additional exposure.

Keep the downloaded ZIP and its provenance. Download completion does not prove
native-oracle feasibility, a qualifying cohort, novel mechanism or journal fit.
No AWS capability, expert validation, user value, clinical efficacy or business
ROI follows from a local workflow demonstration. The earlier US$300 publication
budget remains a venue constraint; no new venue's costs are approved here.

## One consolidated decision recommended before execution

**A: adopt a versioned amendment based on the new attachment**, within the
unchanged remaining CPU/GPU ceilings and current seven-day deadline. Specify:
one local RDKit compound-table workflow; the version-bound requirement/evidence
mechanism; a matched checklist primary comparator; one primary model drawn from
the already authorized models; fixed bounded feasibility before choosing and
freezing the matrix. Suggested feasibility subceiling:4 CPU-hours/1 GPU-hour,
at most the existing96 development provider-call cap, charged to existing stage
caps. No model search, new dataset, paid API or automatic scope expansion.
Finalize the numerical matrix before locked execution, never from its outcomes.
Any permitted software/pilot fallback must be bounded explicitly in that same
amendment. Complete negative/inconclusive results are legitimate deliverables.

The proposed bounded fallback is to finish the same local workflow, its real
model execution, engineering checks and a negative/inconclusive feasibility
report if external native evaluation is infeasible. It does not authorize a
replacement benchmark, a second mechanism, model search or outcome-driven
retries. Clearly label the unrun external comparison and limit the manuscript
to evidence actually obtained. This fallback is part of option A, subject to
the same cumulative caps and deadline.

If A is selected, execute continuously through these milestones without routine
phase approval requests:

1. Verify source-level distinction, exposure/rights, available GPU/model and
   native-scoring feasibility within the subceiling above; preserve failures.
2. Implement and test the one local CSV-to-RDKit-to-report workflow with real
   artifacts, durable jobs, cancellation and restart recovery where supported.
3. Freeze eligible tasks, lineage groups, model/prompts, all arm budgets,
   numerical matrix and scoring before locked execution. Compare proposed
   version binding primarily with the equal-information checklist; retain
   self-debugging, deterministic where applicable, and invalidation ablation.
   Use only development timing/metadata for sizing, never locked outcomes.
4. Run once under the frozen protocol, retain every failed/fallback attempt,
   analyze native task success, uncertainty, completion errors, coverage and
   total costs. Deliver reproducible artifacts, localhost evidence, English
   guide/manuscript/figures and an honest publication-readiness assessment;
   commit/push main. Use the bounded fallback above if admission fails.

**B: retain the original LR-DC2 design** and treat the attachment as design
reference only. The fixed8/32/two-model/816-mission design and its original stop
rules remain, with no substitution of the new checklist primary contrast.

No choice is recorded as approved by this document. Routine phase approvals are
not proposed after a complete amendment is approved. Original final16, private
CF1 rows, hidden outcomes, frozen results and old ledgers remain protected.
