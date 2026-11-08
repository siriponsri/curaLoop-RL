# Method-first plan

Current decision: **8 November 2026**. Canonical design:
[M2 contribution](docs/03_research/M2_CONTRIBUTION_PROPOSAL_20261108.md), approved
in direction; [detailed experiment plan](docs/06_execution/M2_EXPERIMENT_PLAN_20261108.md)
was subsequently approved. Its [resource checkpoint](docs/06_execution/M2_RESOURCE_OWNER_CHECKPOINT_20261108.md)
now requires an owner decision before further computation.
The paper should contribute a method; existing datasets support evaluation.

| Phase | Work and acceptance evidence | Current state |
| --- | --- | --- |
| M0: method design and correction | Closest-work matrix, precise objective, pseudocode, constructed implementation/checks; reconcile old benchmark-first guidance | COMPLETE_FOR_OWNER_REVIEW; novelty HOLD |
| M1: novelty and scalable predictor adapter | Reduction audit, delivered-information GP adapter, two revisions and shared-cache timing diagnostics on exposed pools | COMPLETE_INVESTIGATION_NO_GO; 17 constructed checks and 36 timing calls; method distinction/calibration insufficient |
| M2: development evaluation | Approved 48 CPU-hour / 96-hour grant; six-pool outcome-blind admission and 12 constructed checks passed; synthetic full-planning CPU cap exceeds 30-second admission bound | INCOMPLETE_RESOURCE_FIT; owner checkpoint; gate/molecular evaluation NOT_RUN |
| M3: protected evaluation | Freeze allowed population, dependence, roles, protocol, intervals and budget before outcomes | NOT_RELEASED |
| P1: plugin method integration | Typed evidence/plan/report boundary, ordinary-tool control, factual/source/abstention/effort assessment | Existing metadata tools retained; new method integration NOT_RUN |
| J1: manuscript and reproduction | Method-supported claims, figures, reproducible evidence, human/venue review | Design draft only; submission NOT_RELEASED |

## Current candidate and decision gate

The current approved direction chooses REUSE/UPDATE/PLAN before expensive work,
using realized development continuation outcomes to learn operation-specific
benefit. Generic switching and metareasoning are prior art. The approved study
tests incremental discovery/CPU value against fixed, threshold and adaptive
controls. Its original [planning specification](research/configs/m2_experiment_plan_20261108_v1.json)
is retained unchanged; the [release](research/manifests/m2_release_20261108_v1.json)
and [current status](research/configs/m2_status_20261108_v1.json) distinguish
authority from execution. A verified synthetic cap lower bound exceeds its
per-campaign admission bound. Dependent molecular work stopped; the total grant
was not exhausted and method utility has not been tested.

The earlier candidate was computation-bounded baseline-relative rollout under
predictive ambiguity. Its robust objective and fallback have close prior art.
The constructed reference is an adaptation, not a finished novel algorithm.
The [LR-M12 report](docs/03_research/LR_M12_M1_RESULTS_20261108.md) maps the robust
objective to established baseline regret. Its confidence variant retained Greedy
in all 12 diagnostic cases. The distinction is insufficient, so M2 did not run.
Its [owner checkpoint](docs/06_execution/LR_M12_OWNER_CHECKPOINT_20261108.md)
and failed gate remain historical. Contribution approval is a new direction,
not a retroactive M1 PASS. Do not pivot to a benchmark/curation paper.

## Existing data use

The approved M2 scope allows only six historically exposed FS-Mol development
pools (1,285 rows / four annotation components). Fresh outcome-blind admission
passed with no cross-component canonical overlap and all training rows retained. Existing
validation/final payloads and new HIV/Tox21/ChEMBL/MF-PCBA intake are excluded.
The proposed global cross-component canonical mask applies to meta-training only;
evaluation pools and historical roles remain unchanged. It requests new scoped
development-label/counterfactual authority, not a dataset publication.

QP32 and QC500 remain deferred/unreleased. The previous QP confirmation question
is superseded by the owner's method-first decision. No numerical validity grant,
source intake, new cohort or molecular experiment is inferred from this plan.

## Execution boundaries

LR-M12 closed one additional phase's investigation, M1, with a negative transition
decision. Its 24 CPU-hour / 72-hour release retained 7,320 seconds including
utilities/delivery. M2/M3/P1/J1 remain incomplete. All old clocks/ledgers and this
release are closed. No unused resource is borrowed or final outcome opened.
The subsequent M2 release began at 08:17:29Z 8 November, with deadline 08:17:29Z
12 November. It stopped at synthetic CPU admission before biological labels or
molecular evaluation. The resource checkpoint proposes a bounded profiling
amendment; no amendment is approved yet. Return and exact cleanup precede delivery.
M2 scientific evaluation remains incomplete; M3 always returns to the owner.
Routine English checkpoint delivery/corrections are authorized.

Historical protocols/results remain linked from the [claim ledger](docs/00_project/CLAIM_LEDGER.md).
The prior roadmap is preserved in Git at checkpoint
`1950b74d12f33eb08dc0b8a0fabf0ec0dbb7ad7a`; it is not current execution authority.
