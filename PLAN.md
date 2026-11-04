# Evidence-led implementation plan

This plan supersedes the completed English/local-persistence delivery plan while retaining its evidence. Milestones advance when their outputs are inspectable. They do not depend on a fixed calendar deadline.

| Milestone | Work | Exit evidence |
| --- | --- | --- |
| M0: preserve and inspect | Verify source identity, protected bytes, current fallback behavior and documentation map | Source manifest, current-state audit and clean restoration point |
| M1: lock the question | Audit closest prior art; choose the primary endpoint and baseline family | Versioned protocol and novelty decision |
| M2: establish data | Build a licensed multi-task registry; canonicalize, audit duplicates and select targets before outcomes | Data/split manifests, exclusions and task roles |
| M3: expose scheduling choices | Add pending-aware observations, event-time transitions and optional deadlines as versioned scientific changes | Small analytically checkable scenarios and scheduler tests |
| M4: establish baselines | Implement static, diverse, uncertainty and asynchronous acquisition methods using the same predictor | Matched-budget/compute checks and public traces |
| M5: test adaptive control | Replace all-fallback transfer with an explicitly trained controller or document inability to transfer | Held-out-target usage, performance and training-cost reports |
| M6: run a development pilot | Execute 3-5 development targets under a small scenario grid | Failure analysis and locked final design |
| M7: execute final study | Run the frozen held-out evaluation, ablations and uncertainty analysis | Complete machine-readable outputs and regenerated figures |
| M8: assess buyer fit | Conduct authorized R&D discovery and negotiate a bounded pilot | Actual interview/pilot decisions; hypotheses retired or revised |
| M9: assemble release | Build manuscript, supplements, archive and customer evaluation materials | Reproduction receipt, claim reconciliation and submission decision |

## Dependency rules

Literature, baseline implementation and business discovery materials can progress together. Final scientific evaluation follows data and protocol freezing. Customer claims follow customer evidence. The paper can report useful null results; do not redesign the final test after seeing them. Model improvements and schedule changes receive new experiment IDs and preserve prior runs.

## First implementation sequence

Start with issues ENG-01 through ENG-05 in the implementation backlog: protected-state audit, data registry, scheduler specification, delay-invariance check and one strong baseline. These steps resolve whether the proposed research question is observable in the simulator. Avoid expanding UI scope before that question is testable.

Use [research protocol](docs/03_research/PROTOCOL.md), [backlog](docs/06_execution/BACKLOG.md), [Codex prompt](prompts/CODEX_RESEARCH_BUSINESS.md) and [verification](docs/05_product/VERIFICATION.md). Log a completed action once, link its evidence and name the next unresolved dependency. A request for owner input must identify the decision and its consequence; it must not substitute for ordinary implementation work.

## Version-2 protocol dependencies

Before data freeze, close relevant entries in `docs/02_literature/VERSION_DISCREPANCIES.md`. Before baseline freeze, implement the selector/update/one-class contracts in `docs/03_research/BASELINE_SPECIFICATION.md`. Pilot uniform and conditional-known-hit starts separately, measure fit/inference runtime and recalculate total run allocation. Assess a local backend adapter before expanding independent optimization infrastructure. All remain future execution tasks.
