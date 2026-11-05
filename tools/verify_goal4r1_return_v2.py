"""Add a verified unchanged-manifest proof without rewriting the v1 receipt."""

import argparse
import hashlib
import json
import time
from pathlib import Path

from tools import verify_goal4r1_return_v1 as base


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=Path, required=True)
    args = parser.parse_args()
    folder = args.folder.resolve(strict=True)
    allowed = (base.ROOT / ".local/goal4r1-20261105-v1/remote-return").resolve()
    if not allowed.is_relative_to(base.ROOT.resolve()) or not folder.is_relative_to(allowed):
        raise ValueError("Return folder must remain in the explicit local retention tree.")
    enhanced = folder / "local-verification-with-manifest.json"
    if enhanced.exists():
        raise FileExistsError("Preserve the existing enhanced verification receipt.")
    manifest = folder / "manifest.json"
    if manifest.stat().st_size > 50 * 1024**2:
        raise ValueError("Manifest exceeds verification bound.")
    before = manifest.read_bytes()
    digest = hashlib.sha256(before).hexdigest()
    source_hash = base.sha(Path(base.__file__))
    started, cpu = time.perf_counter(), time.process_time()
    # Existing verifier checks archive checksum, every member, and a complete
    # re-read of all restored bytes. Its original PASS remains unchanged.
    base.main()
    original = folder / "local-verification.json"
    receipt = json.loads(original.read_text())
    if (
        receipt["status"] != "PASS_LOCAL_ALL_FILES_VERIFIED"
        or manifest.read_bytes() != before
        or base.sha(folder / "task.zip") != receipt["zip_sha256"]
        or base.sha(Path(base.__file__)) != source_hash
    ):
        raise ValueError("Manifest/archive/verifier changed during complete verification.")
    report = {
        **receipt,
        "schema_version": "curaloop.remote-return.manifest-proof.v2",
        "manifest_sha256": digest,
        "manifest_unchanged_during_verification": True,
        "base_verifier_sha256": source_hash,
        "base_receipt_sha256": base.sha(original),
        "enhanced_verifier_sha256": base.sha(Path(__file__)),
        "verification_wall_seconds": time.perf_counter() - started,
        "verification_cpu_seconds": time.process_time() - cpu,
    }
    with enhanced.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
