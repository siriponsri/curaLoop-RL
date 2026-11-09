"""Test whether existing protein metadata can resolve the author roster."""
# ruff: noqa: E402

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start
from research.qualification_v1.reconcile_v1 import family_overlay


def main():
    old = ROOT / ".local/goal4r2a3-20261106-v1/remote-return/full-v1"
    assert sha(old / "manifest.json") == "eb2eeeef2de9915b08c35c0f73ac5bfeb32b1e5fff8fad3c081f8f3b8315aa0c"
    pins = {r["path"]: r["sha256"] for r in read(old / "manifest.json")["files"]}
    source = old / "files"
    names = ["runs/xref-metadata-v1/protein-metadata-private.json",
             "runs/metadata-audit-v1/protection-private.json",
             "private-inputs/protection-inputs/family-registry-v3.json",
             "private-inputs/protection-inputs/interpro-ftp-entries110-curl-v2/body",
             "private-inputs/protection-inputs/uniprot-family-bulk-v1/families.json",
             "private-inputs/protection-inputs/uniprot-family-exposure-v1/families.json"]
    for name in names:
        assert sha(source / name) == pins[name]
    # This supplements a positive protection anchor only. It never removes it.
    overlay, state = family_overlay(source,
        read(source / names[0])["records"], read(source / names[1]), {"IPR050332": "family"})
    rows = read(TASK / "role-review-private-v1.json")["records"]
    output = []
    for row in rows:
        record = overlay.get(row["source_target"])
        output.append({"codename": row["codename"], "source_pair": row["pair"],
                       "cached_target": record, "source_mapping_crosscheck": "AUTHOR_METADATA_PENDING_SI_CHECK",
                       "admitted": False})
    new(TASK / "cached-target-review-private-v1.json", {"inputs": {n: pins[n] for n in names},
                                                       "protection_state": state, "records": output})
    counts = Counter("NO_AUTHENTICATED_CACHED_TARGET" if r["cached_target"] is None
                     else r["cached_target"]["verdict"] for r in output)
    summary = {"status": "CACHED_TARGET_REVIEW_NOT_ADMISSION", "campaign_count": len(output),
               "aggregate_verdict_counts": dict(counts), "historical_metadata_rewritten": False,
               "source_mapping_verified": False, "confirmation_values_analyzed": False,
               "protected_payloads_opened": False}
    new(PUBLIC / "cached-target-review-v1.json", summary)
    print(summary)
    print("SAFE_CANDIDATE_CODES", [r["codename"] for r in output if r["cached_target"]
                                   and r["cached_target"]["verdict"].startswith("NO_KNOWN")])


if __name__ == "__main__":
    guard = start("cached-target-role-review", 180, 600)
    try:
        main()
        finish("cached-target-role-review", guard, "PASS_REVIEW_NOT_ADMISSION")
    except BaseException:
        finish("cached-target-role-review", guard, "FAIL")
        raise
