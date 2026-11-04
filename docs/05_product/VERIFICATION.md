# Verification plan and evidence boundaries

## Documentation release checks

For this package validate active Markdown paths, reference IDs, source/PDF identities, protected runtime/evidence hashes, configuration syntax and economic calculations. Those checks establish package integrity. Record the result in `docs/07_audit/PACKAGE_AUDIT.md`. The legacy Windows/Python/frontend/browser reports remain historical execution evidence and are not counted as rerun tests.

## Future scientific changes

Run focused unit/integration checks for new scheduler boundaries, hidden-label privacy, reservation/settlement, simultaneous events, deadlines, one-class states, invalid selections and restart. Verify tiny cases against enumeration. Add a matched-delay invariance test and a constructed heterogeneous-duration case where information order affects decisions. These tests target behavior that could invalidate the study.

## Existing application commands

From a configured Windows checkout:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src app api scripts tests
.\.venv\Scripts\python.exe scripts\start_web.py --check
cd frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

These are instructions, not a claim they were executed for this documentation package. Rebuild and commit `frontend/dist` after an actual frontend change. Run browser checks when UI or served behavior changes, including desktop/mobile, exports, recovery and no unauthorized external requests. A documentation-only migration does not require repeating every expensive browser campaign when runtime bytes are unchanged.

## Scientific verification

After the software checks pass, reconcile every plotted value to completed event artifacts. Check independent policies and predictor fit boundaries. Inspect per-task failures, fallback and missingness. Run the preregistered analysis and retain all eligible seeds. A passing test suite cannot replace this scientific validation.

## Commercial verification

Measure the pilot's installation, reproducibility, report usability and actual effort against agreed acceptance. Record support burden and repeated use. Customer outcome claims require customer evidence and permission. The business hypothesis can remain unresolved even when software and research checks pass.

## Added research checks

Check source-version/phenotype conflicts at import, label-blind uniform starts, separately declared known-hit starts, frozen-model no-refit behavior, no-active similarity fallback, pending-score ablations, metric denominator/tie rules and compute accounting. Use the requirements in `docs/03_research/BASELINE_SPECIFICATION.md`. These are future application tests; package validation checks the documentation and declarative schemas only.
