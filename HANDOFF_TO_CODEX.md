# HANDOFF TO CODEX — CuraLoop-RL Research Edition v0.1

## Repository identity

- Actual build repository: `/workspace/scratch/d375f2fe413e/curaloop-rl`
- Branch: `main`
- Exact tested **implementation commit**: `fbc8973043daeec6ff745ba3d58749050a37b273`
- A separate source-revision packaging fix and later audit/evidence/handoff commits follow. Benchmark execution uses the implementation commit above; installed-wheel identity is checked separately. The exact final distribution HEAD is recorded in the ZIP's `SOURCE_COMMIT.txt` and `RELEASE.json`, and is restorable from the supplied Git bundle. Those generated files avoid pretending this committed document can contain its own commit hash.
- No remote configured; no push, public GitHub repository, deployment, paid API, GPU or company-system access performed.
- Owner's Windows filesystem was not accessible. No claim that a repository was created on that machine. Example Windows locations are instructions only.

## Implemented and tested

Installable `src/curaloop` package and built wheel; Streamlit application; three base acquisition policies; actual tabular Q-learning and contextual bandit training with frozen JSON checkpoints; Gymnasium environment; attributed historical HIV replay; deterministic synthetic fixtures; private oracle and public immutable contracts; reserved/spent/remaining budget ledger; simulated delays, jitter, missing outcomes and batch capacity; independent matched comparisons; event-derived metrics/curves; valid JSON/CSV exports; deterministic completed-run replay and reconciliation/resume of pending snapshots; all four UI screens; live local browser downloads; Thai offline font and actual app screenshots; multi-seed benchmark and scaffold-disjoint predictor audit; professional logo in README/UI.

## Executed checks (actual, not generated statuses)

Python 3.12.14 on Linux. Main virtual environment: `/workspace/scratch/d375f2fe413e/venv`; isolated clean environment: `/workspace/scratch/d375f2fe413e/clean-room`.

1. `python scripts/validate_handoff_pack.py . --zip <attached zip>` in extracted v3 requirements: 56 source/archive entries, 25 references, 0 article PDFs, zero reported errors.
2. `python -m pip install -e '.[dev]' --no-deps` after installing resolved dependencies: succeeded.
3. `python scripts/prepare_hiv.py --source /workspace/scratch/d375f2fe413e/dataset_download/hiv.csv`: actual downloaded 41,127-row source; 7 invalid SMILES excluded; 0 canonical duplicates / conflicts; label-blind 1,200 molecules prepared; source hash recorded.
4. `python -m curaloop.learning`: **160 actual episodes each** for Q-learning and contextual bandit. Training source synthetic only, seeds 10000–10159. Values, counts, returns and checkpoint checksums are real.
5. `python -m pytest -q --junitxml=docs/evidence/pytest.xml`: **79 passed, 0 failed, 0 skipped**, 1 Altair theme API deprecation warning. Final source test log copied into evidence.
6. `python -m build --wheel --no-isolation`: produced `curaloop_rl-0.1.0-py3-none-any.whl`, including historical resource and trained checkpoints.
7. Fresh virtual environment, `pip install -r requirements-lock.txt`, then install wheel `--no-deps`: succeeded. `pip check`: no broken requirements. Same suite: **79 passed, 0 failed, 0 skipped**, one Altair warning; isolated installation evidence saved.
8. `python scripts/browser_smoke.py`: actual local Streamlit server and local Chromium, 4 pages, budget 5, 5 policies. Select → pending → advance twice → delivered → compare → JSON/CSV downloads parsed. 5 JSON runs / 335 CSV event rows. Non-local browser HTTP blocked; no external HTTP requests observed. Six genuine app screenshots captured, including mobile viewport. Thai font subsequently embedded locally and screenshots regenerated successfully.
9. `python -m curaloop.benchmark --output docs/evidence/hiv-benchmark`: real HIV replay, 10 paired seeds × 5 policies = **50 campaigns**, each budget 30, seed labels 48, capacity 5, delay 2. Actual per-event JSON/CSV and paired descriptive/bootstrap summaries. Final committed-code run metadata includes implementation SHA above. The large benchmark CSV is distributed losslessly as `benchmark.csv.gz` with the original CSV hash; normal UI/CLI CSV exports remain uncompressed.
10. `python -m curaloop.cli compare --config configs/hiv-demo.json --output <final-cli>` and `python -m curaloop.cli replay --input <final-cli>/report.json`: three actual historical baseline campaigns and exact event replay check. Output seed 42: Random 2 hits, Greedy 0, Uncertainty 1 at cost 30. No seed cherry-picking to make the default look successful.
11. `python -m ruff check src app scripts tests`, `git diff --check`, credential-pattern and remote inspection: clean. These are scoped checks, not an independent security certification or comprehensive vulnerability audit.

## Historical benchmark findings

Within this fixed HIV subset and seeds 0–9, mean new hits at B=30: Random 0.7, Greedy 3.8, Uncertainty 0.9, Q-learning 3.8, contextual bandit 3.8. Learned controllers invoke the explicitly labelled unseen-state Greedy fallback on historical states; equal outcomes are **not evidence that learned transfer outperformed or even replaced Greedy**. Confirm usage counts in the final benchmark `metrics.controller_requests` / `controller_fallback_requests`.

Separate custom whole-scaffold predictor audit: 960 train / 240 test, 36 / 6 actives, 0 shared Murcko scaffolds. AUROC ≈0.5563, average precision ≈0.03266, Brier ≈0.04408. This is weak predictive evidence, a useful limitation rather than a result to market. The split is not the official MoleculeNet leaderboard split.

## Dataset provenance / rights

Bundled `hiv_replay_v1.json.gz`: derivative of public NCI DTP / MoleculeNet HIV downloaded from DeepChem. Source SHA256 `9ffa7fe57dc86c342627ee1d5255e937e2ab812393c73c4d16c697022f6e1d22`; resource manifest retains row IDs, source/release/hash, label definitions, transforms, RDKit version, attribution and changes. CC BY 4.0 is the HIV dataset license explicitly stated by TDC. See `THIRD_PARTY_NOTICES.md`. Source paper and dataset license are distinct; no article PDF is bundled.

LIT-PCBA was checked against its official source/paper but not redistributed: unambiguous dataset redistribution terms were not established. Tox21/other assays need file-level rights, missing-label and target-definition checks. The original pack's 25-item literature catalogue is retained, with its original verification limits; this work does not certify all references.

## Windows reproduction

Extract the delivered source folder wherever the owner chooses. On a machine with Python 3.11/3.12:

```powershell
cd C:\Projects\curaloop-rl  # example location only
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app\streamlit_app.py
```

No virtualenv activation or PowerShell execution-policy change is necessary. `Start-CuraLoop.cmd` automates setup/start but was **not run on Windows here**. Dependency installation needs internet once; built-in data, models and fonts require no internet afterward. Optional raw-data rebuild needs RDKit and a download; it is not required for the bundled real-data demo.

For actual Git history, use the ZIP-level instructions to clone `CuraLoopRL-history.bundle` into a fresh folder. The unpacked plain source is runnable without cloning; `SOURCE_COMMIT.txt` records the packaged revision.

## Planned / blocked / not run, with honest scope

- **NOT_RUN:** clean Windows installation/CMD launcher, prospective scientist usability study, Python 3.11 runtime execution, production load/concurrency, comprehensive malicious-upload fuzzing/penetration testing, dependency vulnerability certification.
- **BLOCKED by absent external evidence:** calibrated real lab cost/delay distributions, operational laboratory Digital Twin, physical feedback loop, clinical/pharmaceutical efficacy, GMP suitability, actual organizational savings/ROI.
- **RIGHTS NOT ESTABLISHED:** redistribution of LIT-PCBA/Tox21 raw datasets in this release. No fake loader/data status is presented.
- **Research limitations:** one historical assay/subset; custom scaffold split; no cross-target biological replication; uncalibrated probabilities/margin uncertainty; salt/tautomer standardization not performed; possible analog leakage inside a within-pool replay; controller unseen-state fallback; synthetic training distribution mismatch; fixed crude reward; no SOTA claim.
- **Security limits:** process separation and private-import guard protect trusted fixed built-ins from accidental leaks. They are not an OS sandbox against a malicious developer who can inspect/reconstruct this public benchmark. Snapshot resume checks and public schemas are not cryptographic authenticity/signatures.
- **Persistence limits:** JSON snapshot/replay/resume provided; no multiuser transactional event database, real LIMS integration or arbitrary replay of rejected malformed-action histories.

## Five prioritized next tasks for Codex

1. Run the exact delivered repo on the owner's Windows machine; verify install, all tests, `.cmd` startup, browser workflow and font rendering, recording actual Windows evidence. Do not rewrite the working app.
2. Extend independent biological validation using rights-cleared multi-target data (especially LIT-PCBA); preserve assay-specific semantics, deduplication and target-family/scaffold exclusions. Keep raw unreviewed data out of Git.
3. Investigate sparse-positive initialization, probability calibration and stronger diversity/cost-aware baselines on development data; lock an external validation protocol before changing the current reported test results.
4. Address learned-controller distribution mismatch on a separate development corpus; quantify fallback and train/validate genuine strategy choices before claiming transfer. Compare against the strongest frozen baseline and preserve negative results.
5. Have a domain reviewer assess terminology and demo usability; only pursue calibrated lab/twin maturity with authorized measured feedback and prospective evidence. Keep personal-project/non-GPO boundaries.

Continue autonomously within local/CPU scope. No external push, deployment, sharing change, paid compute, proprietary data or organizational integration without the owner's explicit instructions.
