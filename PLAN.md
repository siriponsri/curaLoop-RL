# Method-first plan

Current decision: **8 November 2026**. Canonical design:
[METHOD_FIRST_DESIGN](docs/03_research/METHOD_FIRST_DESIGN_20261108.md).
The paper should contribute a method; existing datasets support evaluation.

| Phase | Work and acceptance evidence | Current state |
| --- | --- | --- |
| M0: method design and correction | Closest-work matrix, precise objective, pseudocode, constructed implementation/checks; reconcile old benchmark-first guidance | COMPLETE_FOR_OWNER_REVIEW; novelty HOLD |
| M1: novelty and scalable predictor adapter | Reduction audit against robust baseline regret/ENS; credible predictive scenarios from delivered information; matched-cache comparison on exposed data | NOT_RUN; scope/resource grant needed before data/compute work |
| M2: development evaluation | Strong matched predictor/controls, discovery/compute frontier, fallback and failure analysis; retain unfavorable results | NOT_RUN |
| M3: protected evaluation | Freeze allowed population, dependence, roles, protocol, intervals and budget before outcomes | NOT_RELEASED |
| P1: plugin method integration | Typed evidence/plan/report boundary, ordinary-tool control, factual/source/abstention/effort assessment | Existing metadata tools retained; new method integration NOT_RUN |
| J1: manuscript and reproduction | Method-supported claims, figures, reproducible evidence, human/venue review | Design draft only; submission NOT_RELEASED |

## Current candidate and decision gate

The candidate is computation-bounded baseline-relative rollout under predictive
ambiguity. Its robust objective and fallback have close prior art. The exact
constructed reference is an adaptation for inspection, not a finished novel
algorithm. Generic memoization or a positive toy is insufficient for a method paper.
If a matched established robust adaptation explains its behavior/tradeoff, reject
the claimed method distinction and return to the owner. Do not silently pivot
to a benchmark/curation paper.

## Existing data use

Use exposed HIV/Tox21 only for later engineering/development checks. FS-Mol is
the preferred existing binary-task evaluation route, conditional on preserved
label semantics and exposure/protection. It does not need to become a new dataset
publication. ChEMBL/QP/QC and MF-PCBA intake are optional later decisions, not
prerequisites for the current mechanism.

QP32 and QC500 remain deferred/unreleased. The previous QP confirmation question
is superseded by the owner's method-first decision. No numerical validity grant,
source intake, new cohort or molecular experiment is inferred from this plan.

## Execution boundaries

This task completes M0 only, including bounded local constructed checks and normal
main delivery. All prior scientific clocks/ledgers are closed. No unused resource
is borrowed, no SSH or final outcome is opened, and no new experimental grant is
created. M1 onward needs the owner's next bounded data/compute decision. Routine
corrections within this approved design task do not require another permission.

Historical protocols/results remain linked from the [claim ledger](docs/00_project/CLAIM_LEDGER.md).
The prior roadmap is preserved in Git at checkpoint
`1950b74d12f33eb08dc0b8a0fabf0ec0dbb7ad7a`; it is not current execution authority.
