"""Pin exposed development inputs and source, then package minimal SSH inputs."""

import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone

from research.planning_v2.runner import FILES, METHODS, ROOT, identity, write


def main():
    path = ROOT / "research/configs/goal_02_real_data_v1.json"
    old = json.loads((ROOT / "research/configs/ncats_development_v1.json").read_text())
    folder = "research/raw_data/ncats-development-20261104/prepared-v1"
    for assay in old["assays"]:
        data = (ROOT / folder / f"{assay}.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != old["cohort_sha256"][assay]:
            raise ValueError("Existing development input changed.")
    cfg = {
        "schema_version": "curaloop.goal2.real-development.v1",
        "protocol_id": "goal-02-real-data-20261104-v1",
        "status": "FROZEN_DEVELOPMENT_ONLY",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "parent_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_sha256": identity(),
        "final_evaluation": False,
        "assays": old["assays"],
        "seeds": [0, 1, 2],
        "input_folder": folder,
        "cohort_sha256": old["cohort_sha256"],
        "raw_source_sha256": old["raw_source_sha256"],
        "methods": METHODS,
        "initial_count": 24,
        "budget": 12,
        "capacity": 2,
        "deadline": 8,
        "conditions": {"common": [2], "heterogeneous": [1, 2, 4]},
        "worlds": 16,
        "clusters": 12,
        "shortlist": 3,
        "max_run_wall_seconds": 1800,
        "max_virtual_memory_bytes": 1073741824,
        "threads": 1,
        "concurrency": 1,
        "expected_runs": 180,
        "hypothesis": "content relaxation reduces total policy compute without changing finite-model rollout choices",
        "scope": "DEVELOPMENT_ONLY; previously exposed real labels; no final or family transfer claim",
        "prefreeze_smoke": "docs/evidence/goal-02-real-data-20261104-v1/local-smoke-disclosure.json",
    }
    write(path, cfg)
    bundle = ROOT / ".local/goal2-real-data-20261104-v1/inputs.zip"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    if bundle.exists():
        raise FileExistsError(bundle)
    files = list(FILES) + [
        "research/__init__.py",
        "research/planning_v2/__init__.py",
        str(path.relative_to(ROOT)).replace("\\", "/"),
    ]
    files += [f"{folder}/{a}.json" for a in old["assays"]]
    with zipfile.ZipFile(bundle, "x", zipfile.ZIP_DEFLATED) as archive:
        for name in files:
            archive.write(ROOT / name, name)
    write(
        ROOT / "docs/evidence/goal-02-real-data-20261104-v1/input-transfer.json",
        {
            "status": "PASS",
            "files": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files},
            "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
            "bundle_bytes": bundle.stat().st_size,
            "private_credentials_included": False,
            "source_and_development_cohorts_only": True,
        },
    )
    print(str(bundle))


if __name__ == "__main__":
    main()
