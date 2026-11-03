# Windows operator guide

## Install and open

1. Put the complete source/release folder in a directory you can write to.
2. Install 64-bit Python 3.11 or 3.12 for your account if it is not available.
3. Double-click **Start-CuraLoop-Web.cmd** in the source folder.
4. First use creates `.venv` and installs the locked local dependencies. Internet
   is needed for installation only. No administrator access is requested.
5. Open **http://127.0.0.1:8000**. The API and production UI share this address.
6. Stop with Ctrl+C in the launch terminal. Subsequent startup uses local assets,
   data, models and fonts and can run offline.

No Node installation is needed for the bundled production frontend. No global
configuration or PowerShell execution-policy change is required. To retry an
interrupted installation, run **Setup-CuraLoop-Web.cmd** again.

Manual PowerShell, without activating the environment:

```powershell
cd C:\Projects\curaloop-rl
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web-lock.txt
.\.venv\Scripts\python.exe -m pip install -e ".[web,dev]" --no-deps
.\.venv\Scripts\python.exe scripts\start_web.py
```

## A 5–7 minute presentation

Use HIV, seed 42, budget 30, capacity 5, delay 2. Explain real historical assay
labels versus simulated operations. Select a batch, show pending privacy, advance
twice and inspect delivered outcomes/budget. Explore a genuine molecular
structure, compare policies, export evidence and show limitations. Guided
presentation uses the same live campaign. Zero hits is a valid result; do not
change seeds to manufacture success.

## Restart, backup and recovery

Run snapshots and comparisons save automatically in `.local/curaloop.sqlite3`.
Reopen the same project and the browser can recover its saved session. Saved-run
controls allow selection when browser storage is cleared or another campaign is
needed. Pending work retains simulated time and reserved budget; restarting does
not deliver early or repeat an accepted assay. A comparison interrupted by process
shutdown is marked interrupted; start a new comparison explicitly if needed.

For a portable backup, export **single-run JSON**. In Research evidence select
that file and use **Validate & resume**. A comparison JSON or CSV ledger cannot
resume one campaign. An invalid file is rejected without replacing the active run.

For a database backup, stop the server cleanly, then copy the `.local` directory.
Do not delete or overwrite corrupted/incompatible saved data. Keep a copy and
follow the error/recovery instructions in [persistence](docs/PERSISTENCE.md).

## Troubleshooting

- **Python not found:** install a supported 64-bit Python for your account, then
  rerun setup. The launcher does not install system software.
- **Dependency download fails:** restore connectivity and rerun setup; an existing
  environment can complete installation safely.
- **Port 8000 occupied:** the launcher reopens the existing CuraLoop service if
  recognized. It never kills another application. Close the other program yourself
  if a different service occupies this port.
- **Browser cannot connect:** check the launch terminal and use Reconnect in the
  app. Keep the server terminal open while demonstrating.
- **Molecular drawing unavailable:** historical SMILES remain public; install the
  web lock including RDKit. Synthetic descriptors have no genuine structure.
- **Missing frontend:** use a complete release or rebuild using a Node version
  compatible with `frontend/package.json`, `npm ci`, then `npm run build`.
- **Saved state error:** retain the database. Validated single-run JSON remains
  the portable recovery route; never replace the database merely to hide an error.

## Streamlit fallback and development

Run **Start-CuraLoop.cmd** for the English fallback at
http://127.0.0.1:8501. Its state is browser-session-local; use JSON export/resume
for portable recovery. Durable API persistence belongs to the primary web app.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\start_web.py --check
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
# Separate terminal for frontend development:
cd frontend
npm ci
npm run dev
```

Development Vite uses loopback port 5173. Build with `npm run build` and restart
the API for the one-address production demonstration. Run one Uvicorn worker.
`Start-CuraLoop-Web.cmd --no-browser` starts without opening a new browser window.

Current Windows verification and exact NOT_RUN items are recorded in
[release verification](docs/RELEASE_VERIFICATION.md). Historical Linux evidence
remains available and is not substituted for current Windows execution.
