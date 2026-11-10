"""English CF1 operator-guide addendum using the final actual application captures."""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from cf2p_admin_v1 import PUBLIC, ROOT, TASK, write
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

OUTPUT = ROOT / "docs/manual/CuraLoop-RL-Confirmation-Evidence-Guide-EN-v4.pdf"
SCREENS = PUBLIC / "screens-v4"
INK = colors.HexColor("#29282b")
MUTED = colors.HexColor("#655e57")
COPPER = colors.HexColor("#a6492d")


def paragraph(c, text, x, top, width, size=11, max_height=500):
    style = ParagraphStyle("body", fontName="Helvetica", fontSize=size,
                           leading=size * 1.48, textColor=MUTED, spaceAfter=0)
    p = Paragraph(text, style)
    _, height = p.wrap(width, max_height)
    if height > max_height:
        raise ValueError("Manual paragraph exceeds its reserved region")
    p.drawOn(c, x, top - height)
    return top - height - 12


def title(c, number, heading, size):
    width, height = size
    c.setPageSize(size)
    c.setFillColor(COPPER)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(36, height - 34, f"CURALOOP-RL / CONFIRMATION EVIDENCE / {number:02d}")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 25)
    assert c.stringWidth(heading, "Helvetica-Bold", 25) <= width - 72
    c.drawString(36, height - 68, heading)
    c.setStrokeColor(colors.HexColor("#ded8d0"))
    c.line(36, 33, width - 36, 33)
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawString(36, 20, "English operator-guide addendum v4 | 10 November 2026 | Internal research prototype")
    c.drawRightString(width - 36, 20, str(number))


def screenshot(c, name, x, y, max_width, max_height):
    path = SCREENS / name
    image = ImageReader(str(path))
    w, h = image.getSize()
    ratio = min(max_width / w, max_height / h)
    c.drawImage(image, x, y, width=w * ratio, height=h * ratio, preserveAspectRatio=True, mask="auto")
    return path, w * ratio, h * ratio


def main():
    qa = json.loads((PUBLIC / "browser-check-v4.json").read_text(encoding="utf-8"))
    assert qa["status"] == "PASS_ACTUAL_PRODUCTION_BROWSER" and len(qa["views"]) == 70
    assert qa["chart_geometry"]["mobile-th"]["labels_inside_viewbox"]
    marker = TASK / "pdf-operation-started.json"
    if not marker.exists():
        script = Path.home() / ".codex/plugins/cache/openai-primary-runtime/pdf/26.1104.22356/skills/pdf/container_tools/mark_artifact_operation_started.mjs"
        result = subprocess.run(["rtk", "proxy", "node", str(script), "--operation-kind", "create",
                                 "--expected-output-count", "1", "--output-format", "pdf"], capture_output=True, text=True, check=True)
        write(marker, {"status": "SUCCESS", "exit_code": result.returncode, "expected_output_count": 1, "format": "pdf"}, True)
    # The successful marker immediately precedes the first PDF authoring operation.
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=landscape(A4), pageCompression=1)
    c.setTitle("CuraLoop-RL Confirmation Evidence - English Guide v4")
    c.setAuthor("CuraLoop-RL")
    c.setSubject("Recorded CF1 study, truthful comparison and local C Workspace export")
    wide = landscape(A4)

    title(c, 1, "Open evidence without starting an experiment", wide)
    screenshot(c, "01-confirmation-desktop-en.png", 36, 65, 500, 395)
    top = 480
    for text in [
        "<b>1. Start the local application.</b><br/>Use the repository's existing Windows launcher. Open <b>Confirmation evidence</b> in the sidebar, or use the CF1 entry on Discovery Overview or Benchmark Arena.",
        "<b>2. Read the scope.</b><br/>Six exposed development campaigns, 6,896 historical assay-specific supported confirmations, and 18 ranker/operator arms. These study totals stay separate from the active simulator campaign.",
        "<b>3. Explore safely.</b><br/>A direct visit to <b>/confirmation</b> needs no simulator campaign. Viewing, filtering and downloading this study do not create, retrain or reset a campaign.",
        "This addendum complements the Dashboard Guide v3. The existing four-screen simulator and its pending-result protections remain available.",
    ]:
        top = paragraph(c, text, 558, top, 245, max_height=top - 55)
    paragraph(c, "Actual served-production screenshot. The source values are historical; no new experiment is shown.", 36, 53, 755, size=9, max_height=20)
    c.showPage()

    title(c, 2, "Read the hit and coverage tradeoff", wide)
    screenshot(c, "02-tradeoff-en.png", 36, 59, 390, 445)
    top = 491
    for text in [
        "<b>H: confirmed positives.</b> Newly selected positives recovered by the recorded portfolio; this is an assay count, not clinical efficacy.",
        "<b>D: positive structure groups.</b> Fixed structure groups containing at least one confirmed positive. It is an assay-specific structural proxy, not proof of a validated lead series.",
        "<b>Read both axes together.</b> Moving upward means more positive groups; moving right means more positive observations. A higher D can come with fewer H. No universal winner is asserted.",
        "<b>Inspect a point or table row.</b> The selected ranker uses copper; other rankers remain visible in gray. Shapes identify top-ranked, group round-robin and classical MaxMin portfolios.",
        "<b>Whiskers are observed seed ranges.</b> Five fixed repetitions describe this conditional computation. They are not confidence intervals across independent biological targets.",
    ]:
        top = paragraph(c, text, 454, top, 345, max_height=top - 52)
    c.showPage()

    title(c, 3, "Choose filters and export a comparison brief", wide)
    screenshot(c, "03-selected-arm-en.png", 36, 60, 286, 444)
    top = 490
    for text in [
        "<b>Campaign.</b> Choose an AID primary/confirmation pair or the equal-campaign mean. The mean first averages the six campaigns within each fixed seed; it does not turn them into independent biological replicates.",
        "<b>Budget.</b> Choose 1%, 2%, 5%, 10% or 20% of the supported universe. Exact integer B differs by campaign and is listed under <b>Source provenance and exact budgets</b>. Mean B is not one physical batch.",
        "<b>All 18 arms remain visible.</b> The table retains unfavorable outcomes. On a narrow screen, scroll horizontally for every metric. D(FP) is the predefined fingerprint-group sensitivity.",
        "<b>H/B and D/B.</b> These are observed counts per confirmation. Equal-campaign ratios are averaged per campaign; do not divide mean H by mean B and assume the same answer.",
        "<b>Export comparison brief.</b> Download JSON with the exact campaign, budget, selected ranker/operator, all 18 arms, limitations and immutable source hashes. It is a historical comparison, not a compound list or laboratory instruction.",
    ]:
        top = paragraph(c, text, 351, top, 448, max_height=top - 51)
    c.showPage()

    title(c, 4, "Use the additive local C Workspace tools", wide)
    screenshot(c, "09-c-workspace-en.png", 36, 75, 493, 384)
    top = 490
    for text in [
        "<b>confirmation_inspect</b> returns the same validated aggregate comparison as the API. <b>confirmation_export</b> creates an immutable bilingual brief in the host-configured local workspace.",
        "Both tools use the same fixed source adapter. English and Thai files preserve identical filters and numerical evidence. No external delivery is performed.",
        "The local bundle contains two HTML views, two JSON briefs and a manifest. Reopening verifies expected contents from authenticated inputs; editing a copied report and its adjacent manifest cannot make it valid.",
        "The native stdio entry point and configuration example are documented in the Integration Guide. They are optional local tools, not a configured paid agent or a connected team system.",
    ]:
        top = paragraph(c, text, 558, top, 245, max_height=top - 55)
    paragraph(c, "Actual local exported report, AID 628/677, 5%, RF / group round-robin. The page scrolls to all 18 arms.", 36, 58, 755, size=9, max_height=24)
    c.showPage()

    title(c, 5, "Switch language. Keep the comparison.", A4)
    screenshot(c, "06a-confirmation-mobile-th-viewport.png", 36, 105, 280, 610)
    top = 720
    for text in [
        "<b>English and Thai.</b><br/>Use EN or the Thai button in the header. Campaign, budget and selected arm remain unchanged.",
        "<b>On mobile.</b><br/>Use the menu button for navigation. Scroll down for the selected arm and export. The comparison table has its own horizontal scroll.",
        "<b>Keyboard.</b><br/>Use Tab to reach controls. Press Enter or Space on a chart point; each arm also has a table button. Focus returns to the changed filter after its result loads.",
        "<b>Reduced motion.</b><br/>The existing application respects the system preference. Scientific counts are displayed directly rather than animated through invented intermediate values.",
    ]:
        top = paragraph(c, text, 340, top, 216, size=10.5, max_height=top - 70)
    c.showPage()

    title(c, 6, "Unavailable evidence and study limits", A4)
    top = 734
    for text in [
        "<b>If evidence is unavailable</b><br/>The page shows an explicit source/API error and no replacement metrics. Confirm that the local application is running, then use Retry study. Keep the original diagnostic when requesting help. Do not replace pinned inputs or hashes to conceal a mismatch.",
        "<b>Visibility</b><br/>CF1 supplies aggregate observations only. It adds no CF1 compound rows, private structures, individual assay outcomes, fabricated queue events or model-update events to Compound Explorer or the simulator.",
        "<b>Interpretation</b><br/>All six campaigns are exposed development data. Missing confirmation is excluded, and source nonpositive includes inactive or inconclusive. Round-robin has D=H mechanically at these budgets. No new selector, independent confirmation benefit, RL superiority, laboratory savings or clinical efficacy is established.",
        "<b>Provenance</b><br/>The source is the author-processed AIC_Finder snapshot 04c58e85188e724ec5ff44cbed2e7b960f6f3df3. Numeric AID pairs govern; 13 of 17 SI/repository aliases conflict. Internal derived-report preparation does not establish raw redistribution or commercial data clearance.",
        '<b>References</b><br/><a href="https://doi.org/10.1021/acscentsci.3c01517" color="#a6492d">Published MVS-A source paper</a><br/><a href="https://github.com/dahvida/AIC_Finder/tree/04c58e85188e724ec5ff44cbed2e7b960f6f3df3" color="#a6492d">Pinned author repository</a><br/>Repository: docs/05_product/CF1_INTEGRATION_GUIDE_20261110.md<br/>Original operating guide: CuraLoop-RL-Dashboard-Guide-EN-v3.pdf',
        "<b>Verification and limit</b><br/>This guide uses actual final served-build and local-export captures. Automated/developer checks cover all 70 language/campaign/budget combinations. This is not a representative-user study, production qualification or publication-readiness certification.",
    ]:
        top = paragraph(c, text, 36, top, 520, max_height=top - 55)
    c.save()
    reader = PdfReader(OUTPUT)
    text = "\n".join(p.extract_text() or "" for p in reader.pages)
    assert len(reader.pages) == 6 and all(term.lower() in text.lower() for term in ("Confirmation", "70", "6,896", "D(FP)", "final", "References"))
    renders = TASK / "manual-v4-render-r2"
    renders.mkdir(exist_ok=False)
    executable = shutil.which("pdftoppm")
    assert executable, "Poppler is required for final visual review"
    subprocess.run([executable, "-scale-to", "1400", "-png", str(OUTPUT), str(renders / "page")], check=True)
    assert len(list(renders.glob("page-*.png"))) == 6
    write(PUBLIC / "manual-generation-v2.json", {"status": "PASS_GENERATED_REOPENED_RENDERED_VISUAL_REVIEW_PENDING",
          "output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
          "pages": 6, "actual_final_capture_source": "screens-v4", "all_pages_rendered_with_poppler": True,
          "old_manual_v3_unchanged": True}, True)
    print(f"PASS generated, reopened and rendered six-page English guide: {OUTPUT}")


if __name__ == "__main__":
    main()
