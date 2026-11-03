# RL Decision Policy Roadmap and Prior Art

## No novelty by combining buzzwords

Prior art already includes GLARE (2025, RL-guided virtual screening with GRPO), SimDMTA (2026, iterative DMTA selection and docking-proxy assays), REINVENT4 (2024, molecule generation and RL optimization), and cost-aware multifidelity Bayesian optimization (2025). Therefore 'RL + drug discovery' and 'closed-loop drug screening simulation' are not novel claims.

## Modelled task

At step t, observation `s_t = (available descriptors, delivered labels, pending requests, predictor summary, remaining budget, simulated time, constraints)`. Action chooses a valid *acquisition strategy* or selected unqueried compound IDs and stop/wait choice. Environment schedules results and reveals only delivered observations. Reward should be a **pre-registered function of delivered hits and allowed cost/time/invalid-action penalties**, not hidden test labels supplied directly to the policy.

**Important causal issue:** a historical fully-labelled dataset lets the simulator reveal outcomes upon selected action, but it does not establish what would happen in a prospective lab. Changes to synthetic noise/cost/delay are scenario studies, not actual measured fidelity levels.

## Recommended complexity ladder

1. **P1:** Random, Greedy predicted probability, Uncertainty; all functioning and equally initialized. Diversified selection optional next.
2. **P2:** Strong non-RL cost-aware baselines, diversity, Bayesian optimization where justified. Baseline tuning budget transparent.
3. **P3:** Contextual bandit/meta-controller selecting between acquisition strategies. Use episodes trained on separate target/task families or synthetic distributions. Compare against fixed and adaptive non-RL rules.
4. **P4:** Gymnasium environment and recurrent/sequential RL (e.g. PPO) **only if** the bandit fails to handle delayed rewards or future state dependencies. Justify algorithm choice and test ablations.

## Pre-registered reward (example hypothesis)

`r_t = a*(new_delivered_active_hits) - b*(new_cost_units) - c*(waiting_penalty) - d*(invalid_actions)`.

Coefficients `(a,b,c,d)` are explicit scenario settings. Primary evaluation **still uses domain metrics** (confirmed hits at equal spent cost), not just return reward because reward shaping can game the metric. No reward to a policy from unrevealed private labels.

## Comparison validity

Shared budget, seed definitions, candidates, starting labelled examples and oracle access. If one policy trains across multiple tasks while baseline cannot, quantify additional data and compute. Split policy training/validation/test by target/family for generalization; report target-level sample size and intervals (multiple repeats on one target do not substitute independent targets). Include calibration/uncertainty diagnostics, not just cumulative hits. Do not call improvements statistically significant without appropriate tests and confidence intervals.

## What could be a genuine publishable question later?

'Under which combinations of delayed assay feedback, heterogeneous costs, calibration drift and target shift does adaptive meta-policy learning improve *confirmed-hit discovery per assay budget* relative to properly tuned non-RL acquisition strategies?' This is a falsifiable question, not a pre-validated contribution.

## Competitor source links

- GLARE / NeurIPS 2025: https://papers.neurips.cc/paper_files/paper/2025/hash/57ac7ccded0eaaec4ad6f05612289b79-Abstract-Conference.html
- SimDMTA / JCIM 2026: https://doi.org/10.1021/acs.jcim.5c02504
- MF Bayesian Optimization / ACS Central Science 2025: https://doi.org/10.1021/acscentsci.4c01991
- REINVENT4 / J Cheminformatics 2024: https://doi.org/10.1186/s13321-024-00812-5
