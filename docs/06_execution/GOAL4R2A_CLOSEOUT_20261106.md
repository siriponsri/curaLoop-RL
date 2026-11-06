# Goal 4R2-A closeout

6 November 2026, Bangkok. **FEASIBILITY COMPLETE; ENGINEERING PASS;
SCIENTIFIC METHOD/PILOT ADVANCEMENT NO_GO.**

The owner approved the [4R2-A contract](GOAL4R2A_EXECUTION_CONTRACT_20261106.md).
The [feasibility report](../03_research/GOAL4R2A_FEASIBILITY_AND_NEXT_STUDY_V1.md)
and [workflow guide](../05_product/OFFLINE_RD_WORKFLOW_V1.md) describe the completed
offline prototype and remaining scientific gates. This goal may complete with
a documented scientific NO_GO; it does not pass the broader Goal4 gate.

## Delivered and actually executed

- New independent `curaloop_rd` package: offline catalogue inspection, typed
  evidence/plan validation, local report bundles, revisions, interruption recovery
  and idempotent preview receipts. No application or frozen research engine changed.
- Twelve engineering cases frozen before implementation, plus eight boundary
  checks, passed on dr-train with Python 3.12.3. The actual demo uses synthetic
  fixtures, not experimental compound measurements or an LLM.
- Source-backed metadata register for 60 MF-PCBA definitions; 54 distinct primary
  and 60 distinct confirmatory AIDs, with nine same-AID definitions. SI Table S2
  corroborates every stage pair; S19 specifies version/revision/date for all
  105 distinct AIDs. Historical row reconstruction and eligible biological groups
  remain unverified; no scientific cohort was cleared.
- An explicit next-study question, controls, observation/identification gates
  and [dataset/benchmark expansion proposal](GOAL4R2A_EXPANSION_PROPOSAL_20261106.md).
  No expansion execution, scientific campaign, training, live agent evaluation,
  MCP/client integration, team-tool write or journal action occurred.

First bounded engineering execution passed all 20 checks. Read-only review found
partial-write, stored-identity and lost-reply retry defects before execution;
these were corrected before that first run. The additional four bounded remote
jobs identified the initial owner PDF, inspected SI sections and checked published
metadata. They are not extra scientific trials or part of the twenty workflow checks.

## Resource evidence

Window: 5 November 23:57:53 UTC to 6 November 11:57:53 UTC; Bangkok 6 November
06:57:53–18:57:53. Cap: four cumulative CPU-hours and two CPU workers.
The [budget closeout](../evidence/goal4r2a-20261106-v1/budget-closeout-v1.json)
reconciles five completed jobs, each with a durable 120 CPU-second reservation
before launch. Actual recorded overlap was one worker, affinity CPU 71; that CPU
was not claimed exclusive on the shared host.

Recorded worker CPU totaled 1.757830859 seconds. All five jobs passed within the
approved window. Conservative charges retain all 600 reserved worker seconds
plus 3,600 seconds for preparation, retrieval, transport, administration,
preservation and local checks: **4,200 seconds / 1.166667 CPU-hours of 4**.
These are conservative charges, not exact host usage. Exhaustive host CPU is
NOT_CERTIFIED. The initial three-job controller envelope was expanded to six,
with three per mode, to accommodate the owner-supplied SI metadata work inside
the same budget. Five jobs actually ran; no unresolved reservation remains.

The full remote snapshot used 0.537918484 CPU-seconds. Inner local verification
recorded 1.546875 CPU-seconds and 23.219153 wall-seconds; the complete guarded
wrapper recorded 1.609375 CPU-seconds. Both are covered by the preservation
reserve. The local verifier had its own one-CPU/300 CPU-second/1,800 wall-second
guard. Its CPU allowance is not added to the already charged utility reserve.
The prototype/checks use the Python standard library. Metadata-only PDF inspection
copied the existing bundled pypdf 6.10.0 source and licence into the private task;
no host package installation, GPU or paid service was used.

## Source and input provenance

The [initial freeze](../evidence/goal4r2a-20261106-v1/source-freeze-v1.json)
identifies the tested runtime and pre-implementation case SHA256
`a0aa21eb13ac38262fc951a1632fba18207627a5ab522e7534626ffd7446ff92`.
Later additive bundles contain the SI inspection/audit helpers; they do not change
the tested workflow source. All bundled source/archive versions remain retained.

The first owner input was a 12-page primary article, identified through first-page
inspection. The owner then supplied the separate 47-page SI, SHA256
`76e6a09af571226b6d5d42708dbee71637e15f9a0e650fbc41b575ec2327b7a7`.
Selected pages 1–3 and 36–47 were extracted on dr-train. The metadata audit uses
S2 on page 3 and S19 on pages 46–47; intervening published model plots were not
used to select cohorts or methods. No compound activity table was ingested.

Local convenience previews contain one additional newline from SSH `print`.
They were not represented as original bytes. [Provenance reconciliation](../evidence/goal4r2a-20261106-v1/si-input-provenance-v1.json)
confirms the complete returned raw text hashes exactly match the audit inputs,
and each convenience preview is the original plus that one LF. Raw PDF/text,
reader sources, licence, original receipts and archives remain ignored locally.
Public JSON proof copies use LF with unchanged parsed content.

## Complete return before exact cleanup

Canonical local return:
`C:\Users\User\Desktop\myProject\curaloop-rl\.local\goal4r2a-20261106-v1\remote-return\full-v1\`.

It retains the original archive/manifest, base and enhanced verification proofs,
resource receipt and `files/` with **220 regular files / 12,823,111 bytes**.
The transfer ZIP is 5,339,875 bytes. Included are source bundles, executed code,
all job evidence/demo artifacts, both owner PDFs, selected private text and the
copied PDF-reader source/licence. System Python and OS libraries are not vendored;
this is not a fully hermetic or separately Windows-tested environment.

| Identity | SHA256 |
| --- | --- |
| Regular-file inventory | `a275c114ce27f40a20c77b6cdb496380068c3318c9052f8488e7a23459a58e18` |
| ZIP | `92712c4a457be917be3b219bff96f4b13eb3d55782635b66f52831796d412ece` |
| Original manifest | `993cf6c33260398a53f2a6973b8b2f2f228d6a513f2bf0874a9091482bc849e6` |

The [enhanced verification](../evidence/goal4r2a-20261106-v1/local-full-return-verification-v1.json)
checked every member and reread all restored files, with the manifest unchanged.
Only after acknowledgment did the pinned preservation core recheck source
identity, ownership and active processes, then remove these exact roots:

- `/home/chaw/curaloop-rl/goal4r2a-20261106-v1`
- `/home/chaw/curaloop-rl/goal4r2a-20261106-v1-return`

Both deletion receipts were decoded and retained. A [fresh read-only probe](../evidence/goal4r2a-20261106-v1/remote-absence-v1.json)
at **6 November 00:41:39 UTC / 07:41:39 Bangkok** confirmed both roots absent.
No subsequent dr-train job or root was created. Prior closed task roots were
not recreated and unrelated projects were not modified.

## Next actor and acceptance limits

Starting main was `1ba48632540c6e8b38bea93ac6a16e23b65d924e`; final publication
is checked separately against live remote main in the local delivery receipt.
No historical scientific bytes or final outcomes were changed. Application,
frontend and browser suites were not rerun for this isolated prototype.

Owner review is next. Consider source/benchmark readiness or P1 integration under
its own approved scope. Novelty, scientific utility, an eligible independent
cohort, real-agent performance, customer demand and laboratory savings remain
unestablished. Do not start 4R2-B, full P1, a final study or journal submission
automatically. Unused budget does not grant a new goal.
