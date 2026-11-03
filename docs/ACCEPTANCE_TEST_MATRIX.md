# Acceptance evidence — implementation v0.1

This is an implementation self-audit, not external certification. Exact test counts and commands: `AUDIT_REPORT.md` and the pytest XML/log artifacts. Source requirements remain archived under `requirements_v3/`.

| Requirement | Status | Actual evidence |
|---|---|---|
| T01–T04 deterministic fixture, duplicate/malformed records, empty pool | TESTED | test_simulator deterministic generation, duplicate IDs, malformed features, empty/zero budget |
| T05–T07 oracle separation, fake leakage, order independence | TESTED | immutable public observations, hidden-key failures, subprocess private-import guard, changed-private-truth first-action test, row-order invariance |
| T08–T12 reserve once, overspend, duplicates, invalid cost, zero budget | TESTED | simulator request/budget tests, raw request NaN/negative-cost rejection |
| T13–T17 delayed visibility, exact delivery, partial completion, replay, termination | TESTED | due-time, jitter, zero-delay, missing, idempotent completion and event-for-event replay tests |
| T18 public snapshot resume | TESTED | partial pending and completed snapshots reconstruct against a fresh oracle; corrupted logs rejected; JSON upload UI provided |
| T19–T22 random, greedy, uncertainty, one-class fallback | TESTED | real policy subprocess decisions; sorted probability/ranking assertions; no fake probabilities in fallback |
| T23–T25 parity and independent state | TESTED | same scenario/pool/initial labels/classifier contracts; distinct run IDs; state contamination tests; five-policy matched comparison |
| T26–T28 metrics and JSON/CSV exports | TESTED | ledger reconciliation, duplicate-outcome corruption test, round-trip config/provenance/event export; real browser downloads |
| T29–T30 four views, buttons, scenario reset | TESTED | Streamlit AppTest + actual Chromium browser flow; scenario change clears comparison/paired results |
| T31 offline demo | TESTED WITH LIMITS | browser permits only localhost requests; no external HTTP requested in smoke test; actual subprocess policies contain no network calls. OS-level global network disable was not used |
| T32–T33 source flags and personal/non-GPO disclaimers | TESTED / INSPECTED | AppTest source flags; screenshots; source-specific historical vs synthetic banners; cost/time always simulated |
| T34 Windows clean execution | NOT_RUN | PowerShell/CMD instructions supplied; actual isolated install and tests were on Linux/Python 3.12 |
| T35 no company data/secrets/unlicensed raw data | INSPECTED | source/asset inventory and Git scan; only attributed benchmark derivative; no internal data/credentials/logos; no remote |
| T36–T38 dataset provenance, normalization and preprocessing | TESTED / PARTIAL | historical source/resource hashes, RDKit parsing, canonical dedup/conflict checks, source row IDs and semantics; no tautomer/salt normalization claim |
| T39 scaffold split | TESTED | whole-scaffold predictor audit, train/test IDs disjoint, scaffold overlap zero; sequential replay is within one fixed pool |
| T40 truth affects decisions only after delivery | TESTED | private-truth substitution before first action; delayed observed-data invariance; worker public JSON interface |
| T41 trained RL checkpoint | TESTED | tabular Q-learning checkpoint with values/counts/returns; 160 episodes; deterministic retraining test |
| T42 learned-policy target separation | LIMITED | controllers train on synthetic tasks only; HIV is not used in training. No cross-biological-target transfer claim; no target-family benchmark available |
| T43 matched learned/baseline evaluation | EXECUTED | 10 seeds × 5 policies on historical HIV, shared conditions; fallback use exposed and not credited to learned decisions |
| T44 simulated constraints | TESTED | jitter/capacity/missingness/stress tests; SYNTHETIC_ASSUMPTION labels; no measured process fidelity |
| T45 uploads/path security | IMPLEMENTED / PARTIAL | JSON-only 10 MB public snapshot input, strict Scenario validation, no pickle or code execution; malformed reconciliation tests. Comprehensive fuzz/penetration testing not run |
| T46 public exports | TESTED / INSPECTED | no hidden truth table; no pre-delivery label in event schema or runtime events; no credentials |

## Scope of browser evidence

`docs/evidence/ui/01-overview.png` through `06-mobile.png` are captured from a real local Streamlit server by `scripts/browser_smoke.py`, including actual requests, time advance and five independent policy runs. Budget 5 was used for fast browser smoke testing; benchmark evidence uses budget 30. JSON and CSV files were downloaded by clicking actual app controls and parsed. Images are not image-generation mockups.

The first browser-engine download failed; the second engine was installed from the normal Playwright distribution and succeeded. The external connected browser could not reach the workspace's isolated localhost; the E2E test starts its own local server and local test browser in the same environment. These failures are separate from the successful final local E2E test.

No Windows UI, real scientist usability study, multi-user concurrency, LIMS/lab integration, prospective assay experiment, GMP/regulatory acceptance, or clinical utility was tested.
