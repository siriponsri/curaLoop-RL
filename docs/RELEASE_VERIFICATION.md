# Release verification — v0.3 localhost POC

Date: 2026-11-04 (Asia/Bangkok). **PASS for the documented single-user localhost
POC.** This is executed software evidence, not clinical or external certification.

## Environment and source

Native Windows 11 (build 26200), 64-bit Python 3.12.10, Node 24.19.0,
npm 12.1.0, Playwright 1.64.1 and Chromium 156.0.8078.4.
Original remote/base: `b16d2fb9ee56d03fdc6cf0628fc444670a433c43`.
Integration branch: `feat/english-durable-poc`.

The extracted source lacked `.git`. Init/fetch and index-only read-tree restored
the original remote ancestry without overwriting files; tracked source matched
the base. The earlier GitHub403 failure remains historical evidence. `main`
exists and final publication is checked separately below.

The final browser ran at Git checkpoint `69cb3a247e7585329c297bcf6c2681c0fd10f53b` with
`working_tree_dirty=true`: the healthy-revision access control, generated build,
verification scripts/docs and new evidence had not yet been committed. The exact
tested content is identified by the following independent digests; the final
committed runtime content is checked against them. A commit alone does not prove
the uncommitted test content.

| Identity | SHA256 |
| --- | --- |
| Scientific engine source | `b08ea28f444b96e9c272d7f914cd03e546fa69d8d31ff7398bf4d37d7bc513e1` |
| API/storage source | `62f50b0753aa955eedbfc40e3eac5a0c6a94b57338daf9d58a2a5aa25cf59d24` |
| Built frontend directory | `15b476a8eb208390a50e298da4a21623667afbf0da87e006124a4c38a514eb43` |

Raw metadata: [api-meta-during-browser.json](evidence/poc-v0.3/api-meta-during-browser.json).
The final runtime commit is recorded in root `SOURCE_COMMIT.txt` and
`evidence/poc-v0.3/release-identity.json` after the content commit; Git remains
authoritative for final documentation/publication HEAD.

## Actual verification

| Gate | Result | Evidence |
| --- | --- | --- |
| Native CMD first-run setup | PASS; project-local environment, locked install, editable package, preflight | Executed before baseline; original launcher commands recorded in continuation |
| Baseline Python | 103 PASS, 0 FAIL/SKIP, 2 inherited warnings, 206.80s | `baseline-python.xml` |
| Baseline frontend | 10 PASS; lint/typecheck/build PASS; old bundle warning retained | Actual initial command execution |
| Fresh final locked installation | PASS; separate `outputs/verify-env`, Pillow 13.0.0, editable package, pip check clean | Locked requirements and executed install |
| Final full Python | **136 PASS, 0 FAIL/SKIP**, 1 inherited Starlette/httpx deprecation warning; 280.60s | `final-python.xml` |
| Final frontend | **18 PASS, 0 FAIL/SKIP** | `frontend-tests-final.json` |
| TypeScript, ESLint, Ruff, production build, diff whitespace | PASS | Executed on final source; build entry 340.06 kB, chart 409.99 kB; no size warning |
| Real web Chromium workflow | **PASS; 31 loaded captures**, 5 comparison reports, 335 CSV event rows | `browser/browser-result.json`, captures and parsed downloads |
| Automated accessibility | 18 route/state audits, **0 violations** | `browser/accessibility.json` |
| Responsive/keyboard/dialog | 1440×1000 and 390×844; 0 page overflow/JS errors/external requests; dialog focus restored; table/events keyboard scroll | Final browser packet |
| Native CMD current build start/restart | PASS; two native starts from another working directory; pending ledger/revision unchanged after abrupt shutdown; unfinished comparison interrupted without replay | `windows-launchers.json`, `windows-start-*.txt` |
| Streamlit fallback | PASS; 4 pages, 5 policies, 5 parsed JSON reports, 335 CSV rows, 0 external requests | `streamlit-browser/` |
| Protected original bytes | **191/191 exact matches** against fixed base | `preservation-final.json` |
| Full npm advisory audit | **0 known vulnerabilities**; no suppression/force fix | `npm-audit-final.json` |
| Locked Python advisory audit | **0 known vulnerabilities** after compatible Pillow13 upgrade | `python-audit-final.json` |

Short evidence names above live under `docs/evidence/poc-v0.3/`.
Initial advisory reports and candidate/first-browser/first-launcher packets are
retained separately. They are superseded for final acceptance without being
rewritten as if they were final.

## Workflow and integrity coverage

The real browser creates a historical campaign, selects five assays, checks
pending privacy and reservation, restarts the actual process, verifies the same
revision/ledger, rejects a stale request, advances twice, checks delivered results,
reconciles replay, explores/searches/filters/paginates genuine structures and
restores dialog focus. It executes five independent matched policies, reloads
saved comparison results, downloads and parses JSON/CSV, rejects invalid import
without replacing the selected campaign, resumes valid JSON, opens a saved run
and recovers its validated revision into a new session with the same events.

Legacy Thai preference still renders English (`lang=en`). All presentation
chapters, back/next limits, mobile navigation, readable charts, keyboard scroll
regions and actual Reset are exercised. Synthetic fixtures verify observed active,
observed inactive and missing outcomes. The observed fixture has 5 new hits / 18
delivered assays; the missing fixture has 18 missing / 0 hits. Both settle 18 units.
They are labelled synthetic; they do not replace the historical zero-hit result.

Python contracts cover restart/pending/completed recovery, delayed visibility,
atomic revision history, real SQLite transaction rollback, stale/concurrent writes,
public-only stored state, durable comparisons/interruption, scientific metadata
corruption, malformed imports, incompatible database retention, explicit damaged
deletion and independent revision recovery. Frontend tests cover blocked browser
storage, API/error/form states, recovery/action race prevention and comparison
status retry without duplicate execution.

Independent code review identified malformed nested snapshot handling, damaged
deletion and an unguarded revision-recovery race. All were corrected, regression
tested and re-reviewed. No material finding remains in that scoped review.
The primary integrator ran and visually inspected the actual browser evidence;
this is not an independent external product/scientific certification.

## Reproduce

```powershell
rtk proxy cmd /c Setup-CuraLoop-Web.cmd --no-pause
rtk proxy python -m venv outputs/verify-env
rtk proxy outputs\verify-env\Scripts\python.exe -m pip install -r requirements-web-lock.txt
rtk proxy outputs\verify-env\Scripts\python.exe -m pip install -e ".[web,dev]" --no-deps
rtk proxy outputs\verify-env\Scripts\python.exe -m pip check
rtk proxy outputs\verify-env\Scripts\python.exe -m pytest -q --junitxml=docs/evidence/poc-v0.3/final-python.xml
rtk proxy .venv\Scripts\python.exe -m ruff check src app api scripts tests
rtk npm ci
rtk npm run lint
rtk npm test
rtk npm run build
rtk proxy .venv\Scripts\python.exe scripts/web_browser_smoke.py --output docs/evidence/poc-v0.3/browser
rtk proxy .venv\Scripts\python.exe scripts/windows_launcher_smoke.py
rtk proxy .venv\Scripts\python.exe scripts/browser_smoke.py --output docs/evidence/poc-v0.3/streamlit-browser
rtk proxy .venv\Scripts\python.exe scripts/verify_preservation.py
```

Frontend commands run in `frontend/`; Python/launcher commands run at repository
root. RTK was used in this execution environment; it is optional for owner runtime.
Browser/launcher checks require port 8000 free and use isolated temporary storage.
Do not overwrite committed evidence when producing a later verification version.

## Scientific and platform limits

No dataset, checkpoint, reward, training or evaluation protocol changed. Original
benchmark results and Git history remain preserved. Recorded learned controllers
used Greedy fallback on 300/300 requests each; current live tables show their actual
request usage. No learned-transfer, clinical/GMP/efficacy, real laboratory savings
or operational Digital Twin validation is established.

**NOT_RUN:** Python 3.11 runtime, Safari/Firefox, physical mobile devices, manual
screenreader usability, load/stress, comprehensive penetration/fuzz testing and
prospective laboratory/clinical studies. Browser requests were restricted to
localhost after installation; OS networking was not globally disabled. Dependency
audits are point-in-time checks, not security certification. One inherited
Starlette test-client deprecation warning remains; it was not suppressed.

Streamlit intentionally uses session-memory state with JSON recovery. Durable
SQLite belongs to the primary web API and requires one active server/worker.
No remaining blocker exists for the tested localhost POC scope.

## Publication

All release gates passed. The final remote freshness check and normal main push
are recorded in the publication receipt after the content commit. No force push,
deployment, access/visibility change, paid service or organizational access.


Verified runtime content commit: `0b1c53df376c9d44a8abefb4c99a6ff69a9741b9`. Engine/API/frontend digests
match the actual final browser metadata. Later documentation commits do not
change the tested runtime files. Publication result is recorded separately.
