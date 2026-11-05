# Goal 4R1 evidence

5 November 2026. **BOUNDED DIAGNOSIS COMPLETE; STOP_CURRENT_ACQUISITION_THESIS.**

Read the [results](../../03_research/GOAL4R1_RESULTS_V1.md) and
[complete closeout](../../06_execution/GOAL4R1_CLOSEOUT_20261105.md).
The GP repair improves familiar-condition Greedy discovery on this exposed
development panel; incremental planning value remains unestablished.
Goal4 scientific advance remains NOT_PASSED, final design NOT_FROZEN.

## Scientific identities and results

- [Frozen protocol/source identities](protocol-freeze-v1.json), with the
  [runtime configuration](../../../research/configs/goal4r1_protocol_v1.json).
- [Reused development-input hashes](development-input-reuse-v1.json): six assays,
  four components, no new source projection or final input.
- [D1 predictor aggregates](predictor-diagnosis-v1.json) and
  [repair selection freeze](selection-freeze-v1.json).
- [Complete aggregate results](results-v1.json) and
  [32 arm/operation cells as CSV](method-cells-v1.csv).
- [Timing-only D1 allocation](diagnosis-allocation-v1.json) and
  [timing-only D2 allocation](campaign-allocation-v1.json).
- [Latest 22-test remote receipt](constructed-v2-resources.json) and
  [log](constructed-v2.log); the earlier 18-test receipt remains separately retained.

3,072 scientific campaigns plus 52 canaries and 52 reexecutions give 3,176 actual
campaign executions. All logs reconciled, with 52/52 fresh-process signatures
matching. D1 has 576 diagnostic cases plus 12 separate canaries. Seven reporting
checks ran on dr-train; one local transport-parser engineering check followed
cleanup. No new validation/final labels or plugin implementation occurred.

## Budget and preservation

- [Execution audit before preservation](execution-audit-v1.json) retains its
  historical PENDING preservation field; [final budget/closure](budget-closeout-v1.json)
  supplies the completed state.
- [Remote full snapshot](remote-full-snapshot-v1.json): 11,499 regular files,
  401,454,270 bytes, including environment, all inputs, outputs and source history.
- [Complete local reread/manifest proof](local-full-return-verification-v1.json)
  and [bounded local verification resources](local-verification-resources-v1.json).
- [Pytest alias metadata](return-preflight-v1.json) and
  [alias/empty-export completion](return-preflight-completion-v1.json).
- [Identified synthetic-fixture cleanup](remote-synthetic-fixture-cleanup-v1.json),
  [transport exception/readback](cleanup-transport-readback-v1.json) and
  [fresh remote absence](remote-absence-v1.json).

Canonical full return is ignored under
`.local/goal4r1-20261105-v1/remote-return/full-v1/`. Original archive, manifest,
raw verification receipts and every restored regular file remain there. Public
proof copies preserve parsed JSON while using LF line endings. Alias metadata
is retained; symlink replication and a fully hermetic/Windows-runnable Linux
environment are not claimed.

Preparation/preservation exceptions remain documented in the closeout. The local
cleanup reply parser failed on two JSON receipts; deletion was not retried, and
an independent fresh read-only probe established actual absence. Its engineering
regression does not count as scientific evaluation.

Application/frontend/browser suites were not rerun for this research-only change.
Agent reviews are scoped source/aggregate reviews, not external scientific
replication, human author approval or journal review.

The [package check](package-check-v1.json) verifies documentation, links and
protected historical content. Its built-in `not_run` list describes actions
outside that check, including remote Git push; it is not a current study or
publication-status ledger. Actual study evidence is listed above, and the local
delivery receipt records the separately verified main push.
