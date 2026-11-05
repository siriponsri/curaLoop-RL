"""Close the exact evaluator/protocol gate before any new semantic outcomes."""

import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from research.benchmark_v3.prepare_features_v2 import sha_file, write_new

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/goal4-20261105-v1"


def main():
    output = PACKET / "protocol-freeze-v1.json"
    if output.exists() or (ROOT / ".local/plan-a-20261105-v2/private-inputs").exists():
        raise FileExistsError("Preserve freeze/access history.")
    config_path = ROOT / "research/configs/goal4_protocol_v1.json"
    config = json.loads(config_path.read_text())
    if config["status"] != "DRAFT_BEFORE_REVIEW_AND_FREEZE":
        raise ValueError("Fresh reviewed draft required.")
    review_path = PACKET / "evaluator-independent-review-v1.json"
    review = json.loads(review_path.read_text())
    if review["status"] != "PASS_FOR_FREEZE":
        raise ValueError("Independent gate not passed.")
    for name, digest in review["source_sha256"].items():
        if sha_file(ROOT / name) != digest:
            raise ValueError("Reviewed source changed.")
    checks_path = PACKET / "evaluator-checks-v3.json"
    checks = json.loads(checks_path.read_text())
    if checks["status"] != "PASS" or not checks["sources_unchanged"]:
        raise ValueError("Constructed checks failed.")
    for name, digest in checks["source_sha256"].items():
        if sha_file(ROOT / name) != digest:
            raise ValueError("Tested source changed.")
    suites = list(ET.parse(PACKET / "evaluator-checks-v3.xml").getroot().iter("testsuite"))
    if not suites or sum(int(s.get("tests", 0)) for s in suites) < 43 or any(
        int(s.get(key, 0)) for s in suites for key in ("failures", "errors", "skipped")
    ):
        raise ValueError("Required passing checks absent.")
    readiness = json.loads((ROOT / "docs/evidence/plan-a-20261105-v1/revision-a-feature-readback-v2.json").read_text())
    if readiness["artifact_integrity"] != "PASS" or readiness["required_group_gate"] != "PASS":
        raise ValueError("Goal3 data gate not passed.")
    if sha_file(ROOT / config["cohort_manifest"]) != config["cohort_manifest_sha256"]:
        raise ValueError("Cohort identity changed.")
    now = datetime.now(timezone.utc)
    if (datetime.fromisoformat(config["deadline_utc"]) - now).total_seconds() < 3600:
        raise ValueError("Insufficient authorized wall window for a new study.")
    config.update(status="FROZEN_BEFORE_GOAL4_OUTCOMES", frozen_utc=now.isoformat(),
                  parent_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  tested_runtime_packages=checks["packages"])
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8", newline="\n")
    doc_path = ROOT / "docs/03_research/GOAL4_PROTOCOL_V1.md"
    doc = doc_path.read_text().replace("DRAFT BEFORE EVALUATOR REVIEW/FREEZE; NO NEW LABEL USE", "FROZEN BEFORE NEW SEMANTIC OUTCOMES")
    doc_path.write_text(doc, encoding="utf-8", newline="\n")
    identities = {name: sha_file(ROOT / name) for name in checks["source_sha256"] if name != "research/configs/goal4_protocol_v1.json"}
    identities["tools/freeze_goal4_protocol_v1.py"] = sha_file(Path(__file__))
    for name in ("docs/03_research/GOAL4_PROTOCOL_V1.md", "docs/evidence/plan-a-20261105-v1/feature-cohort-v2-result.json"):
        identities[name] = sha_file(ROOT / name)
    write_new(output, {"status": "PASS_FROZEN_BEFORE_NEW_SEMANTIC_OUTCOMES", "frozen_utc": now.isoformat(),
              "protocol_sha256": sha_file(config_path), "source_sha256": identities,
              "review_sha256": sha_file(review_path), "checks_sha256": sha_file(checks_path),
              "cohort_manifest_sha256": config["cohort_manifest_sha256"],
              "parent_commit": config["parent_commit"], "new_real_outcome_use_before_freeze": False,
              "final_outcome_use_authorized": False})
    print(json.dumps({"status": "PASS_FROZEN", "protocol_sha256": sha_file(config_path), "source_files": len(identities)}))


if __name__ == "__main__":
    main()
