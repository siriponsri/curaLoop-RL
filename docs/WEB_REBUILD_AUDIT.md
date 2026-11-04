> Documentation update, 4 November 2026: [current programme](00_project/CURRENT_STATE_AUDIT.md) and [documentation map](README.md). The detailed record below is retained from the inspected POC checkpoint. New research and commercial capabilities are specifications until implemented; prior test counts are historical execution, not new checks.

> Historical release record (2026-11-03). Statements below describe that
> execution, including its publication failure and unrun Windows checks.
> The original remote now has `main` (verified 2026-11-04). See
> [current release verification](RELEASE_VERIFICATION.md) for present state.

# Local web rebuild audit — 2026-11-03

## Outcome and scope

A real React/TypeScript/Vite/Tailwind/shadcn-style frontend and FastAPI adapter operate locally on CPU over the existing Python research engine. All seven requested pages are functional. The original Streamlit source, historical resource, trained controller checkpoints and recorded benchmark files are preserved. No retraining, assay relabeling, lab integration, cloud service or new performance claim was introduced.

The owner's later instruction explicitly authorizes publishing to the existing `siriponsri/curaLoop-RL` repository's `main` branch. Publication is **BLOCKED**, not completed: the connected GitHub write returned HTTP403 `Resource not accessible by integration`; direct CLI dry-run also has no authentication credential. The GitHub connection can read repository metadata, but that does not establish integration write permission. A subsequent branch query still returns no main branch. No remote file/commit/ref/visibility/permission was changed. Do not retry through an alternative route to evade this access control. The release-level full Git bundle and Windows push instructions let the owner publish the exact local history with ordinary authenticated Git and no force update.

## Actual verification

| Check | Result | Evidence |
| --- | --- | --- |
| Original Python suite independently rerun before changes | 79 passed,0 failed,0 skipped | `evidence/web-v2/baseline-rebuild.txt` and XML |
| Final fresh virtualenv installation, locked web dependencies, editable package | PASS; pip check clean | `web-clean-install.txt` |
| Final Python suite | 103 passed,0 failed,0 skipped;2 warnings | `web-clean-tests.txt` and XML |
| Frontend unit/API-client tests | 10 passed,0 failed,0 skipped | `web-tests-final.txt` |
| TypeScript + Vite production build | PASS; >700kB bundle warning retained | `web-build-final.txt` |
| ESLint / Ruff | PASS | `web-lint-final.txt`,`web-ruff-final.txt` |
| Actual production Chromium workflow | PASS;28 screenshots;5 comparator runs;335 CSV event rows | `browser/browser-result.json` and downloads |
| axe automated WCAG tag checks | 18 route/state audits,0 violations | `browser/accessibility.json` |
| Desktop/mobile | 1440×1000 /390×844;0page horizontal overflow;0JS errors;0external requests | browser result and actual captures |
| Launch script from another directory | PASS; actual SPA served by FastAPI at127.0.0.1:8000/lab | `launcher-result.json` |
| Byte preservation | All8 protected dataset/model/benchmark files unchanged;Streamlit unchanged | `preservation-check.json` |
| Runtime npm advisory scan | 0 advisories at audit time | `web-runtime-audit.json` |
| Full npm advisory scan | 11 moderate dev-tool advisories;ESLint/minimatch migration debt | `web-dependency-audit.json` |

All short evidence filenames above live under `docs/evidence/web-v2/`. Actual commands are listed in the handoff and logs. The Python warnings concern the inherited Altair theme API and FastAPI TestClient/httpx transition; no tests were skipped to conceal them.

The browser creates a historical run, selects five requests, verifies no pending labels/new hits, advances two steps, validates delivered outcomes and accounting, reconciles replay, searches/filters/pages public candidates, renders real RDKit molecules, checks dialog focus restoration, runs five independent matched policies, downloads/parses JSON and UTF-8 CSV, validates/resumes a snapshot, switches Thai/English, traverses presentation chapters, and exercises mobile navigation, keyboard-scroll tables/events, synthetic active/inactive/missing states and source-specific scientific copy. Synthetic success fixtures are labelled synthetic and are not a substitute for the historical run's unfavorable zero-hit result.

## Review and corrections

The original review packet contained an invalid loading-only mobile lab capture and serious contrast/keyboard issues. It is retained in `browser-round1/` as superseded evidence. The final packet waits for route content/fonts/molecules/candidates and settled nonanimated chart whiskers. Intermediate browser harness syntax/readiness/focus assertions failed during development; these were corrected and the complete final workflow was rerun, not marked skipped. An overbroad formatter briefly changed JSON whitespace in three resource files; semantic equality was checked and their original bytes restored before final preservation checks and the final103-test run.

The full visual review accepted the core workbench, then required four bounded corrections: active data-origin consistency, Thai font fallback, live-language resume status, and loaded mobile explorer evidence. The final scoped verdict scored all four resolved and said SHIP for the reviewed localhost portfolio scope. This is not a Windows certification, security certification, or scientific model validation. See `finish-review.md` for the actual review scope and residual limits.

## Scientific findings remain unchanged

The historical v0.1 10-seed HIV comparison is recorded evidence, not automatically rerun by opening a page. Both learned controllers used Greedy fallback on300/300 historical requests each. No learned-transfer or RL-superiority claim follows. The custom scaffold predictor's weak AUROC≈0.556/AP≈0.0327 and6test actives remain visible. Costs, delays, capacity and missingness are synthetic assumptions; only delivered new active labels count as hits. There is no clinical efficacy, real savings, GMP, endorsement or operational Digital Twin claim.

Two metadata bugs were corrected: historical dataset.source now cites its actual URL, and new RUN_STARTED wording is source-neutral. Exact legacy event descriptions remain replayable with an explicit limitation. Original recorded benchmark files were not rewritten.

## Not run and technical debt

- Windows CMD execution and Python3.11 runtime: NOT_RUN. Linux/Python 3.12.14 was used; Windows guide is reproducible instructions, not fabricated evidence.
- Safari/Firefox, manual assistive-technology testing, native Windows font inspection, user research, load/concurrency stress, malicious-upload fuzzing and comprehensive Python dependency security audit: NOT_RUN. axe covers automated rules only.
- Local sessions/jobs are in memory, single-worker, bounded and not transactionally persistent. Export single-run JSON before restarting. No user authentication/remote serving is intended.
- Main JS chunk is about825kB minified; lazy routes/chart chunking are future performance work. The release directory retains earlier hashed build assets; index.html references the final tested entry, and the full content hash identifies the shipped directory. No perf budget or Lighthouse score is invented.
- Several raw scientific identifiers, provenance text, API diagnostics and global confirmations intentionally remain English. Key decision copy, boundaries, scenario validation, origin labels and resume success are bilingual; complete localized screenreader review remains future work.
- Open dev-tool advisories and ESLint9support migration should be resolved with a tested compatible update, not a blind audit-fix downgrade.
- LIT-PCBA/Tox21 redistribution rights remain unestablished; no new unverified raw datasets were added.
