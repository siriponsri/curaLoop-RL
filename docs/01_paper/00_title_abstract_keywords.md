# Title, abstract and keywords

**Manuscript state: WORKING_DRAFT_WITH_HISTORICAL_PILOT.** The new multi-target study is specified but unexecuted. The final-study title below is conditional on completing that study. Do not submit this draft as a completed multi-target experiment.

## Current working title

CuraLoop: An Auditable Molecular Screening Workbench, Historical Pilot and Protocol for Evaluation under Delayed Feedback

## Candidate final-study title

When Does Pending-Aware Selection Help? A Reproducible Study of Molecular Screening under Delayed Feedback and Resource Constraints

## Abstract

Molecular screening requires sequential decisions under limited budgets and incomplete assay feedback. We describe CuraLoop-RL, a local research workbench that separates public candidate information from unrevealed historical outcomes and records accepted requests, pending commitments and delivered results in an inspectable ledger. The existing pilot uses a frozen 1,200-molecule MoleculeNet HIV derivative, 48 preexisting labels, a 30-assay budget and ten paired initialization seeds. Recorded mean newly delivered actives were 0.7 for Random, 3.8 for Greedy and 0.9 for margin-based Uncertainty. Frozen Q-learning and contextual-bandit controllers each matched Greedy while using an unseen-state Greedy fallback for all 300 requests; this does not establish learned transfer. We specify a multi-target evaluation of pending-aware acquisition under heterogeneous simulated duration, limited capacity and deadlines, with matched predictors, independent comparisons and task-level uncertainty analysis. That evaluation has not yet been executed. The workbench and protocol support reproducible retrospective research; prospective assay utility, laboratory savings and operational Digital Twin fidelity remain unvalidated.

## Scientific contribution statement

The implemented contribution is an inspectable local replay workflow with explicit information and accounting boundaries. The proposed research contribution is a controlled evaluation of when pending work and operational timing change acquisition performance. Learned-controller superiority is a hypothesis and is not supported by the existing pilot.

## Keywords

Molecular screening; active learning; delayed feedback; asynchronous optimization; reinforcement learning; reproducibility; retrospective benchmark; research software.
