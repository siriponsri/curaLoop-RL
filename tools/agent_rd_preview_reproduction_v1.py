"""Verify offline figure reproduction in a new directory, with no old writes.

Uses public inputs and existing optional plotting packages on this machine.
This is an author reproduction check, not independent or clean-machine proof.
"""

import os
import subprocess
import sys

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write
from PIL import Image


def main():
    edition = sys.argv[1] if len(sys.argv) == 2 else "v1"
    assert edition in ("v1", "v2")
    freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    preserved = dict(freeze["pins"])
    for folder in ("analysis-v1", "descriptive-v1", "locked-results-v1", "result-figures-v1", "result-figures-v2"):
        preserved.update({p.relative_to(ROOT).as_posix(): sha(p) for p in (PUBLIC / folder).rglob("*") if p.is_file()})
    preview = TASK / ("offline-figure-reproduction-" + edition)
    assert not preview.exists()
    environment = {**os.environ,
                   "PYTHONPATH": str(TASK / "plotdeps-v1") + os.pathsep + os.environ.get("PYTHONPATH", ""),
                   "MPLCONFIGDIR": str(TASK / ("offline-figure-reproduction-mpl-cache-" + edition))}
    command = [sys.executable, "tools/agent_rd_result_figures_v1.py", "--edition", edition, "--preview-dir", str(preview)]
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True, encoding="utf-8")
    receipt = {"status": "FAIL", "command": command, "exit_code": result.returncode,
               "stdout": result.stdout, "stderr": result.stderr,
               "scope": "Author offline same-machine figure reproduction from public study inputs into a new directory",
               "new_model_calls": 0, "ssh_or_http_requests": 0,
               "independent_validation": False, "clean_machine_test": False}
    try:
        assert result.returncode == 0, result.stderr[-1500:]
        replay = read(preview / "preview-build.json")
        original = read(PUBLIC / ("result-figures-build-" + edition + ".json"))
        assert replay["source_pins"] == original["source_pins"]
        matched = []
        for filename in ("02-task-completion.png", "03-cost-completion.png"):
            with Image.open(PUBLIC / ("result-figures-" + edition) / filename) as first, Image.open(preview / filename) as second:
                assert first.size == second.size and first.mode == second.mode and first.tobytes() == second.tobytes()
            matched.append(filename)
        assert all(sha(ROOT / path) == value for path, value in preserved.items())
        receipt.update(status="PASS_OFFLINE_REPRODUCTION_IN_FRESH_OUTPUT_DIRECTORY", matching_png_pixels=matched,
                       original_files_unchanged=len(preserved), source_pins=original["source_pins"],
                       svg_byte_identity_claim=False)
    except BaseException as exc:
        receipt["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        write(PUBLIC / ("offline-figure-reproduction-" + edition + ".json"), receipt, True)
        print(receipt["status"])


if __name__ == "__main__":
    main()
