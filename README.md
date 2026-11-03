<img src="assets/curaloop-logo.png" alt="CuraLoop-RL logo" width="520">

# Pharmaceutical Screening Decision Lab

CuraLoop-RL is an independent personal research portfolio for retrospective
screening decisions. Select compounds under a simulated budget, wait for delayed
feedback, inspect the public event ledger and compare independent policies.
It runs locally on CPU without API keys, authentication or cloud services.

Historical MoleculeNet HIV assay labels and genuine molecular structures are
available alongside clearly labelled synthetic fixtures. Costs, delays, capacity
and missingness are simulated assumptions. This is a retrospective research
simulator, not clinical validation, drug efficacy evidence, an official GPO
system or an operational Digital Twin.

## Start on Windows

Install 64-bit Python 3.11 or 3.12, then double-click **Start-CuraLoop-Web.cmd**.
First use installs project-local dependencies in `.venv`; later use works offline.
The bundled production frontend requires no Node installation. Open
**http://127.0.0.1:8000**. Stop with Ctrl+C in its terminal.

See [Windows operator guide](START_WINDOWS.md) for installation, troubleshooting,
backup/recovery, fallback and developer commands. No administrator access or
execution-policy change is required.

```powershell
cd C:\Projects\curaloop-rl
.\Setup-CuraLoop-Web.cmd
.\Start-CuraLoop-Web.cmd
```

Linux/macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-web-lock.txt
.venv/bin/python -m pip install -e '.[web,dev]' --no-deps
.venv/bin/python scripts/start_web.py --no-browser
```

## Complete a campaign

1. **Overview:** inspect data origin, the current scenario and research boundary.
2. **Scenario builder:** choose HIV or a synthetic fixture, policy, seed, budget,
   capacity, delay, jitter and missingness. Create a fresh independent campaign.
3. **Simulation lab:** Select batch → pending → Advance time → delivered results.
   Inspect selection explanations, reserved/spent/remaining units and events.
4. **Compound explorer:** search, filter, sort, paginate and inspect public
   descriptors/structures. Unrevealed assay labels remain hidden.
5. **Benchmark arena:** execute matched independent policies and inspect actual
   controller fallback usage. Download comparison JSON or the CSV event ledger.
6. **Research evidence:** inspect sources, limitations, recovery and portable
   single-run JSON. Validate and resume an exported campaign.
7. **Guided presentation:** use the same campaign for a 5–7 minute walkthrough.

The default seed may yield zero new hits. Keep that result. Recorded v0.1
benchmark charts are explicitly separate from newly executed comparisons.
Frozen learned controllers used Greedy fallback for **300/300 historical
requests each**; this is not evidence of successful learned RL transfer.

## Local persistence and portable evidence

The API stores versioned public run snapshots, revisions and comparison records
in `.local/curaloop.sqlite3`. Pending and completed runs recover through the same
validated Python reconstruction used for JSON resume. Pending labels are never
serialized. Interrupted comparison jobs are reported honestly and are not
automatically repeated. Use one server process and one Uvicorn worker.

Single-run JSON is a portable recovery snapshot. Comparison JSON contains several
independent campaigns and cannot resume one campaign directly. CSV is an event
ledger for analysis, not a recovery file. See [persistence](docs/PERSISTENCE.md)
for schema, corruption handling, backups and source identity.

## Verify and develop

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

Frontend development requires a compatible Node version listed in
`frontend/package.json`. Vite uses loopback port 5173 and proxies the local API.
Production uses one address, port 8000. Rebuild committed `frontend/dist` after
changing frontend source and restart the server to refresh build identity.

Optional browser/security tools: `python -m pip install -r requirements-qa.txt`,
then `python -m playwright install chromium` and
`python scripts/web_browser_smoke.py --output docs/evidence/poc-v0.3/browser`.
Browser QA uses temporary local state and never replaces the owner's campaigns.
Streamlit fallback: `Start-CuraLoop.cmd` or
`python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1`.

## Scientific evidence and delivery status

- [Release verification](docs/RELEASE_VERIFICATION.md): current executed checks
  and explicit NOT_RUN items; older counts are historical until rerun.
- [Evaluation protocol and limitations](docs/EVALUATION.md).
- [Research benchmarks and provenance](docs/RESEARCH_BENCHMARKS.md).
- [Architecture](docs/ARCHITECTURE.md), [continuation](docs/CONTINUATION.md),
  [handoff](HANDOFF_TO_CODEX.md), [change log](CHANGELOG.md).
- [Third-party notices](THIRD_PARTY_NOTICES.md): MIT code, separately attributed
  CC BY 4.0 HIV derivative, local font and dependency licenses.

Original data, models, benchmarks, screenshots and logs remain preserved.
`requirements_v3/`, `docs/requirements/` and dated evidence are archived source
requirements or historical records, not current implementation status.
GitHub `main` exists at the verified starting revision `b16d2fb`; the earlier
403 publication failure is preserved as historical evidence. Current commit and
push status belong in the release verification report, not inferred from old logs.
