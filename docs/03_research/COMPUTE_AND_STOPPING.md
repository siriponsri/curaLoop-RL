# Compute plan and stopping rules

## Default resources

The initial programme uses local CPU execution, Morgan features and classical predictors. No cloud account, paid API or GPU is required for the existing POC. The budget for new paid compute is unset. Existing approvals from other projects do not authorize spending here.

Measure runtime and peak memory on representative small and large pools before a large run. Cache features by data/preprocessing hash; do not cache labels into public features. Cache completed scientific outputs only when the full run identity matches. Reserve separate accounting for controller training, validation, final evaluation and figure generation.

For planning, if a representative run takes r seconds, N runs require approximately N*r CPU-seconds before orchestration overhead. Report measured r, CPU/thread configuration and a conservative range. Parallel execution changes wall time and memory use; it does not reduce total work automatically. Keep comparison independence and deterministic operational schedules.

## Stopping rules

Stop an individual run for deadline, budget/candidate exhaustion, a declared training horizon or an explicit logged failure. Stop a batch for the prespecified resource cap or a scientific defect that invalidates the remaining work. Preserve partial artifacts and record why. Do not terminate merely because a favorable significance threshold has been reached unless a sequential-testing procedure was designed in advance.

If a method produces identical actions across every pilot condition, inspect its information and training signal before scaling. If a controller always falls back, count the pilot as a transfer failure and repair the method or narrow the paper. If baseline performance cannot be reproduced, resolve the discrepancy before interpreting adaptation.

## Owner escalation

Ask for a concrete spending cap only when measured runtime demonstrates a need. Present the proposed job count, hardware, expected cost range and what scientific question it resolves. Continue CPU-compatible documentation, analysis and smaller checks while the decision is pending. A no-cost literature or documentation task should not wait for hypothetical compute approval.

## Source-informed compute and stopping scope

R05's preprint reports approximately 8,000 hours of compute on specified server hardware for its study. This is neither an approved project budget nor a precise GPU-hour estimate to apply to this package. Begin with inexpensive matched fingerprint controls, benchmark measured fit/inference time and scale only within the frozen resource cap.

BayBE demonstrates a reaction-yield stopping rule. Boolean best-value improvement can saturate after one hit while further actives still have value. Retain fixed budget/deadline termination in the primary comparison. Any learned or probability-based early stopping is a separate objective with a stated opportunity-cost rule and false-stop analysis; it must not create an unequal hidden budget advantage.
