# Digital twin: operational definition, fidelity and VVUQ

## Do not rename a simulator a twin

This project is an offline screening simulator at the start. A true digital twin requires a physical counterpart and dynamical information exchange with the ability to make useful predictions that influence decisions. The National Academies' 2024 definition explicitly emphasizes a dynamically updated model and bidirectional physical-digital interaction: https://www.ncbi.nlm.nih.gov/books/NBK605502/ . A biological patient twin is a different and significantly harder research agenda, not claimed here.

## Proposed maturity ladder

| Level | Exact term in papers/repo | Real feedback? | Decision to physical system? | Acceptable validation |
|---|---|---|---|---|
| L0 | Static benchmark | No | No | Predictor and dataset diagnostics |
| L1 | Retrospective screening simulator | Historical labels replayed on request, not live updates | No | Algorithmic verification and replay checks |
| L2 | Calibrated process simulator / digital-twin-ready simulator | Uses measured distributions from a known process | No | Calibrated costs, outcome delays, uncertainty and external checks |
| L3 | Assay screening digital shadow | New real assay results ingested in time | No closed real decision-feedback cycle | Actual ingestion audit, drift and calibration monitoring |
| L4 | Decision-support assay screening digital twin | New real results arrive and update predictive state | Recommendations are acted on by a human-approved real screening process | Prospective comparison, feedback provenance, risk/failure monitoring |

This ladder is a **project convention**, not a formal international standard. Do not claim L4 from simulation-only benchmark runs.

## Verification, validation and uncertainty quantification (VVUQ)

**Verification:** the event queue behaves exactly as specified. Given 10 choices with 3-step assay delay, no label becomes visible before step 3; costs are reserved once; each delivered result is counted at most once. Tests should cover terminal budget and interrupted runs.

**Validation:** compare simulated distributions against real process measurements, where those exist. For example: real time-to-result distributions, instrument batch capacity, missing outcomes, replicate disagreement. If they do not exist, annotate every scenario as synthetic and do not claim process calibration.

**Uncertainty quantification:** report whether policy recommendations change across plausible assumptions about delay variance, false-positive rate, observation missingness and prediction calibration. Use distinct uncertainties: model epistemic, aleatoric/assay noise, simulator structural, and external shift.

## Minimum safe integration design for later work

A `LabFeedbackAdapter` validates CSV schema, unique identifiers, signature/provenance and permitted access. It never sends a command to a robot or initiates a wet-lab procedure. A human supervisor can approve a proposed batch and later upload results. Every versioned event stores `measured`, `simulated` or `predicted` source flags. The system then recalibrates forecasts with an explicit model version, reports prediction errors and proposes options; it may not autonomously authorize a hazardous laboratory action.

## Demonstration quality rubric

Do not call any scientific claim validated unless the relevant condition is satisfied:

- **Prediction reliability:** calibrated probabilities and uncertainty intervals on prospectively relevant data.
- **Decision utility:** a real decision is changed, and its outcome is measured.
- **Data synchronization:** new laboratory results are ingested with documented latency and provenance.
- **Operational fidelity:** modeled batch constraints, costs and turnaround time match measured ranges.
- **Feedback loop:** predictions affect a human-approved action and that action produces new measurements used to update the model.
- **Auditability:** end-to-end provenance, versioned snapshots, rollback and error handling.

## Non-goals

No human physiological twin, clinical trial twin, disease progression model, pharmacokinetic body model, synthetic experiment execution by a real robot, hospital intervention, or claim of regulatory approval.
