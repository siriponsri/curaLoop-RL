# Metadata portfolio: verified core guide

The internal research prototype inspects registered cached metadata, prepares
cited readiness/gap reports and exports a local handoff. Users select a supported
intent, source IDs and, where needed, a readout ID. The question labels the report;
it is not interpreted by an AI model. Qualified molecular replay remains UNMET.
Live-model/client efficacy and commercial data permission remain NOT_RUN or
NOT_CLEARED respectively.

The owner requested a minimal/modern EN/TH redesign after reviewing the first
preview. That work is [active](../06_execution/UI_REDESIGN_EXECUTION_20261106.md).
The [preserved first preview](metadata-portfolio-demo/workspace.html) below is a
functional baseline, not the redesigned final interface.

## Three interfaces share one core

| Interface | Implemented job |
| --- | --- |
| Evidence Workspace | Search the registered cached catalogue and inspect positive metadata projections, declared units and captured source identities. |
| Decision Workbench | Prepare metadata-readiness/gap plans and cited reports, including useful blocked reports. No molecular experiment is released. |
| Integration Kit | Four typed tools over MCP stdio, idempotent local exports and a portable static HTML preview. |

Search does not contact current papers or molecular databases. Unknown source IDs
are rejected before payload access. Raw activity, full papers and private skill
clients are excluded from public demonstrations.

## One complete path

1. Call `evidence_search` with `{"query":"1259375"}`.
2. Call `evidence_inspect` with `{"source_id":"D1259375"}`.
3. Call `draft_metadata_plan` with:

   ```json
   {"report_id":"readiness-ic50","question":"Inspect the declared IC50 endpoint and unit.","kind":"endpoint","source_ids":["D1259375"],"tid":2}
   ```

4. Read `report.report_sha256` from the result. Call `local_export` with the same
   `report_id` and returned `report_sha256`. An identical repeat returns the same handoff.
5. Open `workspace.html` from the returned local folder. It is a static portable
   report preview. Its links open the exact report, readiness plan and manifest.

Selecting TID3 from that source produces `BLOCKED_ENDPOINT_UNRESOLVED`, because
the source does not declare its unit. The system preserves that absence rather
than inferring a unit from the readout name.

## Interpret a report

| State | Meaning |
| --- | --- |
| VALUE | The captured source declares this value. |
| ABSENT | The leaf key is missing from an existing source record. |
| NULL | The captured key explicitly contains null. |
| UNRESOLVED | The reviewed evidence does not establish the requested conclusion; an explicit inference rule may apply. |

Source enums such as unit code5 are preserved without conversion. The source
URI/hash/locator enables further inspection. `METADATA_REPORT` means this metadata
report succeeded; it does not qualify a molecular study. Hashes establish content
identity, not source truth or permission.

An export contains `report.json`, `report.md`, `preview.json`,
`readiness-plan.json`, `workspace.html` and `handoff-manifest.json`. Existing
different content, stale revisions and changed sources are rejected. Local export
does not deliver to a team service or clear publication/commercial data rights.

## Run the stdio surface locally

The verified private return includes the permitted cache at
`.local/lrbc-c-20261106-v1/remote-return/full-v1/files/bundles/portfolio-v2/`.
From the repository root, using the existing Python environment:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
python -m curaloop_rd.mcp_v1 --source-root .local/lrbc-c-20261106-v1/remote-return/full-v1/files/bundles/portfolio-v2 --registry .local/lrbc-c-20261106-v1/remote-return/full-v1/files/bundles/portfolio-v2/inputs/workflow-registry.json --workspace .local/rd-workspace
```

The cache is intentionally excluded from public Git. A fresh checkout needs its
own permitted, hash-bound registered cache; it must not substitute hidden/final
data or copy unrestricted-looking provider payloads into the public package.

The pinned [MCP stdio](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
subset supports `initialize`, `notifications/initialized`, `ping`, `tools/list`
and `tools/call`, with optional base-request `_meta`. Required client name/version
are validated. Tool errors expose safe categories, not private source/parser text.
The four tool input schemas are returned by `tools/list`.

## Verification and limits

Two independent processes passed10 frozen C engineering cases each and produced
matching export signatures. Four native pipe checks passed. An actual deterministic
stdio test client completed11 responses, including the full inspect→plan→export
path and duplicate-export check; worker and client both passed.

Desktop1440px and mobile390px browser checks found no horizontal overflow; all
four artifact links returned200. Pointer and keyboard disclosure/navigation were
checked. The standalone preview server's missing favicon produced one404; the
report/artifact path had no error. These results do not establish complete browser,
screen-reader, user-task or live-model efficacy coverage.

See the [evidence packet](../evidence/lrbc-c-20261106-v1/README.md). No external
model/client was configured, no paid service was used and no team report was sent.
