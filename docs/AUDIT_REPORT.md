> Documentation update, 4 November 2026: [current programme](00_project/CURRENT_STATE_AUDIT.md) and [documentation map](README.md). The detailed record below is retained from the inspected POC checkpoint. New research and commercial capabilities are specifications until implemented; prior test counts are historical execution, not new checks.

> Historical release record (2026-11-03). Statements below describe that
> execution, including its publication failure and unrun Windows checks.
> The original remote now has `main` (verified 2026-11-04). See
> [current release verification](RELEASE_VERIFICATION.md) for present state.

# Implementation and QA audit — 2026-11-03

**Decision:** local research demonstration is implemented and reproducible on the tested Linux/Python 3.12 environment. It is not a validated pharmaceutical decision tool, a Windows-tested release, an official GPO product or an operational Digital Twin. This is a tool-executed implementation self-audit, not third-party certification.

## Executed evidence

| Check | Result | Scope |
|---|---|---|
| Attached v3 ZIP | PASS | 56 files; static validator zero errors; 25 references; 0 original PDFs; specification only |
| Package build | PASS | wheel includes historical resource + actual trained checkpoint JSONs |
| Fresh isolated dependency installation | PASS | 50 resolved packages plus current platform markers; no inherited site-packages |
| Fresh wheel `pip check` | PASS | no broken requirements |
| Pytest / main environment | 79 PASS, 0 FAIL, 0 SKIP | simulator, leakage, budget, delay, parity, metrics, exports, models, schemas, resume, UI |
| Pytest / isolated installed wheel | 79 PASS, 0 FAIL, 0 SKIP | same suite; one Altair API deprecation warning; not a failure |
| Actual UI / Chromium | PASS | 4 views, B=5, 5 policies, request/pending/deliver/compare/download; 5 JSON runs and 335 CSV event rows |
| Offline browser operation | PASS within tested boundary | only localhost allowed; zero external HTTP requests observed; no global OS network-disable claim |
| Historical benchmark | EXECUTED | 10 paired seeds × 5 policies = 50 campaigns; B=30; actual events and statistics |
| Predictor scaffold audit | EXECUTED | 960/240 split; 0 scaffold overlap; six test actives; custom split |
| Exact public-record replay | PASS | three completed historical baseline runs reconstructed event-for-event by CLI |
| Thai font / logo | INSPECTED | transparent generated logo + locally embedded OFL Thai font; real screenshot Thai labels readable |
| Source checks | PASS scoped inspection | Ruff, diff whitespace, no credential-pattern hits, no remote, no company assets/raw data |
| Windows execution | NOT_RUN | PowerShell and CMD paths documented; no access to owner's machine |
| Real lab / efficacy / GMP / Digital Twin | NOT_VALIDATED | no physical counterpart, measured process calibration or prospective validation |

The first live-browser engine download failed and the external cloud browser could not access isolated localhost. The successful final test uses the actual local Streamlit process and local Chromium in the same environment. Initial screenshots exposed missing Thai glyphs; the shipped screenshots were regenerated after adding the locally embedded licensed font. No generated UI mockup was used as evidence.

## Findings closed

- v3 was documentation only → real installable package, dashboard, CLI, wheel, tests and local Git history now exist.
- Hidden-label/dataframe leakage → immutable public observation, private backend, separate built-in policy process, import guard and negative leakage tests.
- Cold-start ambiguity → shared seed IDs, explicit historical/synthetic seed selection rules, sunk-cost accounting and labelled one-class random fallback.
- Pending/predicted compounds counted as hits → only delivered Boolean active results count; seeds and missing results excluded.
- Budget ambiguity → reservation at acceptance, settlement exactly once at delivered/missing event, conservation/stress tests.
- Comparator contamination → new private backend for each run, parity assertions and independent-state tests.
- Simulated costs confused with real labels → source-specific provenance: HISTORICAL_PUBLIC_DATA vs SYNTHETIC_ONLY; scenario parameters remain SYNTHETIC_ASSUMPTION.
- Fabricated RL readiness → actual Q-learning and contextual bandit checkpoints with 160 episodes each, values/counts/returns/hash, plus explicit actual-use/fallback counts.
- Installed wheel could not identify source commit without `.git` → build-time provenance marker and installed-wheel SHA check added; actual installed source revision `86f1665f2f7a7d90c0d1af9a9ba684c05b68d10c`.
- Broken export/resume claims → real browser downloads parsed; strict JSON public snapshot reconstruction validates log/metrics and reopens pending experiments. No pickle loading.
- Old schema rejected zero budget / lacked actual lifecycle → runtime v1.1 schemas and validation tests; old contracts retained only in archived requirements.

## Measured findings that remain limitations

At B=30 on this HIV subset/seeds, mean new active hits were Random 0.7; Greedy 3.8; Uncertainty 0.9; Q-learning 3.8; contextual bandit 3.8. The two learned controllers used **300/300 unseen-state Greedy fallback requests each**. Their equality to Greedy is explained by fallback and is not evidence of useful learned transfer. Training does exist, but synthetic training states do not cover the historical evaluation distribution. No retuning or seed replacement was used to hide this result.

The separate custom scaffold predictor achieved AUROC 0.5562678, average precision 0.0326585 and Brier 0.044083 against test prevalence 0.025 (6 positives / 240 test molecules). These weak results are not drug-discovery effectiveness. The published MoleculeNet/TDC splits differ; no direct leaderboard comparison is valid.

Bootstrap intervals in the export measure paired initialization variability within one assay, not biological-target replication. There is no validated cross-target generalization, calibrated uncertainty, advanced chemistry standardization, actual savings or prospective wet-lab evidence.

## Data/rights audit

DeepChem HIV source actually downloaded: 41,127 rows; SHA256 `9ffa7fe57dc86c342627ee1d5255e937e2ab812393c73c4d16c697022f6e1d22`. Seven invalid SMILES removed; no canonical duplicates or label conflicts under the stated rules. The 1,200-molecule derivative was sampled without labels; fingerprints and scaffolds are RDKit-derived. TDC explicitly states HIV CC BY 4.0; attribution, changes and license links are included. This records that source statement rather than legally certifying all upstream rights. No paper PDF or full raw CSV is redistributed.

LIT-PCBA and Tox21 are researched benchmark options, not included data or implemented loaded targets in this release. File-level redistribution rights and endpoint handling remain to be established. No company data, patient information, formula, LIMS record, credential or GPO emblem is present.

## Remaining engineering risks

Built-ins run in separate processes, but this is not an OS security sandbox against hostile arbitrary policy code or a developer reconstructing the public synthetic generator. No arbitrary code/plugin uploads are enabled. Snapshot parsing is bounded and reconciled, but comprehensive hostile-input fuzzing, dependency vulnerability auditing, concurrent users and production deployment are not tested. The Windows launcher and Python 3.11 runtime need their own executed evidence. One pinned Altair theme API is deprecated; it currently works and produces one test warning.

## Evidence identity

The historical benchmark ran on exact implementation commit `fbc8973043daeec6ff745ba3d58749050a37b273`. The packaging provenance fix is `86f1665f2f7a7d90c0d1af9a9ba684c05b68d10c`, with installed-wheel source hash `db603856502d9ab48b8e9549e55d216dfcf374effa734a31e8fe17b4d3bc34f5`. Final delivery adds documentation/evidence commits; see generated `RELEASE.json` / `SOURCE_COMMIT.txt` and the Git bundle. Run manifests retain actual execution identities and dirty flags, not a retroactively invented revision.
