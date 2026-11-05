# Plan A method decision: conditional event-time active search

5 November 2026. **CONSTRUCTED PROTOTYPE IMPLEMENTED; REAL-DATA EVALUATION
NOT_RUN.** Goal4 is conditional on Goal3 data/source/readiness review. The
independent methods reviewer recommended this single architecture, with three
prespecified parameter-support sizes, after the failed Goal2 relaxation.

## Research candidate and closest-work boundary

Use a coherent conditional parameter mixture, one public event of recourse,
and a fixed-list continuation over the whole remaining assay budget. The
computational hypothesis is that valid posterior/rank bounds eliminate enough
fantasy rescoring to outperform an efficient vectorized unpruned calculation.
Compare the discovery/compute tradeoff, not merely bound tightness.

This is an event-time adaptation of [ENS2017](https://proceedings.mlr.press/v70/jiang17d.html).
[Batch ENS2018](https://proceedings.neurips.cc/paper/2018/file/a7aeed74714116f3b292a982238f83d2-Paper.pdf)
already prunes nonmyopic search. [Azimi2011](https://proceedings.neurips.cc/paper_files/paper/2011/file/3a066bda8c96b9478bb0512f0a43028c-Paper.pdf)
already considers waiting/scheduling. [ANS2024](https://arxiv.org/html/2405.15031v1)
already amortizes nonmyopic acquisition. Laplace approximation, TV/chi-square
inequalities, top-k screening and an RL label are not new contributions. A
useful algorithmic combination and its transfer evidence remain to be tested.

## Public state and predictor

Use public Morgan radius2/1024-bit nonchiral fingerprints, deterministic
farthest-first Tanimoto anchors and64 anchor-similarity features plus intercept.
Fit regularized Bayesian logistic regression from delivered/initial labels only;
a proper Gaussian prior includes the intercept, retaining one-class starts.
No class-balancing weights that change hit-probability semantics. Freeze prior,
optimizer/tolerances, feature construction and all fallback behavior before runs.
The constructed implementation uses a zero-mean N(0,4) intercept and N(0,1)
anchor coefficients, L-BFGS-B100iterations/ftol1e-12/gtol1e-8/maxls30, and
probability clipping1e-9. Nonconvergence/Cholesky failure explicitly returns the
prior mixture. Antithetic nested draws retain hypothesis prefixes across M.
Study seeds are explicit unsigned32-bit integers; caller provenance is reviewed.

At each real decision, freeze M parameter hypotheses theta_m drawn from the
declared Laplace approximation, with weights w_m and probabilities p_mi.
Do not sample complete future binary label vectors as the belief. Virtual joint
observations z update q_m proportional to w_m times the Bernoulli likelihood
product. Normalize in log space and predeclare probability clipping. Parameter
weights w and q are nonnegative and normalized. Chi-square is evaluated only
on positive-w support, with q=0 wherever w=0; freeze all numerical tolerances.
draws depend on public features and delivered-label history, not time, pending
identities or sampled durations. Finite support remains an approximation.

Duration law is a separate public distribution, independent of labels/parameters.
Integrate duration events exactly under its finite support; pending residual
times follow D-age conditional on D>age. Timing-only observations never reweight
the label hypotheses. Policy-owned acceptance history supplies elapsed times;
private Task outcomes, due times and outcome-containing resource hashes do not
cross the selector boundary.

## Decision objective and continuation

Root actions are feasible shortlisted dispatch subsets, including partial
capacity, plus WAIT if pending work exists. Include exploitation and information-
sensitive candidates in the shortlist, with deterministic ties; a mean-only
shortlist can miss useful information. The final exact construction is frozen
in the Goal4 configuration. Certificates remain root-shortlist-relative.
The prototype retains posterior-mean top capacity candidates and fills a
four-candidate shortlist by maximizing finite-mixture Bernoulli mutual
information, with deterministic ties. It supports1–2assay workers; with capacity2
there are at most11root actions including WAIT. Every accepted ID is excluded.

For a forced root action, integrate the next public delivery time/identities
and JOINT labels. Update hypothesis weights from labels and choose a fixed list
of remaining compounds, dispatched whenever capacity frees until budget/deadline
exhaustion, with no further hypothetical label feedback. This is deeper than a
single terminal batch but is not unrestricted Bayes-optimal planning.

Under unit costs and candidate-independent IID positive integer durations,
let omega_r be the probability that future-dispatch position r finishes by T,
conditional on the queue AFTER the next public event and its pending ages.
Let B' be the smaller of uncommitted budget after root dispatch and unused
candidate count. Exclude ALL already accepted IDs from the future list.
A queue/renewal dynamic program computes future-list completion weights only.
They are identity-independent and nonincreasing: launch times are ordered
and each newly dispatched duration has the same law, independent of its own
start. Hence the optimal fixed list orders posterior probabilities and its value
is sum_r omega_r*p_(r), up to remaining budget and remaining candidate count.
Sequential unit-duration/sufficient-time conditions recover the ENS exploitation
tail. Candidate-specific duration/cost generality needs another solver; it is
outside this sorting argument and cannot be silently claimed.

Expected positive reward from accepted/root-dispatched jobs completing by T is
added once, separately. Direct pending reward remains even when no new job can
finish. H(T) counts only new delivered source-positive labels, excluding seeds,
predictions, pending jobs and missingness. FS-Mol positives retain their source
potency-threshold meaning; this is not proof of therapeutic efficacy.

## Cheap valid screening and fair reference

For each candidate precompute mu=w dot p, sigma^2=Var_w(p), and range=max(p)-min(p).
For branch weights q, the probability deviation is bounded by the smaller of
range*TV(q,w) and sigma*sqrt(chi2(q||w)). These are standard inequalities under
the frozen finite model, not new theory or biological coverage guarantees.

Clamp mu plus/minus that deviation to[0,1]. Ordered weighted top-budget lower/
upper endpoints bound the fixed-list value. A candidate upper below the kth
lower cutoff cannot enter the top-k list; strict comparisons preserve ties.
Here k=min(B', unused candidate count, number of strictly positive omega).
For k=0 the continuation is zero, with direct pending reward retained. The
kth-largest lower endpoint is computed across the full eligible pool. Retained
top-k candidates still require exact evaluation or certified rank refinement.
Refine only unresolved candidates, and optionally prune root actions when their
integrated upper is below an evaluated feasible lower. Validate every bound
and chosen action against exact evaluation; record remaining gap/fallback.
The prototype reports actual evaluated-root gap and the1e-12 numerical tie
tolerance; it does not round that loss to zero. Nonfinite chi-square arithmetic
falls back to the finite TV bound. Screening preparation is lazy: dense
references never pay for bounds they do not use. The fixed dense-fallback
retained-fraction threshold is0.7, with per-branch fallback reporting.

The primary computational reference is batched **vectorized** full q@P with
partial selection THEN sorting of the selected top-budget values, since omega
depends on rank. Match immutable hypotheses, actions, branches, queue weights
and features using independent copies/state, never shared mutable fitted
campaign state. Do not compare against deliberately slow Python candidate loops.
If dense evaluation is cheaper, a prespecified compute-only fallback is allowed
and its share/cost must be reported. Bound construction, model fit, queue DP,
scoring, caching and failure handling count in actual policy computation.

## Frozen candidates, controls and validation

One architecture, varying only M: C1=32, C2=64, C3=128 hypotheses;64 anchors fixed.
Use nested parameter draws where feasible and matched seeds/histories. No fourth
candidate or outcomes-driven expansion. A failed configuration remains recorded.

Controls: Random, finite-mixture posterior-mean Greedy, frozen-model Greedy,
nearest-hit, parameter Thompson sampling, count-budget ENS adaptation,
unpruned event-time recourse, Azimi2011-inspired CPE scheduling and full greedy
rollout. Include strong standard fingerprint exploitation where feasible in the
measured allocation. Specify every adaptation and do not inherit source theory.
Count-budget ENS and CPE are proxy acquisition references evaluated by H(T);
unpruned recourse and H(T)-valued rollout are objective-matched references.
Freeze root-action, queue-state and rollout-trajectory caps before the canary.
Charge fitting, DP and all baselines to the allocation. Random and nearest-hit
skip unused belief construction. Alternate repeated compute-only comparisons
on identical retained development states to reduce timing-order effects.
The constructed CPE control prioritizes expected additional completions, then
expected prior completed-experiment counts at launch. This explicit adaptation
differs from the source's safety-constrained policy generator. Its20000-state
cap/cache belongs to one campaign; fallback and per-call expansions are logged.
The greedy-rollout reference uses16common-random-number trajectories, lazy
virtual label draws and at most16events. It retains samples/Monte Carlo standard
errors; these are not family-level uncertainty or an exact-value certificate.
No extra exact-recourse computation or full candidate sort is added to that
reference. Unused-candidate count caps the count scheduler's remaining budget.
Required ablations: no-WAIT, suppressed anticipated pending-label information,
and timing-blind budget tail. Shared exclusion of observed/pending duplicates
is feasibility, not a treatment. Model and acquisition effects stay separate.

Exact constructed checks precede real runs: queue probabilities against full
enumeration, deterministic ENS limit, weighted-mixture label/duration integration,
probability/rank/tail bounds, XOR complementary choices, residual conditioning,
direct reward exactly at T, binding budget, omitted root actions, deterministic
ties and hidden-label permutation invariance. Pruned/unpruned decisions must
match when no approximation allowance is used.

Goal4 uses only development/validation labels after role/feature preparation.
Uniform starts retain zero-active cases. Freeze source/config/data identities,
trial plan, effect/uncertainty analysis and compute allocation before outcomes.
Measure a retained canary before projecting all required controls into40CPUh.
Unseen families and operating regimes are tested with explicit crossed design;
no retuning after validation. Final-family labels remain sealed for Goal5.

The output is an evidence-backed candidate decision, not guaranteed success.
If all three configurations lack credible value, consult the owner before a
new thesis or larger study. No confirmatory material-effect threshold is added.
Separate-operator computational reexecution is not external scientific replication.

## Constructed adapter and remaining real-data gate

`research/planning_v3/` now contains the queue, mixture/rank bounds, Laplace
belief, one-event recourse, count/rollout controls and public-Observation adapter.
The adapter receives no Task, source file, resource hash or private due-time
object. Only initial/delivered labels enter fitting; an owned acceptance log
reconciles pending ages, unit commitments and missing results. Hidden-outcome/
duration permutation and actual-engine accounting tests cover all14arms.

Initialize and finish one campaign per worker before initializing another so
the process-global pure queue cache cannot confer an arm-order advantage.
Policy computation is `setup_seconds + sum(decision.policy_seconds)`, counting
setup once, including frozen-model fitting. Source-preparation CPU and process
startup remain separate recorded costs, never simulated assay time.

These are constructed correctness checks, not molecular discovery results.
The first real feature cohort failed required4/2/12group quotas at2/2/7;
the owner must select a [data revision](../06_execution/GOAL3_COHORT_REVISION_OPTIONS_20261105.md)
before dependent preparation/real Goal4 work. A real-data protocol, role-checked
private evaluator, canary/all-arm feasibility measurement, fixed trial selection,
validation and reexecution remain NOT_RUN. No method advantage or novelty is
established by the prototype.
