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


## Local web v0.2 adapter

`frontend/` is React/TypeScript/Vite/Tailwind with shadcn-style Radix components and Recharts. It presents public API reports; no acquisition model, label oracle or budget arithmetic was ported to JavaScript. `api/main.py` validates input with strict Pydantic integers and calls existing `RunService`, `compare`, and JSON/CSV exporters. Random UUID HTTP sessions are distinct from deterministic scientific run IDs. Each session has a lock and monotonic revision; stale/concurrent mutations return HTTP 409 rather than charging twice. Policies remain fixed/allowlisted. A two-worker executor handles comparison jobs without blocking the main request, each comparison creating fresh campaigns. No model was retrained by the UI rebuild.

Production serves the committed `frontend/dist` through FastAPI on loopback port 8000. Development Vite binds to 127.0.0.1:5173 and proxies API. CORS, Host and Origin checks permit loopback origins only. These are browser isolation measures, not user authentication or a sandbox against local software. Do not bind externally or add arbitrary-code upload. `/api/docs` provides the actual generated contract.

In-memory sessions (limit 40), job history (limit 20), process-local locks and executor are for a solo local demo, not multiuser durable storage. Use one Uvicorn worker. Public JSON can reconstruct pending campaigns after restart through strict event/metric reconciliation; CSV is a ledger export and cannot resume a run. Comparison JSON is not a single-run resume file. No external database, browser CDN, remote fonts or runtime API key is required. Real historical structures are rendered from public canonical SMILES by optional RDKit; synthetic descriptors have no invented molecular drawings.

`/api/v1/meta` separates engine source digest, current Git/dirty state, and a content digest of the built frontend (sorted relative paths plus bytes, cached per server start). Restart after rebuilding assets. A commit alone does not identify uncommitted files. Historical run manifests retain the source identity at creation; newly resumed runs report the current implementation, not a claim of the same executable environment.

### Narrow compatibility and provenance corrections

1. `RunService.report()` now reads historical `source_url` from the existing dataset metadata; synthetic fixtures keep their original source string. No dataset bytes/hashes, assay labels, model checkpoints, scheduler, accounting or acquisition algorithms change.
2. New RUN_STARTED lifecycle descriptions are source-neutral. The former text incorrectly called even a historical replay an "Original synthetic fixture". Resume recognizes that exact legacy description and reconstructs it before exposing the replay log, retaining original frozen events and metrics; a manifest limitation explicitly explains the inherited text. Historical benchmark files are not rewritten. Event schema/IDs and assay semantics remain unchanged.
3. Engine/service formatting was normalized alongside the bounded metadata fixes; no general scientific-engine rewrite was performed. Existing 79 tests were retained, and API regressions cover both corrected provenance and legacy snapshot reconciliation.

Frontend unit fixtures are captured synthetic API responses in `src/__fixtures__`; production imports none of them. Every displayed chart uses actual live public curves or explicitly labelled recorded evidence. Seed-only and pending outcomes are excluded from confirmed new hits. SD whiskers in recorded count charts display a zero-clipped lower bound with an explicit note; exact sample SD is retained in the table.
