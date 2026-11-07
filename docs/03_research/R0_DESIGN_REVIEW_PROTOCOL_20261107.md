# R0-Design Review: contribution and benchmark protocol

**Design proposal ready for owner/domain review. Scientific R0 remains REVISE.**
This document retains the original molecular-decision question and support
floors. It proposes a replacement construction protocol; it does not adopt a
new split, certify a family, qualify numerical support or start R1.
The [machine-readable contract](../../research/configs/r0_design_review_protocol_20261107_v1.json)
is marked `execution_authorized: false`.

## One primary contribution

**Test a policy that chooses when to resolve shared assay-context evidence,
when to reveal a supported molecular measurement, when to recommend compounds,
and when to abstain, using reference-endpoint discovery utility under explicit
resource limits on held-out reviewed family/source units.** Hold the predictor
fixed when testing the policy contribution.

The intended research result is a defensible improvement on a common resource
frontier, with source facts linked to changed admissibility or molecular actions.
A retrieved paragraph, an agent wrapper, a dependency graph or a new name for
value of information is insufficient. The source-linked benchmark and typed
R&D interfaces support this one research contribution; they are separate
engineering deliverables, not substitutes for a method result.

Method novelty is **not established**. The cached [closest-work ledger](../02_literature/R0_CLOSEST_WORK_20261107.md)
and [formalization](R0_METHOD_FORMALIZATION_20261107.md) already identify
decision-region determination, multifidelity active search, assay matching,
assay-aware prediction and annotation as relevant prior work. This phase made
no fresh paper/version checks. Before a later method claim, document the
precise reduction to those controls and any computational distinction, then
test it. A finite deterministic recommendation-stability special case can
reduce to existing decision-region problems; no new theorem is claimed here.

The decision-changing witness required in development is concrete: name the
unresolved context factor, its source-supported alternatives, the supported
edges/actions affected, the decision before resolution, and the decision after
the independently reviewed fact. Keep the predictor and all other observations
fixed. A witness establishes conditional action sensitivity, not better utility;
the later matched experiment must establish the latter.

## What the existing evidence changes in this protocol

The [cached diagnostic](../evidence/r0-design-review-20261107-v1/design-diagnostic-v1.json)
uses only the old frozen frame and written evidence. It is not a new search.

| Observed construction failure | Design response |
| --- | --- |
| Only 11 of 200 selected targets had the declared reference-capable priority; seven of 1,254 selected assays had a nominal 128-ID reference count | Census nominal support before the bounded draw; prioritize reference-capable opportunities |
| Equal allocation over 15 broad functional categories and a 20-assay/target draw could omit useful references or auxiliaries | Functional labels become descriptive strata; require complete whole-target graphs within declared caps |
| Four shared-source components contain 85 frame targets, including six tagged final and one validation | Close family/source/exposure constraints before any proposed evaluation role; preserve old labels as provenance and quarantine conflicts |
| CHEMBL8809 is a known planning molecule without a reconciled canonical alias in the returned derivations | Resolve its structure from the pinned DB under a later metadata-only grant; absence of the exact ID is insufficient |
| One nominal development pair, no accessible methods bodies or independently reviewed facts | Keep the evidence-relevance gate closed; do not claim that reading papers improves decisions |
| A heuristic auxiliary search can miss a feasible combination outside its shortlist | Require exact search completeness or mark UNKNOWN; a failed prefix is not evidence of absence |

These observations concern the inspected frame. They do not prove universal
ChEMBL infeasibility, method failure or lack of useful facts in the source papers.

## Population, task and estimand

Use the same pinned **ChEMBL 37** release. A task has one reconciled SINGLE
PROTEIN target/accession/organism, one explicit reference construct/context,
one reference endpoint type, 128 unique canonical reference compounds, and
one to three distinct auxiliary contexts. Reference Ki and Kd remain separate;
IC50 is auxiliary only. Direct/confidence-9 B/F assay and primary-source gates
remain. A null variant does not establish wild type.

Keep at least **32 shared panel compounds per auxiliary** and **64 across their
union**, after all canonical, exposure and role exclusions. Unknown/censored,
nonfinite or absent measurements cannot become oracle observations. Numerical
qualification requires a later restricted-validator grant; this review and the
proposed next census cannot establish finite positive support.

The default scale remains **36 bundles / 18 conservative isolation units**:
four development, two validation and twelve reserved-final units, with two
distinct reference contexts per unit. Report reviewed biological-family counts
and isolation-unit counts separately. Two tasks or two family names in one
source-connected unit do not create independent biological samples. These
counts and the 128/64/32 floors are design targets, not a power calculation.

The future primary endpoint remains within-panel recovery of the ten strongest
reference compounds among **delivered reference measurements**. The trusted
evaluator alone later ranks each task's Ki or Kd in its own context; no rank is
computed during this review or the proposed census. All arms begin with zero
delivered reference outcomes; any outcome-blind bootstrap is matched and charged.
Auxiliary responses and predictions are not confirmed reference discoveries.

The proposed primary resource point is 32 supported measurement reveals and
two new evidence-fact reviews; secondary measurement budgets are 16/64 and
evidence budgets 0/1/4. Report evidence actions, actual CPU, retrieval/cache
latency and any measured reviewer effort separately. A benchmark reveal is not
a laboratory price; no currency/CPU/assay exchange rate is assumed.

The estimand is the isolation-unit macro-average paired utility difference
against the strongest preregistered feasible same-predictor control, selected
using development/validation only. It applies to qualified finite historical
panels, not the entire database, a prospective chemical library or clinical
efficacy. Report every control, Ki/Kd strata, paired effects, intervals,
abstention/coverage, unsupported actions, fallback and access failures.
Repeated seeds are within-unit repetitions. No meaningful-effect threshold is
set, consistent with the owner's decision; favorable point estimates alone
do not establish confirmatory benefit. Freeze a precision/analysis plan before
any new final evaluation. Twelve final units do not guarantee precision.

## Family membership and isolation are different records

The proposed primary biological unit is a **reviewed protein-level family**.
Its certificate needs a pinned family-type assertion, assayed accession and
organism, an assayed-chain/domain-architecture check, evidence location/version,
and two qualified reviewers' independent dispositions plus adjudication of
disagreement. Existing InterPro family-type and UniProt family records are
candidate source types. Availability for the missing targets is unconfirmed;
this review does not fetch them or treat current snapshots as sufficient.

ChEMBL functional class names are descriptive. A shared domain or homologous
superfamily is retained as a warning/isolation constraint until qualified review
resolves its relevance to the assayed protein. Unknown mapping or unresolved
relevant homology blocks final admission. The parent cannot certify family
membership by choosing a convenient graph level.

Keep the legacy **87-label exposed component as a hard nonfinal constraint**.
Keep every other inherited protected/exposed component and role declaration.
The diagnostic 254-component family-edge-only graph is not adopted. No new
family name, accession alias or domain review clears a historical protection.

Build a separate isolation graph over the intent frame and inherited constraint
nodes. Close reviewed-family, legacy-lineage, normalized-primary-DOI,
`ASSAY_GROUP`, deposition/reused-protocol and unresolved relevant homology links
**before** any proposed role assignment. Shared source membership constrains
independence; it never proves assay-procedure equivalence.

Identifier scope is part of that certificate. Normalize DOI wrappers/case and
whitespace with a frozen rule, retaining the original value. Qualify assay-group
and deposition keys by their documented namespace; a repeated bare number is
not proof of a global source identity. If global versus document-local scope
cannot be established from pinned documentation, retain an UNKNOWN constraint
and withhold final use. Do not remove a legacy edge on that basis. The four old
mixed-role components describe the prior DOI/group-ID graph; this review does
not certify the semantic scope of every group identifier.

If a component connects conflicting historical roles, retain the old records
and labels unchanged, mark new tasks `QUARANTINE`, and seek review. Do not move
an old validation/final record into training to make a quota work. Pure new
unexposed, reviewed components may receive proposed roles under a frozen salt
and 4/2/12 quotas only at a separately approved cohort freeze. No such assignment
is performed here or released by the next census proposal.

## Exposure, identity and procedure certificates

Retain every historical exposure declaration even if its origin was metadata.
For future new records, distinguish common catalog metadata, canonical identity
exposure, inspected reference facts and outcome/policy-result exposure. Catalog
metadata can support blinded cohort construction; it does not itself become
reference gold. This distinction cannot downgrade an existing exclusion.

Carry all DQR canonical identities and inspected task/source dependencies into
the next protection input, alongside the earlier 4,723 protected identities,
additional exposed structures, R0/R0-R/R0-A1 records and planning identities.
Preserve any old final provenance as protected/quarantined. Resolve CHEMBL8809
and canonical aliases before final clearance. Unresolved structure or alias
mapping is UNKNOWN, not an unmatched clean example.

Exclude protected exact identities from every new task role. Proposed new
validation/final panels also exclude known exposed canonical identities. Apply
final > validation > development exact-identity ownership to the remaining new
allocation, then recheck all floors. Preserve the pinned canonical-isomeric-SMILES
policy; no silent salt, charge, isotope or tautomer normalization. Report
scaffold/analogue similarity later; make no chemical-OOD or pretraining-clean claim.

A reference is normally one assay/context/type. A future pooled procedure unit
needs explicit source concordance for accession/organism, construct/variant,
endpoint/readout, procedure and relevant conditions, with an assay-to-source
mapping certificate. Every included assay must pass; unknown or contradictory
conditions prevent pooling. Same target, paper, endpoint, description hash or
assay group alone is insufficient. The next census accepts no new pooled unit;
any hypothetical pooled capacity is labelled an ineligible upper bound.

## Fixed support-first construction and censoring

1. **Freeze rules and aggregate scope.** Pin archive/schema, permitted metadata
   projection, identity policy, historical exposure inputs and proposed family/
   isolation rules. Record catalog counts using IDs/type/relation/unit only.
   Do not inspect values, nonmissingness, comments, flags, potency or ranks.
2. **Freeze a bounded intent frame.** Prefer targets with a nominal single-assay
   Ki/Kd reference of at least 128 raw molecule IDs and a potential auxiliary;
   use a fixed hash for ties. Catalog categories are reported, not equal quotas.
   Raw ID counts are only an upper bound before canonical pruning. Keep the
   full selected intent list and rejected/capped states; do not replace failures.
3. **Require complete whole-target support.** Include all metadata-eligible
   endpoint assays for an admitted target. If a target exceeds assay/row/identity
   caps, retain it as incomplete and do not count a convenient prefix. Apply
   canonical and protection joins before nominal feasibility. Search one to
   three distinct auxiliary contexts exactly, or report `UNKNOWN_AUX_SEARCH_CAP`.
4. **Freeze candidate IDs.** Record at most 120 nominal bundles with deterministic
   panels and full attrition. Do not refill after canonical, source, family,
   numerical or independent-review failures. Single-assay and unverified-pool
   diagnostics remain distinct; both cannot be counted as the same independent task.
5. **Later qualification, by separate grant.** Only after owner/domain review may
   a trusted validator test numerical eligibility on the frozen candidates.
   Methods/reference interpretation and a cohort freeze need their own scope.
   Neither operation follows automatically from this review or the next census.

`RAW_ID_UPPER_BOUND`, `COMPLETE_CANONICAL_NOMINAL`, `UNKNOWN_CAP` and
`NOT_ASSESSED` must be separate output states. Access failure is not a negative
assay result. Missingness is not inactivity. A bounded search failure cannot
establish global infeasibility. Retain the entire intent-to-qualify denominator
and source-access bias; do not select final cases for favorable paper impact.

## Evidence relevance and competent comparisons

All arms receive complete permitted metadata, including safely projected
procedural conditions when separately authorized. A field hidden because its
projection/access has not been approved is not natural scientific uncertainty.
The next census does not assess information gain or read methods/parameter values.

A later development audit targets eight bundles in four reviewed units, at
least two source-grounded decision-sensitive factors across two units, and at
least two clear-metadata controls. Reviewers inspect outcome-masked source
locations independently and blind to activity values/policy results. Parent
drafts, metadata flags and LLM consensus are not independent gold. Current
reviewers are **not nominated or booked**; no payment or outreach is authorized.
Unknown/contradictory facts remain explicit. A source fact's possible effect on
32 supported edges is a structural candidate, not demonstrated benefit.

Later comparisons require the same predictor/features/update rule, matched
seeds, support masks and caching. Include strong metadata-only acquisition,
budget-matched upfront evidence, fixed/random evidence schedules, competent
decision-region and multifidelity adaptations, Random and retrained Greedy.
Separate predictor improvement from policy value.

Already cached admissible facts are free to all arms. Full upfront context is
also reported at its actual resource point; if it exceeds a budget, do not hide
it or compare mismatched resource points. A zero-cost full-context policy is an
information ceiling: an optimal informed policy can emulate an adaptive one.
Any apparent advantage caused by withholding free metadata/cache or weakening
the control defeats the claim. Real acquisition costs/latency must be measured,
and a regime where evidence is effectively free must remain in the report.

## Stop rules and the next ready decision

- Incomplete exposure/family/procedure mapping: no final clearance.
- Insufficient complete nominal support in a bounded frame: report REVISE and
  the unassessed remainder. A globally complete upper bound below the target
  can motivate a reference-unit decision; it does not authorize lower floors.
- No independently grounded facts beyond complete metadata, or no source-linked
  action sensitivity: stop the current adaptive-evidence route and ask the owner.
- No nontrivial distinction from strong existing policies, or advantage only
  over a deprived baseline: no method-novelty claim.
- Data-only, within-family, endpoint-expanded or product-only pivots require
  an explicit owner decision. None is selected automatically.

The next recommended proposal is [R0-QC: support-first census](../06_execution/R0_SUPPORT_CENSUS_PROPOSAL_20261107.md),
**3 CPU-hours / 24 hours / at most two combined workers**, with no scientific
HTTP, methods bodies or numerical activity/presence queries. It would test the
support ceiling and repair metadata isolation inputs before another reference
intake. It is **NOT_RELEASED**. Independent reviewer nomination and lawful family/
methods snapshots are parallel human dependencies, not agent jobs launched here.

## Product and journal boundary

The same typed records can later support a read-only evidence lookup, proposed
next action and local reviewable report, with adapter-specific approval for
external writes. These are proposed interfaces, not newly implemented tools.
Product evaluation must separately test source correctness, abstention, workflow
burden and integration behavior against ordinary tools using the same model.
No live team writes, deployment, paid pilot or business ROI follows from this review.

The cached JCAMD scope assessment motivates a substantial computational strategy
and rigorous retrospective molecular validation. It is not a fresh journal
policy check or acceptance forecast. Submission still needs method distinction,
independently reviewed references, held-out molecular results, uncertainty and
reproduction. The USD300 publication ceiling and subscription direction remain
historical owner constraints; this phase authorizes no spending or submission.
