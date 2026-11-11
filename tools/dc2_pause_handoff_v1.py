"""Prepare and record an owner-requested pause after bounded dataset intake."""

import json
import sys
from datetime import datetime, timezone

from dc2_admin_v1 import PUBLIC, ROOT, TASK, preserve, read, save, sha, write


def prepare():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    preserve(release)
    assert ledger["owner_scope_mode"] == "DATASET_INTAKE_THEN_PAUSE"
    assert ledger["evaluation_clock_state"] == "AWAITING_OWNER_RESUME"
    annotation = read(PUBLIC / "dataset-annotation-intake-v1.json")
    archive_path = PUBLIC / "dataset-archive-receipt-v2.json"
    if not archive_path.exists():
        archive_path = PUBLIC / "dataset-archive-intake-v1.json"
    archive = read(archive_path)
    ready = archive["status"] in (
        "PASS_OFFICIAL_ARCHIVE_DOWNLOADED_HASH_REREAD_AND_DIRECTORY_CHECKED",
        "PASS_COMPLETE_OFFICIAL_ARCHIVE_RECEIPT_QUARANTINED_NOT_EXTRACTION_ADMITTED")
    if ready:
        assert sha(ROOT / archive["relative_path"]) == archive["sha256"]
        assert (ROOT / archive["relative_path"]).stat().st_size == archive["bytes_received"]
    for name, capture in annotation["captures"].items():
        assert sha(TASK / "dataset-intake-v1" / name) == capture["sha256"]
    metadata = {"status": "PASS_AUTHOR_DATASET_PAUSE_HANDOFF_PREPARED", "dataset_archive_ready": ready,
        "archive_status": archive["status"], "archive_sha256": archive.get("sha256"),
        "archive_bytes": archive["bytes_received"], "archive_receipt": archive_path.name,
        "full_extraction_within_12_gib": archive.get("full_extraction_within_12_gib"),
        "declared_expanded_bytes": archive.get("declared_expanded_bytes"), "annotation_rows": annotation["rows"],
        "annotation_hf_revision": annotation["hf_revision"], "source_members_extracted": False,
        "full_crc_decompression": "NOT_RUN", "native_gold_or_labels_opened": False,
        "new_model_downloads": 0, "model_inference_calls": 0, "gpu_allocated_seconds": 0,
        "remote_task_root_created": False, "ssh_connection_started": False,
        "gate0_contribution": "INCOMPLETE_NOT_ADJUDICATED", "gate1_cohort": "NOT_ADMITTED",
        "development_and_locked_evaluation": "NOT_RUN", "original_protected_data_access": False,
        "owner_resume_required": True, "evaluation_clock_state": "AWAITING_OWNER_RESUME",
        "elapsed_hours_after_next_owner_resume": 168, "cpu_gpu_budget_reset": False,
        "prior_ledgers_preserved": len(release["prior_ledger_pins"]),
        "prior_agent_rd_artifacts_preserved": len(release["prior_agent_rd_artifact_pins"])}
    write(PUBLIC / "dataset-pause-preparation-v1.json", metadata)
    state = "ARCHIVE_DOWNLOADED_AND_QUARANTINED" if ready else "ARCHIVE_TRANSFER_PENDING_OR_FAILED"
    location = archive.get("relative_path", "research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip.part")
    text = f"""# LR-DC2 dataset checkpoint and owner pause

Prepared 11 November 2026. Status: **OWNER_PAUSE_REQUESTED / {state}**.
This is an intake checkpoint, not a passed research gate or a completed goal.
The owner asked to finish the dataset download, pause for work on other projects,
and start the seven-day research clock only on the next explicit owner resume.

## Exact current state

- Original source/release base: main4247a2c63c6eaf32c87028738282888c8ef52791.
- Annotation: official ScienceAgentBench **verified**,102 rows, HF revision
  `{annotation['hf_revision']}`. Structural metadata only was read.
- Archive status: **{archive['status']}**.
- Bytes received: **{archive['bytes_received']:,}**.
- Archive SHA-256: `{archive.get('sha256', 'NOT_VERIFIED_COMPLETE')}`.
- Archive location: `{location}`. Large benchmark files are ignored/private;
  they must not be added to Git or redistributed as an unzipped archive.
- Files remain quarantined. No extraction, full encrypted-member CRC test,
  reference-solution execution, labels, scoring gold or candidate evaluation.
- Declared whole-archive expanded bytes: **{archive.get('declared_expanded_bytes', 'NOT_VERIFIED')}**.
  Whole-archive extraction within12 GiB: **{archive.get('full_extraction_within_12_gib', 'NOT_VERIFIED')}**.
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
"""
    target = ROOT / "docs/08_agent_rd/LR_DC2_DATASET_PAUSE_HANDOFF_20261111.md"
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    print(json.dumps(metadata))


def pause():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    preserve(release)
    assert not any(b["status"] == "RESERVED" for b in ledger["bookings"].values())
    prepared = read(PUBLIC / "dataset-pause-preparation-v1.json")
    ledger.update(status="PAUSED_OWNER_REQUEST", paused_utc=datetime.now(timezone.utc).isoformat(),
                  dataset_archive_ready=prepared["dataset_archive_ready"],
                  owner_scope_mode="WAIT_FOR_EXPLICIT_OWNER_RESUME", evaluation_clock_state="AWAITING_OWNER_RESUME",
                  effective_resume_start_utc=None, effective_resume_deadline_utc=None)
    save(ledger)
    measured = 0
    jobs = {}
    for name, booking in ledger["bookings"].items():
        resource = TASK / "jobs" / name / "resource.json"
        if resource.exists():
            value = read(resource)
            measured += value["aggregate_cpu_seconds"]
            jobs[name] = {"status": booking["status"], "resource_sha256": sha(resource),
                          "observed_cpu_seconds": value["aggregate_cpu_seconds"], "retained_cpu_seconds": booking["cpu_cap"]}
    receipt = {"status": "PAUSED_OWNER_REQUEST", "paused_utc": ledger["paused_utc"],
        "dataset_archive_ready": prepared["dataset_archive_ready"], "evaluation_clock_state": "AWAITING_OWNER_RESUME",
        "effective_resume_start_utc": None, "effective_resume_deadline_utc": None,
        "hours_from_next_explicit_owner_resume": 168, "cpu_gpu_budget_reset": False,
        "retained_cpu_seconds": sum(ledger["retained_cpu_seconds"].values()),
        "observed_guarded_job_cpu_seconds": measured, "administrative_cpu_separately_metered": False,
        "retained_gpu_seconds": sum(ledger["retained_gpu_seconds"].values()),
        "authorized_cpu_seconds": release["cpu_cap_seconds"], "authorized_gpu_seconds": release["gpu_allocated_cap_seconds"],
        "downloads_bytes": ledger["downloads_bytes"], "all_started_jobs_settled": True,
        "model_calls": ledger["model_calls"], "ledger_sha256": sha(TASK / "ledger.json"),
        "handoff_sha256": sha(ROOT / "docs/08_agent_rd/LR_DC2_DATASET_PAUSE_HANDOFF_20261111.md"),
        "guarded_jobs": jobs, "prior_ledgers_preserved": len(release["prior_ledger_pins"])}
    write(PUBLIC / "owner-pause-v1.json", receipt)
    print(json.dumps({key: receipt[key] for key in ("status", "dataset_archive_ready", "retained_cpu_seconds", "retained_gpu_seconds", "observed_guarded_job_cpu_seconds")}))


if __name__ == "__main__":
    assert sys.argv[1] in ("prepare", "pause")
    {"prepare": prepare, "pause": pause}[sys.argv[1]]()
