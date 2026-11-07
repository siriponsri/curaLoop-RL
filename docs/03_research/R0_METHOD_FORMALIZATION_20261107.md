# R0 method formalization and novelty boundary

Date: 7 November 2026. Status: TECHNICAL_CANDIDATE_ONLY; no fitted method,
policy experiment, theorem of improvement or established novelty.
This analysis uses the already reviewed [closest-work ledger](../02_literature/R0_CLOSEST_WORK_20261107.md).

## Decision problem

Let a declared finite measured panel contain compounds x, assay contexts a and
actually observed outcomes y(x,a). The panel is held by a trusted evaluator.
This phase does not read it or assume that unmeasured pairs have outcomes.
The intended endpoint and compatibility rule are fixed before using outcomes
for development choices; binding and functional endpoints remain distinct.

Let z(a) represent uncertain assay semantics, such as the stated biological
system or the compatibility of a source measurement with that endpoint.
Assays can share a latent context factor, so one verified fact may affect several
candidate transfers. A source graph records exactly which downstream decisions
depend on each fact. A source citation is not itself a compatibility judgment.

The state contains verified facts, explicit competing interpretations, available
supported actions, observed development measurements and remaining resources.
An action can obtain permitted evidence about a context factor, reveal one
supported panel measurement, recommend a shortlist, or abstain/stop. The
observation model must say what each action actually reveals and whether that
observation is trusted, noisy or unresolved. No invented oracle or prior is
supplied by this formalization.

The target is endpoint-compatible molecular decision utility subject to separately
declared measurement and evidence/compute budgets. A later study must choose an
appropriate utility, endpoint thresholds and uncertainty/coverage readout before
final evaluation. CPU, network, analyst and lab costs are not interchangeable.
No resource exchange rate or significance/material-effect threshold is chosen
from the old pilot or this metadata sample.

## Candidate implementation principle

Construct an explicit dependency map from unresolved shared context to admissible
transfer, predictor input and shortlist changes. At a decision step, identify
whether plausible context resolutions could change a supported next action.
If they cannot, skip evidence acquisition for that decision. If they can,
estimate its decision value and compare against supported measurement actions
under the actual remaining resource constraints. Stop or abstain when the
remaining recommendation is unsupported or the cost exceeds the released budget.

This describes a candidate policy family, not a new algorithm. A practical
implementation would need a computable approximation, well-defined semantic
alternatives, audited evidence resolution and fair compute accounting. Enumerating
every joint context/outcome hypothesis may be intractable; a factorization is a
design hypothesis, not an efficiency result. A recommendation stable across
enumerated interpretations is only conditionally stable; omitted interpretations,
prediction error and new biology can still invalidate it.

## What existing work already covers

[Javdani et al.](https://proceedings.mlr.press/v33/javdani14.html) already study
tests that resolve decision regions. In the finite, deterministic special case
where the task is to identify a stable recommendation from fixed hypotheses,
our description is an instance of that established problem. A dependency graph
or another name for value of information does not establish a new contribution.

[Nguyen et al.](https://proceedings.mlr.press/v139/nguyen21f.html) already combine
cheaper surrogate observations with expensive faithful observations for active
search. Treating metadata as a cheap oracle does not establish novelty. Shared
semantic uncertainty might require a different practical observation model, but
correlation alone is not a proof that prior methods cannot represent the task.

[AssayMatch](https://arxiv.org/abs/2511.16087),
[PCAM](https://link.springer.com/article/10.1186/s13321-026-01316-0) and
[ChEMBL annotation](https://link.springer.com/article/10.1186/s13321-026-01165-x)
already address assay compatibility, context-aware prediction or annotation at
different layers. The candidate must demonstrate incremental decision value
while holding the predictor fixed and using a competent upfront-context control.
The current finite formulation is a standard sequential decision problem; the
novel technical/computational element remains to be established.

## A falsification result from the assumptions

If all relevant context evidence is available upfront at zero cost in every
constrained resource, and a policy is allowed to ignore evidence, an optimal
upfront-informed policy cannot be worse than an optimal adaptively informed one.
To see this, the upfront policy can simulate any adaptive policy and expose to
its own decision rule only the facts that the adaptive policy would have obtained,
thereby taking the same measurement actions and obtaining the same utility.
It can also choose to use the additional facts. This is an elementary argument
about information availability, not a claimed novel theorem or a guarantee for
any particular fitted implementation.

Therefore real evidence cost, latency, admissibility or access limits are needed
to justify an adaptive-evidence benefit. A badly implemented upfront baseline,
artificially hidden free metadata or an invented lab-price ratio would not be
convincing evidence. Retrieval latency in this metadata audit is technical burden,
not demonstrated decision-resolution cost or experimental savings.

## Readiness verdict

The problem can be specified, but the present proposal has not yet demonstrated
a substantive method distinction. The metadata audit provides no reference
interpretations, observed panel or evidence-action yield; it cannot test planner
value. The defensible next discriminating study is a bounded, outcome-masked
development reference audit establishing natural decision-changing uncertainty
and real resolution cost, followed by a frozen same-predictor comparison.
Do not skip that data/reference gate by starting an RL or lookahead run.

R0 method gate: REVISE. Method benchmark result: NOT_RUN. No publication-ready
claim follows from this formalization. Any benchmark-only or product-only pivot
is a material owner decision, not automatic continuation.
