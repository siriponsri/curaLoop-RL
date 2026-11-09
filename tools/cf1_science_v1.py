"""Blinded data release, append-only science code and matched CPU job waves."""
# ruff: noqa: E402

import ast
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import (
    PUBLIC,
    REMOTE,
    TASK,
    authority,
    finish,
    new,
    read,
    sha,
    start,
)
from tools import cf1_remote_v1 as remote
from tools.cf1_stage_v1 import stage


def admit_and_deploy():
    metadata = read(TASK / "metadata-admission-v1.json")
    campaigns = []
    for row in metadata["selected"]:
        name = "protect-" + row["campaign"].replace("/", "-")
        if (TASK / "jobs" / (name + "-repair-v2") / "result.json").exists():
            name += "-repair-v2"
        value = read(TASK / "jobs" / name / "result.json")
        assert value["status"] == "PASS_BLINDED_STRUCTURE_SUPPORT" and value["confirmation_values_analyzed"] is False
        assert read(TASK / "jobs" / name / "kernel-proof.json") == {
            "cpu.max": "100000 100000", "memory.max": "4294967296", "memory.swap.max": "0"}
        campaigns.append({**value, "provider_block": row["source_experiment_block"], "role": row["role"], "job": name})
    assert 4 <= len(campaigns) <= 6 and len({r["provider_block"] for r in campaigns}) >= 2
    assert sum(r["counts"]["source_rows"] for r in campaigns) <= 2000000
    assert sum(r["counts"]["eligible_confirmation_observations"] for r in campaigns) <= 100000
    support = {"status": "PASS_BLINDED_DATA_ADMISSION", "campaigns": campaigns,
               "confirmation_values_released": False, "final16_access": False,
               "owner_choice_sha256": sha(TASK / "owner-source-a-v1.json"),
               "original_source_files_unchanged": True, "no_outcome_based_cohort_selection": True}
    new(TASK / "blinded-support-v1.json", support)
    new(PUBLIC / "blinded-support-v1.json", support)
    old = read(TASK / "code-pins-v1.json")
    extra = ["research/confirmation_v1/" + name + ".py" for name in ("features", "rankers", "portfolios", "scientific_worker")]
    check = subprocess.run(["rtk", "proxy", "ruff", "check", "--fix", *extra], capture_output=True, text=True, timeout=60)
    new(TASK / "science-code-lint-v2.json", {"exit_code": check.returncode, "stdout": check.stdout, "stderr": check.stderr})
    assert check.returncode == 0, check.stdout
    pins = dict(old)
    for name in extra:
        ast.parse((ROOT / name).read_text(), feature_version=(3, 8))
        pins[name] = sha(ROOT / name)
    for name, expected in old.items():
        assert sha(ROOT / name) == expected
    new(TASK / "code-pins-science-v2.json", pins)
    protocol = ROOT / "docs/03_research/LR_CF1_CONTROLS_AND_ADMISSION_PROTOCOL_V1.md"
    files = [(ROOT / name, "code-v2/" + name) for name in pins]
    files += [(TASK / "blinded-support-v1.json", "inputs/blinded-support-v1.json"),
              (protocol, "inputs/controls-protocol-v1.md")]
    stage("science-code-v2", files)
    print({"status": support["status"], "campaigns": len(campaigns),
           "source_rows": sum(r["counts"]["source_rows"] for r in campaigns),
           "retained_rows": sum(r["counts"]["retained_primary_rows"] for r in campaigns),
           "eligible_confirmation_observations": sum(r["counts"]["eligible_confirmation_observations"] for r in campaigns)})


def book(name, handler, cpu, bucket, processor=69, extra=None):
    source = {r["path"]: r["sha256"] for r in read(TASK / "transport-manifest-v1.json")["files"] if r["path"].startswith("author/")}
    values = {"interpreter": REMOTE + "/python/bin/python3.8", "code_directory": "code-v2",
              "code_pins": read(TASK / "code-pins-science-v2.json"), "source_code_pins": source,
              "bundle_sha256": sha(TASK / "stages/science-code-v2.tar.gz")}
    if extra:
        values.update(extra)
    remote.book(name, handler, cpu, bucket, processor=processor, extra=values)


def dispatch(name):
    code, permit = remote.rendered(name)
    code = code.replace("research.confirmation_v1.technical_worker", "research.confirmation_v1.scientific_worker")
    compile(code, "<frozen-cf1-scientific-dispatch>", "exec")
    folder = TASK / "jobs" / name
    with (folder / "remote-command.py").open("x", encoding="utf-8", newline="\n") as file:
        file.write(code)
    result = remote.transport.remote(code, timeout=permit["wall_seconds"] + 60)
    new(folder / "ssh-response.json", {"exit_code": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()})
    assert result.returncode == 0, "INSPECT_LIVE_UNIT_AND_RECEIPTS_BEFORE_RETRY"
    return json.loads(result.stdout)


def waves(specifications):
    # Each wave waits for all three jobs before reusing any assigned core.
    for begin in range(0, len(specifications), 3):
        names = []
        for i, specification in enumerate(specifications[begin:begin + 3]):
            item = dict(specification)
            name = item.pop("name")
            book(name, processor=69 + i, **item)
            names.append(name)
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(dispatch, name): name for name in names}
            for future in as_completed(futures):
                assert remote.settle(futures[future], future.result()) == "PASS"


def constructed():
    book("constructed-controls-v2", "constructed", 180, "utilities_return_handoff_delivery")
    assert remote.settle("constructed-controls-v2", dispatch("constructed-controls-v2")) == "PASS"


def features():
    assert read(TASK / "jobs/constructed-controls-v2/result.json")["status"] == "PASS_CONSTRUCTED_FROZEN_CONTROL_CHECKS"
    specifications = []
    for row in read(TASK / "blinded-support-v1.json")["campaigns"]:
        key = row["campaign"].replace("/", "-")
        specifications.append({"name": "features-" + key, "handler": "features", "cpu": 1200,
            "bucket": "features_and_baseline_reproduction", "extra": {"campaign": row["campaign"], "output_name": key}})
    waves(specifications)


def stage_features():
    results = []
    for row in read(TASK / "blinded-support-v1.json")["campaigns"]:
        value = read(TASK / "jobs" / ("features-" + row["campaign"].replace("/", "-")) / "result.json")
        assert value["status"] == "PASS_SOURCE_FEATURES_AND_FIXED_GROUPS" and not value["confirmation_values_analyzed"]
        results.append(value)
    value = {"status": "PASS_FROZEN_SOURCE_FEATURE_MANIFEST", "campaigns": results, "confirmation_values_analyzed": False}
    new(TASK / "feature-manifests-v1.json", value)
    new(PUBLIC / "feature-manifests-v1.json", value)
    stage("feature-manifest-v1", [(TASK / "feature-manifests-v1.json", "inputs/feature-manifests-v1.json")])


def calibrate_first_seed():
    # These twelve fits are actual first-seed baseline units, reused later.
    specifications = []
    for row in read(TASK / "feature-manifests-v1.json")["campaigns"]:
        for method in ("mvsa", "rf"):
            key = row["campaign"].replace("/", "-") + "-" + method + "-90101"
            specifications.append({"name": "first-seed-" + key, "handler": "fit", "cpu": 600,
                "bucket": "features_and_baseline_reproduction",
                "extra": {"campaign": row["campaign"], "ranker": method, "seed": 90101, "output_name": key}})
    waves(specifications)


if __name__ == "__main__":
    action = sys.argv[1]
    actions = {"admit-deploy": admit_and_deploy, "constructed": constructed, "features": features,
               "stage-features": stage_features, "first-seed": calibrate_first_seed}
    assert action in actions
    guard = start("science-controller-" + action, 300, 18000,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        authority()
        actions[action]()
        finish("science-controller-" + action, guard, "PASS_SCIENCE_CONTROLLER_" + action.upper())
    except BaseException:
        finish("science-controller-" + action, guard, "FAIL")
        raise
