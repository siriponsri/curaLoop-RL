# Plan A execution contract

5 November 2026, Asia/Bangkok. **OWNER_AUTHORIZED / IN_PROGRESS.**
Base main: `6d7d9da67b488b6e2c0b31bc33b864e9ffa4353d`.
The owner authorized Plan A through Goals3–4, permitted existing dr-train if
local resources are inadequate, and requested local retrieval of code, data,
artifacts and evidence followed by remote code/data deletion.

## Budget, deadline and scope

Execution window starts 2026-11-04 22:37:04 UTC (5 November05:37:04 Bangkok)
and ends 2026-11-05 22:37:04 UTC (6 November05:37:04 Bangkok). Stop at the first
wall or compute ceiling. CPU is cumulative process/subprocess CPU across both
hosts, not logical-core availability, simulated assay time or LLM tokens.

| Stage | CPU ceiling | Workers | RAM | Additional scratch/output |
| --- | ---: | ---: | ---: | ---: |
| Goal3 |8CPU-hours |2, one thread each |8GiB total |16GiB |
| Goal4 |40CPU-hours |4, one thread each |16GiB total |32GiB global |
| Total |48CPU-hours |4 maximum |16GiB maximum |32GiB global |

Goal3 additional official metadata/feature downloads remain capped at200MB;
the existing archive is excluded. No GPU, paid resource or final-study execution.
At most three prespecified Goal4 candidate configurations. No retuning against
final outcomes. No external publication, editorial contact or payment.

Goal3 follows [its detailed contract](GOAL_03_PROPOSAL_20261105.md): source/
endpoint/rights, family/source and structure overlap, split/access manifests and
a stronger method decision. Goal4 starts only after its relevant gates pass.
If required source/family scope or method direction remains uncertain, present
options/evidence/impact and ask the owner before dependent work. Continue
independent authorized tasks. A completed audit is not automatic data readiness.

## Data access before ingestion

1. Preserve the original `fsmol.tar`, SHA256
   `528a9c4e8d74c4287acda79536eecbf91418d6d0ac2c55918b270d78c2333ebc`.
2. First inspect tar headers only: names, types, sizes and paths. No member
   content, labels or structures in this first phase. Reject unsafe paths,
   links, unsupported entries and excessive member/expanded sizes before writes.
3. Resolve source metadata and role rules before semantic assay parsing.
   Metadata/structure preparation may use trusted code that suppresses label
   fields, records access and never emits final outcomes to agents/policies.
   Label inspection is limited to explicitly declared development tasks.
4. Any agent/human label exposure is recorded and changes the applicable role.
   Do not relabel exposed tasks as untouched. Final-study outcomes stay sealed.
5. Keep raw/derived assay files ignored. Publish only permitted code, metadata,
   audits and non-leaking aggregate evidence with exact hashes.

## Execution and team

Parent is the sole repository writer/integrator. Existing specialists are
read-only: journal_fit owns source/rights/family metadata research;
journal_submission owns method/closest-work review; english_documentation owns
English contract/evidence review. No shared-file concurrent edits or subdelegation.
All workers preserve other changes. Normal main integration/push remains
authorized. Every scientific run/version has a distinct immutable identity and
attempt ledger. Report actual outcome/compute at stage boundaries.

Preflight checks local/remote load, memory, disk, active jobs and allowed CPU
affinity. Use low-priority, explicitly limited task processes and project locks.
Do not stop unrelated jobs, borrow another project's environment/allowance,
read private-key contents or modify SSH configuration. Existing IP profile
100.77.149.83 authenticates to dr-train as configured; no new key/profile.

## Remote retrieval and deletion

New remote task root, if used:
`/home/chaw/curaloop-rl/plan-a-20261105-v1`.
Previous task-owned Goal2 root may also be cleaned after its complete local
preservation is established:
`/home/chaw/curaloop-rl/goal2-20261104-v1`.

Inventory every regular file with relative path, byte size and SHA256; reject
symlink/path surprises. Retrieve code, inputs, outputs, logs, environment
records and failure/checkpoint files. A matching original local archive may
satisfy input retrieval without duplicating it, provided the mapping and hash
are recorded. Do not count a partial transfer or a zip's existence as success.

Before recursive removal, verify the exact remote absolute root and resolved
parent, task ownership, absence of active task processes, and complete local
byte/hash correspondence. Retain the verified manifest/cleanup receipt locally.
Delete only those explicitly named, verified task roots, never the project
parent, home, a computed unverified path or other projects. Then verify absence.
If transfer/identity fails, retain the remote files and ask about the blocker.
These cleanup checks implement the owner's deletion instruction; they do not
create a new approval requirement for already verified task-owned copies.

## End state

Deliver English data/method/result artifacts, clear Thai Goal3/4 reports,
budget ledger, main commit/push verification and local retrieval/remote cleanup
proof. Stop for joint owner review after Goal4. No favorable result, external
replication or publication readiness is guaranteed by execution authorization.
