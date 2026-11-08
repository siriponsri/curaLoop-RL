# Method-first plan

Current decision: **8 November 2026**. Canonical design:
[METHOD_FIRST_DESIGN](docs/03_research/METHOD_FIRST_DESIGN_20261108.md).
The paper should contribute a method; existing datasets support evaluation.

| Phase | Work and acceptance evidence | Current state |
| --- | --- | --- |
| M0: method design and correction | Closest-work matrix, precise objective, pseudocode, constructed implementation/checks; reconcile old benchmark-first guidance | COMPLETE_FOR_OWNER_REVIEW; novelty HOLD |
| M1: novelty and scalable predictor adapter | Reduction audit, delivered-information GP adapter, two revisions and shared-cache timing diagnostics on exposed pools | COMPLETE_INVESTIGATION_NO_GO; 17 constructed checks and 36 timing calls; method distinction/calibration insufficient |
| M2: development evaluation | Strong matched predictor/controls, discovery/compute frontier, fallback and failure analysis; retain unfavorable results | NOT_RUN_GATE_NOT_PASSED |
| M3: protected evaluation | Freeze allowed population, dependence, roles, protocol, intervals and budget before outcomes | NOT_RELEASED |
| P1: plugin method integration | Typed evidence/plan/report boundary, ordinary-tool control, factual/source/abstention/effort assessment | Existing metadata tools retained; new method integration NOT_RUN |
| J1: manuscript and reproduction | Method-supported claims, figures, reproducible evidence, human/venue review | Design draft only; submission NOT_RELEASED |

## Current candidate and decision gate

The candidate is computation-bounded baseline-relative rollout under predictive
ambiguity. Its robust objective and fallback have close prior art. The exact
constructed reference is an adaptation for inspection, not a finished novel
algorithm. Generic memoization or a positive toy is insufficient for a method paper.
The [LR-M12 report](docs/03_research/LR_M12_M1_RESULTS_20261108.md) maps the robust
objective to established baseline regret. Its confidence variant retained Greedy
in all 12 diagnostic cases. The distinction is insufficient, so M2 did not run.
Return to the [owner checkpoint](docs/06_execution/LR_M12_OWNER_CHECKPOINT_20261108.md)
before a new mechanism. Do not silently pivot to a benchmark/curation paper.

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

LR-M12 closed one additional phase's investigation, M1, with a negative transition
decision. Its 24 CPU-hour / 72-hour release retained 7,320 seconds including
utilities/delivery. M2/M3/P1/J1 remain incomplete. All old clocks/ledgers and this
release are closed. No unused resource is borrowed or final outcome opened.
A new mechanism or phase requires the owner's bounded decision. Routine English
delivery/corrections for this checkpoint are already authorized.

Historical protocols/results remain linked from the [claim ledger](docs/00_project/CLAIM_LEDGER.md).
The prior roadmap is preserved in Git at checkpoint
`1950b74d12f33eb08dc0b8a0fabf0ec0dbb7ad7a`; it is not current execution authority.
