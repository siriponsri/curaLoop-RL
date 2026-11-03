# Agent handoff protocol: GPT Work -> Git -> Codex

## Single source of truth

Git repository files, commits, tests and manifests take precedence over a chat summary. Read `GOAL.md`, `PLAN.md`, `docs/ARCHITECTURE.md`, `docs/RESEARCH_PROTOCOL.md`, `docs/EVALUATION.md`, `docs/DATASETS.md` and this file before writing application code. No silent scope expansion.

## Work phase: build a functional starter app, not the entire lab

Recommended sequence:

1. Read packet, map ambiguities to ADRs; assume CPU-only offline fixtures, no paid API, no access to actual wet-lab data.
2. Create Python `src/curaloop/` package with `data`, `chemistry`, `oracle`, `simulator`, `policies`, `predictor`, `metrics`, `cli` and `report` modules.
3. Provide one fully deterministic 100-500 record synthetic fixture with explicit `synthetic` marker and hidden truth store.
4. Implement random + greedy + uncertainty baselines; require strong error handling and `pytest`.
5. Make end-to-end `make demo` or equivalent run and write `reports/demo/*.json`, metrics CSV and a static figure.
6. Add dataset rights template and LIT-PCBA ingestion stub; do not claim production ingestion before actual sample data verified.
7. Add future RL hooks without unnecessarily installing PyTorch in v1.
8. Commit in small milestones and leave a `HANDOFF_TO_CODEX.md` generated **inside the new repository**, pointing to exact commit SHA, test results and prioritized issues.

## Codex phase: improve through evidence

- Open work on a feature branch, avoid overwriting work without reading tests and ADRs.
- Stabilize assay parser, dataset checks and oracle boundaries before adding new agents.
- Add stronger comparators and evaluation harness; independently rerun old baselines.
- Add bandit meta-policy only after fair benchmarks; add Gymnasium/PPO/DQN only if a testable hypothesis justifies it.
- Implement shift/delay/cost scenarios with reproducible, versioned names and paired seeds.
- Produce reproducible charts, performance tables and negative results.
- Write PR summaries that distinguish code completion, benchmark outcomes and unresolved scientific validation.

## Required status format in every agent report

```
Current branch / commit:
Objective achieved:
Implemented and tested:
Commands executed with results:
Data sources / license status:
Claims supported by evidence:
NOT_RUN / BLOCKED / SYNTHETIC_ONLY:
Open risks and reproducible failures:
Next smallest useful action:
Explicit owner decisions required (only if needed):
```

## Operations policy

- No automatic creation of a public GitHub repo, public deployment, invites, e-mail or external sharing.
- No GPU, paid API, mass download or private connector access without the owner authorizing those changes.
- Small official OA paper retrieval via the included downloader is permitted only in an internet-enabled environment and subject to license checks.
- Do not alter the scientific protocol or evaluate on final held-out labels without documenting and freezing that decision.
- Use a synthetic fixture on every CI run and avoid downloading external data in automated unit tests.
- The owner does not need to mediate each small technical design choice; agents should add an ADR.

## Exit criteria for the starter

A clean clone can install, run tests and execute the synthetic replay; documentation accurately states that no physical twin exists; the oracle remains opaque; reports include source and synthetic flags; the first Codex task queue is actionable without requiring the owner to repeat context.

## Portfolio Edition override

The **primary user goal is a personal professional portfolio demo** for a pharmaceutical R&D audience, not publication at the first handoff. GPT Work must ship **a genuinely usable Streamlit demonstration** in P0–P1, rather than only a CLI + plot. Code correctness, oral/real label separation and truthful twin claims stay mandatory. Codex should first verify the UI and reproducibility, then expand public assay datasets and adaptive/RL comparisons. Do not assume GPO affiliation or authority to access GPO data, identity or visual assets. See `docs/PRODUCT_REQUIREMENTS.md`, `docs/PORTFOLIO_BRIEF_TH_EN.md` and `docs/DATA_GOVERNANCE_FOR_DEMO.md`.
