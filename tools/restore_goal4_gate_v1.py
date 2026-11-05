"""Mirror a verified partial development return without replacing any bytes."""

import json
import shutil
from pathlib import Path

from research.benchmark_v3.prepare_features_v2 import sha_file

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / ".local/plan-a-20261105-v1/remote-return/goal4-development-v1"
    proof = json.loads((folder / "local-verification-with-manifest.json").read_text())
    manifest = json.loads((folder / "manifest.json").read_text())
    if proof["status"] != "PASS_LOCAL_ALL_FILES_VERIFIED" or not proof["manifest_unchanged_during_verification"]:
        raise ValueError("Enhanced complete partial-return proof required.")
    if sha_file(folder / "manifest.json") != proof["manifest_sha256"] or manifest.get("inventory_scope") != "PARTIAL_DEVELOPMENT_GATE_EXPORT_NOT_CLEANUP_AUTHORIZATION":
        raise ValueError("Wrong or changed partial return.")
    permitted = [(ROOT / ".local/plan-a-20261105-v2").resolve(),
                 (ROOT / "docs/evidence/goal4-20261105-v1").resolve()]
    for row in manifest["files"]:
        source = folder / "files" / row["path"]
        target = (ROOT / row["path"]).resolve()
        if not any(target.is_relative_to(prefix) for prefix in permitted) or sha_file(source) != row["sha256"]:
            raise ValueError("Unverified/out-of-scope mirror path.")
        if target.exists():
            if not target.is_file() or sha_file(target) != row["sha256"]:
                raise ValueError("Never replace different existing scientific bytes.")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if sha_file(target) != row["sha256"]:
            raise ValueError("Mirror readback mismatch.")
    report = {"status": "PASS_VERIFIED_PARTIAL_MIRROR", "files": len(manifest["files"]),
              "tree_sha256": manifest["tree_sha256"], "not_full_remote_cleanup_proof": True}
    (ROOT / "docs/evidence/goal4-20261105-v1/development-return-mirror-v1.json").open("x", encoding="utf-8").write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
