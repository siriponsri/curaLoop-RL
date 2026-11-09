# Proposed contribution: confirmation-budget molecular portfolios

**Status: PROPOSED_FOR_OWNER_REVIEW. No scientific phase is released.**

The owner requested contribution revision after supplying a Consensus review.
This document is a research-design proposal, not approval to change endpoints,
ingest records, read activity values, train, use SSH, or inspect protected data.
All LR-D23 and earlier closed ledgers, source/result bytes and final roles remain
unchanged. The report is a literature lead, not an instruction or a novelty
certificate. Its original PDF remains outside public Git.

## Recommended core

**Working title:** Confirmation-budget allocation for assay-confirmed chemotype
coverage in retrospective molecular screening.

**Research question:** On eligible held-out screening campaigns, can a simple
confirmation-selection policy recover more distinct assay-confirmed chemotypes
at the same number of follow-up measurements than strong ranking-and-diversity
controls, while keeping confirmed-positive loss within a pre-agreed margin?

The practical decision is which primary-screen hits deserve scarce confirmation
slots. The scientific outcome is an actual follow-up assay observation. Measured
CPU remains an implementation cost. Monetary laboratory savings, clinical
efficacy and validated lead-series discovery are not inferred from this setup.

This replaces the proposed contribution of choosing when to refresh an RF model.
LR-D23 remains a completed negative result; v0, no-history and new thresholds are
not substituted after evaluation. Its simulator, privacy boundary, provenance,
matched comparisons and four-screen interface remain reusable engineering assets.

## Contribution claims, conditional on evidence

| Component | Proposed deliverable | What must be demonstrated |
| :--- | :--- | :--- |
| C1: scientific core | A minimal confirmation-portfolio policy and a matched discovery/coverage trade-off study | A useful frontier improvement beyond strong rankers with the same diversification options, on held-out campaigns |
| C2: scientific evidence | Analysis of where confirmation allocation helps, with explicit observation support and dependence | Effects survive campaign exclusion and plausible chemotype definitions; missing outcomes do not create a spurious advantage |
| C3: product extension | An inspectable evidence-to-confirmation-plan workflow | Correct provenance, valid proposed actions and measured review/decision usefulness against deterministic controls in a later product study |

C2 is part of evaluating C1, not a proposed benchmark publication or a new
general-purpose decision-certification theorem. C3 is a separate software/product
claim. A dashboard or LLM layer cannot substitute for C1's result. All three are
unvalidated proposals today.

## Define the estimand before selecting a method

For campaign c, let U_c be the frozen, eligible candidate universe with justified
follow-up observation support. For a selected set S within U_c, |S| <= B:

- H_c(S): number of selected compounds with eligible assay-confirmed positive
  outcomes, excluding any confirmations already supplied as initial knowledge.
- D_c(S): number of prespecified structure groups containing at least one such
  confirmed positive among the selected compounds.
- B: number of new confirmatory measurements, not CPU seconds or a monetary bill.

Compare H and D together across a prespecified budget range. The intended primary
endpoint is D at fixed B subject to a meaningful H-loss preference; an exact
margin, reference control and budget range require owner/domain agreement before
outcomes. Report absolute H/D as well as paired effects and uncertainty.

The proposed term is **assay-confirmed chemotype coverage**. Fingerprint clusters
or Murcko scaffolds are operational structure groupings, not automatically
medicinal-chemistry series, independent mechanisms, validated leads or effective
drugs. A stronger series claim would need a separately justified rule for analog
support and further biological evidence. Prespecify structural definitions and
sensitivity checks rather than selecting the most favorable definition later.

Do not assume calibrated confirmation probabilities or independent outcomes
within chemical groups. No probabilistic coverage guarantee is proposed here.

## Observation support is a claim boundary

Historical follow-up is selected. The conditional replay population must not be
silently expanded to every compound in the original primary screen. A comparison
within a historically confirmed subset estimates value in that selected subset.
It does not identify a new policy's value across untested primary compounds.

Retain separate states for observed confirmation outcomes, censored quantitative
measurements, inconclusive/invalid observations, conflicting records and absent
or unperformed follow-up. A source-defined tested inactive can be usable for a
binary endpoint even when exact potency is censored. An unmeasured outcome cannot
be converted to inactive or an invented potency floor.

Every compared action must use the same declared support universe. Training and
selection receive only information available at that point; hidden confirmation
labels stay in the evaluator. If broader-library value is not identifiable,
restrict the claim or decline that estimate. Weighting does not repair absent
support without justified selection assumptions and provenance.

## Closest work constrains novelty

Boldini et al. already introduce MVS-A for HTS hit prioritization and evaluate
17 primary/confirmatory pairs. Their paper and official AIC_Finder repository
provide a concrete comparator and processed-data candidate. Ranking likely true
hits is therefore established work, not our proposed invention. Source:
[ACS Central Science, 2024](https://doi.org/10.1021/acscentsci.3c01517).

Hesse et al. extend data valuation to screening, true/false-positive detection
and undersampling. Selected indexed full-text sections report a confirmation
precision/diversity trade-off, with primary-score ordering strong for diversity.
This motivates a coverage question but does not establish that our policy can
improve it. Sources:
[JCIM, 2024](https://doi.org/10.1021/acs.jcim.4c01547),
[author repository](https://github.com/JoshuaHesse/DataValuationPlatform).

MF-PCBA supplies published paired-screen resources rather than a ready-made
certificate for our intended replay. Earlier repository A2/A3 qualification
already left support, endpoint completeness and cohort readiness unresolved.
Do not relaunch its stopped source or infer clearance from the new review.
Sources: [MF-PCBA paper](https://doi.org/10.1021/acs.jcim.2c01569),
[existing A3 qualification](GOAL4R2A3_QUALIFICATION_V1.md).

The verified OPAL v3 preprint already frames held-out evidence for replacing
measurement plans. Its selected methods distinguish profile-replicate quality
from hit confirmation. We cannot claim general held-out decision certification
as our novelty. Source:
[arXiv:2607.27651v3](https://arxiv.org/abs/2607.27651v3).

The remaining question is a **potential empirical gap**, not certified novelty.
A fingerprint-cluster quota alone is an inadequate contribution claim.

## Method and comparator contract to develop next

Choose the smallest method only after the baseline and data feasibility gate.
An initial ranking-plus-coverage rule is a reference implementation candidate,
not a named new algorithm. A credible comparator set must include:

1. Random selection within the same eligible universe.
2. Primary readout ranking, with source-specific direction fixed beforehand.
3. Reproduced MVS-A and relevant feasible data-valuation comparators.
4. RF/GBM controls with explicit, legitimate training information and compute.
5. Classical diversity controls, including cluster quotas and max-min selection.
6. The same diversification option applied to every relevant strong ranker.

If a sequential variant is proposed, add its fixed/no-retraining counterpart and
a clearly defined nearest-hit control. Distinguish primary-hit references from
already delivered confirmation-positive references; never supply hidden
confirmation labels or a guaranteed known positive to only one arm. A sequential
method is not required merely because the existing simulator supports it.

All controls use matched source records, available information and assay budgets.
Report fitting/inference/offline costs separately. Data-valuation methods with
validation information need an explicit legal source for those labels. No
current-campaign confirmation target can become free predecision information.

Freeze the candidate, structural grouping, endpoint and comparisons before
evaluation. Campaign-level exclusion is primary; target/publication/compound
dependencies must be inspected before calling campaigns independent. More seeds
do not compensate for dependent biological tasks. No cross-family or scaffold-OOD
claim follows automatically.

## Data candidates and assets

| Resource | Intended role | Current state |
| :--- | :--- | :--- |
| AIC_Finder published processed pairs | First candidate for baseline reproduction on an author-provided snapshot | Repository/README and paper source verified; data bytes/schema/rights/support not inspected or admitted in this task |
| DataValuationPlatform | Comparator and additional published resource candidate | README/selected paper methods inspected; advertised data path and overlap require verification |
| MF-PCBA | Endpoint/provenance reference and possible later resource | Existing A2/A3 NO_GO remains; no new activity access or reconstruction certificate |
| ChEMBL | Possible metadata/context enrichment | No new intake; a shared target is insufficient evidence of compatible assays |
| FS-Mol six exposed assays | Preserve negative-method evidence | Not a substitute for primary/confirmatory measurement pairs |
| Protected final16 | Existing reserved evaluation | Sealed and outside this proposal |

Do not add 17, 25 and 60 published task counts as independent campaigns. Deduplicate
sources using assay IDs, compound/endpoint identity and publication provenance.
Article/code licenses do not automatically clear every contributed data row or
commercial product use. A public folder or processed CSV is not scientific
admission. No dataset or result row was downloaded for this contribution review.

## Product expression

The proposed product is an evidence-to-confirmation-plan workspace:

paper/assay discovery -> compatibility/support review -> competing confirmation
portfolios -> inspectable evidence report -> owner approval.

The portfolio shows assay slots, candidate provenance, structural coverage,
alternative plans and unavailable evidence. Assay-confirmed outcomes appear only
after delivery; planning views show expected/proposed coverage distinctly from
observed results. Reuse the existing Python engine and EN/TH screens where their
contracts fit. No frontend or runtime integration is implemented here.

An optional agent can gather evidence and prepare plans. The scientific selector
must remain independently evaluable. Compare the future agent with deterministic
retrieval/rules/templates using the same selector. Measure decision correctness,
unsupported claims, review burden and invalid actions in a separately authorized
product evaluation. No LLM, paid API, live team write, customer ROI or GPO data
access is assumed.

## Smallest next decision, without another open-ended training loop

First ask the owner to confirm the shift to confirmation allocation and
operational chemotype coverage. Then prepare one bounded feasibility proposal:

1. **Admission:** pin candidate source snapshots and intended-use terms; inspect
   endpoint/support fields, source overlap, exposure roles and dependence. Reuse
   old metadata findings rather than resetting their failures.
2. **Baseline reproduction:** only after separately approved record access,
   reproduce primary ranking/MVS-A and simple diversified versions on a fixed
   development subset. Report H/D frontiers and failure cases before adding a
   selector. Do not count baseline fitting as data-free metadata work.
3. **Owner checkpoint:** decide whether an observable, useful improvement remains
   beyond those controls. If support is inadequate, controls cannot be reproduced
   or simple diversity already explains the opportunity, report that and stop.
   Do not substitute another method or endpoint automatically.

Actual campaign counts, hit-loss/coverage preferences, independent evaluation
units, record access, CPU/elapsed budget and split must be proposed and approved
before execution. The Consensus review's compute/person-time estimates are not
timing measurements or available grants. No new clock or remote task starts here.

**Decisions requested now:** confirm or revise the contribution, then consider
the separately specified [LR-CF1 proposal](../06_execution/LONG_RUN_CONFIRMATION_FEASIBILITY_PROPOSAL_20261109.md).
It requests fresh 48 CPU-hours / 96 hours for scoped data and baseline opportunity,
with no new-selector training or independent final evaluation. The owner asked
for this long-run plan, not its execution. Data intake and all experimental
phases remain NOT_RELEASED. Journal novelty/sufficiency and the USD300 publication
route remain unestablished; any later submission needs its own evidence/decision.

See [the source review and access boundaries](../02_literature/CONFIRMATION_DIRECTION_SOURCE_REVIEW_20261109.md).
