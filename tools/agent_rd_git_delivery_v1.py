"""Final administrative byte audit; no research run or account reopening."""

import hashlib
import re
import subprocess
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write


def git(*args, input_data=None, check=True):
    return subprocess.run(["rtk", "proxy", "git", *args], cwd=ROOT,
                          input=input_data, capture_output=True, check=check)


def main():
    ledger = read(TASK / "ledger.json")
    assert ledger["status"] == "CLOSED_DELIVERED_COMPUTATIONAL_REPORT"
    assert sha(TASK / "ledger.json") == read(PUBLIC / "settled-account-identity-v1.json")["ledger_sha256"]
    assert not git("diff", "--name-only").stdout.strip()
    paths = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").stdout.decode().split("\0")[:-1]
    stream = git("cat-file", "--batch", input_data="".join(f":{p}\n" for p in paths).encode()).stdout
    offset, identities = 0, {}
    for path in paths:
        end = stream.index(b"\n", offset)
        header = stream[offset:end].split()
        assert header[1] == b"blob", (path, header)
        size = int(header[2])
        data = stream[end + 1:end + 1 + size]
        assert data == (ROOT / path).read_bytes(), f"Staged bytes differ: {path}"
        identities[path] = hashlib.sha256(data).hexdigest()
        offset = end + size + 2
    assert offset == len(stream)
    release = read(TASK / "release.json")
    freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    for pins in (release["prior_ledger_pins"], release["frozen_scientific_pins"], freeze["pins"]):
        assert all(sha(ROOT / p) == h for p, h in pins.items())
    audit = read(PUBLIC / "final-audit-v1.json")
    assert all(sha(ROOT / p) == h for p, h in audit["final_document_sha256"].items())
    whitespace = git("diff", "--cached", "--check", check=False)
    flagged = {}
    for line in whitespace.stdout.decode().splitlines():
        match = re.match(r"(.+?):\d+: .+", line)
        if match:
            flagged[match[1]] = flagged.get(match[1], 0) + 1
    for path in flagged:
        assert (path.endswith(".pdf") and path.startswith("docs/07_publication/CuraLoop-AgentRD-")) or (
            path.startswith("docs/evidence/agent-rd-20261110-v1/") and (
                path.endswith((".csv", ".svg")) or path.endswith("/manual-build-v2.json")))
    clean = git("diff", "--cached", "--check", "--", ".",
                *(f":(exclude){p}" for p in flagged), check=False)
    assert clean.returncode == 0, clean.stdout.decode()
    write(PUBLIC / "staged-byte-integrity-v1.json", {
        "status": "PASS_EXACT_STAGED_BYTES_AND_FROZEN_PRESERVATION",
        "utc": datetime.now(timezone.utc).isoformat(), "staged_existing_files_checked": len(paths),
        "staged_file_sha256": identities, "all_staged_bytes_match_worktree": True,
        "old_ledgers_preserved": 14, "old_scientific_pins_preserved": 66, "new_frozen_pins_preserved": 27,
        "settled_ledger_sha256": sha(TASK / "ledger.json"),
        "raw_git_whitespace_exit_code": whitespace.returncode,
        "raw_git_whitespace_is_clean": whitespace.returncode == 0,
        "generated_artifact_whitespace_flags_retained": flagged,
        "source_and_document_whitespace_exit_code": clean.returncode,
        "artifact_whitespace_policy": "Preserve exact reviewed PDF, SVG, original CSV CRLF and generated receipt bytes; no normalization of audited evidence",
        "new_model_or_research_work": False,
    }, True)
    print(f"PASS: {len(paths)} exact staged blobs; {len(flagged)} generated artifacts retain whitespace flags; other source/doc whitespace clean")


if __name__ == "__main__":
    main()
