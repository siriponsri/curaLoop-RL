# Product requirements — v1 personal portfolio demonstration

## Scope statement

Build a **usable demonstration application** for pharmaceutical virtual-screening decision support. The application is not a live wet-lab controller, not a manufacturing system and not a validated digital twin. Work locally on Windows and CPU. Write explanations that a pharmaceutical scientist without an RL background can follow.

## Four-screen information architecture

| Screen | User question | Required components | Acceptance |
|---|---|---|---|
| 1. Overview | What is this and what is it NOT? | concise value, 4-step loop, data/source banner, disclaimer, KPI definitions | no unsupported real-world claims |
| 2. Scenario Setup | What should we test and what are constraints? | dataset selection, target name, seed, test-count/cost budget, batch size, delay scenario, policy selector | every input validated; reset explicit |
| 3. Screening Run | How does AI choose and what happened next? | candidate table, selected IDs, policy rationale, step/play control, remaining budget, queued vs revealed results, event timeline | replay deterministic; no unobserved truth shown |
| 4. Compare & Export | Was the approach better than alternatives? | cumulative confirmed assay hits vs budget, comparisons under same seed, elapsed simulated time, diversity if available, legend, report CSV/JSON download, limitations | no fake chart or comparative conclusion |

## User experience

- Start with a **Try Example Demo** state; every screen usable offline on the fixture.
- English UI can be primary; provide Thai titles and simple explanations or a basic language toggle. No machine-translated jargon as user-facing labels.
- Use generous whitespace, readable legends, sensible defaults, progress state and helpful empty/error states. No gradients or animation required; do not consume scope polishing before functionality.
- Use explicit `Run`, `Next round`, `Reset`, `Compare`, `Export` controls with functional state changes and explanatory tooltips.
- Show compact scientific metadata: dataset origin, assay name, label source, seed, policy, scenario ID, cost assumptions and last run version.
- Never let visual design disguise unavailable data or simulated quantities.

## Domain model and data separation

`Compound` (ID, canonical SMILES, optional properties/fingerprint, data source), `Assay` (target, endpoint, label semantics), `Policy`, `Scenario` (cost/delay/budget assumptions), `ExperimentRequest`, `OutcomeEvent`, `RunManifest`, `MetricSnapshot`.

Public historical assay labels and synthetic fixture labels must have different `source_type` flags. The simulator's private oracle is never passed to policy objects. Results are revealed only by approved query actions or timer completion; duplicate selections do not double count hits or spend unpredictably.

## Functional requirements

F01. Offline `try demo` creates a deterministic run, with synthetic numerical descriptors for first offline demo (optional valid SMILES later) and seeded label truth.

F02. At least random, predictor-greedy and uncertainty baselines can be independently executed. Diversity and adaptive bandit added later, not presented as finished until implemented.

F03. Policies make selections based only on visible labels, candidate features, budget and pending queue; tests assert no future/hidden labels enter observations.

F04. Budget ledger reserves or spends cost consistently; overspending and duplicate submissions rejected; stopping conditions exposed.

F05. A result timeline shows `requested`, `pending`, `delivered`; no result is scored before delivery.

F06. Charts and metric counts come from actual persisted events, not hand-coded examples. All results associated with source type and seed.

F07. Export JSON and CSV with run metadata, labels and limitations; never export private oracle table or unauthorized data.

F08. One page explains `digital model -> retrospective simulator -> digital shadow -> digital twin` maturity, marking current stage correctly.

## Nonfunctional requirements

- Windows PowerShell instructions and 1–2 CLI commands for installation and launch after virtualenv activation.
- Offline demo requires no server, credentials, GPU or paid services.
- Python package with type hints, minimal deps, robust exception messages, `pytest` tests; CI smoke test optional after stable local run.
- Synthetic dataset small enough to run in seconds–minutes locally; large dataset ingestion optional and must be resumable.
- Source/rights policy documented before adding third-party downloaded data.

## Honest metrics

- **Confirmed hits discovered:** sum of assay-active outcomes among *delivered* queried tests, not number of predicted positives.
- **Hit recall / EF:** only when full labeled held-out benchmark and valid denominator permit it.
- **Budget used:** simulated units, *not Thai baht savings* unless actual verified cost inputs exist.
- **Policy comparison:** match initial labeled seed sets, query budgets, predictor and other privileged resources; show uncertainty over seeds before claiming method superiority.
- **Discovery timeline:** simulated step/delay, not real clock unless measured.

## Security

All personal portfolio data are public/synthetic. No automatic integration with GPO accounts, internal LIMS, email, shared drives, enterprise SSO, regulated manufacturing or patient data. Do not paste internal proprietary information into test fixtures or generated screenshots. No public host by default.

## Scope acceptance

First release can be considered *Portfolio Demo Ready* when all screens work, fixture replay matches tests, three baselines really run, export matches event log, README uses correct disclaimers and at least one user can follow the scripted 5–7 minute walkthrough on a fresh local run. It is not `Research Validated` or `Digital Twin Operational`.
