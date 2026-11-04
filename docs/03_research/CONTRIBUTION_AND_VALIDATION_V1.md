# Goal 1 research thesis and validation decision

Goal 2 amendment: the owner approved real datasets and SSH. The subsequent
[180-run real-data prototype](GOAL_02_RESULTS_V1.md) passed correctness checks
but failed to show useful computation/discovery gains. Its standard relaxation
is not a new theorem. The ambitious thesis below remains a research target;
this dated Goal 1 decision is preserved, not retroactively rewritten.

4 November 2026. Base: main `e181c1b4a7b2ee0c770209e0d6c0287bb893005f`.
**Decision: pursue a high-upside planning-method research target.** The owner
explicitly rejected a narrow benchmark as the final ambition. Existing replay
engineering and development results are foundations for testing the method.
This document selects the research programme; it does not announce a new
validated algorithm, priority claim, trained policy or journal-ready result.

## Research thesis

Working title: **Learning When to Wait in Molecular Discovery**.

Develop a computationally efficient planner that chooses **which compounds to
test, how much capacity to use, and whether to wait for particular pending
information**, using expected new positive labels actually delivered by a
deadline. The intended advance is to obtain useful action-value bounds cheaply
enough to guide these joint decisions. Evaluate whether the decision principle
transfers across independently held-out biological families and operational
regimes. A fast learned approximation is a later extension if the planner first
proves useful; neural imitation alone is already established prior art.

The strongest result would combine a valid planning approximation/error result,
a meaningful discovery-versus-compute advantage over strong non-RL planning,
and transfer in the joint unseen-family/unseen-operations setting. Each part
requires evidence. No numerical benefit or publication outcome is promised.

## Directions considered

| Direction | Potential advance | Main risk and decision |
| --- | --- | --- |
| Posterior-content-sensitive planning of dispatch and waiting | Informative bounds/approximation for cumulative delivered-hit utility under queue, budget and deadline constraints | Strong closest prior art; GO as the core research target, subject to algorithm/theory falsification |
| Risk-controlled assay commitments with delayed calibration | A useful statistical bound on erroneous adaptive pre-delivery commitments | Distinct conformal/selection literature and scarce independent calibration labels; DEFER as a higher-risk alternative |
| Multi-fidelity confirmation scheduling | Allocate cheap tests and expensive confirmations to obtain useful discoveries | Linked endpoint-consistent measurements, confirmation missingness and operational data are not established; DEFER until suitable data exist |

The target is an algorithmic/decision-theoretic contribution. Additional plots,
a WAIT button, an RL name, more endpoints or an interface upgrade do not by
themselves satisfy it. If the core method fails the tests below, report that
result and return the direction for review rather than quietly declaring the
benchmark an equivalent high-impact contribution.

## Prior art that changes the design

The [closest-work review](../02_literature/GOAL_01_CLOSEST_WORK_20261104.md)
records the actual sources and version limits. In particular:

- NIPS 2011 already models a deadline, experiment budget, concurrent workers,
  running experiments with elapsed times and a possibly empty launch action.
  Its count-based scheduling approximation is a direct comparator, not evidence
  that joint timing was missing from the field.
- Batch active search already optimizes finite-budget positive discovery and
  uses aggressive pruning. Hybrid/adaptive batching also predates this project.
- ANS already amortizes nonmyopic active search using synthetic training and
  transfer to real search tasks. Synthetic pretraining is not our novelty claim.
- BayBE and BoTorch already provide substantial acquisition, pending,
  backtesting, modeling and serialization infrastructure. Extend/reuse compatible
  components; do not infer incapability from an absent example.

The research question is whether **the content of the pending information**,
combined with feasible future completions and resource commitments, enables a
better computational decision principle than count/age proxies and existing
lookahead approximations. Neither this intersection nor a proposed error bound
has yet been established as novel. A precise nearest-method comparison remains
part of the prototype challenge.

## Proposed decision model

Use a finite library without replacement. A public state contains delivered
labels, public features/cost quotes, pending identities and elapsed times,
remaining uncommitted budget, free capacity and time to deadline. A declared
joint posterior represents uncertain labels; a residual-time model conditions
on elapsed pending time. Actual unrevealed labels, private due times and task
resource hashes do not enter the policy or its simulated future samples.

Actions are feasible candidate subsets, including partial-capacity dispatch,
or WAIT until the next delivery/deadline. With no pending work or external
arrivals, WAIT is not an unrestricted way to create information. The trusted
scheduler determines the next event; selecting WAIT does not reveal its future
time or outcome in advance. Count only new positives delivered at or before T.
Keep initial labels, predictions, pending work and missingness separate.

Let `Q_model(s,a)` be expected terminal H(T) under a precisely declared
continuation policy/model. The research target is informative lower/upper
bounds `L(s,a), U(s,a)` and a compute-limited action choice. If all bounds are
valid simultaneously, the elementary action-error bound is
`max_b U(s,b) - L(s,a_chosen)`. This identity is a correctness requirement, not
a new theorem. The substantive work is to obtain tight bounds efficiently and
state what policy class, shortlisted actions and continuation they cover.
An exact oracle must use those same semantics when checking a bound. Compute
Bayes-optimal values separately as a quality reference; a bound for one fixed
rollout continuation does not automatically enclose the globally optimal value.

Potential pruning uses whether pending information can still change feasible
future hit-bearing decisions. Preserve a pending result's **direct** H(T)
reward even if it can no longer inform another completed assay. Unknown tails
must contribute to a valid remaining-utility error allowance; a mean-duration
cutoff is insufficient. High-order information interactions and global budget
coupling prevent a certificate based solely on pairwise chemical similarity.
Any claim of adaptive Monte Carlo validity needs simultaneous/time-uniform
control or an appropriate fixed sampling design.

These are theory/algorithm targets, **not implemented guarantees**. Bounds under
a specified posterior and timing model concern planning error within that
model. Biological/model misspecification and real turnaround uncertainty are
separate problems. No distribution-free laboratory guarantee is proposed.

## Concrete algorithm sketch to challenge in Goal 2

The proposed prototype is a bounded search over observation/dispatch events:

1. Construct feasible candidate-batch alternatives, WAIT and a reference-policy
   action. Record shortlist omissions; guarantees relative to a shortlist do
   not automatically cover the full library.
2. Represent a coherent joint label/residual-time belief. Begin with finite
   exact synthetic beliefs so model-relative values can be enumerated. Imagined
   environments may sample latent worlds; continuation policies receive only
   observations that would have been delivered in those worlds.
3. Maintain a lower value from a feasible continuation and an optimistic upper
   value from a relaxed problem. A basic remaining-reward cap at a tree node is
   `possible_pending_completions + min(unrequested_count, floor(uncommitted/c_min))`,
   where future costs are strictly positive. Add already delivered prefix hits
   once. Reduce the future term to zero only when no new completion can occur
   within the declared timing support. Empty candidate sets need no c_min.
4. Prune a branch/action only when its valid upper value cannot improve the
   best feasible lower value, or explicitly account for the discarded value.
   The basic cardinality cap and ordinary branch-and-bound are baseline tools,
   not our claimed novelty. The research task is a cheaper, materially tighter
   bound using the predictive content and completion opportunities of pending
   results, with high-order dependence and shared budgets retained.
5. Spend the online computation allowance on unresolved action comparisons;
   stop with the selected value gap and a declared fallback when the allowance
   ends. Sampling-based bounds require their own validity argument; a finite
   posterior calculation does not remove posterior misspecification.
6. Compare the useful-bound rate, exact action loss and total compute with
   ordinary rollout/MCTS, active-search pruning and the 2011 scheduler. Train
   a student only if this teacher provides a worthwhile decision/compute target.

No step above is a trained/planning implementation in the current workbench.
The algorithmic contribution is rejected if the alleged tightening is merely
the existing bound with a deadline filter or fails the comparator tests.

## Exact motivating example

Two workers; one pending assay P finishes at time 1 and the other worker is free
at time 0. Two uncommitted assay units remain. A1/A2 are active iff a fair latent
bit Z is 1; B1/B2 are active iff Z is 0. New tests cost one assay-budget unit and
take one simulated time unit. Compare:
dispatch A1 immediately, then use its delivered label to choose a distinct active
candidate at time 1; or wait for P and dispatch two candidates at time 1.

| Posterior and deadline | Expected candidate hits: immediate | Expected candidate hits: WAIT |
| --- | ---: | ---: |
| P reveals Z; T=2 | 1.5 | 2.0 |
| P independent of Z; T=2 | 1.5 | 1.0 |
| Either posterior; T=1 | 0.5 | 0.0 |

P itself contributes an expected 0.5 delivered hit equally to both policies.
The queue count/age, costs, capacity and all marginal hit probabilities match
between the first two cases; the **joint dependence differs**, so full belief
states are not identical. A legitimate model must supply that dependence; the
policy cannot inspect Z. This exact constructed calculation distinguishes
content-sensitive decisions from count-only scheduling, not from every prior
content-aware planner. It is not an assay result, a new-priority theorem, a
proven controller or a selected material-effect margin.

The [enumeration](../evidence/goal-01-contribution-20261104/waiting-example-v1.json)
retains all worlds and rational expectations. Goal 2 would test a real planner
against general exact tiny-state oracles; that implementation has not started.

## What the existing implementation actually supports

The research reference exposes public observations at
`research/event_time.py:256`. The old runner refills feasible capacity at each
integer tick (`research/development/runner.py:140`); it does not optimize an
explicit dispatch-versus-WAIT value. The Gaussian selector conditions variance
on pending locations but does not incorporate deadline utility into its score
(`research/development/gaussian_controls_v1.py:119`). Its Gaussian-on-binary
approximation is not a calibrated joint Bernoulli planning model. Final roles
are rejected by the existing development cohort loader.

New post-hoc checks verified all 162 original development/Gaussian run-file
hashes and recomputed 36 matched pairs. In the 72 matched-arm runs:

| Aware arm / heterogeneous condition | Decision calls | Calls with pending work | Fitted calls with pending work | Selected requests with changed score/std |
| --- | ---: | ---: | ---: | ---: |
| LR pending penalty | 86 | 62 | 58 | 88 lowered scores |
| GP pending conditioning | 89 | 67 | 63 | 89 lowered standard deviations |

Every common-delay arm had zero pending work at its decision calls. The
heterogeneous LR pair still had eight hit ties and one loss; the GP pair had
nine ties despite changed trajectories. Thus the old treatment was not simply
inactive, and adding a pending feature does not establish useful planning.
Counts are within-run diagnostics, not independent biological repetitions.
Only selected-score changes are logged; this does not reconstruct every
unselected ranking. [Diagnostic packet](../evidence/goal-01-contribution-20261104/development-diagnostics-v1.json).

## Evidence that could justify the ambitious claim

1. **Mechanism and theory:** exact tiny problems challenge action bounds,
   informative/irrelevant/high-order pending information, stochastic residual
   times, binding budgets and deadline reversals. Any invalid bound blocks the
   corresponding guarantee. Strongly correlated labels must not leak into the
   observation boundary.
2. **Algorithmic comparison:** use matched predictors/information/feasible sets
   for work-conserving expected-hit heuristics, adapted 2011 scheduling, pending
   qTS/UCB, ENS/batch-ENS adaptations and non-RL fantasy rollout/MCTS. Compare
   against both fixed and adaptive parallelism. A predictor change is a separate
   contrast. Published-method adaptations retain their deviations.
3. **Computational value:** measure bound construction, model fitting, fantasy
   generation and selection; report accuracy/utility versus compute, not just
   inference latency. A learned student includes teacher generation and training
   cost. Do not assume the published ANS training programme is affordable here.
4. **Transfer:** distinguish familiar-family/familiar-operations checks,
   unseen-family transfer, unseen-operations transfer and their joint holdout.
   Family/source/chemistry overlap and operational splits must be declared
   before final outcomes. Repeated seeds are within-task repetitions.
5. **Substantive validation:** use the owner's intended 12+ family scope only
   after eligibility/rights closure. Report task/family effects and uncertainty;
   retain uniform zero-hit starts, negative effects, failures and actual
   learned/fallback shares. No confirmatory material margin is selected.

The [validation matrix](../../research/configs/goal_01_validation_requirements_v1.csv)
specifies concrete observations and failure conditions. It is a requirement
catalogue, not an executable/frozen final config or authorization to run it.

## Stop and redesign criteria

Reject the proposed guarantee if any supposedly valid bound excludes exact
tiny-state value, ignores joint information or discards direct pending reward.
Reconsider the method if useful bounds require more computation than a strong
ordinary rollout, remain too loose to alter decisions, or its advantage
disappears under matched predictor/compute and simple content-aware WAIT
controls. A student that uses fallback throughout does not establish transfer.
No synthetic-only gain or growth in endpoint count substitutes for real held-out
evidence. A wide empirical interval is inconclusive, not equivalence.

Goal 1 can finish with this reviewed research decision. Novelty, the planning
result and high-impact empirical claims remain to be earned in later goals.
The next proposed goal is a bounded synthetic prototype/oracle challenge;
data outcome access, large training, remote jobs and Goal 2 are not started here.
