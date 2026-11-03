# Implementation architecture / design decisions

`domain.py` defines frozen dataclasses for public candidates, Scenario, PolicyObservation, ExperimentRequest, ExperimentResult, Selection and Event. `_oracle.py` holds private labels and refuses unregistered, early or repeated deliveries. `_datasets.py` loads the attributed historical replay resource in the simulator process only.

`engine.py` validates full batches before mutation, reserves the known integer cost once, caps concurrent pending experiments at batch_size and settles cost once at a delivered or missing outcome. All IDs are unique within a run; no retries or confirmatory duplicate assays exist in this version. Due steps use configured delay plus deterministic per-candidate nonnegative jitter. `advance(n)` processes intermediate steps, so results keep their actual due delivery times. Zero delay delivers only after request acceptance.

Budget invariant: total = spent + reserved + available. Missing results settle cost but produce no Boolean training label or active hit. Seed labels are preexisting sunk cost and excluded from campaign hits. Initial seeds are uniform random without labels for HIV; stratified via a disclosed oracle intervention for synthetic fixtures.

`policies.py` starts a fixed allowlisted worker using `python -I`, public observation JSON, an empty temporary working directory and a reduced environment. `policy_worker.py` has no oracle imports; it fits StandardScaler/LogisticRegression only on revealed labels. Missing/one-class initialization yields explicit uniform-random fallback with no probabilities. Process memory and import guards prevent accidental code access; **this is not a hostile-code sandbox**. Do not add arbitrary Python policy upload.

Greedy maximizes uncalibrated logistic probability. Uncertainty maximizes `1−2|p−0.5|`. It is a probability-margin heuristic, not calibrated epistemic uncertainty. Tie-breaking sorts IDs; uniform sampling is seeded by public state. Changing an unrevealed truth cannot change a first action.

`learning.py` implements a Gymnasium environment and actual tabular Q-learning plus contextual sample-average epsilon-greedy bandit. Actions select one of the three acquisition strategies. State bins use only budget, previously revealed outcomes, known sample count/class availability and pending status. Checkpoints contain actual Q/reward values, action counts, episode returns, seed lists and hashes. Both train on 160 synthetic episodes and are frozen for historical evaluation. No real-assay generalization or optimality claim is made.

`service.py` is the only UI facade. Comparison creates fresh independent campaigns with the same scenario/pool/seed/feature/classifier contracts and checks manifest parity. `evaluation.py` reconstructs metrics and curves solely from public events and rejects corrupt duplicate outcomes. No pool-wide activity prevalence enters a policy observation.

`benchmark.py` runs 10 paired HIV initializations across five policies, computes descriptive means/SD and exploratory paired bootstrap intervals across seeds. A separate evaluator fits a predictor on custom scaffold-disjoint train data and reports test AUROC/AP/Brier; its model/labels are not fed to policies. Within-assay repeated seeds are not independent biological targets. Published MoleculeNet performance uses different data/splits and is not directly comparable.

## Decisions correcting the source handoff

- Schema version **1.1** explicitly supports zero budget, initial-label and clock events, nullable compound IDs for global events, source-specific provenance, and actual controller training status. The v3 1.0 contracts remain archived under `requirements_v3/`.
- Runtime contracts are regenerated in `contracts/` to match actual exports; no claim of compatibility with the older schema is made.
- Original synthetic-only scope expanded at owner request to a licensed historical HIV resource and actual learned controllers. Real labels + simulated operational costs remain distinct.
- No salt/tautomer standardization is claimed. Canonical isomeric SMILES deduplication and Murcko split checks have narrower guarantees; analog/scaffold leakage within a replay pool is not a held-out-generalization test.
- JSON/CSV export is an immutable public audit snapshot; CLI full-campaign replay recomputes and compares records. It is not a full arbitrary event-sourcing persistence server.
- Source identity contains package/dependency versions, source hash, current Git SHA and dirty status. The distribution includes a Git bundle, allowing the owner to restore the actual tested history without claiming access to their Windows machine.

## Digital Twin maturity

Current: **RETROSPECTIVE_SIMULATOR**. Synthetic capacity/delay/missingness are scenario stress tests, not process calibration. No physical counterpart, measured turnaround time, LIMS connection, prospective validation or bidirectional live laboratory loop exists. The ladder is a project convention: static benchmark → retrospective simulator → calibrated simulator → digital shadow → operational decision-support twin. Stages beyond retrospective replay require external evidence and cannot be manufactured by additional UI/code.
