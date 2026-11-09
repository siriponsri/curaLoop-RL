# LR-CF1 methods checkpoint

**Preparation only. No biological data analysis or comparative result.**

**SI update:** the owner supplied the25-page SI. Pages6–7 visually confirm13/17
codename conflicts with the repository, despite the same AID roster. Pages11–12
confirm100 LightGBM iterations,1.0 lambda regularization,0.95 feature fraction,
1024-bit radius2 ECFP, low MVS-A ranking for positives and high primary activity
Score ranking for positives. Dependent intake awaits the
[owner's explicit source convention](../06_execution/LR_CF1_SOURCE_CONCORDANCE_DECISION_20261109.md).
Earlier SI-pending text below records the pre-inspection checkpoint, not current
availability. Other admission and actual reproduction gates remain unpassed.

## Research question and source

At a fixed count of confirmation experiments, how do published primary-only
rankers and identical classical diversification controls trade off
source-confirmed positive compounds H(B) and the number of prespecified structure
groups containing such a positive D(B)? The owner approved this question and the
bounded [LR-CF1 protocol](../06_execution/LONG_RUN_CONFIRMATION_FEASIBILITY_PROPOSAL_20261109.md).
Its exact matrix must still be frozen after admission, before value analysis.

The candidate is the author-provided
[AIC_Finder snapshot](https://github.com/dahvida/AIC_Finder/tree/04c58e85188e724ec5ff44cbed2e7b960f6f3df3),
associated with Boldini et al.,
[ACS Central Science2024](https://doi.org/10.1021/acscentsci.3c01517).
Only code, license, environment, metadata and the official main-article text
have been retrieved. The source article itself selected its17 campaigns using
hit-count/noise criteria. Our proposed metadata-only subsetting does not remove
that inherited selection bias or turn this resource into a representative sample
of pharmaceutical campaigns.

## Observable endpoint

Let U be the admitted primary-active compounds with an observed source
confirmation label. For a selection S(B) contained in U, H(B) is the number with
source confirmation1, and D(B) is the number of fixed structural groups containing
at least one such selected positive. This supports a conditional retrospective
description within U. It does not identify prospective value on unconfirmed
primary hits or the complete screening library.

The [main article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11046457/) treats
confirmation inactivity **or inconclusiveness** as false-positive evidence.
The author cleanup maps all non-Active source labels to0 and takes a parent-SMILES
majority across duplicates. Therefore, the safe labels are SOURCE_CONFIRMED_POSITIVE,
SOURCE_NONPOSITIVE_INACTIVE_OR_INCONCLUSIVE and NOT_OBSERVED. Original ambiguous
or replicate states cannot be recovered from this binary reduction. A missing
confirmation must never become a negative or default potency. Activity potency,
kinetic affinity, validated mechanism and clinical efficacy are not this endpoint.

The role/observation mask may use approved identifiers and presence information;
changing hidden positive/nonpositive values must not change the supported
universe. The current constructed test verifies that invariant, not a real
campaign's observation support or exchangeability.

## Comparators and source fidelity still to qualify

The mandatory controls are primary readout and MVS-A. The approved envelope also
includes random, RF, GBM and nearest-primary reference, each paired with the same
top-ranked, ranked-cluster-round-robin and classical max-min operators. None of
these is a proposed new selector. Confirmation labels cannot train, validate or
tune a ranker. Fixed seeds, budgets and grouping sensitivity remain those in the
approved proposal; no current evidence permits changing them.

Pinned source code defines a 1024-bit radius2 Morgan fingerprint option, default
LightGBM influence scoring and primary-only model fitting. Its exact representation
and implementation conventions must be checked against SI. Preserve source code
behavior in a named reproduction; any CPU-thread restriction or compatibility
adaptation needs an explicit concordance record. Do not silently repair code
conventions and present a modified algorithm as the original reproduction.

## Position relative to published work

The main article already reports the structural concentration of prioritized
true hits and suggests hybrid scaffold-aware selection as a remedy. Its finding
is prior evidence, not a result reproduced by CuraLoop-RL. The later data-valuation
study also compares ranking/diversity behavior. Consequently, a demonstration that
a scaffold quota changes diversity is insufficient as a novel contribution.
The authorized pilot asks whether an unresolved, reproducible decision opportunity
remains after strong matched controls. A negative answer is a valid closeout.

Chemotypes here are operational structure groups. They are not independent
biological mechanisms, medicinal chemistry series or validated leads. Source
publication groups, annotation-connected families and experimental dependence
blocks are different objects; none can be substituted for another to meet a
minimum sample count. Seed variation is conditional variation within campaigns.

## Results and publication disposition

No eligible campaign universe, biological baseline fit, confirmation-portfolio
cell or effect estimate has been produced. H(B), D(B), paired differences and
uncertainty are **NOT_RUN**, not0. The11 constructed tests and read-only SSH
preflight are engineering evidence only. The manuscript has no new empirical
result from LR-CF1 and is not ready for journal submission.

Exact source-role/intended-use admission, SI concordance, structure exclusions,
resource calibration and mandatory baseline reproduction remain pending.
[The execution checkpoint](../06_execution/LR_CF1_EXECUTION_STATUS_20261109.md)
records the missing file and current action boundary. No new-method training,
protected final16 access, actual product integration or submission is released.
