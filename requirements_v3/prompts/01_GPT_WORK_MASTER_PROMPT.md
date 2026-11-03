# MASTER PROMPT — GPT Work | Build the Actual CuraLoop-RL Starter Project

You are acting as a senior software engineer, pharma-informatics research engineer, UX designer, technical writer and independent QA reviewer. **Implement the first usable version now**, not only a proposal or visual mockup. The attached ZIP is a *specification/handoff pack*; it is not yet a source-code repository.

## 0. Non-negotiable user intent

This is the owner's **independent personal Git portfolio project** for a professional presentation to a pharmaceutical R&D audience, potentially people inside Thailand's Government Pharmaceutical Organization (GPO). It is **NOT** an official GPO project, is not approved or affiliated, and does not access its internal systems, materials, know-how, data or branding. The owner is a solo builder without an existing proprietary dataset and wants a project that can be opened locally, operated during a 5–7-minute presentation, inspected on Git, and later extended by Codex into a proper research benchmark.

Project name: **CuraLoop-RL — Pharmaceutical Screening Decision Lab** (working title). Scientific objective: show how algorithms choose which compounds to test next when assay budget and feedback are limited. Implement a **retrospective screening simulator / digital-twin-ready process model**, not a validated or real-time Digital Twin. RL is an optional later module; do not mislabel heuristics as trained RL.

## 1. Read and audit inputs before coding

Unzip into a safe temporary workspace. Read, in this order:

1. `START_HERE.md`, `audit/AUDIT_REPORT.md`, `GOAL.md`, `PLAN.md`, `README.md`.
2. `docs/PRODUCT_REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/DATASET_AND_LEAKAGE_PLAYBOOK.md`, `docs/ACCEPTANCE_TEST_MATRIX.md`, `docs/UX_BLUEPRINT_TH.md`.
3. `docs/EVALUATION.md`, `docs/RESEARCH_PROTOCOL.md`, `docs/TWIN_VALIDATION.md`, `docs/COST_DELAY_MODEL.md`, `docs/DATA_GOVERNANCE_FOR_DEMO.md`, `docs/SECURITY_AND_PORTFOLIO_BOUNDARIES.md`, `papers/PRIORITIZED_READING_WITH_VERIFICATION.md`.
4. `docs/DEMO_STORYBOARD_TH.md`, `docs/PORTFOLIO_BRIEF_TH_EN.md`, `docs/PRESENTATION_7_MIN_TH.md`.

If old documents differ on priority, use this prompt and `START_HERE.md` for **implementation order** while retaining all strict scientific/privacy requirements. Record ambiguities as ADRs and make practical, well-documented CPU/offline choices rather than stopping for noncritical owner input.

## 2. Scope: deliver a working, modest but polished MVP

**P0:** Create a *new local personal Git repository* `curaloop-rl` in a user-appropriate workspace (never inside an organization's shared directory without approval). Create `pyproject.toml`, `src/curaloop/` Python package, `app/`, `tests/`, `docs/`, `configs/`, `data/demo/` or fixture generator, `.gitignore`, `README.md`, `AGENTS.md`, `CHANGELOG.md`, `ISSUES.md`, and `HANDOFF_TO_CODEX.md`. Pin or lock dependencies in a reproducible way. Python 3.11 is recommended, Windows PowerShell first; offline runtime after installation. Respect owner-controlled Git remote settings: **do not create public repo, push, publish, deploy, invite or change permissions without explicit owner permission**. Local `git init` and local commits are authorized as part of this build.

**P1:** Build an actually usable **Streamlit** 4-tab app with: `Overview`, `Scenario Setup`, `Screening Run`, `Compare & Export`. It must start locally and run without API keys, paid services, GPU or internet, with a deterministic **SYNTHETIC_ONLY** fixture by default. Do not require RDKit for the very first synthetic demo if installation fails; cleanly add RDKit as optional/second milestone for chemical structures. App pages must have real editable controls, working run/step/reset buttons, waiting/delivered outcome display, source banners, true calculations and JSON/CSV exports from an event log. Thai-friendly explanatory labels with correct English scientific terms. Show no fabricated performance/savings numbers.

**P1 simulation core:** Build an `Environment` and `TruthStore` with genuinely separated interfaces. The *agent/policy* receives only feature vectors, valid eligible candidate IDs, previously delivered results, pending IDs, remaining budget, current simulated time and published scenario parameters. No `y_true`/hidden truth in policy input. Private oracle reveals labels only after accepted request and due time; no label to be displayed before delivery. Maintain immutable ordered event records with scenario ID and source type, request ID, policy, seed, step, cost, status, and result when delivered.

**P1 policies:** implement three distinct functioning baseline selectors: (a) seeded Random, (b) Greedy selection from fitted predicted activity, and (c) Uncertainty sampling based on predictor uncertainty. Use a simple sklearn logistic regression or RandomForest with a **common visible initial labeled seed set** and explicit no-two-class fallback. Seed examples must be identical for all policies, and the run manifest must declare whether their assays are included in the campaign cost. Expose policy explanations in plain language, not a complex black-box visual. If a policy cannot legitimately produce probabilities, show fallback status rather than fake a model.

**P1 metrics:** `confirmed_hits` counts *delivered active results only*, not predictions; cumulative confirmed hits vs consumed cost, total selected, pending count, simulated elapsed steps and comparison across policies. Use the same pool, shared initial labels, budget, cost/delay scenario and seed definitions for each comparator. Ensure simulator and UI numbers reconcile. Provide at least one example seed where comparison curves genuinely differ; it must emerge from rules, not hard-coded chart values. Clearly label single-run curves as illustrative, not proof of superior policy.

**P1 security/UX:** no internal GPO assets, no official logo or seal, no organizational endorsement, no claim that the demo saves actual baht, discovers a safe/effective drug, is GMP-validated, or operates a real twin. Prominently label synthetic labels, costs and delays. Handle invalid fields, zero budget, missing labels, no positives, pending-only, duplicate requests, invalid costs and inability to train predictively. Safeguard local paths; avoid arbitrary executable `pickle`/joblib loads from untrusted input. No cloud upload or analytics on user data.

## 3. Build process and real verification

A. Create an implementation plan inside repo as concise checked tasks and a minimal architecture diagram; **then implement code immediately**. No speculative dozens of features before a functional app.

B. Add unit/integration tests from `docs/ACCEPTANCE_TEST_MATRIX.md`; highest priority: no truth leakage; deterministic replay; budget conservation; zero/negative budget; pending/delivered separation; duplicate charging/hits; equal initial labels and budget across policies; export redaction; chart reconciliation. Implement **at least 15 meaningful passing tests** with names and coverage evidence, not tests that only assert `True`.

C. Actually run commands, e.g. `python -m pip install -e '.[dev]'`, `python -m pytest -q`, `python -m curaloop.demo --seed 42`, and `python -m streamlit run app/streamlit_app.py` with a real local UI smoke test. Adapt commands to the actual package. If graphical inspection is unavailable, report that specifically and record what was CLI-verified; do not claim screenshots or UI tests performed.

D. Smoke the end-to-end UX: set budget, run 2–3 cycles, advance to deliver outcomes, compare three policies and export report. Verify event log provenance and that exported data excludes unrevealed labels. Capture real screenshots only if a browser/rendering tool is available; do not use synthetic image-generation as evidence of app behavior.

E. Do not access third-party public datasets until the synthetic MVP works. Public LIT-PCBA loader is a follow-up milestone after site terms and provenance review. The attachment's 25 entries are *bibliographic catalog*, **not** 25 downloaded PDFs. If you can access eligible OA articles, verify per-article license, identity, retraction status and PDF magic/signature; keep binaries out of public Git unless redistribution is explicitly allowed. Do not spend long fetching papers before P1 is working.

F. Use local Git in coherent commits. Before changing the Git remote, pushing or publishing, ask the owner for explicit consent; do not block local repo creation waiting for remote authorization.

## 4. Mandatory outputs

1. Actual runnable local repo, with path and exact git branch and SHA.
2. A functional local dashboard and CLI replay route with commands the owner can copy on Windows PowerShell, plus `start_demo.ps1` when safe.
3. At least 15 substantive passing tests (or transparent log if environment blocked), and examples of CLI output from real runs.
4. `runs/<timestamp>/<run_id>/` or similar stored event traces and run manifest with source/seed/budget/assumptions, no hidden private oracle in public artifacts.
5. README with correct screenshots (real only), architecture diagram, provenance rules, limitations, installation and scientific references.
6. `HANDOFF_TO_CODEX.md` containing: current repo path, exact SHA/branch, implemented vs planned, commands **actually executed**, test results, any mismatches, demo walkthrough status, external data status, top five next issues, how to reproduce, and any owner-only approvals.
7. Local commits. Do not push without permission.

## 5. Acceptance gate / how to stop appropriately

The work is DONE for this phase only if there is a *real tested offline demo* and a valid code repository. If blocked by the environment or tools, still deliver all code and files created, a downloadable source archive if possible, and a truthful blocker report with exact commands; **do not claim the app launched if it did not**. Do not present an empty skeleton as a completed starter.

**Keep first release simple:** no generative molecule synthesis, no docking, no molecular dynamics, no large language model, no patient twin, no GPO data, no regulatory/GMP automation, no actual financial ROI, no purchased service and no purported RL paper results. The first milestone is a compelling but scientifically honest portfolio demo.
