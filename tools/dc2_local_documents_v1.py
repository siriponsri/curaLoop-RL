"""Build English guide/report from actual receipts and real application captures."""
import csv
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, KeepTogether

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write

ACCENT = "#7C354B"  # Owner's existing non-green brand preference overrides generic teal defaults.
INK = "#171717"
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("BodyLocal", fontName="Helvetica", fontSize=10, leading=15, textColor=colors.HexColor(INK), spaceAfter=9, splitLongWords=True))
styles.add(ParagraphStyle("TitleLocal", parent=styles["BodyLocal"], fontSize=24, leading=30, spaceAfter=20, textColor=colors.HexColor(ACCENT)))
styles.add(ParagraphStyle("HeadingLocal", parent=styles["BodyLocal"], fontName="Helvetica-Bold", fontSize=14, leading=20, spaceBefore=15, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle("SubLocal", parent=styles["HeadingLocal"], fontSize=11, leading=16))
styles.add(ParagraphStyle("CodeLocal", parent=styles["BodyLocal"], fontName="Courier", fontSize=8.5, leading=12, backColor=colors.HexColor("#F7F5F3")))
styles.add(ParagraphStyle("NoteLocal", parent=styles["BodyLocal"], fontSize=9, leading=13, textColor=colors.HexColor("#5E5654")))


def paragraph(text, style="BodyLocal"):
    text = text.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", ": ")
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', text)
    return Paragraph(text, styles[style])


def markdown(text, *, title=True):
    flow, buffer, code = [], [], False
    def flush():
        if buffer:
            flow.append(paragraph(" ".join(buffer), "CodeLocal" if code else "BodyLocal"))
            buffer.clear()
    for line in text.splitlines():
        if line.startswith("```"):
            flush()
            code = not code
        elif code:
            if line.strip():
                flow.append(paragraph(line, "CodeLocal"))
        elif not line.strip():
            flush()
        elif line.startswith("#"):
            flush()
            level = len(line) - len(line.lstrip("#"))
            flow.append(paragraph(line.lstrip("# "), "TitleLocal" if level == 1 and title else "HeadingLocal" if level <= 2 else "SubLocal"))
        elif re.match(r"^(?:[-*] |[0-9]+\. )", line):
            flush()
            buffer.append(line)
        else:
            buffer.append(line)
    flush()
    return flow


def image(path, width=487, height=550):
    with PILImage.open(path) as im:
        ratio = min(width / im.width, height / im.height)
        return Image(str(path), im.width * ratio, im.height * ratio)


def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor("#D8D8D4"))
    canvas.line(54, 40, A4[0] - 54, 40)
    canvas.setFillColor(colors.HexColor("#5E5654"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(54, 27, "CuraLoop-RL | Local workflow | 13 November 2026 | Author engineering evidence")
    canvas.drawRightString(A4[0] - 54, 27, str(doc.page))


def build_pdf(path, flow):
    assert not path.exists()
    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=54, rightMargin=54, topMargin=48, bottomMargin=56, title=path.stem, author="Siripon Srihangpiboon").build(flow, onFirstPage=footer, onLaterPages=footer)


def case_table(rows):
    content = [["Request / language", "State", "Selected", "Calls", "Tokens", "Wall (s)"]]
    short = {"molecular_weight_max": "MW <=100", "logp_max": "LogP <=0", "tpsa_max": "TPSA <=0"}
    for r in rows:
        field, locale = r["case"].rsplit("-", 1)
        content.append([short[field] + " / " + locale.upper(), r["status"], r["selected_count"], r["provider_attempts"], r["generated_tokens"], f"{float(r['observed_wall_seconds']):.3f}"])
    table = Table(content, colWidths=[129, 93, 60, 43, 53, 75], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),9),("LEADING",(0,0),(-1,-1),13),("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9),("LEFTPADDING",(0,0),(-1,-1),0),("ALIGN",(2,0),(-1,-1),"RIGHT"),("LINEABOVE",(0,0),(-1,0),.8,colors.HexColor(INK)),("LINEBELOW",(0,0),(-1,0),.5,colors.HexColor("#888888")),("LINEBELOW",(0,-1),(-1,-1),.8,colors.HexColor(INK))]))
    return table


def main():
    summary = read(PUBLIC / "descriptive-analysis-v1.json")
    assert read(PUBLIC / "product-browser-v5.json")["status"] == "PASS_ACTUAL_SERVED_WORKFLOW_EN_TH"
    assert read(PUBLIC / "model-product-browser-v1.json")["status"] == "PASS_ACTUAL_MODEL_SAVED_REOPEN_NO_NEW_INFERENCE"
    figures = PUBLIC / "figures-v2"
    figures.mkdir(exist_ok=False)
    spec = {"claim": "Native admission misses the predefined repository-diversity minimum", "form": "Horizontal observed/required dot comparison", "metric": "Qualified count within each prespecified rule", "unit": "count", "category_order": ["Development tasks", "Evaluation candidates", "Evaluation lineages"], "observed": [1,6,3], "required": [1,6,4], "uncertainty": "Not a random sample; exact bounded readiness counts, no interval", "dimensions_mm": [178,100], "palette_override": "Owner-approved burgundy instead of generic teal", "source": "native-admission-final-v1.json", "references": ["GPT-6 Astra system card table/figure grammar", "Professional evaluation table", "Append-only context diagram", "Deployment simulation bars with uncertainty"], "formats": ["svg","pdf","png"]}
    write(figures / "visual-spec-v1.json", spec)
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":9,"axes.spines.top":False,"axes.spines.right":False,"axes.spines.left":False,"axes.edgecolor":"#AAAAAA","axes.linewidth":.6,"text.color":INK,"axes.labelcolor":INK,"xtick.color":"#5E5654","ytick.color":INK,"svg.fonttype":"none"})
    fig, ax = plt.subplots(figsize=(178/25.4,100/25.4))
    fig.subplots_adjust(left=.29,right=.96,top=.68,bottom=.18)
    fig.text(.06,.94,"Native readiness stops before the agent comparison",fontsize=11,fontweight="semibold",ha="left")
    fig.text(.06,.87,"One prespecified diversity requirement remains unmet",fontsize=9,color="#5E5654",ha="left")
    y = [2,1,0]
    ax.scatter(spec["required"],y,s=65,marker="D",facecolors="white",edgecolors="#777777",linewidths=1,label="Required minimum",zorder=2)
    ax.scatter(spec["observed"],y,s=33,color=ACCENT,label="Observed qualified",zorder=3)
    ax.set_yticks(y,spec["category_order"])
    ax.tick_params(axis="y",length=0,pad=12)
    ax.set_xlim(0,7); ax.set_ylim(-.6,2.7); ax.set_xticks(range(8)); ax.set_xlabel("Qualified count (each rule assessed separately)",labelpad=9)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles,labels,loc="upper left",bbox_to_anchor=(.05,.80),frameon=False,ncol=2,fontsize=8.5)
    ax.text(3,.32,"3 observed",ha="center",va="center",fontsize=8.5,color=ACCENT)
    ax.text(4,-.32,"4 required",ha="center",va="center",fontsize=8.5,color="#666666")
    fig.text(.06,.035,"Exact counts from a selected subset; not agent success rates or independent publication counts.",fontsize=8,color="#5E5654")
    for extension in ("svg","pdf","png"):
        fig.savefig(figures / ("native-readiness."+extension),dpi=300,facecolor="white")
    plt.close(fig)
    with PILImage.open(figures / "native-readiness.png") as im:
        im.convert("L").save(TASK / "native-readiness-grayscale-v2.png")
    rows = list(csv.DictReader((PUBLIC / "tables-v2/author-model-cases.csv").open(encoding="utf-8")))
    manual = ROOT / "docs/manual/CuraLoop-Local-Molecular-Workflow-Guide-EN-v2.pdf"
    paper = ROOT / "docs/07_publication/CuraLoop-Local-Workflow-Feasibility-EN-v2.pdf"
    flow = markdown((ROOT / "docs/08_agent_rd/LOCAL_WORKFLOW_GUIDE_EN_20261113.md").read_text(encoding="utf-8"))
    screens = PUBLIC / "model-product-screens-v1"
    flow += [PageBreak(), paragraph("A saved actual model request", "TitleLocal"), paragraph("The model translated MW <=100 while other defaults stayed unchanged. This capture was made after the lease stopped; the disabled button correctly shows the model is offline.","NoteLocal"), image(screens / "request-en.png",width=245,height=640)]
    flow += [PageBreak(), paragraph("Inspect and collect actual results", "TitleLocal"), paragraph("Seven input rows yield five valid structures, two rejected rows and two within-limit compounds. The molecule drawing and table come from the completed RDKit process."),image(screens / "compounds-en.png",height=350),Spacer(1,18), image(screens / "status-en.png",height=100),paragraph("Choose a compound ID to inspect its 2D structure. Review report.html, selected.csv, rejected.csv, evidence.json and manifest.json, then download bundle.zip. Reopening a saved result does not repeat inference.","NoteLocal")]
    # Give the screenshot footer its own paragraph breathing room.
    for index, item in enumerate(flow):
        if isinstance(item, Image) and index + 1 < len(flow) and isinstance(flow[index + 1], Paragraph):
            flow.insert(index + 1, Spacer(1, 10))
    build_pdf(manual,flow)
    text = (ROOT / "docs/07_publication/LOCAL_WORKFLOW_FEASIBILITY_20261113.md").read_text(encoding="utf-8")
    first, second = text.split("## 4. Limitations and interpretation",1)
    flow = markdown(first)
    flow += [paragraph("Table 1. Frozen author software cases", "HeadingLocal"), case_table(rows), Spacer(1,12), paragraph(f"All {summary['author_cases_passed']}/{summary['author_cases_attempted']} cases passed the frozen engineering checks; deterministic conformance passed 3/3. Twelve genuine product responses generated {summary['actual_product_generated_tokens']} tokens with {summary['actual_prompt_tokens']} prompt tokens. All responses recorded nonzero GPU residency. No case was repeated. These related author-selected cases are not an independent scientific sample.","NoteLocal"),paragraph("Timing covers sequential end-to-end job observation, including a cold first model request. No EN/TH or agent/control speed comparison is inferred. Model container observed CPU: 89.452 seconds; actual allocated GPU-container wall: 123.461 seconds. Retained CPU/GPU lease reservations were 2,400/1,200 seconds; local controller work is separate.","NoteLocal"),paragraph("Figure 1. The native admission gate did not pass", "HeadingLocal"),image(figures / "native-readiness.png",width=487,height=300),paragraph("Qualified evaluation candidates occupy three source-repository lineages against the required four. The threshold remained unchanged. No locked agent program generation or comparative estimate followed.","NoteLocal")]
    flow += markdown("## 4. Limitations and interpretation"+second,title=False)
    build_pdf(paper,flow)
    qa = TASK / "pdf-qa-v2"
    qa.mkdir(exist_ok=False)
    outputs = []
    poppler = shutil.which("pdftoppm")
    assert poppler
    for path in (manual,paper):
        reader = PdfReader(path)
        assert all(p.extract_text().strip() for p in reader.pages)
        folder = qa / path.stem
        folder.mkdir()
        subprocess.run(["rtk","proxy",poppler,"-scale-to","1500","-png",str(path),str(folder / "page")],check=True,timeout=120)
        outputs.append({"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path),"pages":len(reader.pages),"renders":str(folder)})
    write(PUBLIC / "document-build-v2.json",{"status":"PASS_CREATED_TEXT_AND_RENDERED_NOT_YET_VISUALLY_REVIEWED","outputs":outputs})
    print(json.dumps(outputs))

if __name__ == "__main__":
    main()
