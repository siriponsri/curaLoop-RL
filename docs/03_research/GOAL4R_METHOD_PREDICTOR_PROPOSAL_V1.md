# Goal 4R: predictor and decision-value redesign proposal

5 November 2026. **READY FOR OWNER REVIEW; EXECUTION NOT AUTHORIZED.**

## Intended advance

Investigate **when a molecular model understands chemical relationships well
enough to turn delayed results into more delivered source-positive labels before a
deadline**. Pair this with an [agentic R&D plugin](../04_business/AGENTIC_RD_PLUGIN_PROPOSAL_V1.md)
that converts a literature question into a sourced, executable plan and an
auditable report. The owner selected literature/molecular-database search and
report delivery to team tools as the first integration workflow.

The intended scientific value is a transferable decision principle, with a clear
account of when planning helps, fails or should be skipped. This is an ambitious
hypothesis, not a novelty claim. The [related-work review](../02_literature/REDESIGN_DEEP_REVIEW_20261105.md)
shows that GP predictors, ENS-style tails, waiting, learned lookahead and chemical
agents already exist. A new predictor plugged into our old planner would be a
diagnostic result, not sufficient headline contribution.

## Why revise before scaling

The [completed Goal4 challenge](GOAL4_RESULTS_V1.md) found 32.2% slower screening
in ten matched timing pairs on one development assay. Refinement savings were
12.0%, with 77.2% dense fallback. Discovery differences were small/mixed, and
nearest-hit/RF were stronger on development/familiar point estimates. Selected
M128 made no optional WAIT in 256 crossed planner campaigns. These facts do not
prove a predictor defect or that waiting should have occurred.

The existing predictor has 64 similarity features plus intercept, against 16
initial labels and at most 28 observed labels. Its proper prior ensures defined
inference, but many coefficient directions remain prior-sensitive. Its induced
prior covariance is `4 + sum_j T(x,a_j) T(x',a_j)`, rather than direct Tanimoto
similarity. This is an inspectable structural explanation to test, not a proved
cause of the result.

## Three competing explanations

| Explanation | Discriminating evidence | What would weaken it |
| --- | --- | --- |
| Representation/prior loses useful signal | Predictor-only ranking/proper-score improvement on identical development histories; stronger same-model Greedy | Cheap RF/kNN remain stronger; repaired model does not improve |
| Joint uncertainty misrepresents useful chemical dependence | Pair-label scores and conditional updates outperform the product of the same model's marginals; constructed dependence tests pass | Only marginal scores improve; shuffled-dependence controls behave similarly |
| There is little usable information before the deadline, or recourse misses it | Matched-predictor acquisition effects, tiny exact references and public-state value gaps under fixed schedules | Better Greedy explains all improvement; no reproducible action-value or discovery difference |

## Recommended next goal: 4R1, diagnosis and predictor repair

**Proposed new cap:** 8 cumulative CPU-hours, 12 elapsed hours from a newly recorded
owner-approved start, at most four CPU workers, no GPU or new paid service.
This does not renew or reuse the original Plan A window. All three original M
configurations are complete; any new trial belongs to a new version and ledger.

| Stage | Maximum CPU charge | Work and reviewable output |
| --- | ---: | --- |
| D0: contract and numerical reference | 1 hour | Freeze candidate definitions, sources, supports, score analysis, exposure rules and tiny exact positive/negative information cases |
| D1: shared-history predictor diagnosis | 2 hours | Evaluate current anchor, two repairs, RF, Tanimoto-kNN and nearest-hit on identical exposed-development partitions; report per-assay/group effects and timing |
| D2: acquisition-factor challenge | 3 hours | Cross three joint predictors with retrained/frozen Greedy and the unchanged efficient dense event planner; retain cheap controls, selected-repair ablations and familiar/shifted schedules |
| D3: independent checks and closeout | 2 hours | Fresh-process signatures, source/claim audit, all-attempt accounting, report and owner decision; scoped verified return/cleanup if remote is used |

These are ceilings, not usage forecasts. Measure one canary before projecting the
allocation. Stop rather than silently reduce controls, increase the cap or add
candidates. A new owned remote root, live allocation checks and retrieve/hash-verify
before deletion are required if approved dr-train processing is used.

### Exactly two repair variants

1. **Variance-normalized anchor model:** keep the existing 64 anchor features,
   divide their feature block by `sqrt(64)`, and retain the proper intercept
   prior. This isolates a declared prior-scale repair; it is not feature learning.
2. **Direct Tanimoto Bernoulli GP:** use the same Morgan1024 inputs with covariance
   `sigma_b^2 + sigma_f^2 * T(x,x')`, a Bernoulli logistic likelihood, declared
   Laplace inference and correlated latent-function draws across the whole pool.
   Fix prior scales, jitter, optimization limits, clipping and failure behavior
   in D0 before outcomes. No hyperparameter search or additional prior variants.

The current anchor model is a frozen control. Each posterior draw must represent
one whole correlated latent function. Fantasy weights are updated by the joint
Bernoulli likelihood of the observed subset. Sampling each candidate marginal
independently would destroy the dependence being investigated. Finite-mixture
conditioning is exact only for that approximate finite belief, not biology.

For `n<=600`, a float64 pool covariance needs about 2.75 MiB, but factorization,
conditional sampling and repeated fitting still need measured timing. Six
development assays/four components do not support assuming successful deep
meta-training. Pretrained FS-Mol models remain excluded until their training
assay/compound overlap with our rebuilt final roles is resolved.

### Fixed comparison design

Use only the six already exposed development assays for selection. Keep the two
previous validation groups in an **exposed diagnostic** role, excluded from the
selection rule. No final outcomes, new-source outcome mining, representation
changes or outcome-selected schedule changes are included in 4R1.

Use component-stratified internal evaluation: fit each task model only on that
task's support and score its fixed query set, then average assays within component
and weight the four components equally. There is no cross-task representation
or prior learning in this stage. Report leave-one-component-out sensitivity of
the repair-selection decision; this is internal development evidence, not an
independent transfer test. Primary support size
is 16; a nested support size of 28 is a predictor learning diagnostic, not an
extra campaign budget. Preserve the existing eight seeds and fix partitions by
public IDs before new evaluation. Retain one-class and zero-hit cases.

RF, Tanimoto-kNN and nearest-hit are strong exploitation controls; their scores
are not automatically a Bayesian joint posterior. Fix one configuration per
control. Use the same fingerprint representation to isolate model changes;
count/2048-bit fingerprints or descriptors are a later separately versioned
sensitivity, not an unrecorded rescue trial.

Score ranking with average precision and top-budget precision. Use Brier and log
loss only for declared probability predictions; nearest-hit similarity is a
ranking score unless an explicit probability model is separately specified.
Retain undefined ranking metrics explicitly when no positives occur.
Do not fit a per-task calibration transform on 16 labels or present five-bin
reliability as proof of calibration. Any later calibration method must preserve
a declared probabilistic model and have a separate development protocol.

For a fixed set of query pairs selected without labels, compare joint predictive
log score with the **exact product of that same model's marginals** as the primary
reference. As a secondary stress test, permute latent-draw indices separately by
candidate only at the uniform-weight, pre-fantasy draw stage. This preserves
empirical marginals, but finite-M permutations do not create exact independence;
do not apply them to a nonuniform-weight mixture. Include conditional predictions after a
new label. Pair/compound counts are dependent; aggregate within assay and then
component. These diagnostics cannot certify a full joint posterior.

The campaign cross has three joint predictors (old plus two repairs), each with
retrained Greedy, frozen-model Greedy and efficient dense event planning: nine
arms. Add RF-Greedy, Tanimoto-kNN, nearest-hit and Random: thirteen arms total.
Six assays, eight seeds and four unchanged operations give **2,496 main campaigns**.
For the one repair selected by D1 scores, add no-WAIT, no-pending-information and
timing-blind-tail ablations: another 576, for **3,072 planned scientific campaigns**
before any accepted canary reuse and separately charged reexecution. Freeze
whether a canary cell is reused, and count every actual execution.
Use identical starts and keyed operational realizations. No screened planner,
third repair/fourth joint predictor, deeper planner, learned controller or new utility is introduced.

Keep `H(T)` as newly delivered source-positive labels; initial labels and pending
work do not count. Include all fitting, covariance construction, decision time,
caching and fallbacks in compute. Simulated assay time remains separate from CPU
and actual laboratory time. Use public-only observations and the existing trusted
accounting boundary.

Choose at most one repair by equal-component-macro query log loss at the primary
16-label support size; the 28-label diagnostic does not select the repair. Resolve
exact ties by lower measured fitting/inference CPU then a fixed variant ID.
Report ranking and campaign results even when they disagree with that choice.
Do not select using previously released validation results or repair a failed
candidate after looking at its outcomes. D0 must make this rule executable before
any D1/D2 labels are consumed by the new code.

## Stop, revise or advance

No clinical/material-effect threshold is invented. Report estimates, group
sensitivity and uncertainty; the following are research decisions, not claims of
statistical significance or guaranteed superiority.

- **STOP this acquisition thesis** if cheap controls dominate, improvements are
  explained by stronger Greedy, or dependence diagnostics provide no actionable
  information value. Keep a useful exploitation plugin if the product workflow
  independently passes its tests.
- **REVISE and consult** if ranking improves but joint evidence or mechanism is
  mixed, numerical failures persist, or the canary cannot fit the cap. Do not
  default to deeper lookahead/RL or tune operations to force WAIT.
- **PROPOSE 4R2** only if the repaired belief has credible joint diagnostics and
  matched-predictor planning value appears across components/operations. Require
  a precise algorithmic distinction from the closest work, not only a GP swap.

WAIT frequency is a mechanism diagnostic, never an optimization target. Any
claimed value gap is relative to its specified model/action set and approximation.
Constructed exact cases must include useful information, irrelevant information,
misleading dependence and no-time-for-recourse cases.

## Later goals, conditional and not started

| Proposed goal | Deliverable and dependency |
| --- | --- |
| 4R2: substantive method | Derive/test a decision principle exploiting verified dependence before deadline; compare with objective-matched ENS/batch/rollout/scheduling adaptations. Deeper or robust recourse is conditional, not already selected. Obtain a new budget/protocol. |
| V2: fresh validation | Metadata/structure-only audit of unused, already assigned validation components/assays under a new deterministic reserve rule. Aim for at least four fresh eligible components before outcome access; availability is unknown. Keep the original 12 final components sealed and unchanged. If unavailable, return options to the owner. |
| P1: plugin prototype | Implement the selected literature-to-plan/report workflow with fixtures and local output, under its own bounded contract; may proceed independently of an algorithmic win after approval. |
| Final study / journal package | Freeze method, independent validation, population, source rights and final protocol only after joint review. A second paper-backed benchmark or actual lab timing would need a separate data/rights decision. |

The two evaluated validation groups cannot be renamed untouched. New data must
be checked against all prior exposure and the frozen final structures, with
purging confined to the new cohort so old evidence bytes stay intact. Seeds and
multiple assays are repetitions within annotation components, not independent
families. Retrospective source-actives are not therapeutic efficacy.

## Approval requested only for the next bounded goal

Recommend approval of **4R1 only**, under the 8 CPU-hour/12-hour/four-worker cap
above. Plugin implementation, external writes, new validation labels, Goal5,
new controllers and journal actions remain separate decisions. Current work
delivers a proposal and source review only. Goal4 scientific exit remains
**NOT_PASSED**, final-study design **NOT_FROZEN**, and all new trials **NOT_RUN**.
