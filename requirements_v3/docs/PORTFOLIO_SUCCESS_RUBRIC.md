# Portfolio readiness rubric

Use binary evidence and explicit statuses: `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`, `PLANNED`. Do not call the demo finished solely because the screens render.

| Area | Check | Acceptance evidence |
|---|---|---|
| Usability | 5–7 minute walkthrough completes offline | actual operator walkthrough from fresh run |
| UI | All tabs and controls affect visible outputs | manual interaction record or UI tests |
| Data | Demo uses public/clearly synthetic sources | visible source flags and `data/README.md` |
| Simulator | No hidden label before reveal | tests against observation leakage |
| Costs | Budget cannot be exceeded/double charged | focused tests and event-ledger assertion |
| Baselines | At least 3 policies genuinely run | distinct executable policy implementations |
| Metrics | Chart and export agree with event log | deterministic replay comparison |
| Repro | Windows setup works from a clean install | PowerShell instructions and test output |
| Scientific claims | No virtual hits framed as drug efficacy | README/UI copy review |
| Twin stage | Correctly labeled simulator | visible maturity statement |
| RL integrity | No fabricated RL evaluation | PLANNED or genuine trained/evaluated policy |
| Ownership | Personal repo, no company data/branding | repo and history inspection before sharing |
| Handoff | Codex can continue without owner restating goals | `HANDOFF_TO_CODEX.md` with SHA and backlog |

**Definition:** `PORTFOLIO_DEMO_READY` requires all first-release applicable checks passing. It does **not** imply `REAL_WORLD_VALIDATED` or `DIGITAL_TWIN_OPERATIONAL`.
