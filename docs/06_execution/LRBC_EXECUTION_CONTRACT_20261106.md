# LR-BC execution contract

6 November 2026. **OWNER_APPROVED; ACTIVE_R0.**

The owner selected “Approve LR-BC as recommended” in response to the explicit
approval question referencing proposal commit
`f1f31723014005e555e9e0ae1603671aeb0242da`. That immutable
[proposal](PARALLEL_LONG_RUN_PROPOSAL_20261106.md) defines scope and exclusions.
This contract starts its R0 stage; it does not declare data/pilot/C gates passed.

## Clocks and cumulative budget

- Recorded R0 start: 2026-11-06T09:46:22Z / 16:46:22 Bangkok.
- R0 deadline: 2026-11-06T17:46:22Z / 7 November 00:46:22 Bangkok.
- B deadline remains 2026-11-09T05:13:23Z / 12:13:23 Bangkok.
- B+C deadline remains 2026-11-13T05:13:23Z; C also ends by its recorded
  release plus 96 elapsed hours. No automatic clock restart.
- Historical A3 conservative charge: 19,800 CPU-seconds / 5.5 CPU-hours.
- Remaining B: 153,000 CPU-seconds / 42.5 CPU-hours. R0 14,400; R1 21,600;
  one pilot 72,000; robustness 28,800; report/return 14,400; contingency 1,800.
- C increment at most 172,800 CPU-seconds only after POTENTIAL_SUFFICIENT;
  combined cumulative B+C at most 345,600 CPU-seconds / 96 CPU-hours.

R0 holds a 1,800 CPU-second utility/preparation reserve. Every initial worker
launch retains a 900 CPU-second reservation; at most fourteen R0 launches fit
the remaining 12,600 seconds. A failed/ambiguous launch keeps its reservation.
Worker guard limits are below that reservation, with explicit wall limits of
at most 1,800 seconds and the absolute R0 deadline. Setup, processing, transport,
verification and preservation remain within the declared stage allowances.

## Cross-host execution

At most four project CPU workers combined. Default one local and three remote;
remote four only while no local worker occupies a slot. A new coordinator leases
distinct CPU IDs and retains durable reservations before dispatch. The frozen
A3 serial launcher is not reused as a parallel launcher.

Local jobs start at one CPU/512 MiB. Above 512 MiB requires a native canary and
at least 4 GiB available at admission; 1 GiB is the hard approved local maximum.
Pause heavy local launches below 1.5 GiB available. Remote jobs use one CPU,
single numerical threads, nice19 and at most4GiB. All CPU-heavy preservation
and verification jobs also occupy coordinator slots. Shared host capacity is
checked at launch and is not an exclusive reservation.

Use fresh owned `/home/chaw/curaloop-rl/lrbc-20261106-v1` and the exact corresponding
export sibling; local private retention is `.local/lrbc-20261106-v1/`.
Never recreate a closed A3/PlanA/4R1/A2 root or modify unrelated files/config/keys.
Parent is sole writer/integrator; specialists inspect read-only. Workers write
disjoint immutable attempt outputs. New source versions are separate immutable
bundles; do not overwrite sources used by an active worker.

## R0 work released now

1. Freeze coordinator/resource cases, build the new bounded cross-host runner
   and test it using synthetic fixtures before any scientific batch.
2. Reuse hash-bound A3 metadata and the already development-exposed first canary
   for value-free ID/readout-presence diagnostics. Do not emit activity values.
3. Review published/source endpoint semantics, target/family/exposure coverage,
   intended-use evidence, novelty and the next observable population.
4. Develop the shared typed-tool/evidence/plan/report interface and a proposed
   real-source workflow evaluation independently of a blocked molecular branch.

R0 opens no new activity source. The old source STOP and NO_GO stay immutable.
All FS-Mol final outcomes remain reserved; feature-only identities retain their
roles. Existing public metadata/source review does not authorize row publication
or commercial reuse. New protected aliases must remain excluded before outcomes.

## Later release and decisions

R1 needs a source/rights/endpoint/population/protection review and a frozen exact
limited request plan. Its start and twelve-hour subdeadline are recorded only
on release, within B's absolute deadline. New source attempts explicitly reference
the old failure and authorization; never clear the old ledger to resume intake.
Inherited intake charges are24/96PUG,27/32UniProt and28,715,980/268,435,456 decoded
bytes. At most64 additional non-PUG/non-UniProt official NCBI protein/document/schema
metadata calls are permitted, with field/endpoint rosters frozen before dispatch.
All new intake bytes share the cumulative ceiling and16MiB response maximum.
No bulk fallback or automatic retry of stopped403/429/schema-denied requests.

Pilot fitting/evaluation needs a frozen outcome, estimand, independent units,
source/exposure identities, strong controls and at most two prespecified variants
plus an unchanged anchor. Retain effects/uncertainty and failures; no new material
effect/significance threshold. C release requires the standing five potential
gates on real-source capability, comparison, intended use and reproducibility.

Routine source-defined implementation and gate-based progression may continue
without another routine permission request. Consult the owner before unresolved
material endpoint/replicate/phenotype/population changes, rights, larger limits,
uncertain potential, final-label release, new paid service, live team write or
journal action. Continue independent work when a dependent branch is blocked.

## Closeout

Return every owned remote code/input/data/output/dependency/evidence file and
completely reread/hash-verify the local reconstruction before exact scoped
deletion. Obtain fresh absence. Keep raw activity/private inputs outside Git;
publish source, safe aggregates and English reports. Normal main push and live
readback remain authorized. Completion requires an honest B potential decision
and conditional C deliverables or a documented stop; no favorable result promised.
