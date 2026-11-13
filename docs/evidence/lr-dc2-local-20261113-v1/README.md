# Local molecular workflow: actual evidence and reproduction

Owner-adopted solo release, 13 November 2026. Fresh budget: 96 CPU-hours and
24 allocated GPU-hours; fixed deadline: 20 November 2026 11:51:07 UTC. Earlier
0.675 CPU-hours remain separately retained. No account or prior result was reset.

## Interpret the results correctly

| Question | Actual status | Authoritative evidence |
| --- | --- | --- |
| Did external native admission pass? | **NO**: 1 development / 6 evaluation candidates / 3 evaluation lineages; minimum lineages = 4 | `native-admission-final-v1.json`, `admission-checkpoint-v1.json` |
| Was the comparative agent experiment run? | **NOT_RUN** | `admission-checkpoint-v1.json` |
| Did version binding improve over a matched checklist? | **NOT_ESTIMABLE**; no point estimate or interval | `descriptive-analysis-v1.json` |
| Does the actual local RDKit/HTTP workflow work? | **PASS**: 58 component/API regression tests; served EN/TH browser, CSV/ZIP/2D checks | private guarded job receipts, `product-browser-v5.json` |
| Did the real model complete the frozen author cases? | **6/6**; 12 real responses; 332 generated / 3,325 prompt tokens | `product-model-acceptance-v1.json`, `product-provider-calls-v1.json`, `tables-v2/author-model-cases.csv` |
| Were deterministic software expectations correct? | **3/3** actual RDKit cases | `product-model-acceptance-v1.json` |
| Could saved actual model jobs reopen after service restart? | **PASS**, 9 saved jobs, unchanged revisions, no new inference | `model-product-browser-v1.json` |
| Is scientific/clinical/user or commercial superiority established? | **NO** | English feasibility report and its limitations |

The six cases are three related request pairs in English and Thai, selected by
the developer. They are software acceptance, not a substitute publication
benchmark or independent expert validation. Timing is a fixed sequence with a
cold first request and later warm requests. No model case was repeated. Source
and scoring were recorded before product responses in
`product-acceptance-freeze-v1.json`. Public request/response evidence is genuine;
it is not mock inference or an endpoint that pretends to generate a new answer.

The initial V100 technical canary passed on an otherwise free device. Before
product cases, another project occupied it. The same checkpoint and fixed
settings were used on the free RTX 2080 Ti within the one-GPU authorization.
`product-device-selection-v1.json` records this availability-only change before
product generation. All twelve product responses recorded GPU residency; full
GPU-only offload is not claimed. Containers used two CPU equivalents and a
20 GiB host-memory ceiling, without changing shared services or model caches.

## Retained failures and supersession

- `native-reference-qualification-v3.json` contains unsupported initial
  scalar-decoder flags. They are **not scientific failures**. Upstream actually
  returns `(success, log_info)`; use the corrected and final receipts. The final
  report retains older raw fields such as `native_return_not_admitted` as history;
  the explicit interface status and corrected `native_success` are authoritative.
- Mount, newline/byte transport, dependency and final source-compatibility
  failures remain in their versioned receipts. Only four failed references had
  the final compatibility attempt; successful reference fits were not repeated.
- Browser attempts v1-v4 were engineering failures: an incomplete failed build,
  same-origin refusal on a separate loopback port, an image-load observation race
  and mobile overflow. Their receipts are preserved. Browser v5 follows concrete
  fixes and checks actual rendering, downloads, search and saved reopening.
- Build v2 exceeded an unnecessarily strict 1 GiB local guard. The dedicated
  guard uses the already authorized 2 GiB ceiling; the historical shared guard
  is unchanged. Later builds passed with bounded Node memory.
- The first descriptive analysis exported valid tables, then failed looking for
  a nonexistent CPU-reservation field in a stop receipt. The corrected analysis
  reads the original ledger booking; tables-v1 remain and tables-v2 are final.
- Initial document jobs lacked local plotting/PDF packages. Their failures are
  retained; document dependencies were installed within the new release. First
  PDFs exposed merged list items and a colliding chart legend in visual review.
  The v2 document set corrects layout without changing results; final guide v3
  adds the actual execution trail to the sparse text page. Manuscript v2 remains
  final. V1 is an unapproved visual draft, not the delivery version.

No benchmark/environment/reference retry is permitted after final admission
closure in this release. There was no hidden model/provider substitution,
outcome-driven case rerun, paid API, public deployment or manuscript submission.

## Files and scope

- `owner-resource-release-v1.json`: new authority and preservation identities.
- `static-task-catalog-v1.json`, `source-exposure-register-v1.json`: metadata
  screening and known source exposure. Repository groups are lineage proxies.
- `native-asset-separation-v1.json`: evaluator/input separation, not an agent score.
- `real-gpu-format-canary-v1.json`: actual seven-token format canary, not a task.
- `actual-*-watchdog-*.json`: real CPU/wall termination probes.
- `product-acceptance-freeze-v1.json`: author software cases, expected numeric
  limits and IDs, scoring and package source identities.
- `product-provider-calls-v1.json`: exact public author-example model messages,
  JSON schema, actual responses and usage, with original private receipt hashes.
- `software-environment-v1.json`: actual software/model/lockfile identities.
- `figures-v2/`: final native-readiness figure in SVG/PDF/PNG, plus visual spec.
- `tables-v2/`: exact software and reference-admission tables in CSV.
- `full-remote-return-v1.json`, `owned-cleanup-v2.json`: complete owned persistent
  return/reread and exact cleanup receipts. Cleanup v1 failed on root-owned
  container files after the complete return. V2 verified every remaining file
  against that manifest and cleared only the exact task bind in a bounded
  container, then removed it. System permissions did not change. The failed
  cleanup v1 receipt and both resource bookings remain intact.
- `delivery-audit-v1.json`: final checks and conservative resource accounting.

Private root: `.local/lr-dc2-local-20261113-v1`. It holds all guarded job logs,
failed receipts, exact remote executed source, local per-job snapshots, original
model receipts, SQLite job stores and complete returned persistent file bytes.
These are excluded from public Git. Earlier local jobs captured their controller
pin only; later jobs additionally captured the listed Python/API/UI sources.
Do not backfill an earlier executed-source snapshot or call these a complete
system/environment capture. Ephemeral container tmpfs bytes were not persistent
and are not claimed returned. External reference/gold bodies stay private.

## Reproduce the software without a model

Install the repository with its chemistry/web extras, then follow the
[English operator guide](../../08_agent_rd/LOCAL_WORKFLOW_GUIDE_EN_20261113.md).
For byte-accurate source-pin verification in a fresh Windows checkout, clone
with `git -c core.autocrlf=false clone <repository-url>`. This release preserves
raw executed source bytes. The historical frozen `.gitattributes` was retained;
no global Git configuration needs changing. Ordinary semantic software
recomputation is distinct from verification of historical source byte identities.
The normal localhost interface is `/workflow`. Deterministic use needs neither
SSH nor a model. A new output directory is mandatory for CLI reproduction:

```powershell
.venv\Scripts\python.exe -m curaloop_rd.local_agent_v1.workflow examples/local-workflow/request.json .local/my-new-molecular-run
.venv\Scripts\python.exe -m research.local_agent_eval_v1.reproduce_software --output .local/my-new-software-reproduction
```

The first command produces a real RDKit report and ZIP. The second freshly
recomputes the three public parameter sets, checks current exports and compares
the frozen expected selected IDs. It makes **zero model calls** and does not
reproduce agent efficacy. Public saved model receipts can be inspected offline;
they are not a new inference. To inspect the owner's saved model jobs locally,
start the app with `CURALOOP_STORAGE_PATH` pointing to the retained
`.local/lr-dc2-local-20261113-v1/product-model-v1/local-api.sqlite3` and a free
loopback port. Do not set an expired session variable.

New live-model work requires a newly authorized bounded resource session and a
configured transport. The research worker is retired after full return/cleanup.
Administrative one-time release/repair/return tools enforce unique identities
and closed accounts; do not rerun them to imitate a reproduction or reset costs.
External benchmark reproduction requires its original licensed data, a separately
reviewed environment and a new resource release; it is not initiated by these
software commands. No final16 or private CF1 data is required for either command.
