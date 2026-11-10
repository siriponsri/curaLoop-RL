"""Check byte-preserved Windows records and generated SVG without rewriting them."""

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/agent-rd-run-20261110-v1"
PUBLIC = ROOT / "docs/evidence/agent-rd-20261110-v1"


def main():
    attributes = TASK / "delivery-check-attributes-v1.txt"
    text = "docs/evidence/agent-rd-20261110-v1/figures-v1/*.svg whitespace=-blank-at-eol,cr-at-eol\n"
    text += "docs/evidence/agent-rd-20261110-v1/figures-v2/*.svg whitespace=-blank-at-eol,cr-at-eol\n"
    if attributes.exists():
        assert attributes.read_text() == text
    else:
        attributes.write_text(text, encoding="utf-8", newline="\n")
    command = ["rtk", "proxy", "git", "-c", "core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol",
               "-c", "core.attributesFile=" + str(attributes), "diff", "064bd3d", "454d1a1", "--check"]
    checked = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    freeze = json.loads((ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json").read_text(encoding="utf-8"))
    pins_preserved = all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == value for path, value in freeze["pins"].items())
    diagrams = {}
    for version in ("v1", "v2"):
        path = PUBLIC / ("figures-" + version) / "01-control-flow.svg"
        document = ET.parse(path)
        assert document.getroot().tag.endswith("svg")
        labels = " ".join(document.getroot().itertext())
        assert all(label in labels for label in ("B0 / Deterministic", "B1 / LLM only", "B2 / LLM + tools", "P / Guarded", "Source"))
        diagrams[version] = {"xml": "PASS", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    receipt = {"status": "PASS" if checked.returncode == 0 and pins_preserved else "FAIL", "commit_checked": "454d1a1",
               "command": command, "exit_code": checked.returncode, "stdout": checked.stdout, "stderr": checked.stderr,
               "exception_scope": "Treat CRLF as Windows line endings; preserve Matplotlib path-command trailing spaces only in the two exact generated SVG folders. Source whitespace checks remain enabled.",
               "default_check": "FAILED on CRLF; a CRLF-aware retry identified generated SVG path spaces. The checkpoint had already been pushed; this follow-up records the completed check transparently.",
               "frozen_27_pins_preserved": pins_preserved, "svg_validation": diagrams,
               "persistent_git_configuration_changed": False, "evidence_bytes_rewritten": False}
    target = PUBLIC / "delivery-format-check-v1.json"
    assert not target.exists()
    target.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": receipt["status"], "exit_code": checked.returncode, "pins_preserved": pins_preserved}))
    if checked.returncode:
        print(checked.stdout[:1400])
    assert receipt["status"] == "PASS"


if __name__ == "__main__":
    main()
