"""Inspect the exact owned delivery scope without inference or source repair."""

import re
import subprocess
import sys

from agent_rd_admin_v1 import PUBLIC, ROOT, read, sha, write


def git(*args):
    return subprocess.check_output(["rtk", "proxy", "git", *args], cwd=ROOT, text=True).splitlines()


def main():
    assert git("branch", "--show-current") == ["main"]
    candidates = set(git("diff", "--name-only")) | set(git("ls-files", "--others", "--exclude-standard"))
    candidates.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "frontend/dist").rglob("*") if p.is_file())
    roots = {"AGENTS.md", "GOAL.md", "HANDOFF.md", "PLAN.md", "README.md", "START_HERE.md"}
    prefixes = (
        "api/agent_", "tools/agent_rd_", "tests/test_agent_product_scope_v1.py",
        "frontend/dist/", "frontend/src/agent-rd", "frontend/src/locales/th.json",
        "frontend/src/pages/AgentMission.tsx", "docs/evidence/agent-rd-20261110-v1/",
        "docs/08_agent_rd/", "docs/manual/CuraLoop-AgentRD-Guide-EN-v",
        "docs/07_publication/CuraLoop-AgentRD-Computational-Report-EN-v",
        "docs/07_publication/CURALOOP_AGENTRD_COMPUTATIONAL_REPORT_EN_V",
    )
    assert all(p in roots or p.startswith(prefixes) for p in candidates), sorted(candidates)
    forbidden = (".local/", "research/raw_data/", "reading_room_private/", "customer_private/")
    assert not any(p.startswith(forbidden) for p in candidates)
    assert not any((ROOT / "output").rglob("*.pdf"))
    secrets = re.compile(rb"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----|\b(?:sk-[A-Za-z0-9_-]{24,}|hf_[A-Za-z0-9]{28,})\b")
    identities = {}
    for name in sorted(candidates):
        path = ROOT / name
        if not path.is_file():
            continue
        assert path.stat().st_size < 10 * 1024 * 1024, name
        if path.suffix.lower() not in (".png", ".pdf", ".ttf"):
            assert not secrets.search(path.read_bytes()), f"Potential secret in {name}; inspect privately"
        identities[name] = sha(path)
    python = [p for p in candidates if p.endswith(".py") and (ROOT / p).is_file()]
    result = subprocess.run([sys.executable, "-m", "ruff", "check", *sorted(python)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, (result.stdout, result.stderr)
    freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    write(PUBLIC / "delivery-preflight-v1.json", {
        "status": "PASS_OWNED_PUBLIC_SCOPE_SECRET_PATTERN_AND_NO_FIX_LINT",
        "candidate_existing_files": len(identities), "no_fix_python_files_checked": len(python),
        "candidate_sha256": identities, "frozen_pins_unchanged": len(freeze["pins"]),
        "private_return_or_model_weights_staged": False,
        "new_model_or_scientific_trial": False,
        "secret_check_scope": "Explicit private-key and common provider-key patterns; not a general security certification",
    }, True)
    print(f"PASS: {len(identities)} owned public files; {len(python)} Python files pass no-fix lint")


if __name__ == "__main__":
    main()
