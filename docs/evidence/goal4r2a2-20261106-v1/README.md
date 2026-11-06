# Goal 4R2-A2 evidence

6 November 2026. **SOURCE READINESS COMPLETE; ENGINEERING PASS;
SCIENTIFIC PILOT NO_GO.**

Read the [readiness report](../../03_research/GOAL4R2A2_READINESS_V1.md),
[MolDesignBench compatibility/exposure assessment](../../03_research/GOAL4R2A2_BENCHMARK_COMPATIBILITY_V1.md)
and [closeout](../../06_execution/GOAL4R2A2_CLOSEOUT_20261106.md).

## Source, requests and observation states

- [Pre-implementation cases](../../../research/configs/goal4r2a2_cases_v1.json)
  and [freeze](cases-freeze-v1.json).
- [Probe bundle](source-freeze-probe-v1.json) and
  [tested/acquisition bundle](source-freeze-contracts-v1.json).
- [Request plan](../../../research/configs/goal4r2a2_requests_v1.json) and
  [107 description-only request receipts](request-receipts-v1.json).
- [Original acquisition summary](metadata-register-v1.json),
  [derived readiness/provider register](readiness-audit-v1.json) and
  [readout definition facts](readout-definitions-v1.csv).
- [Allowlisted aggregate transfer proof](aggregate-transfer-v1.json).
- [Pinned benchmark/exposure manifest](../../../research/manifests/goal4r2a2_benchmark_readiness_v1.json).

All 105 current descriptions returned version/revision pairs matching SI S19.
The inspected date field is absent in all 105; full historical rows remain
NOT_CERTIFIED. The invalid AID 873 selector returned current metadata, so the
description selector is NOT_VALIDATED. The immutable acquisition summary keeps
its initial UNVERIFIED status; the derived audit records the control-based
interpretation without rewriting that earlier result.

There are eleven provider names, 3,287 readout definitions and target lists for
95 AIDs. No activity/compound rows are present. Readout names/unit enums are
column definitions; units remain undecoded, endpoints unselected, provider rights
unresolved and actual eligible cohort/group counts UNKNOWN. Zero certified
groups is a clearance count. No benchmark task/gold rows were ingested; source
examples and the unsuccessful external schema-preview attempt are disclosed.

## Engineering and resource evidence

- [Ten actual cases](contract-results-v1.json), [check log](contract-checks-v1.log)
  and [test resources](contract-resources-v1.json).
- [Probe resources](probe-resources-v1.json), [roster resources](metadata-resources-v1.json)
  and [three-job durable launch ledger](remote-launch-ledger-v1.json).
- [Review record](review-record-v1.json), [release audit](release-audit-v1.json)
  and [package/link check](package-check-v1.json).
- [Budget closeout](budget-closeout-v1.json): 9.000529007 measured worker CPU-
  seconds, 3,960 conservative charged seconds / 1.1 of four CPU-hours including
  utility reserves; exhaustive host CPU accounting is NOT_CERTIFIED.

These are engineering checks and source reviews, not scientific campaigns,
native benchmark scores, live-agent validation or business evidence. Generic
package-check NOT_RUN entries describe that check's scope; actual main
publication is verified separately after commit.

## Preservation

- [Snapshot](remote-snapshot-v1.json), [complete local reread/manifest proof](local-verification-v2.json)
  and [proof acknowledgement](return-acknowledged-v1.json).
- [Both deletion records](remote-delete-v1.json) and [fresh absence](remote-absence-v1.json).

All 244 regular task files / 4,919,055 bytes returned and reread before exact
task/export deletion. Original ZIP, manifest, immutable proofs and all restored
files remain in ignored `.local/goal4r2a2-20261106-v1/remote-return/full-v1/`.
Raw description/protocol text and the copied skill client remain private. Source
hash manifests intentionally identify the private client without republishing it.
The host's Python/requests/system libraries were not fully vendored.

Fresh absence was confirmed 6 November 01:44:59.394922 UTC. Closed A2 roots must
not be recreated. Future data intake, P1, scientific or benchmark execution
requires its own owner-approved goal.
