# R0 Contribution & Data proposal

Date: 7 November 2026. Base: main at
91aebeca21fa0a225b94c58a6ec686a364d205ca.
Status: **READY_FOR_OWNER_CONTRIBUTION_DATA_DECISION**.
Scientific method: **NOT_ESTABLISHED**. New data cohort: **NOT_QUALIFIED**.

Owner decision, 7 November 2026: contribution direction APPROVED; ChEMBL selected
as the primary source. The owner requested the next readiness plan within R0,
kept final outcomes closed and retained joint decisions before phase transitions.
The original proposal status above records its publication checkpoint. The
current frontier is [the readiness plan](R0_CHEMBL_DATA_READINESS_PLAN_20261107.md).

## Objective and scope

Recommend one falsifiable research direction that can support both a molecular
decision-method paper and the owner's paper/database-to-team R&D plugin.
This is the new phase R0, not the completed historical LR-BC R0. The owner
requested phase-by-phase decisions. The present work covers literature,
source/card metadata and a proposal, not experimental execution.

No new activity rows, public benchmark question/answer files, model fitting,
protected final outcomes, SSH jobs, stopped-source retries, paid services or
external team writes were used. Ordinary literature review exposes published
examples; those examples cannot later be called untouched evaluation cases.

## Recommendation

Working title: **Evidence-Adaptive Molecular Screening under Assay Transfer
Uncertainty**. This is a hypothesis to qualify, not a claim of a novel algorithm.

Study when an R&D system should resolve uncertainty about assay context before
using measurements from another assay to choose the next compound. A source
clarification can affect many candidate compounds because they share an assay,
protocol, endpoint or target assignment. The proposed decision system would
choose between verifying a shared context, obtaining a supported measurement,
making a supported recommendation, and abstaining or stopping.

Illustrative case, not an observed result: two sources concern the same target,
but it is unclear whether their readouts support transfer to a specified binding
endpoint. The system should determine whether resolving that uncertainty could
change a compound shortlist. A retrieved passage does not itself make the
measurements comparable. A typed rule or an explicit unresolved judgment must
link the source to the allowed downstream action. If the context is already
clear and cheap to obtain, the system should proceed without extra verification.

The intended payoff is to improve decisions with a limited evidence/measurement
budget and explain which shared uncertainty caused each action. It is broader
than adding a search connector, while retaining one testable scientific core.

## Candidate contributions and required proof

| Candidate contribution | What must be delivered | What does not establish it |
| --- | --- | --- |
| C1. Joint evidence/measurement decision rule | An explicit policy for shared assay-context uncertainty, with a technical distinction from decision-region active learning and multifidelity active search; same-predictor controlled evaluation | Renaming value of information, adding an LLM, or combining existing tools |
| C2. Source-linked assay-transfer benchmark | Versioned measured outcomes, assay/document provenance, independently adjudicated context, natural ambiguities, visible observation support and protected evaluation partitions | Treating missing measurements as negative labels, database flags as truth, or synthetic corruption as the primary test |
| C3. Transferable R&D workflow | A host/tool contract that turns verified sources into typed plans, reports and reviewable exports; separate evaluation of evidence correctness and workflow benefit | Current metadata demo, authored-case ties, protocol compatibility or a polished UI |

C1 is the scientific centerpiece. C2 enables a credible test. C3 is a product
and reproducibility contribution; it cannot compensate for an unestablished C1.
No theorem, guarantee, named new algorithm or performance gain is claimed yet.

## Closest-work test

The [source ledger](../02_literature/R0_CLOSEST_WORK_20261107.md) records inspected
scope, counterevidence and access limits. Decision-resolving tests and cheap versus
expensive measurements are established ideas. Assay-aware prediction, automatic
assay annotation and assay-specific data selection are also occupied territory.
Recent semantic-decision and follow-up-decision preprints further narrow the gap.

The remaining candidate gap is a practically supported joint policy for
**shared assay interpretation plus molecular selection**, with a fair comparison
to complete upfront context resolution. Its novelty remains uncertain. Before
implementation, express the state, observations, costs and objective, then try
to reduce the proposal to HEC/decision-region learning or existing multifidelity
search. If the reduction removes any substantive new technical element, do not
present the combination as a new method. A benchmark-only paper would require a
separate owner decision and a new publication rationale.

## Data recommendation

Use a **single pinned ChEMBL release with original assay and document links** as
the primary candidate. Proposed reference release: ChEMBL 35, listed with DOI
10.6019/CHEMBL.database.35 in the official download documentation. This is a
deliberate version candidate, not a latest-release assertion or a completed
byte-level pin. File access, checksums, schema, source-specific terms and the
availability of later annotation artifacts still need qualification.

| Data/source | Intended role | Current support and material limit | R0 disposition |
| --- | --- | --- | --- |
| ChEMBL assay/activity/document data | Main source for a newly constructed assay-transfer benchmark | Published curation and linked entities support the rationale. No eligible panel, natural ambiguity rate or adjudicated reference exists in this project yet | Recommended candidate; metadata qualification next |
| Papyrus and PCAM | Prediction/data-preparation references and compatible comparators | Published curation and assay-aware modeling are relevant. Aggregation or concordance filtering may remove the disagreements of interest; GPCR targets are not independent families | Reference/secondary candidate; mapping and scope audit required |
| MF-PCBA | Possible paired-follow-up extension | Existing incomplete primary tuples and a retained service STOP prevent a complete replay. Unrequested pairs are unknown | Preserve; not on the critical path; no retry authorized |
| FS-Mol | Existing development regression reference only | Old final 12-component/16-assay outcomes remain reserved; annotation-connected components are not certified evolutionary families | No final access; no transfer of old counts to a new benchmark |
| LAB-Bench LitQA2/DbQA | Auxiliary retrieval/comprehension controls for the plugin | Public card has these tasks and CC BY-SA 4.0 metadata. This is not an experiment-policy or end-to-end team-workflow benchmark | Card inspected only; tasks/gold NOT_READ; separate protocol required |

Primary dataset papers: [ChEMBL curation](https://link.springer.com/article/10.1007/s10822-015-9860-5),
[ChEMBL annotation, updated article](https://link.springer.com/article/10.1186/s13321-026-01165-x),
[Papyrus](https://link.springer.com/article/10.1186/s13321-022-00672-x),
[PCAM](https://link.springer.com/article/10.1186/s13321-026-01316-0), and
[LAB-Bench](https://arxiv.org/abs/2407.10362).

These are real paper-backed sources. A benchmark derived from them would be a
**new CuraLoop benchmark**, not an existing published standard or an exact
reproduction of one. Qualified counts are UNKNOWN, not the headline counts of
the source databases. Retain the ambition of at least 12 independently verified
biological family groups; never relabel 12 targets or annotation components as
12 certified families. A feasibility audit must report the actual count.

### Required data layers

1. Immutable source layer: release/file identity, raw field meanings, molecule,
   target, assay and document IDs, publication provenance, measured/censored/
   missing status, and source-specific terms. Keep endpoints separate; IC50,
   EC50, Ki and KD are not interchangeable labels by default.
2. Evidence layer: natural assay descriptions and eligible primary-source
   passages, with independently adjudicated resolved/unresolved context. Missing
   metadata is not evidence of an error. Curator flags and later revisions are
   signals for review, not automatic gold labels.
3. Outcome layer: only actually observed, endpoint-compatible measurements in
   a declared finite replay panel. The trusted evaluator holds hidden outcomes;
   the decision agent cannot retrieve those values from papers or full tables.

The policy's estimand is initially **conditional performance on eligible measured
panels**. It is not value over an entire library, prospective lab discovery,
clinical benefit or commercial savings. Selective historical measurement can
bias those panels. Any primary-to-confirmation study needs actual paired support
and its own population definition; a model prediction cannot serve as its oracle.

### Leakage and partition requirements

- Before outcomes are used for method choices, freeze eligibility, endpoint,
  action support and partition rules from metadata. A trusted qualification
  process may inspect support under a separately approved contract; the planner
  must not see held-out values.
- Group by source document/assay lineage and validated biological relationships;
  do not count seeds, overlapping assays or targets as independent families.
  Enforce exact molecular identity protections and report residual scaffold
  similarity. Do not claim chemical OOD without an appropriate design.
- Carry forward all existing protected identity exclusions using the existing
  label-free manifests. No old final outcomes are required for that check.
- Audit evidence passages for outcome leakage. A paper containing the answer is
  not a harmless metadata source merely because access is called retrieval.
- Freeze task definitions, tools and prompts before final evaluation. Public
  availability means model pretraining contamination cannot be certified absent.

## Evaluation that would make the contribution convincing

Use the same predictor, measured panel, action support and total declared budget
when isolating planning value. Retain a strong GP/appropriate assay-aware
predictor; a weaker prediction baseline must not manufacture planner gain.

Required controls are: (a) resolve all available context upfront plus strong
acquisition, (b) typed validation plus acquisition without adaptive evidence
selection, (c) fixed/random evidence allocation, and (d) a compatible published
or clearly labeled adapted decision-region/VOI/multifidelity policy. AssayMatch
and PCAM concern data selection/prediction; compare at the appropriate layer,
not as if their native outputs were an entire planner. Report adaptations and
resource differences, including any GPU requirements of exact reproduction.

Report source-confirmed endpoint-compatible utility under a fixed budget,
unsupported recommendations, abstention/coverage, and evidence/compute burden
separately. Effect estimates and uncertainty should respect independent family
or document groups. Report easy/clear-context and genuinely ambiguous regimes,
including ties and costs of abstention. Any ranking threshold, loss function,
coverage requirement and material-effect criterion must be set before final
results; none is chosen from the previous pilot here.

CPU time, source requests, analyst time and laboratory cost are different
resources. Use measured technical burden and separately declared budget axes;
do not invent lab-price ratios or convert CPU savings into business ROI. If
human adjudication time is claimed, it must actually be measured in a suitable
workflow study. Product comparison needs a separate same-model ordinary-tool
baseline and fresh source-disjoint cases.

## Falsification and phase gates

| Gate | Evidence needed | Stop or revise when |
| --- | --- | --- |
| G1. Substantive method distinction | Explicit formal problem and closest-work reduction analysis | Existing policy plus an interface exhausts the contribution |
| G2. Real observable task | Adjudicable natural context uncertainty, supported measurements and admissible evidence | Useful ambiguity exists only after artificial corruption, or requested outcomes were never measured |
| G3. Sufficient independent scope | Versioned lineage/family audit with actual eligible counts and rights | Diversity is overstated or the required population is unsupported |
| G4. Fair value test | Frozen development comparison including upfront resolution and strong acquisition | Upfront resolution dominates/ties after honest cost accounting, or apparent gain comes only from predictor changes/leakage |
| G5. Later confirmation | Separately approved untouched evaluation and reproduction | Development gains are promoted to general or final evidence |

R0 closes only after a documented contribution decision, a feasible data contract,
rights/access assessment, falsification plan and explicit next-phase resources.
This brief prepares those decisions; it does not close R0 scientifically.

## Decision tickets and next frontier

| ID | Owner | Decision / dependency | Present status |
| --- | --- | --- | --- |
| R0-D1 | Project owner | Adopt the recommended shared-context decision problem and ChEMBL primary source; final measured-panel population still requires qualification | DIRECTION_APPROVED on 7 November 2026; no cohort/endpoint approval implied |
| R0-D2 | Lead engineer, then owner | After D1, define bounded metadata-only qualification: proposed first slice up to 50 assay records and 20 document metadata records, no activity values or protected benchmark rows | PLAN_READY_FOR_REVIEW; see linked readiness plan; execution caps remain proposed |
| R0-D3 | Lead engineer, then owner | Data schema, raw/source mappings, access/rights and natural ambiguity feasibility; D2 first | NOT_RUN |
| R0-D4 | Owner | Approve any material population/endpoint change, bounded outcome qualification and independent reference review | NOT_RELEASED |
| R0-D5 | Owner | Choose GO, revise or stop R0; separately authorize P1/R1 | NOT_RELEASED |

The D2 slice is a proposed ceiling, not a success sample size or permission to
exceed existing source STOPs. If it is inadequate, report uncertainty and propose
a bounded extension. No source failure should silently trigger another endpoint.

Rejected as the current main route: more blind MF-PCBA calls, another deeper
lookahead/RL run, an LLM wrapper presented as method novelty, and an automatic
portfolio expansion. Each misses an unresolved methodological or data gate.

## Evidence, limits and handoff

PASS: current main checkpoint and local scientific closeouts inspected; primary
literature and source/card metadata reviewed; candidate/verified distinctions,
counterevidence, source access failures and decision dependencies documented.

NOT_RUN: new cohort intake/qualification, independent adjudication, training,
method comparison, host-agent efficacy, final validation and commercial rights
clearance. Independent review of this brief has not occurred; the parent wrote
it serially and does not label its own checks independent review.

The proposed method has potential, not established novelty or journal readiness.
[JCAMD's scope](https://link.springer.com/journal/10822/aims-and-scope) allows
appropriate retrospective validation of novel computational strategies while
prioritizing experimental validation. A connector alone does not meet that bar.
Subscription publication cost choice does not change the scientific standard.

Current handoff: R0-D1 is resolved for direction and the bounded qualification
plan is prepared. Its metadata intake is not yet run. Review the new plan before
releasing its execution; do not run old LR-BC jobs, renew old clocks, open frozen
outcomes or advance phases automatically.
