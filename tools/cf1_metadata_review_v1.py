"""Bounded author roster and official full-text retrieval, without data rows."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import finish, start
from tools.cf1_source_inventory_v1 import fetch


def main():
    commit = "04c58e85188e724ec5ff44cbed2e7b960f6f3df3"
    for name in ("Logs/dataset_metadata.csv", "Logs/README.md", "Scripts/README.md"):
        data = fetch(f"https://raw.githubusercontent.com/dahvida/AIC_Finder/{commit}/{name}",
                     "metadata/" + name, maximum=32768)
        print(name, len(data))
        print(data.decode("utf-8"))
    # Official open-access endpoints only; no challenge circumvention or purchase.
    for name, url in (
        ("oa.xml", "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC11046457"),
        ("bioc.xml", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC11046457/unicode"),
    ):
        try:
            data = fetch(url, "paper/" + name, maximum=2 * 1024**2)
            print("OFFICIAL_PAPER_RESPONSE", name, len(data), data[:160])
        except Exception as error:
            print("OFFICIAL_PAPER_UNAVAILABLE", name, type(error).__name__, str(error)[:160])


if __name__ == "__main__":
    guard = start("author-metadata-methods", 180, 600)
    try:
        main()
        finish("author-metadata-methods", guard, "PASS_RETRIEVAL_REVIEW_REQUIRED")
    except BaseException:
        finish("author-metadata-methods", guard, "FAIL")
        raise
