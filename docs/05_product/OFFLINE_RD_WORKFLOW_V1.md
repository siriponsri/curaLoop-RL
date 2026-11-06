# Offline evidence-to-plan/report prototype

6 November 2026. Implemented in Goal 4R2-A; **fixture-backed engineering demo**.

The prototype makes an inspectable study proposal from declared offline evidence,
preserves measurement-status distinctions, validates the plan, and creates a local
Markdown/JSON bundle and preview receipt. It does not call an LLM, retrieve live
sources, run molecular campaigns or write to a team workspace.

## Run the fixed example

Use Python 3.11 or newer with this checkout's `src` directory on its import path,
for example through the existing editable project installation. No additional
package is needed for this prototype.

```text
python -m curaloop_rd --output .local/rd-demo-v1
```

From PowerShell without an editable installation, set the import path in that
session before the command:

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
python -m curaloop_rd --output .local/rd-demo-v1
```

The example is fixed and synthetic. Its output states that no scientific result
or external delivery occurred. A repeated invocation with the same output folder
returns the same bundle and one preview receipt; it does not duplicate a delivery.
Inspect `state.sqlite3` for workflow revisions and `bundles/<identity>/` for
`bundle.json`, `report.md` and their hash manifest. Preserve an interrupted folder
and rerun the same command to resume. A conflicting or altered artifact is an
explicit error, rather than a silently replaced report.

The demonstrated run was on Linux/dr-train with Python 3.12.3. These instructions
describe the portable standard-library interface; a Windows runtime run and a
complete host-agent integration were not executed in this goal.

## Typed Python tools

`curaloop_rd.contracts` supplies `Source`, `Brief`, `search_evidence`,
`inspect_source`, `draft_plan` and `validate_plan`. The search scans the supplied
offline catalogue. It performs no network retrieval. `Workflow` supplies `start`,
`state`, `build_report` and `preview_delivery` under a separate local output root.

The plan records source/version/locator identities, target/endpoint/unit, explicit
measurement status, proposed cost, limitations and a content digest. Exact unit
matching is required; this version does not convert units or reconcile phenotypes.
A shared target name does not establish that two assays measure the same thing.

Supported statuses are measured-exact, tested-censored, default-filled, missing,
untested, predicted and metadata-only. The demo labels all its records synthetic;
even its measured-exact example is not a real measured molecule. No numerical
potency values or confirmed hits are generated.

State changes use expected revisions. An exact preview retry after a lost reply
returns the previous receipt, while unrelated stale changes fail. Partial staged
files are retained after interruption; complete files are published atomically.
Stored plans, bundle bytes and preview receipts are rechecked before returning
success. The implementation does not claim multi-tenant security, adversarial
filesystem-race resistance or a power-loss certification.

## Exposure and integration limits

The catalogue contains declared synthetic fixtures only. It rejects reserved
roles and two registered synthetic reserved aliases before payload inspection.
This is not a complete protected-source registry. A live adapter must enforce
authoritative identities/aliases and source permissions independently; caller-
supplied role flags are not enough to protect real reserved outcomes.

Report identity establishes content consistency, not the truth of an arbitrary
source statement. The LLM/MCP layer, external molecular-source loader, actual
destination adapter and standing write authority are not implemented. A future
connector must not turn source text into execution authority or expose reserved
labels through alternative database identifiers.

## Evidence

The [results and feasibility report](../03_research/GOAL4R2A_FEASIBILITY_AND_NEXT_STUDY_V1.md)
links the twelve frozen contract cases and eight integrity/boundary checks.
The [public synthetic report](../evidence/goal4r2a-20261106-v1/demo-report.md)
is a completed example, not a scientific or business result. Paper-backed
candidate-data metadata is recorded separately from these fixtures.
