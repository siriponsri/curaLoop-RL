# Acceptance and Test Matrix (Work → Codex)

This matrix defines tests **required of the future app**. It is a specification, not a claim that the tests have been implemented or run in this ZIP. Mark each test `NOT_RUN` until executed.

| ID | Class | Verification / invariant | Expected behavior | Required stage |
|---|---|---|---|---|
| T01 | Data | synthetic fixture generator deterministic under seed | same records & labels hash | P0 |
| T02 | Data | unique candidate IDs | duplicates fail validation | P0 |
| T03 | Data | malformed numeric descriptors | rejected with safe error | P0 |
| T04 | Data | empty candidate pool | explicit empty status, no crash | P0 |
| T05 | Policy | policy observes no private label | hidden label inaccessible via API | P0 |
| T06 | Policy | fake leaking-policy attempt | blocked/test fails if policy can read truth | P0 |
| T07 | Policy | candidate order shuffled, public state held constant | same first proposed set with deterministic tie-break | P1 |
| T08 | Budget | accepted selection reserves known cost once | budget ledger balances | P0 |
| T09 | Budget | insufficient budget | action rejected without mutation | P0 |
| T10 | Budget | duplicate submitted in same batch | no double charge or double hit | P0 |
| T11 | Budget | negative/NaN cost | rejected with safe error | P0 |
| T12 | Budget | zero budget scenario | stop cleanly | P1 |
| T13 | Time | pending labels remain hidden before due time | no observed label or hit increment | P0 |
| T14 | Time | results delivered exactly at due event | result appears once | P0 |
| T15 | Time | partial batch completion | only delivered outcomes counted | P1 |
| T16 | State | reset/seed replay | exact event sequence (where deterministic) | P1 |
| T17 | State | stop after capacity exhausted | no infinite loop | P0 |
| T18 | State | resume from event log | spent + reserved + available balances | P2 |
| T19 | Baseline | random sampling uniform from eligible IDs | no duplicates, seeded | P1 |
| T20 | Baseline | greedy uses only trained available labels | meaningful initialized predictor or labelled fallback | P1 |
| T21 | Baseline | uncertainty uses only available predictor outputs | no oracle score | P1 |
| T22 | Baseline | no both-class seed | documented fallback, no crash | P1 |
| T23 | Comparison | same initial labeled IDs and pool | pairwise run manifests agree | P1 |
| T24 | Comparison | same total cost and constraints | no policy receives extra budget | P1 |
| T25 | Comparison | independent state per policy | no cross-policy result contamination | P1 |
| T26 | Metric | hits count delivered confirmed labels only | pending/predicted excluded | P1 |
| T27 | Metric | budget vs hit chart derived from events | reconcile to ledger | P1 |
| T28 | Metric | run report export | no unrevealed labels, includes provenance | P1 |
| T29 | UI | all four pages are navigable with real data | no dead buttons | P1 |
| T30 | UI | scenario input validation | clear errors; reruns not silently mixed | P1 |
| T31 | UI | demo works with network disconnected | no API/GPU/external data calls | P1 |
| T32 | UI | synthetic cost/time visible in legends | no real-world savings assertion | P1 |
| T33 | UI | personal/non-GPO disclaimers visible | no institutional endorsement | P1 |
| T34 | Release | Windows PowerShell clean start | documented commands succeed | P1 |
| T35 | Release | no sensitive data/license files in git status/history | scan and manual review clean | P1 |
| T36 | Dataset | source license/assay/split/preprocess recorded | provenance manifest reproducible | P2 |
| T37 | Dataset | canonical SMILES collisions and label conflicts | handled according to documented rule | P2 |
| T38 | Dataset | withheld labels not in model preprocessing | guard/negative test | P2 |
| T39 | Evaluation | target/scaffold splits verified | no overlap per defined protocol | P2 |
| T40 | Evaluation | result depends on hidden truth only via delivered events | no pre-reveal oracle access | P2 |
| T41 | RL | learned policy checkpoint actually exists, trained/seed recorded | no RL label without evidence | P3 |
| T42 | RL | training targets disjoint from claimed held-out targets | automated assertion | P3 |
| T43 | RL | paired seeded baselines and RL run on same test scenario | evaluation parity | P3 |
| T44 | Twin | simulated delay/cost tagged as synthetic | no validated twin status | P4 |
| T45 | Security | malicious path/upload payload rejected if upload enabled | no traversal or code execution | P4 |
| T46 | Security | local exports contain no secret or original oracle table | sanitization + review | P4 |

## First demo minimum gate

**Must pass before saying 'demo ready':** T01, T02, T05, T06, T08-T14, T16-T17, T19-T20, T22-T24, T26-T30, T31-T35. All other tests remain named and tracked, not silently abandoned. This gate is more important than the number of tests alone.

## Evidence format

Each automated test has a named file/test function and stdout/CI artifact. Record command, Python version, platform, git SHA, fixture hash, seed, pass/fail/skip counts and what was NOT_RUN. For manual UI checks, record screenshot path and genuine user action; no generated mock screenshots represented as real app captures.
