# AGENTS.md — rules for future work on the generated source repository

## Project identity
Independent personal pharmaceutical screening decision-support portfolio. It is not an official GPO product, regulated lab tool or validated Digital Twin.

## Core invariants
- Never pass private historical labels to policy observations or UI before a delivered assay event.
- Do not equate predicted candidates with confirmed active hits.
- Do not overspend, double-charge, count pending results or share results between independent comparator runs.
- Retain deterministic seeds, data-source provenance and run manifest in every experiment.
- No model, RL, claims, paper files or UI screenshots presented as verified without actual evidence.
- Never include confidential company/internal information or unreviewed third-party binary/data.

## Engineering practice
- CPU/Windows first; keep an offline synthetic demo usable after each commit.
- Run tests and demo before calling a milestone complete; report actual pass/fail counts and NOT_RUN.
- Small changes with type hints and precise error messages, no broad rewrites of stable code.
- Do not push/publish/deploy/change access or pay for services without explicit owner authorization.
- Follow attached `docs/ACCEPTANCE_TEST_MATRIX.md` and audit docs for next gates.

## Local web application
- Primary UI: frontend/ React/TypeScript; API: api/main.py; preserve app/streamlit_app.py fallback.
- Reuse RunService/compare/export; do not duplicate scientific inference/accounting in JavaScript.
- Keep source-origin wording conditional for every live historical/synthetic result surface; recorded HIV evidence has its own label.
- Serve loopback only and one Uvicorn worker. Document durable public SQLite snapshots, revisions, interrupted comparisons and validated single-run resume. Streamlit remains session-memory-local.
- When rebuilding frontend, update and commit frontend/dist; record actual build hash and fresh browser evidence for material UI changes.
- Run locked clean-env Python tests, frontend build/lint/tests, and actual browser checks. Preserve resource/benchmark bytes unless a separately documented scientific version change is intended.
- GitHub main publication to siriponsri/curaLoop-RL was explicitly authorized on 2026-11-03. No deployment, paid infrastructure, visibility/access change or organizational integration is implied.
