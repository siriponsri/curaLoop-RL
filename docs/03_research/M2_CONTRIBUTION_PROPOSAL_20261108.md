# Proposed M2 contribution: predictor-aware selective computation

**Subsequent owner decision, 8 November 2026:** contribution direction APPROVED.
The [detailed M2 experiment plan](../06_execution/M2_EXPERIMENT_PLAN_20261108.md)
now awaits approval of scope and a fresh grant before execution. This dated
proposal is retained below; its original not-yet-adopted wording is historical.
No M2 result or change to the failed M1 verdict is implied.

8 November 2026, Asia/Bangkok. **READY_FOR_OWNER_REVIEW; NOT_RELEASED.**
Starting checkpoint: `77341494ef3141a48402c94b31f141e10045bbf4`.
This is a literature-grounded proposal, not a new method implementation, an M2
result, a novelty certificate, or permission to reuse the closed LR-M12 budget.
The owner requested paper reading and an M2 contribution proposal. No assay
records, labels, protected features/presence, final outcomes or SSH were accessed.

## Recommendation

Target an **innovative molecular computational strategy**, with the candidate
method and its empirical distinction as the contribution. Do not make a new
benchmark publication, generic RL acquisition, or the old robust objective the
central claim.

Working title: **Predictor-Aware Selective Computation for Budgeted Molecular
Active Search**.

Proposed contribution statement, not a completed finding:

> Develop and evaluate a strategy that uses observable screening history to choose
> whether to reuse a surrogate, update it, or invoke nonmyopic search, targeting
> confirmed assay discoveries under separate experimental and computational budgets.

The research question is whether this operational choice can avoid unproductive
or harmful planning and retain useful planning, compared with strong fixed and
adaptive controls. Generic switching and metareasoning are established. The
specific incremental claim must therefore be a demonstrated, identifiable strategy
for this molecular decision problem, rather than a renamed general principle.

## Why this is a different proposal from the failed candidate

The retained [M1 report](LR_M12_M1_RESULTS_20261108.md) measured 36 isolated
planning calls in 12 cases, not discovery campaigns. Its first robust objective
reduces to an established baseline-regret adaptation; its second revision kept
Greedy in all 12 cases under its trace cap. Small-pool predictor diagnostics were
weak, but do not establish that all predictors or nonmyopic search fail.

The proposed controller would learn from **realized development continuation
outcomes**, rather than treating a positive score inside the same uncertain
forecast as proof that planning helped. It selects the computational operation
before paying for expensive candidate generation. The old robust rollout remains
a historical control/component, with no transferred safety guarantee.

This is not a retroactive M1 PASS or a third revision executed under LR-M12.
Changing the entry criterion to a computational-strategy evaluation requires an
explicit new owner decision and fresh execution scope. Readiness to test a frozen
strategy is different from showing that strategy works or is publishable.

## Closest prior art and consequences

Selected primary methods/results were inspected, not merely discovery summaries.
Exact local reading scope and hashes are in the
[reading receipt](../02_literature/M2_READING_RECEIPT_20261108.json).
This is a targeted single-reviewer review; it is not exhaustive or independently
replicated. The 25 downloaded PDFs are not all claimed read in full.

| Source and inspected version | Relevant established idea | Consequence for this proposal |
| --- | --- | --- |
| [MolPAL, arXiv v1](https://arxiv.org/abs/2012.07127v1), local PDF pp.16-18 | Strong Greedy behavior in docking pools; uncertainty estimates may be unreliable; frequent refitting has a cost | Use a competent Greedy predictor and count refitting. Docking top-k recovery is not our measured binary-assay endpoint. |
| [Query Matters, JCIM 2026](https://doi.org/10.1021/acs.jcim.5c02504), local PDF pp.2-4,11 | Acquisition changes behavior in scaffold-focused BRD4 SimDMTA; predicted uncertainty has limitations | Do not infer a universal winner from conflicting acquisition results. Its predicted top-50 docking-defined hit assessment differs from cumulative delivered assay positives. |
| [GLARE, NeurIPS 2025](https://papers.neurips.cc/paper_files/paper/2025/hash/57ac7ccded0eaaec4ad6f05612289b79-Abstract-Conference.html), local PDF pp.4,7 | A learned select/exclude molecular policy trained with GRPO and an uncertainty-modified reward | RL-based molecule acquisition is occupied. A controller/tool wrapper alone does not distinguish CuraLoop. |
| [Adaptive Acquisition, arXiv v1](https://arxiv.org/abs/1906.11471v1), local PDF pp.3-5 | An on-the-fly learned acquisition policy, predictor updates and matched predictor architecture; image classification experiments | Do not claim online acquisition adaptation or alternating predictor/policy training as new. Its objective is not assay-hit discovery. |
| [ENS, ICML 2017](https://proceedings.mlr.press/v70/jiang17d.html); [batch ENS, NeurIPS 2018](https://papers.nips.cc/paper_files/paper/2018/hash/a7aeed74714116f3b292a982238f83d2-Abstract.html) | Budget-aware nonmyopic active search, including batch adaptivity and pruning | Include a credible nonmyopic comparator. A four-step generic rollout is not a reproduction of full-remaining-budget ENS. Batch handling is not new. |
| [ANS, arXiv v1, 2024](https://arxiv.org/abs/2405.15031v1), raw method/evaluation pages | Synthetic-task imitation amortizes ENS into a cheap policy | Learning a cheap approximation of an expensive planner is already established. The proposed target is operation-specific realized benefit, not simply copying expert actions. |
| [MF-ENS, ICML 2021](https://proceedings.mlr.press/v139/nguyen21f.html), inspected arXiv 2106.06356v2, raw PDF pp.2-3 | Expensive and cheap oracle queries run concurrently; pending high-fidelity outcomes enter expectations | Pending-aware or multifidelity search is not an untouched gap. No new fidelity, noisy oracle or assay endpoint is needed for the proposed core. |
| [BMPS, arXiv v3 / UAI 2018](https://arxiv.org/abs/1711.06892v3), raw PDF pp.3-4,9,12 | Learned selection of computations using value-of-information features and computation cost; metareasoning overhead matters | "Learn when to think" is established. No general metareasoning novelty or bound is claimed. The proposed molecular outcome supervision and operation set need empirical justification. |
| [GP-Hedge, arXiv v2 / UAI 2011](https://arxiv.org/abs/1009.5419v2), raw PDF pp.6-7 | Acquisition portfolios; each arm nominates a point, and updated GP means supply rewards even for unchosen nominees | Compare with an adaptive portfolio. Our proposed gate operates before expensive nominees are generated and is trained on realized development hits; this is a testable difference, not proof of novelty. |
| [Learning Active Learning, arXiv v3 / 2017](https://arxiv.org/abs/1703.03365v3), raw PDF pp.3-5 | Classifier/data features predict outcome-based error reduction; simulated training histories account for selection bias | Feature-based learning from counterfactual outcomes is also established. The proposed target is cumulative assay hits and computation allocation, not classification-error reduction. |
| [Online Choice of Active Learning Algorithms, JMLR 2004](https://www.jmlr.org/papers/v5/baram04a.html), primary record and Section 6 excerpt | A bandit master selects active learners; evaluation under selection bias is difficult | A cheap bandit/router control is mandatory. Error on acquired samples is not automatically calibration on the unseen pool. |
| [Adaptive Candidate Restriction, CMES 2026](https://www.techscience.com/CMES/v149n1/69203/html), primary Sections 3 and 6 | Predictive dispersion controls acquisition-scoring effort in RF-SMBO | Reliability-driven computation is close prior art. Its objective is HPO simple regret, and the original rule scores all points below its 2,500-point floor. Our six development pools total 1,285 rows, so its large-pool speedups cannot be borrowed for M2. |
| [LookaHES, January 2026 preprint v1](https://arxiv.org/abs/2601.06505v1), raw PDF pp.1,3-4,6 | Neural long-horizon BO with history-dependent query costs; evaluated with A100 hardware | General neural lookahead and dynamic costs are occupied. Protein/global optimization is not binary pool-hit discovery. Do not call a CPU-limited adaptation an exact reproduction. |
| [CAST, arXiv v1, 2022](https://arxiv.org/abs/2210.02259v1), raw PDF pp.3-6 | MCTS, stochastic multi-agent sensing and cost-aware planning in spatial simulations | Cost-aware asynchronous active search already exists outside chemistry; do not claim the broad conjunction as new. |

Additional local context: [asynchronous BO](https://proceedings.mlr.press/v97/alvi19a.html),
PDF pp.3-4, already handles busy locations; [experimental multifidelity drug
discovery](https://doi.org/10.1021/acscentsci.4c01991), selected PDF passages pp.7-8, includes
actual synthesis/assays with manual intermissions and error handling. They are
context, not evidence that CuraLoop is laboratory validated. BayBE/R05 remain
unavailable for a fresh complete local PDF refresh, as recorded in the
[download status](../02_literature/LITERATURE_DOWNLOAD_STATUS_20261108.md).

## Candidate mechanism to freeze before execution

### Available state

Use only public compound features, labels already delivered, cached model state
and charged runtime history. A small state vector can include:

- Remaining experimental units and remaining computation allowance.
- Number of observed labels and observed class counts, including one-class starts.
- Number of new observations since the last model update.
- Prequential errors: predictions logged before the corresponding labels arrived.
- Cheap ranking-stability/local-support summaries from an already cached model.
- Past measured fitting/planning costs; public pending count/status when applicable.

Feature calculation must be charged. Do not run the expensive planner or fit an
ensemble merely to decide whether to run it. Prequential errors describe selected
queries; they are not an unbiased estimate of error or calibration across the
unobserved pool. No hidden prevalence, final labels, lookahead truth or hindsight
best operation may enter runtime features.

### Three operations

| Operation | Action and information boundary |
| --- | --- |
| Reuse and act | Use the current cached surrogate with a cheap acquisition rule; use the declared common cold-start fallback if a model is unavailable |
| Update and act | Refit the declared surrogate using delivered labels, then apply the same cheap acquisition rule |
| Plan and act | Pay for the necessary declared update and invoke the fixed nonmyopic planner under its remaining computation cap |

Start with one low-capacity operation selector, not an LLM or a deep RL agent.
A regularized benefit regressor or small contextual selector is sufficient to
test the idea. Its exact features, capacity, fallback, tuning slots and training
schedule must be frozen before development evaluation. The operation selector
is frozen during evaluation; ordinary surrogate updates still use new delivered
labels. Choosing a new predictor family within a campaign is outside this minimal
three-operation version.

CPU-friendly RF and Tanimoto-neighbor predictors are candidates for matched
strata, not presumed improvements. A compatible ENS implementation should be
compared within its predictor assumptions. The M1 logistic GP is not the sole
mandatory predictor and is not declared repaired by changing its name or cap.

### Supervision and objective

If later authorized, create training targets only inside development folds:
clone a permitted observed state, force one operation, and simulate its continuation
under a common frozen continuation policy. Pair branches using the same pool,
initial observations and exogenous random schedule. The evaluator may read the
newly approved development truth to deliver requested results; the policy and
state features may not. Branch outcomes are training supervision, not runtime
oracle access or causal treatment-effect estimates in a real laboratory.

For operation `o`, the proposed target is the realized difference
`Delta_H(s,o) = H_B(force(o), common_tail) - H_B(cheap, common_tail)` together
with measured computation cost. This is an outcome under a specified continuation,
not an optimal-action label or an exact value of using the learned gate forever.
Use mixed-policy training histories so training is not confined to Greedy states.

The primary research objective remains newly delivered historical assay positives
at experimental budget `B`, under a separate computation ceiling `C`. Report hits
and CPU separately. Do not invent an exchange rate between a hit, CPU time, money
and clinical value. Initial seed hits remain excluded; zero-hit/one-class starts
remain valid and are not replaced with guaranteed positives.

Do not add a free WAIT operation and market it as a scheduling contribution.
With terminal hits as utility, no time penalty/deadline and no other cost of waiting,
waiting for available information has no declared resource disadvantage. A
meaningful wait-versus-dispatch problem would require an explicitly changed time
objective/constraint and owner approval. Delay is operational context here.

## Proposed paper contributions, conditional on evidence

1. **Method:** a precisely specified, inexpensive, predictor-aware controller
   selecting among reuse, update and planning before their expensive computations.
   The intended distinction is in its observable state, hit-benefit supervision
   and resource-constrained operation choice, not generic algorithm selection.
2. **Scientific/computational finding:** establish when this strategy helps,
   fails or reduces negative planning effects relative to strong matched policies.
   Show the mechanism through ablations and report per-assay variation. This is
   evidence about a method on existing benchmarks, not a benchmark-publication pivot.
3. **Reusable artifact:** a controller interface and public decision/compute
   trace that an R&D agent can call and explain. This supports reproducibility
   and product integration; it is a secondary artifact, not independent evidence
   of a novel algorithm, laboratory autonomy or customer value.

If only a familiar threshold or portfolio explains the benefit, claim at most
that supported simpler strategy. If no incremental benefit remains, the proposed
method contribution is not supported. A nonconstant gate or different actions
are not themselves evidence of improvement.

## M2 evidence needed

### Minimum meaningful controls

- Strong cheap acquisition with the matched predictor; periodic-update and
  update-on-every-delivery schedules selected only in development training folds.
- Always-plan under the same information and CPU limits; credible ENS or a
  clearly labeled adaptation where applicable, with equal cache opportunities.
- A simple cost/stability threshold gate and a bandit portfolio with observed
  feedback. A GP-Hedge adaptation must disclose its surrogate-scored rewards
  and charge all nominated acquisition computations.
- The learned gate without predictor-history features, and without either update
  or planning, to separate state information from extra capacity or tuning.
- Random/uncertainty references for context; hindsight operation choice only as
  an explicitly unavailable diagnostic upper bound, never a deployable comparator.

### Data and independence

The six already exposed FS-Mol development pools can support a first development
study after a fresh explicit release. They contain 1,285 task rows across four
broad annotation groups, not 1,285 independent compounds/families or six untouched
test tasks. They retain the published FS-Mol/ChEMBL-derived binary-assay semantics;
they are not a newly qualified ChEMBL 37 benchmark.

Train/tune the gate within assay-held-out development folds, keeping all states
and seeds from a held-out assay out of its gate training/tuning. Account for
shared molecules/group dependence. These assays have prior exposure and such
folds remain development validation. Do not present them as final validation,
validated biological-family generalization or a publication-complete sample.
No raw-archive expansion, new split or protected cohort is proposed for automatic
execution. Any larger study needs a separate, bounded owner decision.

### Outcomes, accounting and interpretation

Report paired terminal-hit differences and uncertainty by assay, discovery AUC
over acquired budget, controller/fitting/feature/selection CPU, wall time, action
usage, interruptions and budget violations. Seeds are paired repeats within a
task, not additional independent assays. A small number of tasks limits inference.
Define the interval/aggregation procedure before outcome evaluation and retain
null/harmful cases. No clinical or economic meaningful-effect margin has been
owner-defined; do not manufacture one or substitute a post hoc percentage gain.

Count gate training, branch generation, preprocessing, tuning and failed work as
offline cost; count every online gate/model/planner operation. Report cold and
shared-cache conditions consistently. If claiming deployment compute savings,
show the number of campaigns needed to amortize offline training; if online
savings are nonpositive there is no compute break-even claim.

M1 planning calls were already on the millisecond scale. Do not manufacture a
bottleneck with sleeps, deprived baselines, arbitrary tiny caps or unavailable
hardware. If the gate costs more than the useful work it avoids, or updating
every time is both cheap and best, that is a substantive falsification.

M2 should end in an owner report: promising, inconclusive or unsupported, with
effect sizes and uncertainty. Do not require proof of positive molecular benefit
before allowing the very experiment intended to measure that benefit. Conversely,
engineering checks alone cannot release a final study or establish publication
readiness. No automatic third/fourth tuning revision or favorable task replacement.

## Journal and product position

The current [JCAMD scope](https://link.springer.com/journal/10822/aims-and-scope)
allows properly retrospectively validated innovative computational strategies,
while prioritizing experimental validation and encouraging prospective work.
Inference: this route can fit if the molecular insight and incremental strategy
are substantive. It does not mean any assembled pipeline qualifies or that the
proposed experiment will produce publishable results.

For a product, the useful capability would be an agent-callable decision service:
observe public state -> recommend a computational operation/assay decision ->
return the evidence and charged cost. Existing UI screens provide a place to
inspect it later. No trained selector, new-method integration, business advantage
or live laboratory/plugin execution is claimed at this checkpoint.

## Owner decision and exact next step

The requested decision is whether to adopt this **computational-strategy
contribution and amended M2 entry scope**, preserving the failed M1 result.
This proposal is not execution approval. If adopted, prepare a concrete fresh M2
contract with selected predictor/planner, folds, permitted development labels
(including counterfactual branch supervision), workload counts, CPU/time limits,
controls and stop rules for owner approval before any data fitting or campaign.
Keep M3/final outcomes closed and require an owner checkpoint after M2.

Current status: literature-grounded contribution **PROPOSED**; general algorithmic
novelty **NOT_ESTABLISHED**; specific incremental mechanism **HYPOTHESIS**;
new code/training/M2 effects/M3/final efficacy **NOT_RUN**.
