# LR-DC2 dataset and resume evidence

## Current owner checkpoint, 13 November 2026

State: **RESUMED_SCOPE_ADOPTED_BUDGET_PENDING**. The owner resumed, requested
review of a new proposal, then adopted its local-workflow scope and a new
budget in principle. One numerical resource choice remains; no model/GPU job
or archive extraction has started. Read the
[proposal review](../../08_agent_rd/LOCAL_AGENT_PROPOSAL_REVIEW_20261113.md),
[protocol design](../../08_agent_rd/LOCAL_AGENT_PROTOCOL_DESIGN_20261113.md),
[initial resume receipt](owner-resume-review-20261113-v1.json) and
[subsequent scope adoption](local-scope-adoption-20261113-v1.json).
The effective seven-day window is 13 November 2026 11:51:07 UTC through
20 November 2026 11:51:07 UTC, both 18:51:07 Bangkok. Prior bookings/results
remain intact; no numerical budget reset is inferred from approval in principle.

## Historical dataset pause, 11 November 2026

Current state: **PAUSED_OWNER_REQUEST**, all started jobs settled. This is a
dataset checkpoint, not a passed contribution/cohort gate or a completed study.
The owner moved the seven-day clock to the next explicit resume. Pre-pause
bookings remain charged within the same64 CPU-hour/24 allocated GPU-hour caps.

- [Detailed dataset/resume handoff](../../08_agent_rd/LR_DC2_DATASET_PAUSE_HANDOFF_20261111.md)
- [Execution/steering record](../../08_agent_rd/LR_DC2_EXECUTION_20261111.md)
- [Original immutable proposal](../../08_agent_rd/NEXT_GOAL_DECISION_CONTRACT_PROPOSAL_20261111.md)
- [Fresh approved release](../../../research/manifests/lr_dc2_release_20261111_v1.json)
- [Owner clock amendment](owner-clock-amendment-v1.json)
- [Settled paused-account receipt](owner-pause-v1.json)
- [Actual preservation/controller checks](pause-checks-v1.json)

## Dataset actually received

The [official ScienceAgentBench repository](https://github.com/OSU-NLP-Group/ScienceAgentBench)
links the verified archive. The [verified annotation snapshot](dataset-annotation-intake-v1.json)
has102 rows at HF revision9c6e96c9e74572e979b0930ee735041cef528cb7.
Only structural columns were read; native solutions/activity values were not.

[Complete archive receipt](dataset-archive-receipt-v2.json):

- File: `research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip`
- Size:1,769,478,786 bytes; full local reread hash checked.
- SHA-256:`46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`
- ZIP directory:955 entries,4,071,815,117 declared expanded bytes, within12 GiB.
- Extraction, full encrypted-member CRC check, native oracle execution and
  candidate evaluation: **NOT_RUN**. No separate publisher-signed checksum claimed.

The archive and private annotation/operational snapshots are intentionally
outside Git. Respect the source's unzipped-data redistribution restriction.
Retained source bodies, directory metadata and executed controller snapshots
are under `.local/lr-dc2-20261111-v1`. No source gold enters public generated
results, model prompts or a production adapter at this checkpoint.

## Failures retained

[Ordinary HTTP access](dataset-archive-probe-v1.json) failed403. A separate
[anonymous browser check](dataset-archive-browser-probe-v1.json) observed the
official download; it was not mistaken for a completed transfer.
[The actual bounded transfer](dataset-archive-intake-v1.json) received every
declared byte, but its whole-file hash reread exceeded the one-GiB guard. The
first controlled followup also failed with MemoryError. Both reservations and
logs remain. A constant-memory hash followup verified and renamed the same
retained file, without downloading again, changing the memory cap or overwriting
the earlier failure receipt. ZIP metadata inspection did not open member bodies.

Retained CPU allocation:2,430 seconds (0.675 hours). Observed guarded-job CPU:
193.65625 seconds. Interactive administrative CPU was not separately metered;
the allocation includes a600-second control allowance and is not measured use.
GPU allocation/model calls/SSH connections/remote task roots: **zero**. No new
model was downloaded. Existing dr-train services and caches were not contacted.

All15 prior ledger identities,66 old scientific pins,27 AgentRD frozen pins
and947 prior AgentRD artifacts passed preservation checks. Final16/private CF1
rows/old hidden outcomes stay closed. Research gates, new evaluation and new
manuscript remain unrun/incomplete until explicit owner resume and passed gates.

The actual main-delivery identity is recorded after push in
`pause-main-delivery-v1.json`. Do not infer delivery from an earlier checkpoint.
