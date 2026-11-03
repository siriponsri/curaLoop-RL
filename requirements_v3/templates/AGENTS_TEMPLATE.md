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
