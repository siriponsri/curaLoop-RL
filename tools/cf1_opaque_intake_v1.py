"""Download only the six metadata-selected whole files; never parse their rows."""
# ruff: noqa: E402

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start
from tools.cf1_source_inventory_v1 import fetch


def main():
    admitted = read(TASK / "metadata-admission-v1.json")
    assert admitted["status"] == "PASS_METADATA_PRECONDITIONS_OPAQUE_INTAKE_ONLY"
    rows = []
    for row in admitted["selected"]:
        name = "campaigns/" + row["campaign"].replace("/", "-") + ".csv"
        body = fetch("https://raw.githubusercontent.com/dahvida/AIC_Finder/" + admitted["source_commit"] + "/" + row["source_file"],
                     name, maximum=row["source_bytes"])
        assert len(body) == row["source_bytes"]
        digest = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
        assert digest == row["source_blob_oid"]
        rows.append({"campaign": row["campaign"], "private_path": "source/" + name,
                     "bytes": len(body), "sha256": sha(TASK / "source" / name), "source_blob_oid": digest})
    source_bytes = sum(p.stat().st_size for p in (TASK / "source").rglob("*") if p.is_file())
    source_bytes += read(TASK / "si-receipt-v1.json")["bytes"]
    assert source_bytes <= 1073741824 and len(rows) <= 6
    summary = {"status": "PASS_SIX_OPAQUE_WHOLE_FILES_AUTHENTICATED", "files": rows,
               "source_received_bytes_including_owner_si": source_bytes,
               "campaign_rows_parsed": False, "confirmation_values_analyzed": False,
               "final16_access": False, "metadata_selection_sha256": sha(TASK / "metadata-admission-v1.json")}
    new(TASK / "opaque-intake-v1.json", summary)
    new(PUBLIC / "opaque-intake-v1.json", summary)
    print({"status": summary["status"], "whole_files": len(rows), "bytes": sum(r["bytes"] for r in rows)})


if __name__ == "__main__":
    guard = start("opaque-six-file-intake", 300, 1200)
    try:
        main()
        finish("opaque-six-file-intake", guard, "PASS_OPAQUE_FILES_NOT_LABEL_ANALYSIS")
    except BaseException:
        finish("opaque-six-file-intake", guard, "FAIL")
        raise
