# Methods and scheduler specification

## State and information

For task k, let X_k be a finite candidate set and y_i the historical Boolean assay label. At simulated time t, the policy may observe public features, delivered labels D_t, pending requests P_t, remaining uncommitted budget, occupied capacity and the remaining deadline. Unrevealed labels belong to an evaluator/oracle store. Public expected durations or cost quotes may be visible if the scenario declares them; realized future completion times should not be exposed to one method unless they are exposed to all.

The true Markov state would include latent activities and any stochastic process variables. The policy observation is a partial information summary. Describe the operational model as an MDP only when its state and transition assumptions justify that terminology; a compact observation does not automatically make the problem fully observed.

## Actions and feasibility

Version 1 of the new study should retain a manageable action space: choose an acquisition strategy, submit a feasible batch and optionally wait for the next event. Batch size is fixed in the primary comparison; variable batching is a separate extension. A WAIT action must advance to a meaningful next event or terminate when no event is pending. Penalize or reject invalid actions consistently; do not allow zero-time loops.

At acceptance, reserve the full quoted cost and capacity. On delivery settle that reservation exactly once. Cancellation rules, failed assays and refunds are explicit scenario parameters; the first study should charge accepted assays even if their result later goes missing. A rejected action never consumes cost. Maintain `total = spent + reserved + uncommitted` after every transition.

## Event order

Process all completions at a timestamp as one declared atomic group before the next decision. A stable request ID resolves log order but does not create an artificial policy opportunity between simultaneous outcomes. Refill available capacity according to the policy's permitted action contract. Stop at a fixed deadline after processing events due exactly at that time. Keep late requests pending in the endpoint snapshot and report their commitments.

The current engine advances integer steps. A future continuous-time implementation must be versioned and compared against an integer reference on equivalent schedules. Do not change old event semantics or re-export the old benchmark as a new scheduler result.

## Operational generators

Use deterministic keys `(task_id, scenario_seed, candidate_id, assay_type)` to generate duration and missingness independently of policy execution order. Cost can be constant in the primary analysis and heterogeneous in a secondary condition. A simple heterogeneous-duration generator samples from a declared discrete distribution such as {1, 2, 4} steps; those values are scenario assumptions, not measured turnaround times. A descriptor-related generator may be added only with an explicit causal interpretation and sensitivity check.

The key requirement is label independence: a hidden active label must not determine whether the assay is cheap or fast unless an activity-dependent stress scenario is intentionally declared. Such a stress scenario answers a different question and cannot be silently combined with the primary analysis.

## Pending-aware methods

A baseline can avoid redundant pending selections by penalizing similarity to pending structures, or a probabilistic method can integrate over hypothetical pending outcomes (“fantasies”). Define exactly which mechanism is implemented. A similarity penalty is a heuristic baseline, not automatically PLAyBOOK or GP-BUCB. Reproduce a published method faithfully, or label and justify an adaptation to a finite binary assay pool.

For an ensemble predictor, distinguish mean score, predictive variability and epistemic approximation. UCB uses a declared mean/uncertainty combination; Thompson sampling draws from a model or posterior approximation. Closeness of a single logistic probability to 0.5 is a margin heuristic and remains labelled as such.

## Adaptive controller

The first learned extension may use a small generalizing controller over public campaign summaries and acquisition choices. Include pending workload, remaining horizon and model state only when available. Train on development tasks and operational distributions, tune on validation tasks and freeze before final tests. Compare to a fixed strategy chosen on development data and to a simple hand-designed mixture. Report training cost and actual use of learned decisions.

The existing tabular checkpoints are preserved baselines. Retraining them with additional states or changing their reward creates a new controller ID and checkpoint hash. Removing the fallback label does not solve transfer. An unseen-state policy, abort condition or fallback must stay explicit.

## Reward and objectives

Use delivered active hits as the primary reward signal with feasibility enforced by the scheduler. A deadline gives earlier delivery practical meaning; an additional time/cost penalty is an explicit alternative objective. Report penalty coefficients and their development selection. Avoid reward terms based on hidden labels, final task-wide rankings or future assay completions. Evaluate with the common endpoint even when training rewards differ.

## Matched baselines and acquisition semantics

Use [baseline specification](BASELINE_SPECIFICATION.md) for the explicit no-retrain, nearest-hit and pending-pair contracts. Duplicate exclusion applies to every arm; the H1 treatment is additional use of pending structures/distributions. Log predictor fit frequency and actual scoring direction. “Entropy,” “margin,” “ensemble variance” and “mutual information” are distinct scores and must not share an ambiguous `uncertainty` name in new run manifests.

Pin an adapter to an existing numerical framework only after testing that it receives public features, delivered labels and permitted operational quotes. Hidden labels remain in the evaluator. A Bernoulli hit-accumulation task needs its own acquisition objective; copying best-observed-value EI or a reaction-yield stopping threshold can suppress further useful positive discoveries. There is no new BayBE/BoTorch integration in this release.
