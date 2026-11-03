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

## Next exact action

Finish the setup launcher, execute the baseline Python suite and record its XML.
Then start the first bounded implementation batch.
