# Method-first research design and executable mechanism reference

**M0 design record. Current follow-up: [LR-M12 M1](LR_M12_M1_RESULTS_20261108.md)
completed with NO-GO for the method transition. A small exposed-data adapter now
executes, but M2 did not pass its release gate and was not run.** The constructed
reference and limits below remain the original M0 scope.

**Owner-approved destination: a methods paper with an R&D plugin. Existing
datasets are evaluation instruments, not the intended publication contribution.**
Date: 8 November 2026, Asia/Bangkok. Base: `1950b74d12f33eb08dc0b8a0fabf0ec0dbb7ad7a`.

## What is selected and what is established

Selected for mechanism development: **computation-bounded, baseline-relative
rollout under predictive-model ambiguity**. This descriptive name is not a claim
to a new algorithm. The scientific question is whether selectively spending
planning computation can improve cumulative historical assay discovery over a
strong matched predictor/Greedy policy when plausible predictive models disagree.

The executable reference is [ScenarioRollout](../../research/method_first_v1/rollout.py).
It uses constructed finite predictive distributions only. Its robust improvement
objective is closely covered by prior work; **NOVELTY_HOLD_PRIOR_ART_OVERLAP** is
the current verdict, not publication GO. The remaining candidate distinction is
a practical active-search computation strategy that must survive matched-cache,
matched-compute and strong rollout comparisons. Generic memoization alone is
insufficient. See the [closest-work review](../02_literature/METHOD_FIRST_CLOSEST_WORK_20261108.md).

The earlier joint paper-evidence/measurement question is no longer a mandatory
core problem. It may be reconsidered only if the method and actual data justify
it. No shared-compound Ki/Kd/IC50 panel or paper-only hidden fact is required to
exercise the current binary active-search mechanism. The 32-target QP and
500-target QC proposals are deferred, not waiting for an execution approval.

## Research hypothesis and candidate contribution

Proposed claim to test, not a finding: a controller can allocate limited planning
computation to baseline-relative alternatives under model ambiguity, retain only
completed favorable comparisons, and preserve a competent baseline at interruption
while offering a useful discovery/compute frontier on existing assay tasks.

The paper must identify a substantive algorithmic or demonstrated methodological
advance beyond robust policy improvement and standard active-search rollout.
A positive toy example, a gate, cached recursion, the RL name or an agent wrapper
does not establish that advance. If the matched established adaptation explains
all benefits, this candidate fails the method contribution test. Do not substitute
a benchmark paper automatically.

## Formal observation and objective contract

- A finite pool has binary historical assay labels. Each acquired label costs
  one measurement unit. Utility is newly delivered assay actives within a fixed
  count budget; initial known positives are excluded.
- The predictor supplies `M` distributions over the same finite predictive
  worlds. These are hypothetical model samples, not withheld historical outcomes.
  All policy controls receive the same distributions, metadata, update rule and
  information. In the reference, equal initial model weights define one common
  mixture and delivered labels update it by conditioning.
- At delivered state `s` and remaining budget `b`, let `G` be deterministic
  common-mixture Greedy with ties by candidate index. Let `G[a]` take `a` once
  and then follow the same adaptive Greedy for `b-1` acquisitions.
- For every declared model with positive conditional support, evaluate
  `Delta_m(a,s) = E_m[U(G[a]) - U(G) | s]` in that **same model**. The candidate
  score is `L(a,s) = min_m Delta_m(a,s)`. It is not a difference between unrelated
  worst-case/optimistic estimates.
- Baseline action has gain zero by identity. Deviate only for a completed score
  greater than numerical tolerance `1e-12`; otherwise return Greedy. This tolerance
  handles floating-point ties, not a meaningful scientific effect threshold.
- The nominal control uses mixture-expected gain with the identical rollout
  engine. Its output explicitly has no robust lower-gain certificate.

## Algorithm and computation boundary

```text
validate predictive distributions and delivered observations
choose common-mixture Greedy action g
initialize best action = g, certified model gain = 0
evaluate Greedy's remaining-budget return vector over predictive worlds
for each remaining candidate in fixed order:
    evaluate candidate-once + adaptive-Greedy continuation
    reuse completed Greedy tails keyed by (delivered state, remaining budget)
    compute within-model return differences and their minimum
    retain candidate only if its completed score exceeds current best
on computation-state limit:
    discard unfinished comparison and retain best completed choice or g
return typed decision, objective, score, cache/state counts and interruption flag
```

The reference allows at most 12 candidates, 64 worlds, 8 models and horizon 6.
Its default bound is 4,096 expanded Greedy states. These are implementation
limits for exact constructed checks, not a new molecular experiment allocation.
The state cap is a computation proxy, not a CPU-hour or wall-clock certificate.
No production-scale pruning, probabilistic approximation bound, assay-model
adapter or asynchronous/multifidelity scheduler is implemented by this reference.

## Narrow property and limits

With exact declared distributions and complete rollout comparisons, a selected
positive minimum difference is nonnegative in each supported declared model for
the evaluated **one-deviation-then-Greedy policy**. Returning Greedy is equality
by identity. Interruption cannot justify a partially evaluated alternative.
This is an algebraic application of established baseline-relative improvement,
not a new theorem or an inherited guarantee from an external paper.

This property says nothing about a true distribution outside the model set,
posterior calibration, approximate samples or a deployed receding-horizon policy
without its own analysis. A constructed counterexample in the tests shows an
apparently positive model certificate accompanying worse realized reward under
model misspecification. Robustness can also cause all-Greedy fallback and forgo
positive nominal gains. Both failure modes are retained.

## Actual constructed evidence

The [mechanism checks](../evidence/method-first-20261108-v1/README.md) include an
independent per-world path enumerator, cached/uncached agreement, last-query
Greedy reduction, interruption, contradictory observations and zero-support models.
One analytical fixture has Greedy expectation 1.1 and deviation expectation 1.3
under a declared synthetic model. Another returns Greedy under ambiguity while
the nominal control deviates. These are mechanism examples, not drug results.

At horizon 3 the recorded cache example uses 15 expanded states versus 17 without
caching and returns the same action. No measured wall-clock speedup follows.
The production screening application and existing scientific runs are unchanged.

## Existing-data evaluation plan

| Existing resource | Intended use | Boundary |
| --- | --- | --- |
| HIV replay and exposed Tox21 derivatives | Later adapter/engineering checks and realistic predictor behavior | Already exposed; not independent efficacy or final evidence |
| FS-Mol original tasks and prepared features | Preferred existing benchmark route for single-assay binary acquisition | Preserve original assay-relative labels, exposure and protected final roles; task counts/groups do not certify families |
| ChEMBL 37 | Optional source/context audit if the selected method needs it | No mandatory QP/QC or new benchmark construction |
| MF-PCBA | Optional later multifidelity extension | Local paired measurement release remains unqualified; do not claim ready data or change endpoint silently |

No new row/label/feature decode, source download, split or model run was done
for this design. A future predictor adapter must build joint predictive scenarios
only from public features and delivered labels, with a provenance boundary that
rejects evaluation-label arrays. A calibrated joint model and usable scaling
approach remain missing. Paper-reading/plugin tools do not supply this for free.

Later comparisons must include Random, frozen/retrained strong Greedy, nearest-hit,
diversity/uncertainty, an objective-matched ENS-style adaptation, ordinary mixture
rollout, matched robust baseline-relative adaptation, cached/uncached variants,
and computation-limited variants. The same predictor/update/cache opportunities
apply across arms. SPIBB/MCTS-SPIBB motivate strong safe-improvement controls;
their offline-MDP assumptions cannot be copied as active-search guarantees.

Primary readout is paired new-actives versus measurement budget plus measured
policy CPU/wall time, memory, predictor calls and fallback/deviation share.
Uniform starts retain zero-hit cases; known-hit starts are separate. Seeds are
within-assay repetitions. Report assay/source/group dependence and uncertainty
without claiming certified 12-family generalization. Do not lower effect criteria
after pilot results; the owner has not set a meaningful-effect margin.

## Gates and next discriminating work

1. **Design/mechanism:** executable reference and constructed checks complete.
2. **Novelty:** HOLD. Compare mathematical reductions and implementation against
   robust baseline regret, ENS and safe rollout; establish a distinction beyond
   a generic gate/cache. A focused review is not proof of an exhaustive gap.
3. **Feasible adapter:** NOT_RUN. A later bounded, exposed-development-only task
   should establish predictive-scenario calibration/scaling and compare the
   candidate with the same cached robust adaptation. QP is not its prerequisite.
4. **Method benefit:** NOT_RUN. A full-scale method paper needs repeated gains
   or a defensible new tradeoff over strong matched controls, with uncertainties.
5. **Final/product/journal:** NOT_RELEASED. Preserve final outcomes and ask before
   the next data/compute phase. No automatic benchmark/curation publication pivot.

Current completion is method-design and small constructed implementation, not
a finished novel method or publishable paper. The [execution/handoff scope](../06_execution/METHOD_FIRST_CHECKPOINT_20261108.md)
records authority, deprecations and next dependencies.
