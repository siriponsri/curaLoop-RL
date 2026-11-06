# Goal 4R2-A2 closeout

6 November 2026, Bangkok. **READINESS COMPLETE; ENGINEERING PASS;
SCIENTIFIC PILOT NO_GO.**

The owner-approved [contract](GOAL4R2A2_EXECUTION_CONTRACT_20261106.md) covered
metadata/source/benchmark readiness, four CPU-hours, twelve elapsed hours and
at most two CPU workers on dr-train. The goal is complete with explicit limits;
the broader Goal4 scientific exit and final-study design remain unresolved.
Read the [readiness report](../03_research/GOAL4R2A2_READINESS_V1.md),
[benchmark assessment](../03_research/GOAL4R2A2_BENCHMARK_COMPATIBILITY_V1.md) and
[evidence index](../evidence/goal4r2a2-20261106-v1/README.md).

## Delivered

- Description metadata for 105/105 fixed MF-PCBA AIDs; all observed version/
  revision pairs match SI S19. The inspected date field is absent in all 105;
  historical activity-byte equivalence remains NOT_CERTIFIED.
- Two description-only version controls. AID 873's deliberately invalid selector
  returned the same HTTP 200/current 1/13 metadata as the publication selector
  and no-selector request. Historical selection is NOT_VALIDATED for this path.
- Provider/source/target/readout register: eleven observed provider names and
  3,287 readout definitions, without compound/activity rows. Provider-specific
  row rights, endpoint bindings, eligible populations and independent groups
  remain open. A conditional observation/population protocol is proposed.
- Pinned MolDesignBench source/licence/output/runtime/metric/exposure review.
  Direct plan/report evaluation is NO_GO; auxiliary molecular design is
  conditional. Commercial dataset reuse is NOT_CLEARED. No benchmark task/gold
  intake, concrete held-out roster or native evaluation occurred.
- Ten pre-implementation metadata/compatibility contract cases passed on
  dr-train; separate read-only source and final-report reviews recorded.

No application, old frozen method/result or scientific panel changed. No assay
activity, compound query, molecular campaign, new model, live LLM/MCP/team
write, GPU, new paid service or journal action was part of this execution.

## Execution and resources

Window: 6 November 01:05:41–13:05:41 UTC / 08:05:41–20:05:41 Bangkok.
Three serialized one-CPU jobs actually ran: description probe, ten-case
validation, and roster/control acquisition. Each durably reserved 120 CPU-seconds
before launch, with a 600-second wall watchdog, 768 MiB address-space ceiling,
nice 19 and CPU affinity 71. The shared CPU was not claimed exclusive.
Python was 3.12.3; the existing skill client used the host's requests 2.31.0.
No dependency was installed. No unresolved launch reservation remains.

Measured worker CPU totaled **9.000529007 seconds**. The conservative charge
retains all 360 reserved worker seconds plus 3,600 seconds for preparation,
retrieval, transport, checks, administration and preservation: **3,960 seconds /
1.1 CPU-hours of four**. This is reserve-based accounting, not an exhaustive
measurement or certified bound of host CPU. See the [budget receipt](../evidence/goal4r2a2-20261106-v1/budget-closeout-v1.json).

Snapshot CPU was 0.263044353 seconds. Enhanced local reread used 1.640625 CPU-
seconds / 7.761426 wall-seconds; the complete guarded wrapper used 1.671875
CPU-seconds / 7.953 wall-seconds. These costs are included in the preservation
reserve. The local verifier has a one-CPU, 300-CPU-second, 1,800-wall-second guard
and the same absolute owner deadline. The remote return wrapper itself does not
implement a hard CPU/deadline guard; its measured snapshot and actual cleanup
completed within the window. Utility/host overhead is not fully instrumented.

## Frozen source and checks

Ten case definitions were frozen at 01:12:17.940029 UTC, before implementation,
SHA256 `c1fca7585e0b49070678cfe41ebf6e490c24816f044d38be1299a46d3d471892`.
The [probe bundle](../evidence/goal4r2a2-20261106-v1/source-freeze-probe-v1.json)
and [tested/acquisition bundle](../evidence/goal4r2a2-20261106-v1/source-freeze-contracts-v1.json)
identify source bytes, request plan, benchmark manifest and prior SI metadata.
The second adds the completed metadata package/tests without changing the first
attempt's saved bundle. No source was silently overwritten without history.

The exact existing skill client, SHA256
`78ddae6460e3dd701cda67df4454532899d20851f8212a74ec8d5b6e2988b690`,
was copied privately, hash-checked before use and completely returned. It is
not republished or a Git-index input. Other bundled public source bytes are
checked against the release index. The preserved task includes both archives,
source history, request receipts, raw decoded descriptions and all job logs.
System Python, requests and OS libraries are not fully vendored; this is not
a hermetic environment reproduction.

Five material pretest review findings were fixed before the first ten-case run.
The final reviewed source and ten actual executed META IDs are recorded in the
evidence packet. These engineering results do not certify a live agent security
boundary, scientific endpoint, benchmark score or method novelty.

## Complete return before scoped cleanup

All **244 regular task files / 4,919,055 bytes** were restored and reread locally
against the full manifest before acknowledgement and deletion. Local retention:

`C:\Users\User\Desktop\myProject\curaloop-rl\.local\goal4r2a2-20261106-v1\remote-return\full-v1\`

- Tree SHA256: `6c400e66a1855b6ad975478e6f688061d49e8a2c2a68df348e6d3bd37ed83173`.
- ZIP SHA256: `4efbdbc2e622b0b583b84f059855236721176f8f4fb03c08f9800ea630acc755`.
- Manifest SHA256: `a475620763993a9586a2f4963478ddcdaf03b0d1dd335388a3fc3b9c385d7f73`.

The immutable original/enhanced local proofs, archive and all restored files stay
outside public Git. Exact approved task and `-return` sibling were deleted only
after complete local proof; both deletion JSON records were retained. A fresh
SSH check at **01:44:59.394922 UTC / 08:44:59 Bangkok** confirmed both absent.
No older closed root or unrelated host project was modified. Do not recreate
these roots. [Proof](../evidence/goal4r2a2-20261106-v1/local-verification-v2.json),
[deletion](../evidence/goal4r2a2-20261106-v1/remote-delete-v1.json),
[fresh absence](../evidence/goal4r2a2-20261106-v1/remote-absence-v1.json).

## Delivery and next decision

Base main was `19979f12bb5a07cabf4624cd8a2940e663953614`. Main integration and a
normal push remain authorized. The final release audit checks package links,
English reports, preserved old bytes, source/index identities and forbidden
payload exclusions. Publication is verified separately against local HEAD,
origin/main and live remote main after the commit; this document does not
self-certify its own future push.

Stop at this completed readiness goal. The report proposes 4R2-A3 historical
observation qualification, eight CPU-hours / twelve hours / maximum two CPU
workers, requiring a new pre-intake rights/scope contract and owner decision.
P1 integration, benchmark task intake, commercial dataset use, new scientific
campaigns and final-study/journal actions do not start automatically. Original
final outcomes remain reserved; no broadly novel method or business benefit
has been established.
