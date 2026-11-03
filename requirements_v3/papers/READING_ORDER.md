# Related papers: reading map for beginners and research agents

**Catalog:** `papers_manifest.json` (25 curated articles / article URLs). **Original PDF status in this ZIP:** none downloaded; use official PMC OA downloader and its verified report. Article PDF retrieval rights vary. Do not claim 25 PDFs are present.

## Essential: read these before making novelty claims

| ID | Article | Why it matters | Read first |
|---|---|---|---|
| P01 | GLARE, NeurIPS 2025 | RL MDP policy already applied to virtual screening | Yes |
| P02 | Query Matters / SimDMTA, 2026 | Closed-loop DMTA simulator and AL query-strategy comparison already exist | Yes |
| P03 | Multi-fidelity Bayesian Optimization, 2025 | Assay cost and accuracy optimized in automated discovery | Yes |
| P04 | Sample efficient RL + AL, 2024 | Additional RL/AL prior art | Yes |
| P05 | Drug Development Digital Twins schema, 2022 | Avoid overstating the meaning of a twin | Yes |
| P09 | Uncertainty Quantification for In Silico Chemistry, 2026 | Model error and calibration | Yes |
| P10 | Foundation / multimodal models practical guidance, 2026 | Leak-safe benchmark and reproducibility | Yes |
| P11 | Benchmarking PubChem BioAssay, 2020 | Dataset artifacts and biases | Yes |
| P23 | LIT-PCBA original paper, 2020 | Dataset provenance and realistic actives | Yes |

## Suggested study stages

**Session A: understand the problem** - P23 -> P11 -> P10. Learn assays, active/inactive labeling, molecular featurization and benchmark leakage.

**Session B: learn acquisition** - P02 -> P03 -> P04 -> P01. Note what is already known, baseline strengths and realistic cost models. GLARE is probably the most important intellectual overlap.

**Session C: define a proper twin** - P05 -> P06 -> P07 -> P20 -> P24. Trace exactly when a replay simulator qualifies as a model, digital shadow or operational twin.

**Session D: understand uncertainty and practical limits** - P09 -> P15 -> P14 -> P12. Calibration, uncertainty, empirical AL case studies and data infrastructure.

**Session E: optional generation research** - P08 -> P13 -> P16 -> P17 -> P18 -> P19 -> P22. Read for context only; **generative chemistry is not the initial product**.

## One paragraph for your related-work chapter

Previous work already demonstrates RL-guided molecule selection (GLARE), in silico active-learning decision cycles (SimDMTA), and the cost-value trade-off of assays with different fidelities (multi-fidelity BO). An operational digital twin additionally requires validated dynamic updates from its physical counterpart and decision feedback. Therefore, CuraLoop-RL's initial empirical contribution must be a clearly scoped study of policy robustness, sequential budget/delay constraints, calibration and held-out target generalization, implemented as a transparent *retrospective replay simulator*. Claims about a physical digital twin and practical drug efficacy remain out of scope until prospectively validated.

## What the future literature review should extract from each article

Write a structured reading note with: research problem; dataset and its rights; assay type; number of independent tasks; train/test split; baselines; how labels became available; simulation vs actual experiments; metric; seed count; effect size with uncertainty; code and data links; direct overlap with CuraLoop-RL; remaining limitations. Do not mistake paper-abstract claims for replicated evidence.

## Paper references

The canonical article URL for each paper is stored in `papers_manifest.json`; use that manifest when compiling a bibliography and never invent missing DOI or rights statements.
