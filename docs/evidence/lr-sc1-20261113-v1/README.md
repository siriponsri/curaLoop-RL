# LR-SC1: native readiness stop, 13 November 2026

Research outcome: **NO_GO_NATIVE_EVALUATOR_READINESS**. The authorized branch
stops after one source-supported technical repair. No agent comparison occurred.

| Evidence | Status / interpretation |
| --- | --- |
| `release-v1.json` | Fresh owner-authorized scope and limits; old accounts remain closed |
| `gate0-v1.json` | Bounded empirical distinction accepted for data admission; novelty unproven |
| `source-intake-v1.json` / `numeric-intake-v1.json` | Official source identities and exact numeric-file hash |
| `development-selection-v1.json` | Six validation IDs fixed by hash order before model outcomes |
| `native-qualification-v1.json` | First reference attempt: 26/29 checks, 4/6 main problems |
| `native-qualification-v2.json` | Single allowed repair: 28/29 checks, 5/6 main problems |
| `validation-reference-checks-v1.csv` | Both technical attempts, including every failure; not independent samples |
| `native-assembly-concordance-v1.json` | Failed 70.8 program AST matches upstream assembly; no rerun |
| `gate1-v1.json` | Failed readiness decision; agent comparison NOT_RUN; effect NOT_ESTIMABLE |
| `remote-return-v1.json` | Full owned persistent file return and independent local reread |
| `remote-cleanup-v1.json` | Exact task root/exports/stopped-container cleanup after verified return |
| `delivery-audit-v1.json` | Final resource, preservation, artifact and delivery checks |

Later closeout files are created only after their checks actually pass. The
delivery audit, not this index, establishes completed return and cleanup.

## Boundaries

The initial adapter omitted the native `scicode.compare` package. Its correction
fixed 70.6 and 10.7; it did not change scientific assertions or numeric targets.
Reference 70.8 still failed. The cause remains unresolved; universal benchmark
defect and agent-method failure are not established. The official 65 test
problems had complete fixture-group metadata, which is not a 65-task numerical
qualification. Their expected numeric values and reference programs remained
outside this evaluation. Original final16/private CF1/hidden outcomes stayed closed.

The source code and dataset revisions are pinned in `gate1-v1.json`. The numeric
asset is private under `research/raw_data/external-benchmarks/scicode-2024/`.
The full task-owned remote return is private under
`.local/lr-sc1-20261113-v1/remote-return-v1/`; its manifest records every file hash.
No raw numeric targets or reference-program content are included in this public
evidence directory.

## Offline audit reconstruction

From the repository root, the report builder's read-only mode reconstructs
counts from the retained public receipts without SSH, HTTP, inference or test
execution:

```powershell
rtk proxy python tools/sc1_report_v1.py --verify-only
```

Full numerical re-execution is not activated by this command. The task runners
require the owner-approved account and must not be replayed after account closure.

The editable English technical manuscript is in
`docs/07_publication/LR_SC1_SCICODE_ADMISSION_MANUSCRIPT_EN_20261113.md`.
Empirical Software Engineering submission readiness: **NO_GO**, because the
proposed comparative agent evidence does not exist. This report preserves the
pre-inference readiness failure without substituting mock or historical results.
