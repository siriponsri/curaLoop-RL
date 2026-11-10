# Confirmation evidence integration

10 November 2026. P-CF1 is an internal local integration of **recorded CF1
aggregates**, not a new experiment or a deployed laboratory connector.

## Open and compare

Start the existing Windows application as described in [START_WINDOWS](../../START_WINDOWS.md).
Open **Confirmation evidence** in the sidebar, or the CF1 entry on Discovery
Overview or Benchmark Arena. A direct visit to `/confirmation` needs no simulator
campaign. With no saved session, that route does not create or list campaigns.
An existing saved session may be read; viewing, filtering and exporting CF1 do
not change it. To start a simulator campaign explicitly, use Scenario builder.

Choose one of six AID pairs, or the equal-campaign mean, and one of five budgets:
1%, 2%, 5%, 10% or 20% of the observation-supported confirmation universe.
All 18 ranker/operator arms remain in the chart and table. Select a point with
the mouse or keyboard, or select its table row. On mobile the table scrolls
horizontally. EN/TH switching preserves the current comparison.

The chart compares confirmed positive observations **H** with positive fixed
structure groups **D**. D is a structural proxy, not a validated lead series.
Whiskers and table intervals are observed ranges across five fixed seeds,
not confidence intervals across independent biological targets. D(FP) is the
predefined fingerprint-group sensitivity. Equal-campaign metrics first average
campaigns within seed; H/B and D/B average the campaign-specific ratios. Dividing
mean H by mean B does not reproduce the displayed macro ratio.

Study totals (six campaigns, 6,896 supported historical confirmations, 18 arms)
are constant scope information. They do not replace live simulator counts.
Exact integer budgets and immutable source hashes are shown under provenance.
The recorded study includes 2,700 cells; no molecular model runs on page load.

## Shared adapter and API

The stdlib-only adapter in `src/curaloop_rd/confirmation_study.py` owns a fixed
registry of four public source files: the aggregate card, schema, portfolio cells
and summary. It verifies exact byte counts and SHA256, closed schemas, complete
cross-products, arithmetic bounds, finite metrics and provider joins before
returning any view. Arbitrary paths, URLs and uploads are not tool/API inputs.
Symlinks, changed or missing files, extra columns and invalid values fail closed.
Every read reauthenticates the inputs; a successful earlier read cannot mask a
later edit. Tests may override the root internally; production callers cannot.

| Endpoint | Accepted query fields | Result |
| --- | --- | --- |
| `GET /api/v1/studies/cf1` | `campaign`, `budget_percent` | Typed scope, all 18 arms with seed summaries, exact budgets, caveats, source identity |
| `GET /api/v1/studies/cf1/export` | Above plus `ranker`, `operator`, `locale` | Downloadable JSON comparison brief, including all arms and selected filters |

Defaults are `equal`, 10, `mvsa`, `top_ranked`, `en`. Valid campaigns are the
six source AID strings; valid rankers/operators/budgets are closed enums.
Unknown or repeated query fields and unsupported selections return 422.
Unverifiable evidence returns 503. The UI shows an explicit diagnostic/retry
state with no fabricated replacement values. Existing local origin/host
restrictions and `/api/v1/evidence` HIV semantics are unchanged.

## Additive C Workspace tools

The new optional local stdio entry point adds two tools without changing the
existing v1/v2 C Workspace implementation or its prior exports. Run from this
checkout in the installed project environment:

```powershell
$env:PYTHONPATH = 'C:\Users\User\Desktop\myProject\curaloop-rl\src'
& .\.venv\Scripts\python.exe -m curaloop_rd.confirmation_mcp_v3 --workspace 'C:\Users\User\Desktop\myProject\curaloop-rl\.local\confirmation-workspace'
```

The host supplies that local workspace. The tools accept only `campaign`,
`budget_percent`, `ranker`, `operator` and `locale`; no destination/path/URL.
For example, use campaign `628/677`, budget 5, ranker `rf`, operator
`cluster_round_robin`, locale `en` or `th`.

| Tool | Effect |
| --- | --- |
| `confirmation_inspect` | Return the shared adapter's validated historical comparison and selection |
| `confirmation_export` | Create or verify one immutable local bilingual comparison bundle |

Each bundle has exactly five files: EN/TH HTML, EN/TH JSON and a manifest.
Writes use a task-owned staging directory and atomic rename. Reopening compares
the expected contents, regenerated from authenticated inputs, and checks the
complete inventory. Editing a report and its adjacent manifest together does
not make a modified export valid. Interrupted staging is retained for diagnosis;
the next call can create the complete final bundle. No external delivery occurs.
The actual local JSON-RPC initialize/list/call/export/error transport was tested;
this is not a claim of certification with every MCP client or an installed agent.

## Visibility and interpretation

CF1 provides aggregates only. Compound Explorer receives no CF1 compound rows,
private structures or per-compound outcomes. The retrospective simulator receives
no invented CF1 queue, delivery or model-update events. Existing pending outcomes
stay hidden. Downloaded briefs describe historical comparisons, not a recommended
compound list or executable laboratory instruction.

All six campaigns are exposed development data in one annotation-connected
component; four provider blocks do not create independent biological families.
Missing confirmations are excluded; source nonpositive includes inactive or
inconclusive. Group round-robin has D=H mechanically at the studied budgets.
Source is the author-processed AIC_Finder snapshot
`04c58e85188e724ec5ff44cbed2e7b960f6f3df3`; numeric AID pairs govern, with 13/17
SI/repository alias conflicts retained. Internal report preparation does not
establish raw redistribution rights or commercial data clearance.

No new selector, independent method benefit, RL superiority, laboratory savings,
clinical efficacy, representative-user performance or journal readiness is
established by this integration.

## Evidence and operator guide

- [Current acceptance evidence and actual EN/TH captures](../evidence/lr-cf2p-20261110-v1/README.md).
- [English PDF addendum v4](../manual/CuraLoop-RL-Confirmation-Evidence-Guide-EN-v4.pdf).
- [Original full Dashboard Guide v3](../manual/CuraLoop-RL-Dashboard-Guide-EN-v3.pdf).
- [CF1 research results](../03_research/LR_CF1_RESULTS_20261109.md).
- [CF2 design decision](../03_research/CF2_DESIGN_DECISION_20261110.md).
