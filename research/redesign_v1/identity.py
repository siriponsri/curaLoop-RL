"""Fixed source/role identities, separate from every public policy."""

import hashlib
import importlib.metadata
import json
from pathlib import Path

RUN = Path(".local/goal4r1-20261105-v1")
PACKET = Path("docs/evidence/goal4r1-20261105-v1")
CONFIG = Path("research/configs/goal4r1_protocol_v1.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def frozen(root):
    proof = json.loads((root / PACKET / "protocol-freeze-v1.json").read_text())
    if sha(root / CONFIG) != proof["protocol_sha256"]:
        raise ValueError("4R1 protocol changed.")
    for name, digest in proof["source_sha256"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path) != digest:
            raise ValueError("4R1 frozen source changed.")
    protocol = json.loads((root / CONFIG).read_text())
    if protocol["status"] != "FROZEN_BEFORE_NEW_CODE_EVALUATION" or protocol["permitted_outcome_roles"] != ["development"]:
        raise ValueError("Invalid 4R1 role/protocol gate.")
    for name, version in protocol["runtime_packages"].items():
        if importlib.metadata.version(name) != version:
            raise ValueError("Frozen scientific package version differs.")
    return protocol


def load_task(root, protocol, task_id):
    expected = {t["task_id"]: t for t in protocol["tasks"]}
    if task_id not in expected or expected[task_id]["role"] != "development":
        raise ValueError("Reject nondevelopment/unselected task before reading any private record.")
    path = root / RUN / "private-inputs" / (task_id + ".json")
    if sha(path) != expected[task_id]["sha256"]:
        raise ValueError("Private input identity changed.")
    payload = json.loads(path.read_text())
    target = expected[task_id]
    if (payload["role"] != "development" or payload["task_id"] != task_id or
        payload["family_id"] != target["family_id"] or len(payload["records"]) != target["rows"]):
        raise ValueError("Private/public task identities differ.")
    return payload
