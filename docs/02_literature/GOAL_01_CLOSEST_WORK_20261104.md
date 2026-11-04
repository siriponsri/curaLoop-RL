# Goal 1 closest work and reuse decision

Checked 4 November 2026. Bounded primary-source refresh, not a comprehensive
novelty certification. The root agent and two read-only research subagents
separated source facts from the proposed method. Existing R01–R28 manifests and
inspected-paper version records remain unchanged. New sources below do not
retroactively become full-text-reviewed entries in that frozen catalogue.

| Source | Established overlap and access | Consequence for the proposal |
| --- | --- | --- |
| [Budgeted Optimization with Concurrent Stochastic-Duration Experiments, NIPS 2011](https://proceedings.neurips.cc/paper_files/paper/2011/file/3a066bda8c96b9478bb0512f0a43028c-Paper.pdf) | Primary PDF inspected: deadline, count budget, parallel labs, pending/elapsed time and possibly empty dispatch; best-value objective and a completed-experiment-count scheduling proxy | Joint when/which/WAIT is already occupied. Adapt this scheduler with the same selector and declared multi-hit objective. |
| [Hybrid Batch Bayesian Optimization, arXiv v3 2012](https://arxiv.org/abs/1202.5597v3) | Primary abstract inspected: dynamically switches sequential and variable-size batch behavior | Neither waiting nor variable batch size alone establishes novelty. |
| [Parallelizing Exploration-Exploitation Tradeoffs in Gaussian Process Bandit Optimization, JMLR 2014](https://www.jmlr.org/papers/volume15/desautels14a/desautels14a.pdf) | Primary paper includes pending uncertainty and adaptive parallelism | Compare a named adaptation; no inherited regret guarantee for binary approximation. |
| [Efficient nonmyopic batch active search, NeurIPS 2018](https://proceedings.neurips.cc/paper_files/paper/2018/hash/a7aeed74714116f3b292a982238f83d2-Abstract.html) | Primary abstract and targeted PDF inspected: finite-budget positive discovery, batching, adaptivity and pruning | Direct objective comparator. Preserve differences in batch feedback, known-positive initialization and sampled-negative data construction. |
| [Nonmyopic Multifidelity Active Search, ICML 2021](https://proceedings.mlr.press/v139/nguyen21f/nguyen21f.pdf) | Primary abstract/PDF sections inspected: budget-aware positive discovery with a cheaper noisy oracle | Multi-fidelity is established and requires actual paired fidelity data; it is a deferred extension. |
| [Cost Aware Asynchronous Multi-Agent Active Search, arXiv 2022](https://arxiv.org/abs/2210.02259) | Primary abstract inspected: asynchronous cost-aware search using Thompson sampling, MCTS and confidence bounds in a robotic sensing setting | Lookahead plus cost/asynchrony is not a new combination. Observation/action and endpoint differences must be retained. |
| [Amortized nonmyopic active search via deep imitation learning, arXiv v1 2024](https://arxiv.org/html/2405.15031v1) | Primary abstract/full-text sections inspected: synthetic imitation of expensive search and real-task transfer | Synthetic pretraining, amortization and generalizing active search already exist. Its reported approximately 15,000 CPU hours concern its whole programme, not a CuraLoop budget estimate. |
| [Adaptive Batch Sizes for Active Learning, AISTATS 2024](https://proceedings.mlr.press/v238/adachi24b.html) | Primary abstract and targeted PDF inspected: probabilistic-numerics adaptive batch sizes | Adaptive parallelism needs a stronger comparator than a fixed-size baseline. |
| [A Nonmyopic Approach to Cost-Constrained Bayesian Optimization, UAI 2021](https://www.auai.org/uai2021/pdf/uai2021.222.pdf) | Targeted primary PDF: constrained Markov decision formulation and feasible rollout planning | A CMDP or lookahead label alone does not establish an advance. |
| [Weighted conformalized selection, arXiv v2](https://arxiv.org/abs/2307.09291v2) | Targeted primary PDF: FDR-controlled selection under specified independence/shift assumptions | Does not automatically cover adaptive delayed calibration or arbitrary cross-assay label shift. |
| [CAP, JMLR 2025](https://www.jmlr.org/papers/v26/24-0452.html) | Primary publisher abstract only; full 74-page paper not inspected | Online selection-conditional coverage/FCR is established; FCR is distinct from FDR and delivered-hit utility. |
| [MF-LAL, ICML 2025](https://proceedings.mlr.press/v267/eckmann25a.html) | Primary abstract: molecular generation with multiple computational oracle fidelities | Multiple fidelities alone are not novelty; computational affinity evidence is not prospective assay validation. |

## BayBE and BoTorch

The BayBE paper reviewed earlier identifies software 0.12.2. Current inspected
release metadata identifies [BayBE 0.15.0](https://pypi.org/project/baybe/),
provenance commit `3d22aeda83cf746ef6e657ece8bda93b248b7f7d`, and
[BoTorch 0.18.1](https://pypi.org/project/botorch/), commit
`cd0249c60b2a81af0d91b5e7d462ef6f574fceec`. These are source inspection pins,
not installed/validated adapters. BayBE is not installed in the inspected local
environment. No installation or dependency change occurred in Goal 1.

BayBE already supplies [finite search spaces](https://emdgroup.github.io/baybe/0.15.0/components/searchspace.html),
[pending recommendations](https://emdgroup.github.io/baybe/0.15.0/concepts/async.html),
[simulation](https://emdgroup.github.io/baybe/0.15.0/concepts/simulation.html),
[constraints](https://emdgroup.github.io/baybe/0.15.0/components/constraints.html),
[serialization](https://emdgroup.github.io/baybe/0.15.0/concepts/serialization.html)
and [transfer](https://emdgroup.github.io/baybe/0.15.0/concepts/transfer_learning.html).
Its [Bernoulli bandit example](https://emdgroup.github.io/baybe/0.15.0/examples/Multi_Armed_Bandit/bernoulli_multi_armed_bandit.html)
targets cumulative reward; saying BayBE only optimizes a best value would be
false. That repeated-arm example does not itself validate without-replacement
molecular generalization. Native bandit source restricts its parameterization;
binary chemical-GP/acquisition compatibility remains a test question.

The inspected simulation helper processes recommended batches with immediate
lookup/addition and does not itself provide this event-time reservation ledger.
That observation is not proof the framework cannot be composed with one.
Likewise, BoTorch's pinned
[multi-step acquisition source](https://raw.githubusercontent.com/meta-pytorch/botorch/cd0249c60b2a81af0d91b5e7d462ef6f574fceec/botorch/acquisition/multi_step_lookahead.py)
already supports configurable utilities, fantasies and pending points. Its
class is a reusable substrate; an absent WAIT parameter is not an incapability
claim about the library.

Exact Boolean EI is zero after an observed value of one when improvement is
defined over that bounded outcome. Gaussian-on-binary or latent improvement
can remain nonzero; do not claim BayBE's default EI necessarily collapses.
The required question is whether the chosen acquisition actually optimizes
cumulative newly delivered hits under the declared model and resources.

Reuse suitable surrogate/acquisition components while keeping the trusted event
clock, public observation boundary and reservation accounting authoritative.
An adapter must preserve exact candidate identity/finite membership, independent
campaign state, common duplicate exclusion, pending treatment distinction,
binary objective semantics, committed cost, RNG/restoration and information
privacy. A recommendation roundtrip alone does not validate this contract.

## Novelty and publication decision

The selected [research thesis](../03_research/CONTRIBUTION_AND_VALIDATION_V1.md)
must demonstrate useful, cheaply obtained action-value bounds or another
substantive decision principle, then test discovery/compute and joint transfer.
This review does not establish that such a result is new or attainable. No
"first joint scheduler", "first learned search", universal guarantee, headline
gain or journal acceptance claim is supported. Review the exact nearest
algorithms before claiming a new theorem or reproducing a comparator.
