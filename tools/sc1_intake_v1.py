"""Bounded official-source intake: no model inference or scientific outcome printing."""
from __future__ import annotations
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from tools.sc1_control_v1 import ACCOUNT, ROOT, digest, write_new

DEST = ROOT / "research/raw_data/external-benchmarks/scicode-2024"
MAX_BYTES = 10 * 1024**3


def fetch(url, path, limit):
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "CuraLoop-LR-SC1/1.0 (public research intake)"})
    record = {"url": url, "path": str(path.relative_to(ROOT)), "limit_bytes": limit,
              "started_utc": datetime.now(timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            record.update(status_code=response.status, content_type=response.headers.get("Content-Type"),
                          content_length=response.headers.get("Content-Length"), final_url=response.url)
            size = int(response.headers.get("Content-Length", 0))
            if size > limit:
                raise ValueError("Declared source exceeds intake ceiling")
            count = 0
            with path.open("xb") as output:
                while chunk := response.read(min(1024 * 1024, limit - count + 1)):
                    count += len(chunk)
                    if count > limit:
                        raise ValueError("Stream exceeds intake ceiling")
                    output.write(chunk)
            record.update(bytes=count, sha256=digest(path), status="PASS_TRANSPORT_ONLY")
    except Exception as exc:
        record.update(status="FAIL_TRANSPORT", error=f"{type(exc).__name__}: {exc}")
    return record


def main():
    sources = ACCOUNT / "source-intake-v1"
    sources.mkdir(parents=True, exist_ok=False)
    records = []
    records.append(fetch("https://huggingface.co/api/datasets/SciCode1/SciCode", sources / "hf-metadata.json", 1048576))
    if records[-1]["status"] != "PASS_TRANSPORT_ONLY":
        write_new(sources / "receipt.json", records)
        raise SystemExit(2)
    metadata = json.loads((sources / "hf-metadata.json").read_text(encoding="utf-8"))
    revision = metadata["sha"]
    for name in ("README.md", "problems_dev.jsonl", "problems_test.jsonl"):
        records.append(fetch(f"https://huggingface.co/datasets/SciCode1/SciCode/resolve/{revision}/{name}", DEST / "upstream-hf" / name, 2097152))
    commit = "e3158ea011d4235245a547460d3688d7ccbf9900"
    records.append(fetch(f"https://api.github.com/repos/scicode-bench/SciCode/zipball/{commit}", DEST / "upstream-code.zip", 33554432))
    write_new(sources / "receipt.json", {"records": records, "hf_revision": revision, "code_revision": commit,
                                       "test_activity_or_expected_numeric_values_inspected": False})
    print(json.dumps({"downloaded": sum(r.get("bytes", 0) for r in records), "files": len(records),
                      "hf_revision": revision, "status": "PASS" if all(r["status"] == "PASS_TRANSPORT_ONLY" for r in records) else "FAIL"}))


if __name__ == "__main__":
    main()
