# Goal 4R2-A3 closeout

6 November 2026. **QUALIFICATION COMPLETE; PILOT NO_GO; RETURN/CLEANUP VERIFIED.**

Read the [qualification report](../03_research/GOAL4R2A3_QUALIFICATION_V1.md),
[execution contract](PLAN_B_EXECUTION_CONTRACT_20261106.md) and
[evidence](../evidence/goal4r2a3-20261106-v1/README.md).
Base main was `f548634cb6ac283ed92772e62fc04956094551ae`.

## Completed scope

- Inspected 60 script bodies and 105 AID metadata records: 53 exact bindings,
  95 programme-supported AIDs and 47 jointly supported/bound pairs.
- Preserved final-feature identities: 4,723 structures, 14 groups and 42 proteins,
  without opening FS-Mol final outcomes.
- Reconciled 27 cached protein responses without refetch: five pairs, four broad
  annotations, one exposed conservative component.
- Qualified 640 outcome-blind SID samples: 589 cleared, 45 ambiguous/missing CID
  and six protected sampled-SID matches excluded without replacement.
- Preserved a live canary failure despite HTTP 200. Native-envelope mismatch
  stopped intake before readout interpretation; no further request occurred.
- Added a reviewed offline adapter: 16 primary rows, 16 numeric cells, 16 missing
  cells, zero complete selected tuples. Paired qualification and campaigns NOT_RUN.
- Passed 29 distinct engineering cases in 32 executions; retained source versions,
  the initial failure and unexecuted preparation variants.

## Budget and window

B starts 6 November 05:13:23 UTC / 12:13:23 Bangkok and ends no later than
9 November at the same time, within 48 CPU-hours/four workers. A3 has a
16 CPU-hour/two-worker cap and a 7 November deadline at the same time. All seven
jobs were serialized one-CPU workers on dr-train.

The conservative charge is **5.5 CPU-hours**: seven 1,800-second launch reservations
plus a 7,200-second utility/preservation reserve. Measured worker CPU and preservation
resources are separate; this is not exhaustive shared-host CPU accounting.
No new paid service or GPU was used. Cumulative source charges: 27 UniProt and
24 PubChem requests, including the single observation canary, and 28,715,980 decoded
bytes. No quota or stopped-service state was reset for the offline adapter.

## Preservation and delivery

All 1,963 files / 689,826,056 bytes were downloaded, extracted and completely
reread/hash-verified before the exact owned task/export roots were deleted.
Fresh absence was confirmed at 07:23:26.859914 UTC / 14:23:26.859914 Bangkok.
The unchanged-manifest proof was acknowledged before deletion; both cleanup
JSON receipts are retained. See [complete verification](../evidence/goal4r2a3-20261106-v1/local-verification-v2.json),
[cleanup](../evidence/goal4r2a3-20261106-v1/remote-delete-v1.json) and
[fresh absence](../evidence/goal4r2a3-20261106-v1/remote-absence-v1.json).
Private retention: `.local/goal4r2a3-20261106-v1/remote-return/full-v1/`.
Raw observations, protected identities, source responses and native dependencies
stay outside public Git. Public delivery contains source, contracts, safe aggregate
evidence and English documentation.

Measured remote worker CPU: 16.217561931 seconds. Snapshot-process CPU:
23.898796408 seconds. The inner enhanced verifier used 21.671875 CPU-seconds
and 91.722826 wall-seconds; these do not measure all preparation/transport work.
The [budget receipt](../evidence/goal4r2a3-20261106-v1/budget-closeout-v1.json)
retains the full 5.5-hour conservative charge, including utility reserves.

Normal main commit/push remains authorized. The ignored final delivery receipt
will record HEAD, origin/main and live remote readback; no commit is claimed here
before that evidence exists.

## Review before the next stage

The selected A3-to-pilot checkpoint is reached. Scientific advancement is NO_GO;
this does not establish that MF-PCBA or the broader direction has no potential.
Endpoint completeness, paired coverage, historical row equivalence, independent
family coverage and method novelty remain unresolved.

Review an endpoint/provenance repair proposal and a source/family expansion plan
before freezing a pilot. Begin with metadata and value-free diagnostics, retaining
the original population and failures. Revised endpoints or new intake need a new
versioned contract and inherited charges. Do not restart the stopped source,
recreate closed roots, expose final outcomes, spend the pilot allocation or trigger
C automatically. Conditional C authority remains available only after B demonstrates
sufficient potential; that verdict has not been established.
