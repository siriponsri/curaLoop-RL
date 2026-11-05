"""Constructed integrity/aggregation regressions; no molecular outcomes loaded."""

import hashlib
import json

import pytest

from research.redesign_v1.worker import case_key, cases
from tools.goal4r1_reporting_v1 import macro, paired, read_phase


def test_nested_macro_does_not_treat_repetitions_as_components():
    rows = ([{"family_id": "A", "task_id": "a", "v": 1}] * 5 +
            [{"family_id": "A", "task_id": "b", "v": 3}, {"family_id": "B", "task_id": "c", "v": 10}])
    assert macro(rows, lambda r: r["v"]) == 6


def row(task, group, seed, value):
    return {"task_id": task, "family_id": group, "seed": seed, "operation": "op", "metrics": {"new_hits": value}}


def test_paired_rejects_duplicate_missing_and_wrong_component():
    left = [row("t", "g", 1, 2)]
    right = [row("t", "g", 1, 1)]
    assert paired(left, right)["mean_difference_H"] == 1
    for a, b in ((left + left, right), (left, []), (left, [row("t", "wrong", 1, 1)])):
        with pytest.raises(ValueError):
            paired(a, b)


def fixture(root, bad=None):
    protocol = {"tasks": [{"task_id": "a", "family_id": "g", "role": "development"},
                          {"task_id": "b", "family_id": "h", "role": "development"}],
                "seeds": [101], "operations": [{"id": "op"}], "main_arms": ["random"]}
    path = root / "research/configs/goal4r1_protocol_v1.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(protocol))
    config_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    shard = root / ".local/goal4r1-20261105-v1/runs/campaign-v1/shard-0"
    shard.mkdir(parents=True)
    (shard / "resources.json").write_text(json.dumps({"status": "PASS"}))
    (shard / "identity.json").write_text(json.dumps({"protocol_sha256": config_sha}))
    entries = []
    values = cases(protocol, "campaign")
    if bad == "missing":
        values = values[:1]
    for i, case in enumerate(values):
        value = dict(case, role="development", family_id="g" if case["task_id"] == "a" else "h", status="PASS", case=case)
        if bad == "substitution" and i == 0:
            case = dict(case, seed=999)
            value.update(case, case=case)
        if bad == "family" and i == 0:
            value["family_id"] = "wrong"
        data = json.dumps(value).encode()
        name = f"{i}.json"
        (shard / name).write_bytes(data)
        entries.append({"file": name, "case_key": case_key(case), "sha256": hashlib.sha256(data).hexdigest()})
    if bad == "duplicate":
        entries = entries[:1] * 2
    (shard / "complete.json").write_text(json.dumps({"status": "PASS", "results": entries}))
    return protocol


@pytest.mark.parametrize("bad", ["missing", "duplicate", "substitution", "family"])
def test_exact_roster_gate_rejects_constructed_corruption(tmp_path, bad):
    protocol = fixture(tmp_path, bad)
    with pytest.raises(ValueError):
        read_phase(tmp_path, "campaign", 2, protocol)


def test_exact_roster_gate_accepts_complete_constructed_phase(tmp_path):
    protocol = fixture(tmp_path)
    rows, identities = read_phase(tmp_path, "campaign", 2, protocol)
    assert len(rows) == len(identities) == 2


def main():
    import os
    from pathlib import Path
    from research.redesign_v1.guard import GoalGuard
    root = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")
    if Path.cwd().resolve() != root:
        raise ValueError("Scientific checks run on dr-train.")
    os.sched_setaffinity(0, {71})
    guard = GoalGuard(root / ".local/goal4r1-20261105-v1/reporting-check-resources.json", 120, 120)
    from contextlib import redirect_stdout, redirect_stderr
    temp = root / ".local/goal4r1-20261105-v1/reporting-test-temp-v1"
    if temp.exists():
        raise FileExistsError("Fresh owned test scratch required.")
    with (root / "reporting-check-v1.log").open("x") as log, redirect_stdout(log), redirect_stderr(log):
        status = pytest.main(["-q", __file__, "-p", "no:cacheprovider", "--tb=short", "--basetemp", str(temp)])
    guard.finish("PASS" if status == 0 else "FAIL", pytest_exit_code=int(status), covered_by_d3_utility_allowance=True)
    print(json.dumps({"status": "PASS" if status == 0 else "FAIL", "pytest_exit_code": int(status)}))
    raise SystemExit(status)


if __name__ == "__main__":
    main()
