# LR-DC2 dataset checkpoint and owner pause

Prepared 11 November 2026. Status: **OWNER_PAUSE_REQUESTED / ARCHIVE_DOWNLOADED_AND_QUARANTINED**.
This is an intake checkpoint, not a passed research gate or a completed goal.
The owner asked to finish the dataset download, pause for work on other projects,
and start the seven-day research clock only on the next explicit owner resume.

## Exact current state

- Original source/release base: main4247a2c63c6eaf32c87028738282888c8ef52791.
- Annotation: official ScienceAgentBench **verified**,102 rows, HF revision
  `9c6e96c9e74572e979b0930ee735041cef528cb7`. Structural metadata only was read.
- Archive status: **PASS_COMPLETE_OFFICIAL_ARCHIVE_RECEIPT_QUARANTINED_NOT_EXTRACTION_ADMITTED**.
- Bytes received: **1,769,478,786**.
- Archive SHA-256: `46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
- Archive location: `research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip`. Large benchmark files are ignored/private;
  they must not be added to Git or redistributed as an unzipped archive.
- Files remain quarantined. No extraction, full encrypted-member CRC test,
  reference-solution execution, labels, scoring gold or candidate evaluation.
- Declared whole-archive expanded bytes: **4071815117**.
  Whole-archive extraction within12 GiB: **True**.
  The initial whole-file hash reread and its first followup failed under the
  one-GiB guard; both failures remain retained. Streaming hash verification
  now rereads the same bytes without a network retry or a memory-limit change.
  Byte receipt is complete; cohort/full extraction is not admitted. After resume,
  assess whether a qualified selected subset can fit the unchanged12 GiB cap;
  full extraction beyond that cap requires a new owner decision. Neither path
  is run during this pause checkpoint.
- The directory/expanded-size check uses ZIP metadata, not a full CRC/decryption
  check. A local reread hash establishes the retained byte identity; no separate
  publisher-signed checksum was supplied or claimed.
- No SSH connection, remote root, GPU allocation, model download or inference
  was started in LR-DC2. Shared dr-train services/cache remain untouched.

The ordinary HTTP archive probe failed403 and remains evidence. A fresh anonymous
headless browser observed the official `benchmark_verified.zip` download. The
separate bounded browser transfer receipt records its initial reread failure;
the versioned byte-receipt followup records actual completion. An earlier
browser-link observation alone is not called a completed dataset download.

## Resources and the owner's clock amendment

The original immutable release records07:39 UTC11 November as its initial
admission timestamp and its original deadline. **That evaluation deadline is
superseded by the explicit owner clock amendment**, retained separately in
`research/manifests/lr_dc2_owner_clock_amendment_20261111_v1.json` and the public
`owner-clock-amendment-v1.json` receipt. Do not edit the original release bytes.

The effective seven-day evaluation clock is **AWAITING_OWNER_RESUME**, with no
new start/deadline assigned. On the next explicit owner resume, record the first
trusted UTC time and set the effective deadline to that time plus168 hours.
The ceiling remains64 CPU-hours +24 allocated GPU-hours, max four CPU cores and
one GPU worker. Every pre-pause booking/failed attempt/download and any unknown
administrative overhead allowance stays charged; no CPU/GPU budget reset.
`owner-pause-v1.json` records the settled paused-ledger identity and retained
allocation after the last intake/handoff job exits.

## Research gates still open

Gate0 contribution distinction is **INCOMPLETE_NOT_ADJUDICATED**. Initial related
work searches are not a novelty PASS. Gate1 cohort/rights/oracle qualification
is **NOT_ADMITTED**. The annotation has20 Computational Chemistry and27
Bioinformatics rows, but these counts do not establish40 usable tasks, the
required publication/data-lineage split,16 molecular locked tasks or native
programmatic scoring without paid judges. Do not infer readiness from raw counts.

GPU identity/free availability, native reference feasibility, fixed development,
source/protocol freeze, all816 model missions, analysis, new product integration
and a new manuscript are **NOT_RUN**. No method effect or journal readiness is
claimed. Preserve the previous AgentRD report and every earlier negative result.

## Resume procedure

1. Wait for an explicit owner `resume LR-DC2`. Dataset placement/readiness alone
   does not release experiments. The goal/account are paused, not completed.
2. Read this handoff, the owner amendment, release, paused ledger and final
   main-delivery record. Verify all15 prior ledger identities,66 old scientific
   pins,27 AgentRD frozen pins and947 prior AgentRD artifact identities.
3. Record the new effective168-hour clock exactly once under the owner amendment;
   retain every existing booking and cap. Update ACTIVE authority to use that
   effective deadline, rather than reopening or rewriting the original clock.
4. If archive readiness above is PASS, reread the exact retained ZIP hash and reuse
   it. Do not download again or interpret it as an admitted cohort. Otherwise
   inspect the preserved transfer receipt/partial bytes and resolve the stated
   access/size/transfer problem before further intake; no silent replacement.
5. Resume contribution/data/GPU admission under the unchanged approved proposal.
   Keep gold/reference files in the separate evaluator, unavailable to generators.
   Stop/report the first actual failed gate; no model/data substitutions or
   outcome-driven retries. Any required rights/budget/scope change goes to owner.
6. Only after passed gates proceed through the frozen study, complete reporting,
   full owned remote return/reread/exact cleanup and authorized main commit/push.

Original final16, private CF1 rows and hidden outcomes remain closed. No paid
API/GPU rental, public deployment, external team writes or journal submission.
The source snapshot proposal/config stays disabled historical planning material;
the separate release and owner amendment are the actual authority records.
