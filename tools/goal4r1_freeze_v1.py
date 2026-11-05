"""Freeze new scientific sources after remote constructed checks, before D1."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    packet = ROOT / "docs/evidence/goal4r1-20261105-v1"
    path = ROOT / "research/configs/goal4r1_protocol_v1.json"
    proof = packet / "protocol-freeze-v1.json"
    if proof.exists():
        raise FileExistsError("Do not refreeze evaluated scientific sources.")
    check = json.loads((packet / "constructed-v2-resources.json").read_text())
    setup = json.loads((packet / "remote-install-v1.json").read_text())
    if check["status"] != "PASS" or check["pytest_exit_code"] != 0 or setup["status"] != "PASS":
        raise ValueError("Remote constructed/environment gates not passed.")
    tested = json.loads((ROOT / ".local/goal4r1-20261105-v1/bootstrap-v4.json").read_text())
    frozen_old = json.loads((ROOT / "docs/evidence/goal4-20261105-v1/protocol-freeze-v1.json").read_text())["source_sha256"]
    sources = {}
    for item in tested["files"]:
        name = item["path"]
        if name == "research/configs/goal4r1_protocol_v1.json":
            continue
        if sha(ROOT / name) != item["sha256"]:
            raise ValueError("Source changed since remote constructed check.")
        if name in frozen_old and item["sha256"] != frozen_old[name]:
            raise ValueError("Historical frozen source changed.")
        sources[name] = item["sha256"]
    config = json.loads(path.read_text())
    if config["status"] != "DRAFT_D0_CHECKS_PENDING":
        raise ValueError("Invalid draft state.")
    config["status"] = "FROZEN_BEFORE_NEW_CODE_EVALUATION"
    config["frozen_utc"] = datetime.now(timezone.utc).isoformat()
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    report = {"status": "PASS_D0_FREEZE_BEFORE_DEVELOPMENT_EVALUATION",
              "frozen_utc": config["frozen_utc"], "protocol_sha256": sha(path), "source_sha256": sources,
              "constructed_checks": {"host": "dr-train", "tests": 22, "status": "PASS",
                                      "receipt_sha256": sha(packet / "constructed-v2-resources.json")},
              "prior_setup_actual_cpu_seconds": setup["cpu_seconds"],
              "setup_aggregate_watchdog_was_implemented": False,
              "setup_actual_compliance_not_a_hard_aggregate_limit_claim": True,
              "final_outcomes_prepared": False, "permitted_outcome_roles": ["development"]}
    with proof.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(json.dumps({k: v for k, v in report.items() if k != "source_sha256"}, indent=2))


if __name__ == "__main__":
    main()
