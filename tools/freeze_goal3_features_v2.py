"""Freeze owner-approved revision A after exact independent review and checks."""

import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from research.benchmark_v3.prepare_features_v2 import sha_file

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/plan-a-20261105-v1"


def main():
    config_path = ROOT / "research/configs/goal3_feature_preparation_v2.json"
    review_path = PACKET / "revision-a-static-review-v2.json"
    output = PACKET / "feature-preparation-freeze-v2.json"
    if output.exists() or (ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1/feature-cohort-v2").exists():
        raise FileExistsError("Preserve frozen/executed attempts.")
    config = json.loads(config_path.read_text())
    review = json.loads(review_path.read_text())
    if config["status"] != "DRAFT_BEFORE_CODE_REVIEW_NOT_FROZEN":
        raise ValueError("New draft required.")
    if review["status"] != "PASS_FOR_FREEZE" or sha_file(config_path) != review["draft_config_sha256"]:
        raise ValueError("Exact independent review mismatch.")
    source = "research/benchmark_v3/prepare_features_v2.py"
    if sha_file(ROOT / source) != review["preparer_sha256"]:
        raise ValueError("Reviewed preparer changed.")
    checks_path = PACKET / "revision-a-checks-v2b.json"
    checks = json.loads(checks_path.read_text())
    if checks["status"] != "PASS" or not checks["sources_unchanged"]:
        raise ValueError("Checks failed.")
    for name, digest in checks["source_sha256"].items():
        if sha_file(ROOT / name) != digest:
            raise ValueError("Tested source/config changed.")
    xml = PACKET / "revision-a-checks-v2b.xml"
    suites = list(ET.parse(xml).getroot().iter("testsuite"))
    if not suites or sum(int(s.get("tests", 0)) for s in suites) < 15 or any(
        int(s.get(key, 0)) for s in suites for key in ("failures", "errors", "skipped")
    ):
        raise ValueError("Missing passing regression evidence.")
    rights = json.loads((PACKET / "source-rights-local-use-v1.json").read_text())
    if rights["local_research_processing"] != "PASS" or rights["raw_or_row_derivative_public_git"]:
        raise ValueError("Local-use boundary unresolved.")
    if sha_file(ROOT / config["family_registry"]) != config["family_registry_sha256"]:
        raise ValueError("Registry identity changed.")
    names = [source, "tools/resource_guard_v1.py", "research/configs/goal3_feature_access_policy_v2.json"]
    identities = {name: sha_file(ROOT / name) for name in names}
    now = datetime.now(timezone.utc).isoformat()
    config.update(status="FROZEN_BEFORE_ASSAY_PARSE", frozen_utc=now,
                  frozen_source_sha256=identities,
                  parent_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip())
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8", newline="\n")
    report = {
        "status": "PASS_FROZEN_BEFORE_NEW_ASSAY_PARSE", "frozen_utc": now,
        "config_sha256": sha_file(config_path), "source_sha256": identities,
        "review_sha256": sha_file(review_path), "checks_sha256": sha_file(checks_path),
        "test_xml_sha256": sha_file(xml), "freeze_helper_sha256": sha_file(Path(__file__)),
        "parent_commit": config["parent_commit"], "previous_failed_cohort_preserved": True,
        "owner_revision": "A", "new_semantic_outcome_use": False,
    }
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
