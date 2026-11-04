"""Fetch three public NCATS challenge training files, never challenge test data."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research/raw_data/ncats-development-20261104"
SOURCES = {
    "ahr": {
        "download_id": "nr-ahrsmiles",
        "aid": 743122,
        "endpoint": "AhR pathway activity",
        "family": "AHR",
    },
    "pparg": {
        "download_id": "nr-ppar-gammasmiles",
        "aid": 743140,
        "endpoint": "PPAR-gamma signaling agonism",
        "family": "PPARG",
    },
    "p53": {
        "download_id": "sr-p53smiles",
        "aid": 720552,
        "endpoint": "p53 pathway activity",
        "family": "TP53",
    },
}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    receipts = []
    for name, meta in SOURCES.items():
        url = "https://tripod.nih.gov/tox21/challenge/download?id=" + meta["download_id"] + "&sec="
        path = RAW / (name + ".smiles")
        if path.exists():
            raise ValueError(
                "Source already exists; verify its saved receipt rather than overwrite: "
                + str(path)
            )
        with urlopen(url, timeout=45) as response:
            content = response.read(20_000_001)
            headers = {
                "content_type": response.headers.get("Content-Type"),
                "last_modified": response.headers.get("Last-Modified"),
                "etag": response.headers.get("ETag"),
            }
        if len(content) > 20_000_000:
            raise ValueError("Source exceeds the bounded download size.")
        lines = content.decode("utf-8-sig").splitlines()
        if (
            not lines
            or not headers["content_type"].startswith("text/plain")
            or any(len(line.split("\t")) != 3 for line in lines)
        ):
            raise ValueError(
                "Unexpected public training-file format; do not treat an HTML/login response as data."
            )
        path.write_bytes(content)
        receipt = {
            "task": name,
            **meta,
            "url": url,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            **headers,
            "format": "tab-separated SMILES, source_id, binary_activity; no header",
            "rows": len(lines),
        }
        receipts.append(receipt)
        print(json.dumps(receipt, indent=2))
        (RAW / (name + "-receipt.json")).write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
    (RAW / "source-receipts.json").write_text(
        json.dumps(receipts, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
