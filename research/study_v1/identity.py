"""Immutable study and selection identities outside the policy boundary."""

import json
import importlib.metadata
from pathlib import Path

from research.benchmark_v3.prepare_features_v2 import sha_file

RUN_RELATIVE = ".local/plan-a-20261105-v2"
PACKET_RELATIVE = "docs/evidence/goal4-20261105-v1"
CONFIG_RELATIVE = "research/configs/goal4_protocol_v1.json"


def verify_frozen(root):
    packet = root / PACKET_RELATIVE
    proof = json.loads((packet / "protocol-freeze-v1.json").read_text())
    path = root / CONFIG_RELATIVE
    if sha_file(path) != proof["protocol_sha256"]:
        raise ValueError("Frozen protocol identity mismatch.")
    for name, expected in proof["source_sha256"].items():
        source = (root / name).resolve()
        if not source.is_relative_to(root.resolve()) or sha_file(source) != expected:
            raise ValueError("Frozen study source identity mismatch.")
    protocol = json.loads(path.read_text())
    if protocol["status"] != "FROZEN_BEFORE_GOAL4_OUTCOMES":
        raise ValueError("Study protocol not frozen.")
    for name in ("numpy", "scipy", "scikit-learn", "rdkit", "threadpoolctl"):
        if importlib.metadata.version(name) != protocol["tested_runtime_packages"][name]:
            raise ValueError("Scientific runtime version differs from the frozen tested environment.")
    return protocol


def verify_selection(root, protocol):
    path = root / RUN_RELATIVE / "selection.json"
    proof = json.loads((root / PACKET_RELATIVE / "selection-freeze-v1.json").read_text())
    if sha_file(path) != proof["selection_sha256"] or sha_file(root / CONFIG_RELATIVE) != proof["protocol_sha256"]:
        raise ValueError("Selection freeze identity mismatch.")
    selection = json.loads(path.read_text())
    if (selection["status"] != "PASS_SELECTION_FROZEN" or
        selection["selected_hypotheses"] not in protocol["hypotheses"] or
        selection["selected_hypotheses"] != proof["selected_hypotheses"]):
        raise ValueError("Invalid selected configuration.")
    for relative, digest in selection["development_result_sha256"].items():
        source = (root / RUN_RELATIVE / relative).resolve()
        if not source.is_relative_to((root / RUN_RELATIVE).resolve()) or sha_file(source) != digest:
            raise ValueError("Selected development evidence changed.")
    return selection
