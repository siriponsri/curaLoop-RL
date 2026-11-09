"""Retrieve the official open paper into private reading storage, no dataset."""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.common import TASK, new, sha, utility_finish, utility_start


def main():
    guard = utility_start("primary-reading", 120, 240)
    try:
        url = "https://raw.githubusercontent.com/mlresearch/v267/main/assets/regol25a/regol25a.pdf"
        folder = TASK / "literature"
        folder.mkdir(exist_ok=False)
        target = folder / "regol25a.pdf"
        with urllib.request.urlopen(url, timeout=45) as response, target.open("xb") as output:
            size = 0
            while block := response.read(1048576):
                size += len(block)
                assert size <= 24 * 1024**2
                output.write(block)
        assert target.read_bytes()[:5] == b"%PDF-"
        import fitz

        document = fitz.open(target)
        pages = [page.get_text() for page in document]
        with (folder / "regol25a-text.txt").open("x", encoding="utf-8") as file:
            for i, text in enumerate(pages):
                file.write(f"\nPAGE {i+1}\n{text}\n")
        new(folder / "receipt-v1.json", {"url": url, "sha256": sha(target), "bytes": size,
                                         "pages": len(pages), "all_pages_read_claim": False,
                                         "source": "official PMLR linked open PDF", "dataset_download": False})
        for i in range(min(6, len(pages))):
            print(f"PAGE {i+1}\n" + pages[i][:6500])
        utility_finish("primary-reading", guard, "PASS")
    except BaseException:
        utility_finish("primary-reading", guard, "FAIL")
        raise


if __name__ == "__main__":
    main()
