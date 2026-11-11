"""Record completed author inspection of all final pages and figure views."""

import re
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write
from pypdf import PdfReader


def main():
    paper = read(PUBLIC / "manuscript-build-v2.json")
    assert paper["pages"] == 11 and sha(ROOT / paper["pdf"]) == paper["pdf_sha256"]
    reader = PdfReader(ROOT / paper["pdf"])
    uris = set()
    for page in reader.pages:
        for reference in page.get("/Annots", []):
            action = reference.get_object().get("/A")
            if action:
                action = action.get_object()
                if "/URI" in action:
                    uris.add(str(action["/URI"]))
    expected = set(re.findall(r"https?://[^\s<>)]+", (ROOT / paper["markdown"]).read_text(encoding="utf-8")))
    assert len(expected) == 9 and uris == expected, (uris, expected)
    stamp = datetime.now(timezone.utc).isoformat()
    write(PUBLIC / "manuscript-visual-review-v2.json", {
        "status": "PASS_AUTHOR_ALL_PAGE_VISUAL_REVIEW", "utc": stamp,
        "pdf": paper["pdf"], "pdf_sha256": paper["pdf_sha256"],
        "pages_reviewed": list(range(1, 12)),
        "rendered_images": {f"page-{n:02}.png": sha(TASK / "manuscript-render-v2" / f"page-{n:02}.png") for n in range(1, 12)},
        "checks": ["All eleven rendered pages inspected individually at original resolution.",
                   "Methods, family-results and delivered-product headings now stay with their following content.",
                   "System labels fit their table column; figure leaders identify B1/B2/P correctly at publication width.",
                   "Actual counts, planned denominators, NA empty-claim rates and matched anchor denominators remain explicit.",
                   "Degenerate zero interval is qualified; gate opportunity was zero; current product task failure remains stated.",
                   "All nine actual PDF link annotations match the source URLs; no required content is clipped or replaced by missing glyphs."],
        "verified_pdf_link_targets": sorted(uris),
        "reviewer_scope": "Author visual/editorial self-check, not independent expert, biological or real-user validation",
        "earlier_failed_edition_preserved": True
    }, True)
    files = {p.relative_to(ROOT).as_posix(): sha(p) for p in (PUBLIC / "result-figures-v2").glob("*") if p.suffix in (".svg", ".png")}
    for filename in ("01-control-flow.svg", "01-control-flow.png"):
        path = PUBLIC / "figures-v2" / filename
        files[path.relative_to(ROOT).as_posix()] = sha(path)
    write(PUBLIC / "result-figures-visual-review-v2.json", {
        "status": "PASS_AUTHOR_COLOR_GRAYSCALE_AND_INSERTION_REVIEW", "utc": stamp, "files": files,
        "views_reviewed": ["Both quantitative figures in full-resolution color and grayscale.",
                           "Control-flow diagram and both result figures in manuscript-v2 pages5,6 and8."],
        "checks": ["B0/B1/B2/P remain visible; counts and min/max seed ranges agree with fixed analysis.",
                   "Displaced latency labels now have leaders; open P marker exposes the clustered B2 triangle.",
                   "Font size, contrast and bounds remain readable; logarithmic time axis is stated; no point was jittered or moved.",
                   "No causal laboratory-cost or external-population equivalence claim is made."],
        "frozen_result_values_changed": False, "reviewer_scope": "Author project visual review only",
        "earlier_failed_edition_preserved": True
    }, True)
    print("Recorded final all-page and color/grayscale/insertion author reviews; nine PDF links verified")


if __name__ == "__main__":
    main()
