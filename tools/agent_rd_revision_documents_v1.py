"""Repair inspected authoring defects in a new edition; no experiment changes."""

import subprocess
import sys
from pathlib import Path

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write

BUNDLED = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"


def main():
    work = TASK / "authoring-revision-v2"
    work.mkdir(exist_ok=False)
    freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    release = read(TASK / "release.json")
    preserved = {**freeze["pins"], **release["prior_ledger_pins"], **release["frozen_scientific_pins"]}
    for folder in ("analysis-v1", "descriptive-v1", "locked-results-v1", "result-figures-v1", "authoring-source-v1"):
        preserved.update({p.relative_to(ROOT).as_posix(): sha(p) for p in (PUBLIC / folder).rglob("*") if p.is_file()})
    for filename in ("docs/manual/CuraLoop-AgentRD-Guide-EN-v2.pdf",
                     "docs/07_publication/CuraLoop-AgentRD-Computational-Report-EN-v1.pdf",
                     "docs/07_publication/CURALOOP_AGENTRD_COMPUTATIONAL_REPORT_EN_V1.md"):
        preserved[filename] = sha(ROOT / filename)
    assert all(sha(ROOT / p) == h for p, h in preserved.items())
    assert read(PUBLIC / "manuscript-visual-review-v1.json")["status"] == "FAIL_AUTHOR_VISUAL_LAYOUT_REVIEW"
    source_copy = work / "sources"
    source_copy.mkdir()
    for path in (ROOT / "tools").glob("agent_rd_*.py"):
        (source_copy / path.name).write_bytes(path.read_bytes())
    checked_paths = ["tools/agent_rd_revision_documents_v1.py", "tools/agent_rd_author_review_record_v1.py",
                     "tools/agent_rd_mechanism_audit_v1.py", "tools/agent_rd_result_figures_v1.py",
                     "tools/agent_rd_preview_reproduction_v1.py", "tools/agent_rd_manuscript_v1.py",
                     "tools/agent_rd_documents_v1.py", "tools/agent_rd_closeout_v1.py"]
    commands = [[sys.executable, "-m", "ruff", "check", *checked_paths],
                [sys.executable, "-m", "py_compile", *checked_paths],
                [str(BUNDLED), "tools/agent_rd_result_figures_v1.py", "--edition", "v2"],
                [str(BUNDLED), "tools/agent_rd_preview_reproduction_v1.py", "v2"],
                [str(BUNDLED), "tools/agent_rd_documents_v1.py", "manuscript-v2"],
                [str(BUNDLED), "tools/agent_rd_documents_v1.py", "render-manuscript-v2"]]
    steps = []
    try:
        for index, command in enumerate(commands):
            with (work / f"step-{index}.stdout.txt").open("xb") as out, (work / f"step-{index}.stderr.txt").open("xb") as err:
                result = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err)
            steps.append({"command": command, "exit_code": result.returncode})
            write(work / "progress.json", {"steps": steps})
            print(str(index) + " exit=" + str(result.returncode), flush=True)
            if result.returncode:
                print((work / f"step-{index}.stdout.txt").read_text(encoding="utf-8", errors="replace")[-2000:])
                print((work / f"step-{index}.stderr.txt").read_text(encoding="utf-8", errors="replace")[-2000:])
                raise SystemExit(result.returncode)
        write(PUBLIC / "authoring-revision-v2.json", {
            "status": "RENDERED_V2_AWAITING_AUTHOR_VISUAL_REVIEW", "steps": steps,
            "preserved_old_file_count": len(preserved), "scientific_values_or_scores_changed": False,
            "new_model_calls": 0, "original_analysis_sha256": sha(PUBLIC / "analysis-v1/analysis.json"),
            "repairs": ["Latency labels have leader lines and an open P marker; original coordinates unchanged.",
                        "Headings stay with following content; system column widened; joined prose words corrected.",
                        "Actual current-product task failure described separately from lifecycle acceptance; references are clickable."]
        }, True)
    finally:
        assert all(sha(ROOT / p) == h for p, h in preserved.items()), "A preserved artifact changed"


if __name__ == "__main__":
    main()
