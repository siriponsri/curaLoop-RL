"""Verify and extract selected methods from the owner's existing reading room."""

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/lr-cf2p-20261110-v1"
PUBLIC = ROOT / "docs/evidence/lr-cf2p-20261110-v1"


def main():
    registry = json.loads((ROOT / "docs/02_literature/literature_manifest.json").read_text(encoding="utf-8"))
    records = []
    for key, pages in [("R04", (2, 3, 4)), ("R10", (2, 3, 4)), ("R11", (2, 3, 4))]:
        row = next(r for r in registry["records"] if r["id"] == key)
        path = Path.home() / "Documents/ChatGPT/Drug Discovery/literature/pdfs" / row["private_reading_filename"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == row["pdf_sha256"]
        pdf = PdfReader(path)
        text = "\n".join(f"=== PHYSICAL PDF PAGE {i} ===\n" + pdf.pages[i - 1].extract_text() for i in pages)
        (TASK / "reading" / f"existing-{key}-methods.txt").write_text(text, encoding="utf-8", newline="\n")
        records.append({"id": key, "title": row["title"], "landing": row["landing"], "sha256": digest,
                        "physical_pdf_pages_extracted_for_review": list(pages),
                        "existing_owner_reading_room": True, "downloaded_this_goal": False,
                        "read_depth": "EXTRACTED_FOR_TARGETED_METHOD_REVIEW_NOT_END_TO_END"})
    (PUBLIC / "existing-reading-identity-v1.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
