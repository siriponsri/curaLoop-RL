"""Measure opaque artifact compression before committing the unchanged matrix."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, REMOTE, TASK, finish, new, read, start
from tools.cf1_remote_v1 import book, settle
from tools.cf1_return_v1 import implementation
from tools.cf1_stage_v1 import stage


def main():
    name = "storage-compression-calibration-v1"
    book(name, "storage_calibration", 180, "admission_and_calibration", extra={"wall_seconds": 600})
    stage("storage-probe-code-v1", [
        (ROOT / "research/confirmation_v1/storage_probe_v1.py", "utility/storage_probe_v1.py"),
        (TASK / "jobs" / name / "permit.json", "jobs/" + name + "/permit.json")])
    module, _ = implementation()
    after = """from pathlib import Path
p=Path(__JOB__)
for field in ('result','resource','kernel-proof','failure'):
 f=p/(field+'.json')
 if f.exists():out[field]=json.loads(f.read_text())
""".replace("__JOB__", repr(REMOTE + "/jobs/" + name))
    result = module.launch(after, unit="curaloop-cf1-20261109-v1-" + name, cpu=69, wall=600, working=REMOTE,
                           args=["--", "/usr/bin/python3", "-B", REMOTE + "/utility/storage_probe_v1.py",
                                 REMOTE + "/jobs/" + name + "/permit.json"])
    assert settle(name, result) == "PASS"
    new(PUBLIC / "storage-compression-calibration-v1.json", read(TASK / "jobs" / name / "result.json"))


if __name__ == "__main__":
    guard = start("storage-calibration-orchestration-v1", 180, 900,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("storage-calibration-orchestration-v1", guard, "PASS_OPAQUE_STORAGE_CALIBRATION")
    except BaseException:
        finish("storage-calibration-orchestration-v1", guard, "FAIL")
        raise
