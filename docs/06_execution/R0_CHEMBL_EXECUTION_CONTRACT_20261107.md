# Bounded R0 ChEMBL execution contract

Owner release: the owner authorized R0 work through its phase readout on
7 November 2026. Base main: 0de9df4a6b772dcbb90ed291cb4c5d4d9fa1e4bf.
This releases [the readiness plan](../03_research/R0_CHEMBL_DATA_READINESS_PLAN_20261107.md)
within its bounds. It is not an unlimited grant or the next phase.

Release time: 2026-11-07T05:43:17Z (12:43:17 Asia/Bangkok).
Absolute end: 2026-11-07T09:43:17Z (16:43:17 Asia/Bangkok).
CPU ceiling: 1800 seconds; reserve 300 for setup, validation, source review and
report utilities. Processing reservations are additional and durable, with a
single local worker; no historical ledger is reset. Use at most one CPU and
1 GiB memory, preferably a smaller hard limit where sufficient. Record actual
CPU separately from conservative reservations; unmeasured utility cost is not
claimed to be zero.

Fresh private root: `.local/r0-chembl-20261107-v1/`. Never recreate closed remote
roots. Parent remains sole writer. No SSH processing or remote deletion needed.
All source attempts, failed jobs, bytes and resource receipts remain auditable.

Retain all plan limits: 50 assay, 20 document metadata, 100 target/lineage records;
32 serialized source attempts, at least one second apart; 30-second request
deadline; 2 MiB per response, 16 MiB decoded total, 64 MiB new working storage.
Do not retry a failed affected source or follow an unknown redirect. Verify
version/source/schema/rights first. Release-35 source metadata is the candidate;
live current-release API data cannot substitute for it. Full database download
is outside this contract. No activity, benchmark/gold or protected final intake,
training, model/paid API, GPU, team writes, deployment or journal submission.

The approved phase endpoint is a readiness decision, including REVISE/NO_GO if
necessary. Metadata alone cannot certify an observed panel, 12 independent
families, method novelty or publication readiness. Perform independent in-scope
formalization/closest-work analysis and reporting even if source intake blocks.
Material release/endpoint/population/rights/resource changes require owner
consultation with concrete evidence. Do not change a failed gate into PASS to
claim phase completion. Do not move to P1/R1 without a new owner decision.

Execution evidence will be recorded in `docs/evidence/r0-chembl-20261107-v1/`.
