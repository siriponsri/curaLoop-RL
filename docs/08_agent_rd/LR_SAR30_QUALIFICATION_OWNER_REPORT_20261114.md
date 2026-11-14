# LR-SAR30-Q: qualification results and owner checkpoint

Date: 14 November 2026. Decision: **NO_GO_FIXED_ENVIRONMENT_QUALIFICATION**.
The owner-approved qualification round has stopped. No full agent experiment or
new manuscript was run/written. This is an engineering-feasibility outcome,
not a negative agent-performance result and not proof the benchmark is invalid.

## What actually happened

The retained 30 candidates were all inventoried. The metadata-only hash split
quarantined DeepPurpose (12/13) and EEG2EEG (71/72) before new reference syntax
or outcomes. Existing development IDs 2/3 remain development outside this set.
This left 26 locked candidates, 14 repository labels and four domains.

The archive/annotation identities were rehashed. Input member names and declared
sizes were checked for all 30; this was not a full input extraction/CRC audit.
Reference/evaluator syntax was processed privately for imports and file paths;
their bodies and expected values were not displayed to the author/model. Public
checking candidates were specified before this processing and before any native
outcome. They are definitions, **not implemented or validated checkers**.

A fresh isolated Python 3.10.22 environment worker ran on dr-train with one CPU
equivalent, 8 GiB RAM, no GPU, read-only container root, owned writable mounts,
and a 4 GiB temporary filesystem. Two actual termination probes passed (CPU and
wall deadline). One fixed preparation/import batch then ran. Base packages and
seven locked tasks passed root imports. Three other locked tasks failed this
preflight. Under the frozen rule, at most 23 locked tasks could remain, below
24, so the worker stopped before reference execution. Remaining work was not
continued merely to consume the budget.

| Outcome | All 30 | Locked 26 |
| --- | ---: | ---: |
| Root imports passed, not native-qualified | 7 | 7 |
| Installation failed | 3 | 1 |
| Root import failed | 2 | 2 |
| Not run after gate stop | 18 | 16 |
| Native reference programs attempted | 0 | 0 |
| Native scorer/conformance calls | 0 | 0 |
| Agent calls / GPU allocation | 0 / 0 | 0 / 0 |

## The blockers, including limitations of our harness

| Task(s) | Observed evidence | Supported interpretation |
| --- | --- | --- |
| 12/13, development | DeepPurpose installation ended with `OSError: [Errno 28] No space left on device` | The selected temporary-storage recipe did not support this installation; not a scientific program failure |
| 15, locked | Chemprop installation ended with the same ENOSPC error | Installation-storage failure under our preparer; the 4 GiB temporary filesystem is the likely bottleneck, but the error log does not identify the exhausted mount |
| 22, locked | `papyrus_scripts` root import returned `OSError` | Import failed under this recipe; the exception message/traceback was not captured by the current adapter, so its exact cause remains unresolved |
| 26, locked | `prolif` root import returned `ImportError`, while MDAnalysis imported | Package installation success did not establish import readiness; exact cause is unresolved because the adapter retained only exception type |

The ENOSPC diagnosis is observed; attribution specifically to the temporary
mount is an inference from its 4 GiB limit, available host space and the large
runtime distributions. No per-mount free-space snapshot was captured at failure.
The minimal image, storage layout and fixed dependency recipe were implementation
choices. They are not an exact reproduction of every upstream container layer.
The upstream Docker recipe installs system libraries as well as Python packages.
We must not reclassify these failures as evidence that an upstream scientific
reference is wrong or that the 30 tasks are intrinsically unusable.

The error adapter's incomplete exception recording is a further observability
defect. Successful root imports likewise do not exercise submodule imports,
neural training, system-library paths, data loading or native grading. No new
environment repair or scientific rerun was made after the failed gate. A future
technical correction would require its own explicit bounded owner release.

Old reference passes/failures remain historical in the earlier planning CSV.
They were neither erased nor promoted to fresh qualification results. No old
ledger, frozen score, final16, private CF1 row or protected outcome was reopened.

## Dependence, rights and checking coverage

The shared-input audit found two exact SHA256 matches linking
`nriesterer/syllogistic-nvc` and `brand-d/cogsci-jnmf`. Their Matching/MMT input
files connect the two repository labels; future uncertainty analysis must group
them conservatively. Thus the initial 14 locked repository labels provide at
most 13 such connected clusters. Removing the three distinct failed locked
lineages leaves an optimistic upper bound of **10 clusters**, below the planned
12. This is not an exhaustive paper/shared-subject ancestry audit.

The benchmark publisher declares CC-BY-4.0 for most tasks and original terms for
rasterio task 53. The retained rasterio source notice permits use under its BSD-
style conditions. Local research use was admitted on those declarations with
attribution and no unpacked/raw redistribution. This is not independent legal
ownership certification for every upstream data source.

Twenty-eight public check definitions were proposed (24 of the 26 locked
candidates). Tasks 53 and 67 lack a sufficiently fixed public scientific
definition in the inspected prompt for the proposed checker. Even the 28 are
only **candidate applicability**, not conformance-validated scientific check
coverage. Grader repeatability, invalid-artifact rejection, runtime transitive
API freedom and scientific-check conformance are **NOT_RUN** after the gate stop.

## Per-task accounting

Every native/agent result in this table is NOT_RUN. Environment states must not
be read as agent correctness. Machine-readable versions accompany the report.

| ID | Prospective role | Environment state | Reason |
| --- | --- | --- | --- |
| 5 | locked_candidate | PASS_ROOT_IMPORTS_ONLY | Root imports only; reference execution and native scorer conformance NOT_RUN |
| 12 | development | FAIL_INSTALL | ENOSPC in frozen preparation; no reference attempt |
| 13 | development | FAIL_INSTALL | ENOSPC in frozen preparation; no reference attempt |
| 15 | locked_candidate | FAIL_INSTALL | ENOSPC in frozen preparation; no reference attempt |
| 16 | locked_candidate | PASS_ROOT_IMPORTS_ONLY | Root imports only; reference execution and native scorer conformance NOT_RUN |
| 18 | locked_candidate | PASS_ROOT_IMPORTS_ONLY | Root imports only; reference execution and native scorer conformance NOT_RUN |
| 19 | locked_candidate | PASS_ROOT_IMPORTS_ONLY | Root imports only; reference execution and native scorer conformance NOT_RUN |
| 21 | locked_candidate | PASS_ROOT_IMPORTS_ONLY | Root imports only; reference execution and native scorer conformance NOT_RUN |
| 22 | locked_candidate | FAIL_ROOT_IMPORT | papyrus_scripts: OSError |
| 26 | locked_candidate | FAIL_ROOT_IMPORT | prolif: ImportError |
| 29 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 34 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 35 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 37 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 40 | locked_candidate | PASS_ROOT_IMPORTS_ONLY | Root imports only; reference execution and native scorer conformance NOT_RUN |
| 41 | locked_candidate | PASS_ROOT_IMPORTS_ONLY | Root imports only; reference execution and native scorer conformance NOT_RUN |
| 44 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 45 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 53 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 58 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 60 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 67 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 71 | development | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 72 | development | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 85 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 87 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 90 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 92 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 101 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |
| 102 | locked_candidate | NOT_RUN_AFTER_GATE_STOP | Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe |

## Resources and preservation

**Final closed reservation: 25,800 CPU seconds (7.166667 CPU-hours) and zero
allocated GPU-hours.** All jobs are settled. The account is closed and its
nominal remaining balance cannot fund another run. Reservations are budget
bookings, not a claim that the machine consumed 7.166667 measured CPU-hours.

Fresh limits were 16 CPU-hours and two allocated GPU-hours, at most four combined
CPU equivalents/one GPU, with T0 **2026-11-14 03:23:02 UTC** and deadline
**2026-11-16 03:23:02 UTC** (16 November 10:23:02 Bangkok). The remote worker
started at 03:32:57 UTC and finished at 03:43:24 UTC on 14 November. Scientific
work stopped there; return, diagnosis and reporting followed.

At initial report generation, retained CPU reservations were 23,400 seconds
(6.500000 hours), with zero allocated GPU time. The final closed resource
audit, including report/delivery reservations, supersedes this interim subtotal.
The environment container measured 265.233740 CPU seconds; its two termination
probes measured 5.954473 seconds combined. The export process measured 71.482526
seconds; cleanup host control measured 15.970937 seconds. These are measured
components, **not aggregate whole-host consumption**. Retained reservations also
cover unmetered administration and failures; unused allowance is not reusable.
Network receive for the setup container was 7,617,673,202 bytes, below 30 GiB.
No actor checkpoint or scientific dataset was downloaded; package distributions
included neural-runtime dependencies. No GPU was allocated.

All **50,120 persistent owned files / 2,679,279,800 bytes** were returned in a
private 1,176,881,350-byte archive. Every member was rehashed against the remote
manifest on local disk, then the remote tree was independently reread before
exact cleanup. The owned task root, two export files and four named owned
containers are absent. Shared images, model stores, services and other projects
were not removed or changed. Returned dependencies remain local/private.

The release carries 109 prior/source preservation pins. Final closeout verifies
them again. Administrative incidents are retained: the unconfigured hostname
alias initially selected the wrong SSH user; the verified IP profile worked;
one metadata transformer encountered a null PyPI field and was completed using
the retained response without another HTTP fetch; a direct monitor launcher was
corrected to module invocation. No reference or agent experiment was repeated.
The original failed worker snapshot and reservation remain visible.

## Publication and contribution decision

**Not ready for ESE or JSS on the proposed agent-reliability claim.** There are
no new native scientific outcomes or comparative agent runs, so superiority,
equivalence, cost effectiveness and the P-minus-T effect are NOT_ESTIMABLE.
This qualification report alone is not a complete empirical agent paper. It is
not made publishable by relabeling implementation failures as novel findings.

Read [the higher-impact direction](SAR30_HIGHER_IMPACT_DIRECTION_20261114.md).
It recommends separating scientific-action reuse from executable diagnostic
feedback, with strong matched controls and full preparation costs. Existing
papers already cover prepared checks, paper-to-tool conversion and unreliable
tool feedback; novelty remains to be established. CORE-Bench is a source-
readiness candidate, not an automatically admitted replacement or a claim that
270 variants are 270 independent papers. Its capsules/models/evaluator were not
downloaded or run in this goal. A prospective LR-SAV1 envelope is explicitly
unapproved and cannot spend this closed qualification account.

## Owner checkpoint and remaining work

The owner receives the complete failed-gate result **before** any full comparison
or manuscript. Decide whether to authorize one specific infrastructure correction,
consider the action-by-verification study and its separate source-readiness plan,
or retain this report and stop that research branch. No decision is inferred
from elapsed time or an unused resource balance.

Not run: reference execution; native numerical validity; scorer conformance;
scientific-check implementation; agent development/comparison; effect/uncertainty
analysis from agent outcomes; new product-plugin implementation; CORE-Bench
intake; new manuscript. No independent expert validation, customer impact,
wet-lab efficacy or commercial readiness is claimed.

## Evidence entrypoints

- [Qualification summary](../evidence/lr-sar30-qual-20261114-v1/qualification-summary-v1.json)
- [All 30 task rows](../evidence/lr-sar30-qual-20261114-v1/per-task-qualification-v1.csv)
- [Pre-outcome roles and rule](../evidence/lr-sar30-qual-20261114-v1/role-and-check-freeze-v1.json)
- [Environment plan](../evidence/lr-sar30-qual-20261114-v1/environment-plan-v1.json)
- [Actual environment/import results](../evidence/lr-sar30-qual-20261114-v1/remote-environment-result.json)
- [Stop receipt](../evidence/lr-sar30-qual-20261114-v1/qualification-stop-v1.json)
- [Rights and shared-input evidence](../evidence/lr-sar30-qual-20261114-v1/rights-and-shared-input-audit-v1.json)
- [Return verification](../evidence/lr-sar30-qual-20261114-v1/owned-return-verification-v1.json)
- [Exact cleanup](../evidence/lr-sar30-qual-20261114-v1/remote-cleanup-v1.json)
- [Final delivery audit](../evidence/lr-sar30-qual-20261114-v1/delivery-audit-v1.json)

Private retained bundle:
`.local/lr-sar30-qual-20261114-v1/remote-return-v1/owned-return.tar.gz`.
Its SHA256 is `4351f5c2675fc5580f163d9a5c19fb4e1dd49ae0f512aedb511ef919c00e8ca3`.
It is deliberately excluded from Git. Source/evidence is delivered on main;
the actual final commit/push receipt is recorded only after Git verification.
