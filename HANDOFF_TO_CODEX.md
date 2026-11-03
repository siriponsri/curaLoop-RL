# HANDOFF TO CODEX — CuraLoop-RL local web v0.2

## Exact source identity

- Build repository: `/workspace/scratch/d375f2fe413e/curaloop-rl` (cloud workspace, not the owner's Windows machine).
- Working branch: `feat/local-web-ui`.
- Original delivered HEAD: `dca5c81a6ee620faa99ad8b22d8e0d78e5121f59`.
- Pre-rebuild checkpoint: `9de9221678c50c7cc9528d1805a9bdaa1f5e7aa2`.
- Exact tested implementation commit: **`05ff36dbda0fd36250e5b80f9185814d05da6fb3`**. Subsequent commits document/audit/package the same implementation.
- Tested frontend directory SHA256: **`2b8c8ea049a3fb1f61f0e9e9647cda81a28d01af2f3debc09ca33fed26aa3fc6`**. Computed over sorted relative file paths and contents, matching `/api/v1/meta`.
- Final release HEAD is in ZIP-level `SOURCE_COMMIT.txt`/`RELEASE.json`; the full Git bundle restores its exact history. A committed document cannot contain its own commit hash.
- Screenshots were taken before the implementation commit, so their Git state correctly shows a checkpoint SHA plus uncommitted changes. They prove the recorded built-content hash, not that all files equalled that checkpoint commit.
- User later explicitly authorized publishing `main` to `https://github.com/siriponsri/curaLoop-RL`. **BLOCKED: no remote write completed.** GitHub returned HTTP403 `Resource not accessible by integration` on the initial file write; direct Git CLI has no credential. A follow-up query confirms main remains absent. Repo metadata permissions are not integration write permission. No deployment or visibility/access change was performed.
- `docs/evidence/web-v2/github-publication.json` records the failed attempt. The ZIP-level `Push-Main.cmd` and `PUSH_MAIN_WINDOWS_TH.md` restore the exact full Git history and use normal authenticated `git push origin HEAD:main` without force. A GitHub connection with working repository write permission is required for an assisted retry.

## Implemented and verified

React19/TypeScript/Vite/Tailwind/shadcn-style Radix components; local FastAPI adapter; seven real pages (Overview,Compounds,Scenario,Lab,Benchmarks,Evidence,Presentation); responsive Thai/English; actual public RDKit molecule drawings; public-candidate search/filter/sort/pagination/grid/list/details; validated scenario form; delayed selection/advance/finish/reset/replay; distinct pending/active/inactive/missing outcomes; real budget/event timeline/curves; fresh independent3–5 policy comparisons in a bounded background executor; explicit learned-controller fallback counts; JSON/CSV downloads and strict single-run resume; local fonts/logo; production SPA at one loopback address; Windows setup/start launchers; preserved Streamlit fallback.

The adapter calls existing Python RunService/compare/export rather than recreating scientific logic in JavaScript. Session UUIDs are distinct from deterministic scientific run IDs; locks plus expected_revision reject concurrent/stale double mutations. No API exposes unrevealed labels or the truth store. Labels visible to the UI are seed or delivered labels only. Seed hits are excluded from new hits. Resource/model/recorded benchmark bytes and original Streamlit source are unchanged.

## Actual executed commands and results

Execution environment Linux,Python 3.12.14,Node 24.22.1,npm 11.9.0. Main venv `/workspace/scratch/d375f2fe413e/venv`; fresh web venv `/workspace/scratch/d375f2fe413e/clean-web`.

1. Inspected full attached Localhost UI Rebuild Master Prompt and existing repo, verified original ZIP/history, reran `python -m pytest -q`: **79 passed,0 failed,0 skipped** before changes. Launched original Streamlit browser workflow independently; fallback source remains unchanged.
2. Created branch/checkpoint, installed locked API dependencies, added contract tests, then integrated UI.
3. Fresh `python -m venv .../clean-web`; `pip install -r requirements-web-lock.txt`; `pip install -e '.[web,dev]' --no-deps`; `pip check`: **successful,no broken requirements**.
4. Fresh-env `python -m pytest -q --junitxml=.../web-clean-tests.xml`: **103 passed,0 failed,0 skipped,2 warnings**. Original79tests retained plus24API/contract cases (including parameterized invalid inputs). Covers deterministic replay, oracle/privacy, budgets, delays, metrics,exports,concurrency,matchedconditions,provenance,legacyresume,productionSPAandgenuineSVG. Exact existing-service/API event equality is tested under the same scenario.
5. `npm ci`/initial install generated locked dependency tree. `npm run build` executes TypeScript check+Vite: **PASS**; `npm run lint`: **PASS**; `npm test -- --reporter=verbose`: **10 passed,0 failed,0 skipped**. Main bundle warning retained, not suppressed.
6. `python scripts/web_browser_smoke.py`: **PASS** on real built FastAPI localhost app with Chromium 131 / Playwright 1.49.1. **28 genuine captures**, desktop 1440×1000 / mobile 390×844; **18 axe route/state audits,0 violations**; **0 JS errors,0 page horizontal overflow,0 external requests**. Five real comparator reports and335 CSV event rows downloaded and parsed. Pending privacy, delayed reveal,replay,search,dialogfocus,comparison,exports,resume,language,keyboardscroll,synthetic active/inactive/missing,and source-specific copy checked.
7. `python scripts/start_web.py --check`: **PASS**. Actual `--no-browser` launcher invoked from another directory served `/lab` at `http://127.0.0.1:8000`: **PASS**.
8. `python -m ruff check src app api scripts tests`: **PASS**. Protected-file hashes8/8 and unchanged Streamlit: **PASS**. Credential-pattern scan:0 matches within its stated scope.
9. `npm audit --omit=dev --json`:0 production advisories; fullaudit11 moderate dev-tool advisories. This is point-in-time evidence, not a security certification.
10. Full visual review followed by a bounded correction batch: final scoped verdict **SHIP**,four findings resolved,0 partial / 0 unresolved. See `docs/evidence/web-v2/finish-review.md` for exact scope; it does not certify Windows/accessibility/performance beyond inspected evidence.

Detailed logs,downloads,28 PNGs,axeJSON,provenance-preservation report,licenses and launcher result are under `docs/evidence/web-v2/`. Initial invalid captures/contrast findings remain under `browser-round1/`, explicitly superseded. Intermediate harness failures were corrected and rerun. A formatter briefly changed resource JSON whitespace; semantic equality was checked and all original bytes restored before final103 tests/hash checks. No failure was hidden by skipping a test.

## Windows reproduction

Extract ZIP, open its `curaloop-rl` folder, install Python 3.11/3.12(64bit), then double-click **`Start-CuraLoop-Web.cmd`**. First run installs local `.venv` dependencies; the shipped built frontend means Node is unnecessary for the demonstration. Browser opens **http://127.0.0.1:8000**. Subsequent demonstrations use bundled data/models/fonts offline. No administrator rights, global installation or PowerShell execution-policy change is requested.

Manual PowerShell (example path, not a claim that we wrote there):

```powershell
cd C:\Projects\curaloop-rl
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web-lock.txt
.\.venv\Scripts\python.exe -m pip install -e ".[web,dev]" --no-deps
.\.venv\Scripts\python.exe scripts\start_web.py
.\.venv\Scripts\python.exe -m pytest -q
```

Fallback: `python -m streamlit run app\streamlit_app.py`. UI development: Node>=22.12,`cd frontend`,`npm ci`,`npm run build`; Vite5173/API8000 loopback only. See `START_WINDOWS_TH.md` and README. **Windows CMD execution and Python 3.11 runtime NOT_RUN here.**

Sessions are memory-only and single-worker. Export a single-run JSON before shutdown; Evidence→validate/resume restores it by reconciliation after restart. A multi-run comparison JSON or CSV cannot resume one campaign. Close only your own running terminal to stop; launcher never kills another app occupying port8000.

To restore exact tested history from the in-repo bundle into a new folder:

```powershell
git clone -b feat/local-web-ui history\CuraLoopRL-tested-history.bundle C:\Projects\curaloop-tested-history
```

The ZIP-level full-history bundle and its instructions restore final documentation as well. No GitHub snapshot commit was created: write access was refused. The owner can push the full original/local ancestry from the restored repository after authenticating.

## Provenance and scientific limits

HIV derivative1200 molecules, original source41127 rows / 7 invalid structures excluded, original sourceSHA/assaysemantics/transforms/CCBY4attribution preserved. Sources in `src/curaloop/resources/hiv_manifest.json` and `THIRD_PARTY_NOTICES.md`. No company/private assay data, GPO identity, clinical efficacy, GMP,real-costsavings or endorsement. LIT-PCBA/Tox21raw redistribution remains unestablished and was not added.

Original Q-learning/bandit160 synthetic training episodes/checkpoints unchanged. Historical50 campaign / 10 paired-seed results unchanged. Each learned controller used300/300 Greedyfallbackrequests, so matching Greedy is not learned pharmaceutical transfer. Custom960/240whole-scaffold predictor audit has only6 test actives,AUROC≈.5563,AP≈.03266; not an official MoleculeNet leaderboard. Probabilities uncalibrated; uncertainty is a margin heuristic. Retrospective results are not drug efficacy evidence. Current maturity **RETROSPECTIVE_SIMULATOR**, not validated/operationalDigitalTwin.

## Planned,blocked,not run and debt

- **NOT_RUN:** native Windows install/CMD,fontverification,Python3.11,Safari/Firefox,manualscreenreader,prospectiveuserstudy,load/stress,penetration/fuzz/securitycertification. Automatedaxe does not establish universal accessibility.
- **Debt:** large JS chunk,lazyroute/chartloading,11 moderate dev-tool advisories,ESLint9migration,someEnglishrawdiagnostics/scientificidentifiers,retainedunusedhashedbuildassets,memory-onlysessions,noauthentication,oneworker. Loopback browser checks are not protection against hostile local programs.
- **Blocked by absent evidence:** measured lab cost/delay calibration,physical feedback,LIMS,in-vivo/clinicalutility,cross-targettransfer,operationalDigitalTwin,GMP/organizationalclaims. Do not invent them through UI or simulation.
- **Planned research:** rights-cleared multitargetexternalvalidation and controller-distribution/fallback improvement using a separate development protocol. No new model was trained in this UI rebuild.

## Three prioritized next tasks

1. Verify the exact release on the owner's Windows machine: install,start,alltests,fullbrowserworkflow,Thai font and offline rerun; record genuine Windows evidence.
2. Migrate compatible development tooling to remove advisories and lazy-load routes/charts; add durable single-user session storage only with explicit migration/reconciliation tests. Preserve the frozen scientific evidence and API privacy boundary.
3. With rights-cleared independent assay data, pre-register stronger external validation/calibration and controller-transfer experiments; quantify fallback before claims. Keep measured lab/twin work blocked until authorized real feedback exists.

No public deployment, paid infrastructure, sharing/permission change or organizational access was performed. GitHub main publication alone is authorized by the owner's later message, but remains blocked by the integration's403 response.
