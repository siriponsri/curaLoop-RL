> Documentation update, 4 November 2026: [current programme](05_product/OPERATOR_GUIDE.md) and [documentation map](README.md). The detailed record below is retained from the inspected POC checkpoint. New research and commercial capabilities are specifications until implemented; prior test counts are historical execution, not new checks.

# Local persistence and recovery

The primary web app uses standard-library SQLite for one local owner, one active
server and one Uvicorn worker. No external database or account is required.
The default path is `.local/curaloop.sqlite3`, excluded from Git and releases.
Set `CURALOOP_STORAGE_PATH` to choose a different project-local database.
Streamlit remains session-memory-local and uses portable JSON export/resume.

## Storage contract

`api/storage.py` manages schema version **1** through `PRAGMA user_version`.
The tables are `runs`, `run_revisions` and `comparisons`. Each public snapshot is
canonical JSON with a SHA256 integrity checksum. SQLite transactions use full
synchronous writes. No campaign object, private oracle, unrevealed outcome table,
pickle or executable code is serialized.

A run row records session UUID, monotonic revision, public snapshot, original
creation identity and timestamps. Each committed revision has a separate immutable
snapshot. Scenario configuration is part of the existing public manifest.
Pending request records contain accepted public requests, not their future labels.
The original stored manifest is retained when read after restart; explicit new
actions use current implementation identity, with creation identity kept separately.

## Atomic actions and restart

The API reconstructs a candidate through `RunService.restore`, applies the
requested action using the existing Python engine, then updates the current row
and revision record in one transaction. The update requires the expected durable
revision. Cached state changes only after commit. Stale/repeated actions receive
HTTP 409; failed writes do not imply a successful action. A retry must refresh
the current public view before deciding what to do next.

Restart reconstructs accepted requests and delivered events against a fresh private
backend using existing reconciliation. Simulated time does not advance merely
because wall-clock time passed. Budget reservation, delayed visibility, new hits
and missing outcomes retain their original semantics. An interrupted mutation
leaves either its prior committed revision or its complete next revision.

Comparison jobs are persisted before submission and after status/result changes.
A previously queued/running job becomes **interrupted** at startup; it is never
silently repeated or represented as completed. Its results are unavailable unless
a complete report committed. Starting a replacement is an explicit user action.
Completed comparison reports remain independent of the active campaign/scenario.

The local retention limits are 40 saved campaigns and 20 comparisons, with up to
two comparison CPU jobs at a time. Export before removing old records. One active
server is required; run revision checks across instances are extra protection,
not multi-server job coordination.

## Corrupt or incompatible state

Checksums detect accidental byte corruption, not a cryptographic trust boundary
against the computer owner. Reconstruction additionally validates scientific
events/metrics and compatible public snapshot versions.

A corrupt run row is retained and listed as a recovery issue. Other valid runs
remain accessible. Saved revision metadata can be inspected and a valid revision
recovered into a **new** session; the original damaged row is not rolled back or
overwritten. Invalid/incompatible imports are rejected without replacing the
active run. A whole-file integrity/schema failure leaves storage unavailable,
reports an actionable error and preserves the original file.

To recover a whole-file failure:

1. Stop the server. Copy the database and any sidecar files before investigating.
2. Keep the original unchanged. Set a new `CURALOOP_STORAGE_PATH` in the launch
   terminal, for example `$env:CURALOOP_STORAGE_PATH = '.local/recovered.sqlite3'`.
3. Restart and validate a previously exported single-run JSON in Research evidence.
4. Do not delete or replace the old database just to clear an error.

For a consistent backup, stop the server cleanly before copying `.local`.
The application never auto-resets an incompatible database.

## Portable exports

| Artifact | Purpose | Can resume one campaign? |
| --- | --- | --- |
| Single-run JSON | Public scenario, provenance, accepted requests, events, metrics and curve | Yes, after full reconciliation |
| Comparison JSON | Reports from multiple independent matched policies | No; it is a comparison evidence container |
| CSV | UTF-8 event ledger for analysis | No; it is not a complete snapshot |
| SQLite backup | Local sessions, revisions and comparison records | Restore a stopped-server backup in the same compatible release |

Saved-state tests and actual process-restart evidence are reported separately in
[release verification](RELEASE_VERIFICATION.md). Persistence does not validate
drug efficacy, controller transfer or operational Digital Twin readiness.
