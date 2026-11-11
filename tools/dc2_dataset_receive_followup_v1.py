"""Verify the complete retained archive with the corrected streaming hash."""

import json
import os
import zipfile
from datetime import datetime, timezone

from dc2_admin_v1 import PUBLIC, ROOT, authority, read, sha, write


def main():
    authority()
    previous = read(PUBLIC / "dataset-archive-intake-v1.json")
    assert previous["status"] == "FAIL_BOUNDED_ARCHIVE_TRANSFER_OR_STRUCTURE_CHECK"
    assert previous["bytes_received"] == previous["declared_content_length"] > 0
    folder = ROOT / "research/raw_data/external-benchmarks/scienceagentbench-verified-20260430"
    source, target = folder / "benchmark_verified.zip.part", folder / "benchmark_verified.zip"
    assert source.resolve().parent == target.resolve().parent == folder.resolve()
    assert folder.resolve().is_relative_to((ROOT / "research/raw_data").resolve())
    assert source.is_file() and not target.exists()
    assert source.stat().st_size == previous["bytes_received"]
    identity = sha(source)
    with zipfile.ZipFile(source) as archive:
        members = archive.infolist()
        expanded = sum(member.file_size for member in members)
        unsafe = [m.filename for m in members if m.filename.startswith(("/", "\\")) or
                  ".." in m.filename.replace("\\", "/").split("/")]
        encrypted = sum(bool(m.flag_bits & 1) for m in members)
        directories = [{"name": m.filename, "bytes": m.file_size, "compressed_bytes": m.compress_size,
                        "crc32": m.CRC, "encrypted": bool(m.flag_bits & 1)} for m in members]
    assert not unsafe, "Unsafe member names; preserve quarantine, do not extract"
    # Exact file move within the checked task-owned directory, no overwrite,
    # extraction, deletion or change to the downloaded bytes.
    os.rename(source, target)
    assert sha(target) == identity
    private = ROOT / ".local/lr-dc2-20261111-v1/dataset-intake-v1"
    write(private / "archive-directory-v2.json", directories)
    receipt = {"status": "PASS_COMPLETE_OFFICIAL_ARCHIVE_RECEIPT_QUARANTINED_NOT_EXTRACTION_ADMITTED",
        "utc": datetime.now(timezone.utc).isoformat(), "relative_path": target.relative_to(ROOT).as_posix(),
        "bytes_received": previous["bytes_received"], "declared_content_length": previous["declared_content_length"],
        "sha256": identity, "full_archive_downloaded": True, "complete_local_reread": True,
        "member_count": len(members), "declared_expanded_bytes": expanded, "encrypted_member_count": encrypted,
        "full_extraction_within_12_gib": expanded <= 12 * 1024 ** 3,
        "archive_extracted": False, "expanded_bytes_written": 0,
        "full_extraction_size_gate": "PASS_DECLARED_SIZE_ONLY" if expanded <= 12 * 1024 ** 3 else "FAIL_DECLARED_EXPANDED_SIZE_EXCEEDS_12_GIB",
        "cohort_or_native_evaluation_admission": "NOT_RUN_BEFORE_OWNER_RESUME",
        "v1_failure_receipt_sha256": sha(PUBLIC / "dataset-archive-intake-v1.json"),
        "v1_failure_preserved": True,
        "v1_diagnostic": "Byte transfer completed; whole-file read_bytes hashing exceeded the one-GiB local guard. The first controlled followup raised MemoryError at that helper. Streaming hashlib.file_digest now verifies the same retained bytes without more memory or a network retry.",
        "streaming_hash_controller_sha256": sha(ROOT / "tools/dc2_admin_v1.py"),
        "failed_followup_resource_sha256": sha(ROOT / ".local/lr-dc2-20261111-v1/jobs/dataset-receipt-followup-v1/resource.json"),
        "rename": {"from": source.relative_to(ROOT).as_posix(), "to": target.relative_to(ROOT).as_posix(), "bytes_changed": False},
        "native_gold_or_activity_values_opened": False, "full_crc_decompression": "NOT_RUN",
        "new_archive_download_or_retry": False, "new_model_calls": 0, "gpu_allocated_seconds": 0,
        "resume_requirement": "Keep archive quarantined until explicit owner resume. If full expanded size exceeds twelve GiB, require a qualified subset within the existing cap or an explicit owner scope decision; never auto-expand or claim cohort admission."}
    write(PUBLIC / "dataset-archive-receipt-v2.json", receipt)
    print(json.dumps({key: receipt[key] for key in ("status", "bytes_received", "sha256", "member_count", "declared_expanded_bytes", "full_extraction_within_12_gib")}))


if __name__ == "__main__":
    main()
