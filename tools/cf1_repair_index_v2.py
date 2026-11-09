"""Repair only the four terminal index-validation failures; keep two PASS jobs."""
# ruff: noqa: E402

import ast
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import TASK, finish, new, read, sha, start
from research.confirmation_v1.technical_worker_v2 import stored_index
from tools import cf1_remote_v1 as remote
from tools.cf1_stage_v1 import stage


def dispatch(name):
    code, permit = remote.rendered(name)
    code = code.replace("research.confirmation_v1.technical_worker", "research.confirmation_v1.technical_worker_v2")
    compile(code, "<cf1-index-repair>", "exec")
    folder = TASK / "jobs" / name
    with (folder / "remote-command.py").open("x", encoding="utf-8", newline="\n") as file:
        file.write(code)
    result = remote.transport.remote(code, timeout=permit["wall_seconds"] + 60)
    new(folder / "ssh-response.json", {"exit_code": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()})
    assert result.returncode == 0
    return json.loads(result.stdout)


def main():
    seen = set()
    assert [stored_index(str(i), seen) for i in (0, 2, 10)] == [0, 2, 10]
    for value in ("2", "-1"):
        try:
            stored_index(value, seen)
        except AssertionError:
            pass
        else:
            raise AssertionError("Duplicate/negative index regression")
    source = ROOT / "research/confirmation_v1/technical_worker_v2.py"
    ast.parse(source.read_text(), feature_version=(3, 8))
    stage("technical-index-v2", [(source, "code/research/confirmation_v1/technical_worker_v2.py")])
    pins = dict(read(TASK / "code-pins-v1.json"))
    pins["research/confirmation_v1/technical_worker_v2.py"] = sha(source)
    new(TASK / "code-pins-index-v2.json", pins)
    selected = read(TASK / "metadata-admission-v1.json")["selected"]
    failed = []
    for row in selected:
        name = "protect-" + row["campaign"].replace("/", "-")
        result = read(TASK / "jobs" / name / "controller-result.json")
        if result.get("result", {}).get("status") == "PASS_BLINDED_STRUCTURE_SUPPORT":
            continue
        assert result["unit_state"]["Result"] == "exit-code" and result["resource"]["status"] == "FAIL"
        assert result["failure"]["type"] == "AssertionError" and "int(row[\"\"]) == i" in result["stderr"]
        failed.append(row)
    assert len(failed) == 4
    names = []
    for i, row in enumerate(failed):
        key = row["campaign"].replace("/", "-")
        name = "protect-" + key + "-repair-v2"
        remote.book(name, "protect", 600, "technical_retry_reserve", processor=69 + i % 3,
                    extra={"campaign": row["campaign"], "output_name": key + "-v2", "code_pins": pins})
        names.append(name)
    for begin in range(0, len(names), 3):
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(dispatch, name): name for name in names[begin:begin + 3]}
            for future in as_completed(futures):
                assert remote.settle(futures[future], future.result()) == "PASS"


if __name__ == "__main__":
    guard = start("index-repair-orchestration-v2", 300, 4200,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("index-repair-orchestration-v2", guard, "PASS_INDEX_REPAIR_DISPATCH")
    except BaseException:
        finish("index-repair-orchestration-v2", guard, "FAIL")
        raise
