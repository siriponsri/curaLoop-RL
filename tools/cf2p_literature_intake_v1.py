"""Bounded free primary-paper copies for design review, not molecular intake."""

import hashlib
import json
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/lr-cf2p-20261110-v1"
PAPERS = [
    ("das2023", "https://proceedings.mlr.press/v206/nguyen23d/nguyen23d.pdf"),
    ("mfas2021", "https://proceedings.mlr.press/v139/nguyen21f/nguyen21f.pdf"),
    ("adaptive_submodularity", "https://arxiv.org/pdf/1003.3967"),
    ("batch_as2018", "https://proceedings.neurips.cc/paper_files/paper/2018/file/a7aeed74714116f3b292a982238f83d2-Paper.pdf"),
]


def main():
    folder = TASK / "reading"
    folder.mkdir(exist_ok=False)
    records = []
    for key, url in PAPERS:
        value = {"id": key, "url": url, "new_free_primary_full_text": True}
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "CuraLoop research reading/1.0"})
            with urllib.request.urlopen(request, timeout=35) as response:
                data = response.read(10 * 1024**2 + 1)
                assert len(data) <= 10 * 1024**2 and data.startswith(b"%PDF-")
                value["resolved_url"] = response.url
            path = folder / (key + ".pdf")
            path.write_bytes(data)
            pages = list(PdfReader(path).pages)
            (folder / (key + ".txt")).write_text("\n".join(f"\n=== PDF PAGE {i + 1} ===\n" + (p.extract_text() or "") for i, p in enumerate(pages)), encoding="utf-8", newline="\n")
            value.update(status="DOWNLOADED_TEXT_EXTRACTED_NOT_YET_ALL_READ", bytes=len(data),
                         sha256=hashlib.sha256(data).hexdigest(), pages=len(pages))
        except Exception as exc:
            value.update(status="UNAVAILABLE", error=repr(exc))
        records.append(value)
    assert sum(r.get("bytes", 0) for r in records) < 128 * 1024**2
    (folder / "intake.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
