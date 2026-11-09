# D0 and outcome-free operation probe evidence

Date: 9 November 2026. Base `bf59b103a789fa2832762abcdc6d5f7dc723466e`.
This is local engineering evidence, not a molecular diagnostic result.

- [D0 audit](../../03_research/M2_D0_OPERATION_AUDIT_20261109.md)
- [D1 proposal and gates](../../06_execution/M2_DIAGNOSTIC_PLAN_20261109.md)
- [Machine-readable plan](../../../research/configs/m2_diagnostics_plan_20261109_v1.json)
- [Constructed test results](constructed-tests-v1.xml)
- [Verification receipt](verification-v1.json)
- [Preservation pins](preservation-pins-v1.json)

New source is `research/m2_diagnostics_v1/operations.py`; constructed regressions
are `tests/research/test_m2_diagnostics_v1.py`. The probe uses frozen engine
operations and independent restored states but never delivers or scores labels.
Injected clocks demonstrate logic only. Actual Linux SIGPROF interruption,
full-horizon counterfactuals, molecular headroom, remote admission and all D2/D3/
M3/product/journal experiments are NOT_RUN here. Independent review NOT_RUN.

An initial test call passed 14 then-current cases, but its shell environment
assignments failed before pytest. That call cannot support a single-thread claim.
The final verification explicitly sets thread limits and one-core affinity in
the Python process before importing numerical libraries, checks the new cases,
and records actual CPU/wall time separately from the old closed M2 accounts.

Final result: **17/17 constructed cases PASS**, Ruff PASS, 10 local links checked,
and 58 historical files hash-checked unchanged, including all ten old ledgers.
Verification parent CPU was 3.03125 seconds, wall 4.859 seconds; the CPU number
excludes the Ruff subprocess and is not a whole-session or scientific charge.
Command: `.venv/Scripts/python.exe -B tools/check_m2_diagnostics_v1.py` via RTK.
Its receipt is immutable; a later source change needs a new evidence version.
