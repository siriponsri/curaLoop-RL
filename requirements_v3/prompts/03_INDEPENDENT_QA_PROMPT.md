# Optional Independent QA Prompt (after Work implementation)

Audit the actual CuraLoop-RL application repository **without rewriting it first**. The intended audience is pharmaceutical R&D professionals, while the project is an independent personal portfolio and not an official GPO system.

1. Read `HANDOFF_TO_CODEX.md`, run tests, inspect the actual UI, run a full synthetic screening campaign and export.
2. Identify critical issues in (i) truth leakage, (ii) shared seed/budget parity, (iii) cost and pending-result ledger, (iv) trained-vs-planned RL claims, (v) simulator-vs-Digital-Twin claims, (vi) synthetic-vs-public labels, (vii) third-party data rights, (viii) any GPO institutional branding/claim.
3. Reproduce a deterministic replay independently using the same seed/manifest. Attempt negative policy attacks that read the private truth; inspect exported artifacts for hidden labels.
4. Classify findings as CRITICAL/HIGH/MEDIUM/LOW with file:line, reproduction and smallest patch. Distinguish `VERIFIED`, `NOT_RUN`, `BLOCKED`.
5. Produce `audit/AUDIT_AFTER_IMPLEMENTATION.md` and a yes/no recommendation for `PORTFOLIO_DEMO_READY`, explicitly without assuming biomedical, manufacturing, clinical or regulatory validation.
