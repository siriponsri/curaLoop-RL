# Local molecular workflow: operator guide

This guide covers `/workflow`, the additive EN/TH molecular workspace. The
historical screening and aggregate AgentRD studies remain separate and unchanged.

## Start locally

From the repository root, use Python 3.11 or newer and Node compatible with the
frontend package's engines. Install the editable project with its `web` and
`chemistry` extras, install the frontend lockfile dependencies, then build the
frontend. The checked Windows environment uses `.venv/Scripts/python.exe`.
For a fresh checkout, first create that virtual environment with
`py -3.12 -m venv .venv`; keep an existing project environment intact.

```powershell
.venv\Scripts\python.exe -m pip install -e ".[web,chemistry]"
npm --prefix frontend ci
npm --prefix frontend run build
.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/workflow`. Keep the service on loopback. Choose another
free local port if an existing service owns 8000; do not stop an unrelated service.
The same-origin loopback interface supports that port. This is a solo prototype,
without multi-user authentication or a public deployment configuration.

## Import and compute

1. Paste or choose a UTF-8 CSV containing unique `compound_id` and `smiles` column
   names. The editable example is an author example, not experimental assay data.
   Limit: 1 MiB, 2,000 rows, IDs up to 128 characters, SMILES up to 2,048 characters
   and parsed molecules up to 512 atoms.
2. Choose **Explicit limits - no model** and set maximum molecular weight
   (g/mol), LogP (dimensionless) and TPSA (square angstroms). All three upper
   bounds are inclusive. The interface calls these limits, not drug-likeness or
   clinical acceptance criteria.
3. Select **Run analysis**. A fixed Python subprocess parses structures with
   RDKit, computes descriptors, applies the recorded limits and validates the
   generated files. Numbers appear after actual computation.
4. Invalid structures, duplicate IDs and malformed rows are retained with reasons
   in `rejected.csv`. Valid structures outside the limits remain in the descriptor
   table; they are different from rejected rows. Distinct IDs with the same
   structure are not chemically deduplicated. Salts, tautomers, stereochemical
   interpretation and standardization require separate scientific decisions.
5. Search the table by ID or canonical SMILES. Choose a compound ID to display its
   actual RDKit 2D drawing. Inspect the applied numeric limits and execution trail.

## Model-assisted execution

The optional model has two restricted roles: translate a filtering request into
the three numeric limits, then acknowledge a local export after tool execution.
Unspecified limits use the displayed defaults. It does not write executable
Python, select arbitrary tools, predict activity or generate scientific evidence.
Schema-constrained JSON alone does not prove correct interpretation of the request.
Review the applied limits in every completed model job.

A model session requires an explicit operator configuration and an active bounded
resource release. Opening the page starts no model call. If the session is absent
or expired, choose explicit-limit mode yourself. There is no paid provider or
automatic deterministic substitution for a failed model attempt. The research SSH
worker is retired after evidence return; the delivered offline workflow remains
usable, while future live inference requires a newly authorized session and
transport setup. A saved actual model response is historical evidence, not a new
inference or proof that a provider is currently healthy.

## Collect and recover

**Download bundle** collects input, parameters, descriptors, selections, rejected
rows, HTML/JSON report, evidence and SHA-256 manifest in a ZIP. The server checks
current file identities and evidence before serving completed results. Edited or
missing files are refused rather than silently regenerated. The hash chain is an
integrity check within the local trust boundary, not a signed external attestation.

Jobs persist in a separate SQLite store. Reopen **Saved analyses** after a page
reload. Unfinished jobs become **Interrupted** after a service restart; a stored
PID is historical and is not used to kill an arbitrary process. Review and select
**Resume as new attempt** for interrupted or cancelled jobs. Previous attempts
remain intact. Failed and completed jobs do not resume automatically. The store
has a 32-job ceiling; archive the entire store before choosing a new storage path.
Keep its access restricted because imported CSV contents are retained.

**Cancel** records a request and terminates an owned active RDKit subprocess. A
model request already in flight can finish before cancellation settles, and its
cost is retained. Closing a browser tab does not cancel a job. Computation has a
45-second tool wall-time limit; the research session adds aggregate CPU, memory,
GPU-allocation and deadline guards. Outside that research runner, the ordinary
localhost service does not claim aggregate OS-level research quotas.

## Troubleshooting and interpretation

- **Model session offline / 503:** no active operator model lease. Explicit-limit
  mode remains available. Do not treat a historical canary as current availability.
- **422:** inspect input columns, file/row limits and finite numeric bounds.
- **429:** finish or cancel the current workflow; this route admits one active job.
- **409 on results:** retain the original store and files for inspection. The
  output or validator version changed; no automatic rerun has occurred.
- **Failed:** inspect the saved execution trail and original error. No synthetic
  success response replaces a failed tool or model call.

This workflow reports physicochemical calculations only. It establishes neither
biological activity, safety, clinical efficacy, laboratory savings nor real-user
benefit. External comparative agent evaluation was not run because bounded native
benchmark admission failed. Software acceptance by the developer is not independent
expert validation. See the accompanying feasibility report for actual results and
the unrun comparisons.
