# Continuation checkpoint

Date: 2026-11-04 (Asia/Bangkok).

## Verified starting point

- Requested checkout: `C:\Users\User\Desktop\myProject\curaloop-rl`.
- The supplied directory was an extracted source tree without `.git`.
- Restored Git metadata from the original remote using init/fetch, a new branch,
  and `git read-tree HEAD` (index only; no source files overwritten).
- Remote: `https://github.com/siriponsri/curaLoop-RL.git`.
- Base and fetched `origin/main`: `b16d2fb9ee56d03fdc6cf0628fc444670a433c43`.
- Branch: `feat/english-durable-poc`.
- Tracked source matched remote exactly. `SOURCE_COMMIT.txt` was an existing
  untracked distribution marker and is retained.
- Windows, Python 3.12.10, Node 24.19.0, npm 12.1.0.

## Task contract

Deliver the existing seven-page localhost research simulator in English, add
durable single-user recovery using public snapshots and existing reconciliation,
repair observed workflow/setup/reliability issues, and verify actual Windows and
browser behavior. Preserve all data, models, historical benchmark bytes, labels,
scientific protocols and Git ancestry. No retraining or cloud deployment.

## Current work

- Original native `cmd /c Setup-CuraLoop-Web.cmd --no-pause`: PASS (first run).
- Original `python -m pytest -q`: 103 PASS, 0 FAIL, 0 SKIP, two inherited warnings,
  206.80 seconds. XML: `evidence/poc-v0.3/baseline-python.xml`.
- Original frontend: 10 PASS; lint/typecheck/build PASS. The build removed three
  stale generated assets and retained the original large-bundle warning.
- Initial npm audit: 11 moderate dev-tool advisories. Initial Python audit: 39
  advisory entries in Pillow 12.3.0. Pillow upgraded compatibly to 13.0.0; final
  locked-requirement audit: zero known vulnerabilities; `pip check`: PASS.
- Protected-file comparison against the fixed base: 191/191 exact byte matches.
- Frontend, storage and Streamlit changes are in isolated local clones under
  ignored `outputs/worker-*`, each with its own branch and non-overlapping scope.
  Managed worktree creation was unavailable for this unregistered source folder;
  the requested checkout remains the integration/delivery location.
- Current English guides, persistence documentation and new Windows/browser
  verification scripts are being integrated. No scientific protocol changed.
- A fresh final locked verification environment is installing in
  `outputs/verify-env`; full candidate tests/browser/native restart checks remain
  NOT_RUN until their integrated execution.

## Milestones / acceptance

1. Baseline and protected-resource inventory.
2. English-only frontend and Streamlit; meaningful locale regression coverage.
3. Versioned SQLite public snapshots/revisions/jobs; atomic restart recovery and
   stale-write protection using `RunService.restore`.
4. Current English documentation, compatible dependency repairs, clean build.
5. Full Python/frontend checks, real 1440/390 px browser flows, native Windows
   first/subsequent startup, exports/resume/restart and offline-local requests.
6. Independent review, preservation check, coherent commits, latest remote check,
   normal push/merge if every required gate is satisfied.

## Owner questions

None. Scientific protocol changes are outside this implementation.

## Integrated checkpoint

- Local commits: `cf9227c` operator/verification preparation; `b9c82d8` Streamlit;
  `4d55842` durable API; `6f24c5c` English frontend; `336112b` guarded revision recovery.
- Fresh locked environment `outputs/verify-env`: candidate **134 PASS**, one
  inherited Starlette/httpx deprecation warning, 388.36s. XML:
  `evidence/poc-v0.3/candidate-python.xml`.
- Final frontend source tests: **18 PASS**; TypeScript/lint/build PASS. Entry
  340.06 kB and lazy chart chunk 409.99 kB, no bundle-size warning. Full npm audit: 0.
- Real Windows Chromium first integrated packet: **PASS**, 29 loaded captures,
  18 axe checks / zero violations, zero JS errors/external requests/page overflow.
  Packet: `evidence/poc-v0.3/browser-round1`; superseded for release by the final
  guarded-recovery/build verification still to run.
- Native CMD start/restart checks: PASS, including exact pending accounting and
  explicitly interrupted comparison after killing only the owned process tree.
- Independent review fixed malformed nested snapshot records and the recovery
  operation race. Remaining bounded fix: explicit deletion of a damaged campaign
  must bypass reconstruction; worker-storage is testing its follow-up commit.
- Parent exposed existing revision inspection for healthy campaigns so reset
  history can be recovered. Final browser script now exercises invalid import,
  saved-open/revision recovery, all presentation chapters and real reset.
- Current uncommitted files include final docs/notices, browser evidence/scripts,
  a small healthy-revision UI access control and generated frontend assets. The
  original untracked source marker has been copied to docs/archive and is retained.
- No push/merge has occurred in this release.

## Next exact action

Fetch/cherry-pick the worker-storage damaged-delete follow-up, independently review
it, then run final full Python tests and final browser packet against the rebuilt
frontend. Record identities/receipts, commit all deliverables, verify the latest
remote and perform the owner-authorized normal main publication if all gates pass.


## Final verification milestone

- Final full locked Python: 136 PASS / 0 FAIL / 0 SKIP, one inherited
  warning, 280.60s (`final-python.xml`).
- Final frontend: 18 PASS; typecheck/lint/build PASS.
- Final real browser: 31 captures, 18 axe audits, 0 violations,
 0 JS/external/overflow issues. Saved/revision recovery, invalid import, reset and
 all presentation chapters passed.
- Native CMD final build start/restart and interrupted comparison: PASS.
- Protected files: 191/191, Python/npm advisory audits: 0; no scientific protocol question.
- Independent review findings all resolved and re-reviewed.
- Next: commit verified content and identities; fetch latest remote, fast-forward
  main only if ancestry permits, normal push and record actual publication result.


Verified runtime content commit: `0de416643726c96b7c9648b615359fafb94d32be`. Engine/API/frontend digests
match the actual final browser metadata. Later documentation commits do not
change the tested runtime files. Publication result is recorded separately.


Fresh-checkout byte preservation: **PASS** on Windows. A new clone of `0de416643726c96b7c9648b615359fafb94d32be`
retains the exact tested frontend/API hashes and all191 original protected files.
Repository attributes preserve these records across Git line-ending settings; no
global Git configuration changed. The previous identity receipt is retained as
a pre-packaging checkpoint. No runtime/scientific behavior changed.
