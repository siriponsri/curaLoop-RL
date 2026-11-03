# Research protocol (pre-registration draft)

## Central hypothesis

A **budget-aware, uncertainty-sensitive sequential acquisition meta-policy** may improve hit discovery over strong non-RL active-learning baselines in particular realistic screening regimes. We expect regime dependence; a null result is possible and must be reported. Prior studies GLARE (2025), SimDMTA (2026) and multifidelity Bayesian optimization (2025) already occupy much of the conceptual territory.

## Scope

Small molecules, offline retrospective *pool-based acquisition*. Given a fixed library with known experimental activity labels in a private replay oracle, each agent selects candidates for costly information revelation. This is a screening prioritization benchmark, not molecular generation, prospective experimental discovery or a PK/PD biological twin.

## Task formalization

For target/task `t`, candidate pool `U_t = {x_i}` with fingerprints and structures public to every policy. True binary assay labels `y_i` are accessible only through the oracle. Start from a common and identically selected revealed set `D0_t`, then select batches `B_k` under budget `C_total` and a scenario-specific result delivery schedule. At step `k` the policy receives `obs_k` with known labels, predictive uncertainty and remaining budget. It chooses among selection strategies and optional batch-size variants. The simulator then reserves expense and releases delayed results when due. Equal time, cost, and measurement access must hold across comparators.

### Action design for first experiments

Let actions be a small set of **strategy choices**: `RANDOM`, `GREEDY`, `UNCERTAINTY`, `DIVERSITY`, `EPSILON_GREEDY`, `COST_AWARE`, `STOP`. A strategy's top candidates are deterministic given the same predictor, visible data and seeded tie-breaker. Keep all policies free to use the same pool without hard-coded advantage. Do not claim meta-strategy selection as original by itself; GLARE and other work predate it.

### State

Examples: available pool size, fraction of budget used, pending results, elapsed simulation time, historical observed hit rate with uncertainty, predictor calibration from visible validation data (avoid peeking at hidden test truth), entropy/variance summaries, fraction of distinct visible scaffolds, strategy performance history based on actually revealed labels. Normalize and cap state inputs.

### Reward

Primary measure is cumulative unique confirmed hits at budget `b`. For RL training, use a simple event-based reward, such as `confirmed_new_hits - lambda_cost * cost_units - lambda_delay * elapsed_time`; document units and weights and do not optimize on held-out evaluation targets. Delayed attribution must be deterministic and audited. Report unshaped primary outcome separately to detect reward hacking.

## Data hierarchy

1. **Tiny synthetic fixture:** for integration and anti-leak tests only. Not efficacy evidence.
2. **LIT-PCBA experimental activity labels:** real retrospective replay. Favor `ESR_antago` for first human-scale demonstration; freeze exact release and check the `index.htm` vs root release counts, which differ.
3. **Additional LIT-PCBA targets:** broaden biological/chemical settings and leave some entire targets held out.
4. **Independent external labels:** TDC/OGB/PubChem assays when provenance and assay definitions are compatible; do not merge differently defined endpoints into a fictitious paired assay.
5. **Genuine multi-fidelity data:** only if exact candidate-level low/mid/high experimental measurements exist with traceable assay protocols. Synthetic proxies should be a sensitivity study with explicit labels, not a demonstration of real multi-fidelity value.

## Experimental matrix

Core factors:

| Factor | Baseline | Stress experiments |
|---|---|---|
| Cost | 1 assay unit / queried label | heterogeneous simulated cost units |
| Delay | immediately revealed | delayed outcomes with queue and timestamp |
| Noise | recorded labels unchanged | explicitly injected label noise |
| Budget | fixed assay count | fractional budget levels: 1%, 2%, 5%, 10% of pool, adjusted for label scarcity |
| Batch size | 10 | 1, 20, or adaptive |
| Predictor | RDKit + RF | calibrated logistic regression, optionally other predictors |
| Task shift | within-target replay | held-out scaffolds/targets |
| Missing data | complete measured dataset subset | missing-at-random and informative synthetic missingness |

Where a target has very few actives, predefine lower bounds for inclusion in statistical comparisons; do not filter targets retrospectively based on an agent's performance.

## Training/evaluation partition

- Stage one **within-target policy comparison**: both baseline and policy may adapt during a single retrospective campaign; they never pretrain on labels not yet revealed within that campaign.
- For a policy learned through *repeated episodes*, repeated replay of the same target can memorize all labels. **Do not evaluate the learned policy on that same target and claim unseen-target generalization**.
- Meta-policy training uses distinct training target families or synthetic generative tasks; hyperparameters tuned on validation targets; final statistical claims on held-out test targets with a frozen policy and frozen evaluation protocol.
- Scaffold split applies to predictive generalization; ensure candidate pools are not trivially purged of all positives. Document separate scaffold- and target-level experiment families.

## Pre-registration checklist

- Define positive label meanings and target/task inclusion rules.
- Freeze cost/delay scenario grid, budgets, seeds, outcome metric and label-processing policy.
- Specify baseline tuning and compute budget equality (or report asymmetric resource use).
- Freeze hyperparameters before held-out results.
- State minimum meaningful effect size and uncertainty interval method.
- Register planned ablations and failure conditions.
- Report all scheduled experimental regimes, including failures and null results.

## Scientific limitations

Replay data has selection biases and assay-specific artifacts; availability of all candidate labels does not make prospective assay behavior causal. Simulated delay/cost/noise assumptions are not empirical laboratory measurements. Retrospective scores cannot establish patient safety, effectiveness, chemical synthesizability or economic benefit in manufacturing. No causal policy efficacy is asserted without prospective intervention and validation.
