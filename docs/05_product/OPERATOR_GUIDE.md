# Operator guide: the existing workbench

## Installation and launch

Use the full source/release folder and 64-bit Python 3.12. Double-click `Start-CuraLoop-Web.cmd`; first use creates `.venv` and installs locked dependencies. Keep the terminal open and browse to `http://127.0.0.1:8000`. Stop with Ctrl+C. The bundled frontend needs no Node.js and the application requires no model API key. Installation needs network access; ordinary runtime uses local assets.

## A transparent first campaign

In Scenario builder choose HIV replay, seed 42, 1,200 candidates, 48 initial labels, budget 30, capacity 5, delay 2 and unit cost. Select Greedy and create a campaign. In Simulation lab choose a batch, inspect reserved budget and pending privacy, then advance twice. Read the delivered outcomes and selection explanations. Complete the campaign without changing seeds to obtain a more favorable result.

Open Benchmark arena for independent matched policies. Check actual controller/fallback counts. The recorded historical comparison is separately labelled; opening its page does not execute a new study. Use Compound explorer to inspect genuine structures and public features.

## Saving and recovery

Primary API state is saved in `.local/curaloop.sqlite3`, outside Git. A pending request remains pending after restart until simulated time advances. Export single-run JSON for portable validated resume; a comparison JSON or CSV ledger is not a single-run snapshot. A database backup should be made after stopping the server. Preserve a corrupt database and recover into a new compatible location rather than deleting evidence.

The retained [persistence reference](../PERSISTENCE.md) provides the detailed storage contract. The [English illustrated manual](../manual/CuraLoop-RL-User-Manual-EN.pdf) covers current UI controls. The new research templates do not add controls to that interface.

## Troubleshooting

If Python is missing, install the supported user-local version and rerun setup. If dependency installation fails, restore connectivity and rerun `Setup-CuraLoop-Web.cmd`. If port 8000 belongs to another application, do not kill it automatically. If a molecular drawing is unavailable, retain the public SMILES and inspect the supported RDKit installation. New research-runner configurations in this package are not inputs to the existing CLI.
