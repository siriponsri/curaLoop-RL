# CF2-Design: one decision on two mechanisms

10 November 2026, Asia/Bangkok. LR-CF2P design workstream.
**Design investigation complete. Verdict: NO_GO_THIS_MECHANISM for the two
generic new-method claims; no selector training is recommended or released.**

This is a contribution decision with a formal contract and falsification
evidence. It is not another failed molecular experiment. Product P-CF1 proceeds
independently using the validated classical CF1 study.

## What was tested as a contribution

| Hypothesis | Plausible scientific value | What is missing | Decision |
| :--- | :--- | :--- | :--- |
| H1: confirmation-error/dependence-aware portfolio selection | A calibrated joint model can change the marginal probability of recovering an additional positive structure group | Generic expected coverage is classical; no specific new computational approximation, uniquely supported joint information or incremental molecular value is established | NO_GO_THIS_MECHANISM as a sufficient new-method claim |
| H2: adapt to delivered confirmation feedback across groups | Feedback may improve future selections under a conditional model | Diversity-aware active search already addresses nonmyopic, diminishing-return discovery; CF1's fixed-arm aggregates do not identify the value of a new adaptive policy | NO_GO_THIS_MECHANISM as a sufficient new-method claim |

The [source matrix](../02_literature/CF2_CLOSEST_WORK_20261110.md) identifies exact
read depth and overlap. Novelty is not disproved for every possible algorithm.
The bounded review did not establish a defensible distinct one. Adding another
mechanism, training round, calibration fit or dataset is outside this release.

## Formal information and objective contract

Let U be an admitted, observation-supported primary-hit confirmation universe.
For each i in U, x_i is public chemistry, g_i is its fixed structure group,
s_i is its permitted primary measurement/score, and y_i is its binary
confirmation label. Source nonpositive includes inactive/inconclusive; unknown
confirmation is outside U. A future model must not replace unknowns with zero.

For a selected set S and outcome realization y, define:

```text
H(S,y) = sum(i in S) y_i
D(S,y) = sum(g) 1{there exists i in S with g_i=g and y_i=1}
F(S | O) = E[D(S,Y) | permitted observations O]
```

State at round t contains permitted primary information, fixed structures/groups,
already delivered confirmation pairs, pending identities and remaining resource
budgets. A policy may choose an eligible confirmation batch or wait if the
future protocol admits delays. Only delivered labels update its state. Hidden
labels, membership/presence from protected final16 and unsupported source
populations are unavailable. Any fitted conditional law must be trained only
within admitted development roles and declared folds.

For a fixed batch and fixed conditional joint law:

```text
F(S | O) = sum(g) [1 - P(Y_i=0 for all i in S intersect group g | O)]
```

Under conditional independence, the all-zero probability is a product of
individual failure probabilities. Without independence it is a joint event.
This distinction is substantive, but the general objective is not a new one.

For each fixed y, adding an item can cover at most its own previously uncovered
positive group. Its gain cannot rise when the selected set grows. Hence D is
monotone submodular pointwise, and a nonnegative weighted expectation over a
fixed joint law preserves that property. Ordinary cardinality-constrained greedy
guarantees require the stated known set-function oracle. They are not guarantees
for estimated marginals, heterogeneous constraints or arbitrary adaptive policies.
This derivation and its limitations align with the classical framework identified
in the source matrix.

After feedback, a conditional marginal can increase: two different groups may
share a latent success state. Observing success in one can raise the other's
probability from 0.5 to 1. Static submodularity therefore does not certify
adaptive submodularity. A future strategy must state and check its own
conditional assumptions instead of importing a theorem by name.

Likewise, encoding label 0 as nonpositive and label g as a positive in known
group g gives D through the group reward min(1, positive_count_g). This is a
reduction to an established diminishing-return discovery formulation, not proof
that a published approximation and a proposed exact optimizer are identical.
Do not transfer hardness results requiring unbounded utilities to this bounded
reward without a valid separate argument.

## Identifiability: what current evidence can and cannot decide

CF1 exposes all six campaigns as development. Its verified aggregates establish
the outcomes of the frozen ranker/operator cells. They do not identify a newly
fitted joint confirmation law, adaptive counterfactual trajectories, causal
effects of measurement policies, unobserved full-library activity or a new final
population. No new row-level outcome was opened to investigate these questions.

Identical marginal probabilities can produce different coverage and even reverse
the best batch. That is a reason to require a joint-information contract, not
evidence that a learned joint model is estimable or helpful in these data. More
CPU or an RL/agent interface does not close this gap. One annotation-connected
component also cannot be promoted to multiple independent biological units by
changing the reporting weight or increasing seeds.

## Constructed falsification evidence

The [twelve exact cases](../evidence/lr-cf2p-20261110-v1/constructed-falsification-v2.json)
use hand-specified finite distributions and rational arithmetic, with zero
molecular records or fits. They are illustrative mechanism checks, not a
biological performance study or a theorem of new-method superiority.

| Case | Actual check | Consequence |
| :--- | :--- | :--- |
| C01 | Two 0.4 marginals give group coverage 0.64 under independence versus 0.40 under perfect correlation | Marginals alone do not determine coverage |
| C02 | Same marginals give same-group coverage 0.40 or 0.80, versus 0.70 for a cross-group batch | A useful choice can change, but requires the joint law |
| C03 | 108 diminishing-marginal inequalities checked under a fixed correlated four-item law | Correlation does not remove static submodularity |
| C04 | Exact conditional gain in another group rises from 0.5 to 1 | Static and adaptive properties must be separated |
| C05 | Two full-library worlds agree on every observed primary-hit confirmation | Selective observations do not identify unsupported full-library outcomes |
| C06 | All eight outcomes under one selected item per group have D=H | Those two endpoints are not independent achievements |
| C07 | A quota gives expected D=0.91; selecting two reliable same-group items gives 0.99 | Expected-coverage greedy is a necessary stronger control |
| C08 | Top ranking gives H=1.70/D=0.98; spreading gives H=1.60/D=1.60 | A hit/coverage tradeoff alone is not a novel selector |
| C09 | Two illustrative utility weights reverse the preferred portfolio | An owner tradeoff preference cannot be inferred from a pilot |
| C10 | Primary ranking selects confirmation probability 0.1 instead of 0.7 | Calibration value is distinct from optimizer novelty |
| C11 | Sixteen outcome patterns agree with the capped multiclass utility | Known-group binary coverage has an established formulation |
| C12 | Exact adaptive utility is 1.5 versus static 1.0 under a supplied latent model | Feedback can help; that fact does not distinguish a new method from active search |

C04 was strengthened after the first constructed run: v1 recorded its simple
inequality, while v2 explicitly conditions and normalizes the finite joint law.
Both attempts are retained; v2 is the decision evidence. No empirical selection,
threshold or result was altered.

## Strong controls required for any later specific method

Keep the existing top-ranked, group round-robin and classical MaxMin arms across
all relevant rankers. Add probability-aware expected-coverage greedy, the same
calibrated predictor with a fixed ranking, the same joint predictor with simple
greedy, and an appropriate diversity-aware active-search adaptation. Compare
adaptive and frozen-feedback variants at matched information and budgets. A
multifidelity comparator needs the actual available-oracle/timing contract;
do not manufacture low-fidelity queries that the retrospective source cannot
support. Oracle diagnostics must be visibly labelled unavailable to deployment.

These controls distinguish predictor/calibration value, dependence-model value,
optimization value and feedback value. Withholding a strong cheap control or
giving the proposed method extra observations would not establish a contribution.

## One final ticket and next actor

Ticket CF2-DESIGN-01 is **RESOLVED_NO_GO_THIS_MECHANISM**. Recommend retiring the
two generic mechanisms as the current new-selector thesis. Do not start another
review/training cycle automatically. P-CF1 still has useful internal product
deliverables; scientific novelty, independent confirmation utility and journal
readiness remain unestablished.

The [conditional evaluation design and cost](CF2_CONDITIONAL_EVALUATION_DESIGN_20261110.md)
is supplied to make the boundary concrete, not as a recommendation to train now.
The next actor is the owner: accept this disposition, prioritize a product
workflow evaluation, or bring a specific materially different scientific claim
for a new bounded decision. No final16, external integration or publication is
released by this design verdict.
