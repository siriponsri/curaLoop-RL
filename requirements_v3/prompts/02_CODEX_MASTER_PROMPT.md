# CONTINUATION PROMPT — Codex | Stabilize, Benchmark, Extend

Work in the **actual source repository already produced by GPT Work**, not in the attached ZIP's specification folder. Your mission: improve a *personal* pharmaceutical R&D portfolio app with reproducible, source-labelled evidence. Do not replace everything by a rewrite or turn it into an official GPO tool.

## Read first, reproduce first

1. `git status --short`, `git log -5 --oneline`, `HANDOFF_TO_CODEX.md`, `AGENTS.md`, `README.md`, `GOAL.md`, `PLAN.md`, `docs/` relevant contracts. If the reference ZIP v3 is accessible, read its `audit/AUDIT_REPORT.md`, `docs/DATASET_AND_LEAKAGE_PLAYBOOK.md`, `docs/EVALUATION.md`, `docs/TWIN_VALIDATION.md`, `docs/ACCEPTANCE_TEST_MATRIX.md` and `papers/PRIORITIZED_READING_WITH_VERIFICATION.md`.
2. Run documented Windows/CPU install, unit tests, CLI demo and Streamlit UI smoke test. Report what actually happened. If an existing test fails, fix the failure before expanding the scope.
3. Compare implementation to requirements: hidden-oracle isolation, shared initial labels, no missing-label leakage, exact cost accounting, delayed feedback timing, no duplicate hits/charge, event-log reconciliation, seeded deterministic replay, export excludes oracle truth and real provenance indicators.

## Execution roadmap

**C0 — Stabilization:** fix defects, security, stale docs and broken controls. Add real integration/property-style tests and a golden replay that verifies an entire campaign and report export. Do not falsely claim RL or a twin.

**C1 — Public data:** implement a **rights-aware optional** LIT-PCBA importer and versioned source manifest after checking official terms. Validate assay target/label semantics, canonical SMILES and conflicts, source hash, split definitions and non-redistribution of raw source by default. Ensure identical historical labels exist only in the private oracle until delivered. Build a small sample legally from allowable source data, or keep link-only and mark blocked if terms unclear.

**C2 — Strong baselines:** add diverse and cost-aware non-RL selection, and only when justified Bayesian optimization; tune fairly, with identical seed labels and budgets. Compare multiple seeds and targets. Don't present any statistical advantage without appropriate confidence intervals and target-level independence.

**C3 — Learned control:** add a contextual bandit selecting acquisition strategies, with reproducible training, checkpoint, reward, algorithm configuration and proper target-disjoint evaluation for cross-target claims. Only introduce PPO/Gymnasium if multi-step policy dependencies warrant it. If agent never trains successfully, mark it PLANNED / NOT_RUN; never fabricate metrics.

**C4 — Twin readiness & UX:** expand synthetic cost/delay/queue/failure scenarios and scenario provenance, visualize policy rankings and sensitivity. Still mark `RETROSPECTIVE_SIMULATOR`, not `VALIDATED_DIGITAL_TWIN`. Improve TH/EN UI, 5–7 min demo, real screenshots, compact summary export and accessible charts. Do not touch company data, LIMS or public deployment without authorization.

## Constraints and scientific integrity

- Refrain from molecular synthesis instructions, real-world assay automation, regulated workflows, clinical decisions or claims of discovered drugs.
- Never use GPO internal data, logos, brand endorsements, intellectual property, credentials, network paths or documents. Check employer IP policies before publication; owner's review is mandatory.
- No paid APIs, new cloud services, GPUs, publication, external push or repo visibility change without owner authorization.
- Never substitute synthetic labels for historical bioactivity results without source flags. Synthetic costs/times are NOT measured savings.
- Train/validation/test separation must protect against policy memorization; repeated evaluation on one fully-labelled target is not generalization evidence.

## Done conditions per iteration

Create small reviewable commits locally. Record commit SHA, run commands, tests PASS/FAIL/SKIP, completed features, untested features, provenance, issue links, diff summary, demo status and the next three smallest meaningful issues in an updated `HANDOFF_TO_CODEX.md`. Keep user-facing demo functional after every iteration. If real data or public deployment requires an unresolved permission decision, mark a specific BLOCKED task rather than freezing unrelated local development.
