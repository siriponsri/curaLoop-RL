# M2 execution evidence, 8 November 2026

**INCOMPLETE_AT_RESOURCE_CHECKPOINT.** One synthetic configuration attempted
twice; zero completed calibration campaigns and zero molecular campaigns. The
second attempt provides a valid cap lower bound above the original admission
ceiling. The first is retained with an explicit invalidity annotation.

Read [results](../../03_research/M2_PREFLIGHT_RESULTS_20261108.md),
[owner decision](../../06_execution/M2_RESOURCE_OWNER_CHECKPOINT_20261108.md) and
[approved original plan](../../06_execution/M2_EXPERIMENT_PLAN_20261108.md).

This directory contains aggregate metadata and engineering/resource receipts.
Complete private code/dependency/permit/log return is retained in
`.local/m2-selective-compute-20261108-v1/remote-return/`. No structures, fingerprints,
biological labels, compound-level histories or third-party dependency payloads
are redistributed here. No biological-label payload was decoded or sent to dr-train.

Key receipts, produced during closeout:

- `data-admission-v1.json`: six input/feature identities, protected-identity checks
  and outcome-blind training-mask coverage.
- `constructed-checks-v1.json`: 12 constructed checks of the admitted predictors/planner.
- `synthetic-admission-summary-v1.json`: both timing attempts, timer invalidity,
  validated resource-fit stop and NOT_RUN scientific stages.
- `ledger-checkpoint-v1.json`: conservative reservations, failed attempts and
  separately measured worker CPU; utility envelopes are not measured CPU.
- `old-history-unchanged-v1.json`: hashes of prior ledgers and frozen M1 code.
- `complete-return-verified-v1.json`: every remote task regular file plus exact
  export files authenticated and reread locally before deletion.
- `scoped-delete-v1.json` and `fresh-absence-v1.json`: exact owned task/export
  cleanup only after verified return, followed by a fresh absence check.
- `delivery-validation-v1.json`: source/config/link/language/checkpoint audit;
  does not establish molecular utility or publication readiness.
- `blocked-reservation-check-v1.json`: a new scientific reservation was actually
  rejected after the resource stop, with no ledger change or dispatched unit.

Failed and censored synthetic attempts are preserved. Passing engineering checks
do not promote the unexecuted learned gate or scientific comparisons to PASS.
