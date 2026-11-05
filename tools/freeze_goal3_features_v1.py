"""Freeze reviewed outcome-independent preparation inputs before archive rows."""

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/plan-a-20261105-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = PACKET / "feature-preparation-freeze-v1.json"
    config_path = ROOT / "research/configs/goal3_feature_preparation_v1.json"
    if output.exists():
        raise FileExistsError(output)
    review = json.loads((PACKET / "family-and-preparation-review.json").read_text())
    if (
        review["preparer_static_verdict"] != "PASS_FOR_FREEZE"
        or sha(ROOT / review["preparer"]) != review["preparer_sha256"]
    ):
        raise ValueError("Exact preparation review mismatch.")
    rights = json.loads((PACKET / "source-rights-local-use-v1.json").read_text())
    if rights["local_research_processing"] != "PASS" or rights["raw_or_row_derivative_public_git"]:
        raise ValueError("Local-use/retention boundary unresolved.")
    tests = ET.parse(PACKET / "preparation-tests-v1.xml").getroot()
    suites = list(tests.iter("testsuite"))
    if (
        not suites
        or sum(int(s.get("tests", "0")) for s in suites) < 27
        or any(int(s.get(k, "0")) for s in suites for k in ("failures", "errors", "skipped"))
    ):
        raise ValueError("Missing/failed preparation tests.")
    config = json.loads(config_path.read_text())
    if config["status"] != "DRAFT_BEFORE_CODE_REVIEW_NOT_FROZEN":
        raise ValueError("Preserve already frozen configuration.")
    if sha(ROOT / config["family_registry"]) != config["family_registry_sha256"]:
        raise ValueError("Reviewed family registry mismatch.")
    files = [
        "research/benchmark_v3/prepare_features.py",
        "tools/resource_guard_v1.py",
        "research/configs/goal3_feature_access_policy_v2.json",
    ]
    identities = {name: sha(ROOT / name) for name in files}
    config.update(
        status="FROZEN_BEFORE_ASSAY_PARSE",
        frozen_utc=datetime.now(timezone.utc).isoformat(),
        frozen_source_sha256=identities,
        parent_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
    )
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8", newline="\n")
    report = {
        "status": "PASS_FROZEN_BEFORE_NEW_ASSAY_PARSE",
        "config_sha256": sha(config_path),
        "source_sha256": identities,
        "family_registry_sha256": config["family_registry_sha256"],
        "frozen_utc": config["frozen_utc"],
        "parent_commit": config["parent_commit"],
        "review_sha256": sha(PACKET / "family-and-preparation-review.json"),
        "test_xml_sha256": sha(PACKET / "preparation-tests-v1.xml"),
        "prior_compound_outcomes_seen": False,
        "known_schema_canary_task": "CHEMBL1614128_DEVELOPMENT_ONLY",
    }
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
