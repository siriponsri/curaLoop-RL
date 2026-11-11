"""Verify dataset receipt, controller code and preservation before owner pause."""

import subprocess
import sys

from dc2_admin_v1 import PUBLIC, ROOT, TASK, preserve, read, sha, write
from dc2_pause_handoff_v1 import prepare


def main():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    preserve(release)
    assert sha(TASK / "release.json") == sha(ROOT / "research/manifests/lr_dc2_release_20261111_v1.json")
    assert sha(PUBLIC / "owner-clock-amendment-v1.json") == ledger["clock_amendment_sha256"]
    assert sum(ledger["retained_cpu_seconds"].values()) <= release["cpu_cap_seconds"]
    assert sum(ledger["retained_gpu_seconds"].values()) == 0
    assert ledger["model_calls"] == ledger["generated_tokens"] == 0
    paths = [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "tools").glob("dc2_*.py"))]
    result = subprocess.run([sys.executable, "-m", "ruff", "check", *paths], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    proposal = read(ROOT / "research/configs/lr_dc2_proposal_20261111_v1.json")
    assert proposal["execution_enabled"] is False and proposal["owner_approved"] is False
    assert ledger["evaluation_clock_state"] == "AWAITING_OWNER_RESUME"
    annotation = read(PUBLIC / "dataset-annotation-intake-v1.json")
    archive_path = PUBLIC / "dataset-archive-receipt-v2.json"
    if not archive_path.exists():
        archive_path = PUBLIC / "dataset-archive-intake-v1.json"
    archive = read(archive_path)
    assert annotation["rows"] == 102 and annotation["split"] == "verified"
    assert ledger["downloads_bytes"] == sum(v["bytes"] for v in annotation["captures"].values()) + archive["bytes_received"]
    write(PUBLIC / "pause-checks-v1.json", {
        "status": "PASS_DATASET_CHECKPOINT_CODE_CLOCK_BUDGET_AND_PRIOR_PRESERVATION",
        "checked_controller_source_pins": {path: sha(ROOT / path) for path in paths},
        "old_ledger_pins_preserved": len(release["prior_ledger_pins"]),
        "old_scientific_pins_preserved": len(release["old_scientific_pins"]),
        "agent_rd_frozen_pins_preserved": len(release["agent_rd_frozen_pins"]),
        "prior_agent_rd_artifacts_preserved": len(release["prior_agent_rd_artifact_pins"]),
        "immutable_proposal_preserved": True, "new_owner_release_and_amendment_are_authority": True,
        "clock_starts_on_next_owner_resume": True, "new_inference": False,
        "download_accounting_scope": "Persisted annotation/metadata bodies and streamed archive payload; protocol/browser-navigation overhead is not byte-metered",
        "dataset_archive_status": archive["status"]})
    prepare()


if __name__ == "__main__":
    main()
