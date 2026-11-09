"""Official description/policy metadata only; never an activity request.

This is an AIC_Finder source crosscheck, not a restart of the stopped A3
observation endpoint. No assay data, summary, SID list or compound payload is
requested, and the earlier source STOPs remain intact.
"""
# ruff: noqa: E402

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start
from tools.cf1_source_inventory_v1 import fetch


def main():
    old = ROOT / ".local/goal4r2a3-20261106-v1/remote-return/full-v1"
    assert sha(old / "manifest.json") == "eb2eeeef2de9915b08c35c0f73ac5bfeb32b1e5fff8fad3c081f8f3b8315aa0c"
    manifest = {r["path"]: r for r in read(old / "manifest.json")["files"]}
    matches = [p for p in manifest if p.endswith("/description-metadata-input-v1.json")]
    assert len(matches) == 1
    old_path = old / "files" / matches[0]
    assert sha(old_path) == manifest[matches[0]]["sha256"]
    cached = {r["aid"]: r for r in read(old_path)["records"]}
    candidates = [r for r in read(TASK / "cached-target-review-private-v1.json")["records"]
                  if r["cached_target"] and r["cached_target"]["verdict"].startswith("NO_KNOWN")]
    assert len(candidates) == 8
    aids = sorted({a for r in candidates for a in r["source_pair"]}, key=int)
    output, failures = [], []
    for aid in aids:
        if aid in cached:
            output.append({"aid": aid, "origin": "AUTHENTICATED_CACHED_DESCRIPTION", **cached[aid]})
            continue
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/description/JSON"
        assert url.endswith("/description/JSON")
        try:
            body = fetch(url, "descriptions/" + aid + ".json", maximum=4 * 1024**2)
            value = json.loads(body)
            containers = value["PC_AssayContainer"]
            assert len(containers) == 1 and set(containers[0]) == {"assay"}
            descriptor = containers[0]["assay"]["descr"]
            assert str(descriptor["aid"]["id"]) == aid
            output.append({"aid": aid, "origin": "FRESH_DESCRIPTION_ONLY", "source_sha256": sha(TASK / "source/descriptions" / (aid + ".json")),
                "provider": descriptor.get("aid_source"), "project_category_raw": descriptor.get("project_category"),
                "target_metadata": descriptor.get("target"), "comment_notices": descriptor.get("comment", []),
                "readout_definitions": descriptor.get("results"), "assay_name": descriptor.get("name")})
        except Exception as error:
            failures.append({"aid": aid, "type": type(error).__name__, "message": str(error)[:200]})
            # Unexpected envelopes and access blocks stop further live calls.
            break
    for name, url in (
        ("ncbi-usage.html", "https://www.ncbi.nlm.nih.gov/home/about/policies/"),
        ("mlpcn-par-09-129.html", "https://grants.nih.gov/grants/guide/pa-files/PAR-09-129.html"),
        ("mlpcn-not-rm-09-020.html", "https://grants.nih.gov/grants/guide/notice-files/NOT-RM-09-020.html"),
    ):
        try:
            fetch(url, "policies/" + name, maximum=2 * 1024**2)
        except Exception as error:
            failures.append({"policy": name, "type": type(error).__name__, "message": str(error)[:200]})
    new(TASK / "description-review-private-v1.json", {"records": output, "failures": failures,
        "cached_input_sha256": sha(old_path), "activity_requests": 0, "prior_stops_reset": False})
    summary = {"status": "DESCRIPTION_REVIEW_REQUIRED" if not failures else "DESCRIPTION_ACCESS_OR_ENVELOPE_STOP",
        "candidate_target_metadata_campaigns": 8, "description_records": len(output), "expected_records": len(aids),
        "fresh_description_records": sum(r["origin"] == "FRESH_DESCRIPTION_ONLY" for r in output),
        "cached_description_records": sum(r["origin"] == "AUTHENTICATED_CACHED_DESCRIPTION" for r in output),
        "failures": failures, "activity_requests": 0, "prior_stops_reset": False,
        "confirmation_values_analyzed": False, "campaign_admission": False}
    new(PUBLIC / "description-review-v1.json", summary)
    print(summary)


if __name__ == "__main__":
    guard = start("description-policy-source-check", 240, 900)
    try:
        main()
        finish("description-policy-source-check", guard, "PASS_RECEIPTS_REVIEW_REQUIRED")
    except BaseException:
        finish("description-policy-source-check", guard, "FAIL")
        raise
