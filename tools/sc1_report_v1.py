"""Render the actual admission report, or reconstruct its counts offline only."""
import argparse
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.sc1_control_v1 import ACCOUNT, PUBLIC, ROOT, digest, write_new

MD = ROOT / "docs/07_publication/LR_SC1_SCICODE_ADMISSION_MANUSCRIPT_EN_20261113.md"
PDF = MD.with_suffix(".pdf")


def verify():
    output = {}
    for version in (1, 2):
        receipt = json.loads((PUBLIC / f"native-qualification-v{version}.json").read_text(encoding="utf-8"))
        data = receipt["worker_result"]["validation_native_results"]
        by_main = defaultdict(list)
        for row in data:
            by_main[row["step_id"].split(".")[0]].append(row["status"] == "PASS")
        output[version] = {"passed": sum(row["status"] == "PASS" for row in data), "total": len(data),
                           "main_passed": sum(all(flags) for flags in by_main.values()), "main_total": len(by_main),
                           "per_main": {key: [sum(flags), len(flags)] for key, flags in by_main.items()}}
    if (output[1]["passed"], output[2]["passed"], output[2]["total"], output[2]["main_passed"]) != (26, 28, 29, 5):
        raise ValueError("Source counts differ; never alter a report to hide this")
    gate = json.loads((PUBLIC / "gate1-v1.json").read_text())
    if gate["agent_model_calls"] != 0 or gate["primary_effect"] is not None:
        raise ValueError("Unexpected efficacy evidence")
    text = MD.read_text(encoding="utf-8")
    for identity in output[1]["per_main"]:
        first = output[1]["per_main"][identity]
        second = output[2]["per_main"][identity]
        row = f"| {identity} | {first[0]}/{first[1]} | {second[0]}/{second[1]} |"
        if row not in text:
            raise ValueError("Manuscript table differs from a retained source row")
    return {"status": "PASS_OFFLINE_AUDIT_RECONSTRUCTION", "counts": output, "model_inference": "NOT_RUN", "primary_effect": "NOT_ESTIMABLE"}


def build():
    import pypdfium2 as pdfium
    import pdfplumber
    from PIL import Image as PILImage
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
    from reportlab.graphics import renderSVG, renderPDF
    result = verify()
    if PDF.exists():
        raise FileExistsError("Keep the inspected manuscript immutable; version a replacement")
    figures = PUBLIC / "figures"
    figures.mkdir(exist_ok=False)
    qa = ACCOUNT / "pdf-qa-v1"
    qa.mkdir(exist_ok=False)
    write_new(qa / "visual-spec.json", {
        "claim": "Native reference qualification stopped the run before agent inference",
        "form": "Execution-status diagram and exact-value tables", "diagram_width_pt": 487,
        "metric": "Native reference checks passed", "denominator": "Same 29 validation subproblems in two technical attempts; not independent samples",
        "uncertainty": "Not estimated; descriptive conformance counts, not sampled agent efficacy",
        "palette": "Near-black/gray plus owner-approved plum #7C354B and semantic risk rust",
        "references": "Local scientific table grammar, no vertical rules; official system-card visual asset was unavailable through web due size",
        "minimum_type_pt": 8.5})
    draw = Drawing(487, 103)
    stages = [("Question review", "PASS", "#7C354B"), ("Official assets", "RECEIVED", "#666666"),
              ("Native references", "NO_GO: 28/29", "#B5473C"), ("Agent comparison", "NOT_RUN", "#666666")]
    for i, (label, state, color) in enumerate(stages):
        x = i * 125 + 1
        draw.add(Rect(x, 25, 110, 60, fillColor=colors.white, strokeColor=colors.HexColor(color), strokeWidth=.8))
        draw.add(String(x + 55, 62, label, fontName="Helvetica", fontSize=9, textAnchor="middle", fillColor=colors.HexColor("#171717")))
        draw.add(String(x + 55, 41, state, fontName="Helvetica-Bold", fontSize=9, textAnchor="middle", fillColor=colors.HexColor("#171717")))
        if i < 3:
            draw.add(Line(x + 112, 55, x + 120, 55, strokeColor=colors.HexColor("#777777"), strokeWidth=.7))
            draw.add(Polygon([x+123, 55, x+119, 57.4, x+119, 52.6], fillColor=colors.HexColor("#777777"), strokeColor=None))
    renderSVG.drawToFile(draw, str(figures / "admission-flow-v1.svg"))
    svg = figures / "admission-flow-v1.svg"
    svg.write_bytes(svg.read_bytes().replace(b"<title>...</title>", b"<title>LR-SC1 stopped before agent inference</title>").replace(b"<desc>...</desc>", b"<desc>Native reference readiness failed at 28 of 29 checks; agent comparison was not run.</desc>"))
    renderPDF.drawToFile(draw, str(qa / "figure-render.pdf"))
    figure_document = pdfium.PdfDocument(str(qa / "figure-render.pdf"))
    figure_document[0].render(scale=2).to_pil().save(figures / "admission-flow-v1.png")
    image = PILImage.open(figures / "admission-flow-v1.png")
    image.convert("L").save(qa / "figure-grayscale.png")
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=10, leading=14.2, spaceAfter=8,
                          textColor=colors.HexColor("#171717"), splitLongWords=True)
    title = ParagraphStyle("Title", parent=body, fontName="Helvetica-Bold", fontSize=22, leading=27, spaceAfter=17)
    heading = ParagraphStyle("Heading", parent=body, fontName="Helvetica-Bold", fontSize=13, leading=18, spaceBefore=8, spaceAfter=9, keepWithNext=True)
    cell = ParagraphStyle("Cell", parent=body, fontSize=9.2, leading=12, spaceAfter=0)
    numeric_cell = ParagraphStyle("NumericCell", parent=cell, alignment=2)
    def para(text, style=body):
        value = html.escape(text)
        value = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", value)
        value = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', value)
        return Paragraph(value, style)
    flow, buffer, table_lines = [], [], []
    def flush():
        if buffer:
            flow.append(para(" ".join(buffer)))
            buffer.clear()
    def table_flush():
        if not table_lines:
            return
        rows = [[text.strip() for text in line.strip().strip("|").split("|")] for line in table_lines]
        rows = [row for row in rows if not all(re.fullmatch(r"[:\- ]+", col) for col in row)]
        content = [[para(value, numeric_cell if len(row) == 3 and j > 0 else cell) for j, value in enumerate(row)] for row in rows]
        widths = [169, 159, 159] if len(rows[0]) == 3 else [203, 284]
        table = Table(content, colWidths=widths, repeatRows=1, hAlign="LEFT")
        instructions = [("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0),
                        ("RIGHTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 6),
                        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                        ("LINEABOVE", (0,0), (-1,0), .8, colors.HexColor("#171717")),
                        ("LINEBELOW", (0,0), (-1,0), .4, colors.HexColor("#777777")),
                        ("LINEBELOW", (0,-1), (-1,-1), .8, colors.HexColor("#171717"))]
        table.setStyle(TableStyle(instructions))
        flow.extend([table, Spacer(1, 9)])
        table_lines.clear()
    for line in MD.read_text(encoding="utf-8").splitlines() + [""]:
        if line.startswith("|"):
            flush()
            table_lines.append(line)
            continue
        table_flush()
        if line.strip() == "<!-- page -->":
            flush()
            flow.append(PageBreak())
        elif line.startswith("!["):
            flush()
            flow.append(draw)
        elif line.startswith("# "):
            flush()
            flow.append(para(line[2:], title))
        elif line.startswith("## "):
            flush()
            flow.append(para(line[3:], heading))
        elif not line.strip():
            flush()
        else:
            buffer.append(line.strip())
    def footer(canvas, document):
        canvas.setStrokeColor(colors.HexColor("#D8D8D4"))
        canvas.line(54, 40, A4[0]-54, 40)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.setFont("Helvetica", 8.5)
        canvas.drawString(54, 27, "CuraLoop-RL | LR-SC1 admission report | 13 November 2026")
        canvas.drawRightString(A4[0]-54, 27, str(document.page))
    SimpleDocTemplate(str(PDF), pagesize=A4, leftMargin=54, rightMargin=54, topMargin=45, bottomMargin=55,
                      title="SciCode pre-inference admission report", author="Siripon Srihangpiboon").build(flow, onFirstPage=footer, onLaterPages=footer)
    document = pdfium.PdfDocument(str(PDF))
    text_document = pdfplumber.open(PDF)
    pages, tiles, outside = [], [], []
    for number, page in enumerate(document):
        path = qa / f"page-{number+1:02d}.png"
        page.render(scale=1.5).to_pil().save(path)
        picture = PILImage.open(path).convert("RGB")
        picture.thumbnail((448, 634))
        tiles.append(picture.copy())
        text_page = text_document.pages[number]
        for word in text_page.extract_words():
            if min(word["x0"], word["top"]) < 0 or word["x1"] > text_page.width + .5 or word["bottom"] > text_page.height + .5:
                outside.append({"page": number+1, "text": word["text"]})
        pages.append({"page": number+1, "text_characters": len(text_page.extract_text() or ""), "render": str(path.relative_to(ROOT))})
    sheet = PILImage.new("RGB", (448*3, 650*((len(tiles)+2)//3)), "#DDDDDD")
    for i, picture in enumerate(tiles):
        sheet.paste(picture, ((i % 3)*448, (i // 3)*650))
    sheet.save(qa / "contact-sheet.png")
    plain = "\n".join(page.extract_text() or "" for page in text_document.pages)
    if outside or "[[" in plain or "NOT_ESTIMABLE" not in plain or "28/29" not in plain:
        raise RuntimeError("PDF structural evidence/layout check failed")
    write_new(qa / "structural-qa.json", {"status": "PASS_STRUCTURAL_PENDING_VISUAL_REVIEW", "pages": pages, "outside_page_spans": outside,
                                          "pdf_sha256": digest(PDF), "source_sha256": digest(MD), "audit_reconstruction": result,
                                          "visual_review": "REQUIRED"})
    print(json.dumps({"status": "BUILT_REQUIRES_VISUAL_REVIEW", "pages": len(document), "pdf": str(PDF), "contact_sheet": str(qa / "contact-sheet.png")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify())) if args.verify_only else build()
