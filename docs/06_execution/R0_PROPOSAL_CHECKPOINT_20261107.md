# R0 proposal checkpoint

Date: 7 November 2026. Base main:
91aebeca21fa0a225b94c58a6ec686a364d205ca.
Delivery: English research/decision documentation only. No application,
scientific runner, dataset, frozen protocol or model configuration changed.

## Scope and observed checks

| Check | Observed result |
| --- | --- |
| Proposal and closest-work ledger written | PASS; linked from current AGENTS.md/HANDOFF.md |
| Candidate manifest parsed | PASS; five candidates, novelty NOT_ESTABLISHED, cohort qualification NOT_RUN |
| Six relative links in the two new briefs | PASS; every local target exists |
| Manifest brief/ledger targets | PASS |
| Proposal zero-intake/zero-run declarations | PASS for the recorded fields; this schema check is not a runtime data-access monitor |
| Git whitespace check | PASS; exit 0 |
| Independent scientific review | NOT_RUN; parent authored and checked serially |
| New cohort qualification, activity/gold intake, fitting and comparative results | NOT_RUN |

The first validation invocation failed before the Python audit because a nested
PowerShell command expanded variables in the outer shell. Its exit code alone
did not reflect those errors. It is not a passing audit. The corrected direct
Python invocation returned exit 0 with PASS, six checked links and five manifest
candidates. No scientific action was attempted by either invocation.

Primary source review is bounded and qualitative. Inaccessible release files
and a correction body are recorded in the closest-work ledger. No claim of an
exhaustive review, established novelty, usable new cohort or publication readiness
follows from successful document checks.

## Next decision

READY_FOR_OWNER_CONTRIBUTION_DATA_DECISION. Resolve R0-D1 in
[the proposal](../03_research/R0_CONTRIBUTION_DATA_PROPOSAL_20261107.md).
The next executable work requires a concrete bounded qualification contract.
No automatic phase advance or old budget/clock renewal.
