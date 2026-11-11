"""Record the actually inspected first document edition; retain exact sources."""

from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write


def main():
    stamp = datetime.now(timezone.utc).isoformat()
    guide = read(PUBLIC / "manual-build-v2.json")
    paper = read(PUBLIC / "manuscript-build-v1.json")
    assert guide["pages"] == 8 and paper["pages"] == 11
    assert sha(ROOT / guide["path"]) == guide["sha256"]
    assert sha(ROOT / paper["pdf"]) == paper["pdf_sha256"]
    write(PUBLIC / "manual-visual-review-v2.json", {
        "status": "PASS_AUTHOR_RENDERED_PAGE_REVIEW", "utc": stamp,
        "pdf": guide["path"], "pdf_sha256": guide["sha256"],
        "pages_reviewed": list(range(1, 9)),
        "rendered_images": {f"page-{n}.png": sha(TASK / "manual-render-v2" / f"page-{n}.png") for n in range(1, 9)},
        "review": "All eight rendered pages inspected individually at original resolution: readable instructions/controls, source-key explanations, explicit saved-evidence behavior, local exports and scope limits; no clipped required content or replacement glyphs observed.",
        "reviewer_scope": "Author project self-check; not independent expert or real-user validation"
    }, True)
    figures = [p for p in (PUBLIC / "result-figures-v1").glob("*") if p.suffix in (".png", ".svg")]
    write(PUBLIC / "result-figures-visual-review-v1.json", {
        "status": "FAIL_AUTHOR_LABEL_ASSOCIATION_REQUIRES_LAYOUT_REVISION", "utc": stamp,
        "files": {p.relative_to(ROOT).as_posix(): sha(p) for p in figures},
        "color_and_grayscale_reviewed": ["02-task-completion", "03-cost-completion"],
        "findings": ["Completion figure is readable with all four controls, denominators and non-CI seed ranges.",
                     "Latency figure displaces B1/P labels near clustered points without leader lines; association is ambiguous in standalone and manuscript views.",
                     "Revise leaders/marker fill or layout only. Preserve all data, original figures and this unsuccessful review."],
        "reviewer_scope": "Author rendered visual review, not scientific or independent validation"
    }, True)
    write(PUBLIC / "manuscript-visual-review-v1.json", {
        "status": "FAIL_AUTHOR_VISUAL_LAYOUT_REVIEW", "utc": stamp,
        "pdf": paper["pdf"], "pdf_sha256": paper["pdf_sha256"],
        "pages_reviewed": list(range(1, 12)),
        "findings": ["Every rendered page inspected individually; numerical tables and candid negative-result scope are readable.",
                     "Displaced Figure3 labels are ambiguous and need the revised figure.",
                     "Headings are stranded at the ends of pages1,8 and9.",
                     "Table3 splits A-NOREPAIR across lines; widen the first column.",
                     "Polish joined words such as full32, The312, fixed256 and inference.46; describe the current model mission's failed task in plain language."],
        "reviewer_scope": "Author project visual/editorial review; not independent expert or user validation"
    }, True)
    preserved = PUBLIC / "authoring-source-v1"
    preserved.mkdir(exist_ok=False)
    copies = {}
    for step, filename in ((6, "agent_rd_documents_v1.py"), (8, "agent_rd_result_figures_v1.py"),
                           (9, "agent_rd_preview_reproduction_v1.py"), (10, "agent_rd_manuscript_v1.py")):
        folder = TASK / "postrun-documents-host-resume-v1" / f"step-{step}-sources"
        source = folder / filename
        assert sha(source) == read(folder / "source-pins.json")[filename]
        target = preserved / (filename + ".txt")
        target.write_bytes(source.read_bytes())
        assert sha(target) == sha(source)
        copies[target.relative_to(ROOT).as_posix()] = sha(target)
    write(PUBLIC / "first-edition-authoring-source-v1.json", {
        "status": "RETAINED_EXACT_EXECUTED_FIRST_EDITION_AUTHORING_SOURCES", "files": copies,
        "guide_edition": "v2", "figure_and_manuscript_edition": "v1", "scientific_results_changed": False,
        "note": "Text suffix marks verbatim source evidence; the original bytes are unchanged."
    }, True)
    print("Recorded eight-page guide PASS and first-figure/manuscript layout FAIL; exact executed sources retained")


if __name__ == "__main__":
    main()
