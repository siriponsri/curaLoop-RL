"""English AgentRD guide and manuscript PDFs from actual retained evidence."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/agent-rd-run-20261110-v1"
PUBLIC = ROOT / "docs/evidence/agent-rd-20261110-v1"
MANUAL = ROOT / "docs/manual/CuraLoop-AgentRD-Guide-EN-v1.pdf"
POPPLER = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"
INK = colors.HexColor("#29282b")
MUTED = colors.HexColor("#655e57")
COPPER = colors.HexColor("#a6492d")
RULE = colors.HexColor("#ded8d0")
W, H = A4
LEFT, WIDTH = 44, A4[0] - 88


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def text(c, value, x, top, width, *, size=10.5, available=650, color=MUTED):
    style = ParagraphStyle("body", fontName="Helvetica", fontSize=size, leading=size * 1.48, textColor=color)
    paragraph = Paragraph(value, style)
    _, height = paragraph.wrap(width, available)
    assert height <= available, "Text exceeds reserved page region"
    paragraph.drawOn(c, x, top - height)
    return top - height - 12


def page(c, number, heading):
    c.setFillColor(COPPER)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(LEFT, H - 38, "CURALOOP-RL / AGENT RD / ENGLISH GUIDE")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 23)
    assert c.stringWidth(heading, "Helvetica-Bold", 23) <= WIDTH
    c.drawString(LEFT, H - 76, heading)
    c.setStrokeColor(RULE)
    c.line(LEFT, 38, W - LEFT, 38)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(LEFT, 24, "Internal research prototype | English guide v1 | 10 November 2026")
    c.drawRightString(W - LEFT, 24, str(number))
    return H - 106


def screenshot(c, path, top, *, width=WIDTH, max_height=500, x=LEFT, crop=None):
    source = Image.open(path)
    # Document-layout crop only. Original actual screenshot bytes are preserved.
    if crop:
        source = source.crop(crop(source.size))
    scale = min(width / source.width, max_height / source.height)
    dw, dh = source.width * scale, source.height * scale
    c.drawImage(ImageReader(source), x, top - dh, width=dw, height=dh, mask="auto")
    return top - dh - 14


def table(c, rows, top, widths, header):
    c.setStrokeColor(RULE)
    c.line(LEFT, top, W - LEFT, top)
    y = top - 18
    for i, value in enumerate(header):
        text(c, "<b>" + escape(value) + "</b>", LEFT + sum(widths[:i]), y, widths[i] - 10, size=9.5, available=40, color=INK)
    y -= 28
    c.line(LEFT, y + 8, W - LEFT, y + 8)
    for row in rows:
        ends = [text(c, escape(value), LEFT + sum(widths[:i]), y, widths[i] - 10, size=9.5, available=y - 60) for i, value in enumerate(row)]
        y = min(ends) - 7
    c.line(LEFT, y + 5, W - LEFT, y + 5)
    return y - 14


def manual():
    marker = read(TASK / "supervisor-v1/receipts/pdf-marker-20261110.json")
    assert marker["exit_code"] == 0  # One successful two-document operation marker; never rerun it here.
    assert read(PUBLIC / "browser-acceptance-v1.json")["status"] == "PASS_ACTUAL_LOCALHOST_REAL_MODEL_ACCEPTANCE"
    assert read(PUBLIC / "browser-refinement-v2.json")["status"] == "PASS_SERVED_UI_REFINEMENT_NO_NEW_INFERENCE"
    assert not MANUAL.exists(), "Preserve an existing edition; use an explicit revision operation"
    screens = PUBLIC / "screens-v2"
    MANUAL.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(MANUAL), pagesize=A4, pageCompression=1)
    c.setTitle("CuraLoop AgentRD - English Operator Guide v1")
    c.setAuthor("CuraLoop-RL")
    c.setSubject("Actual localhost model mission, source checks and recorded evidence")

    top = page(c, 1, "From question to evidence")
    top = text(c, "A bounded pharmaceutical evidence mission, from a research question to an inspectable local report. The screenshots show an actual Typhoon 12B CPU-model run, not a generated interface or a mocked agent result.", LEFT, top, WIDTH, size=12)
    top = screenshot(c, screens / "03-agent-result-detail-en.png", top, max_height=270, crop=lambda s: (0, 0, s[0], min(s[1], 410)))
    top = text(c, "<b>What the workbench does</b><br/>Read the admitted historical CF1 aggregates. Let the real model answer or request a fixed calculation. Check released numbers against those sources. Preserve the trace and export an EN/TH dossier when explicitly requested.", LEFT, top, WIDTH)
    top = text(c, "<b>What the numbers mean</b><br/>H is the mean number of historical confirmed-positive observations. D is the mean number of positive fixed structure groups. HB and DB are fractions per confirmation. These are not new experiments, monetary savings or clinical outcomes.", LEFT, top, WIDTH)
    text(c, "<b>Important:</b> a source-correct answer can still fail the user's task. Review the question, required fields, scope and refusal behavior as well as the numbers.", LEFT, top, WIDTH, color=INK)
    c.showPage()

    top = page(c, 2, "Start a bounded mission")
    top = text(c, "Start the repository's Windows web launcher, open its printed localhost URL, then choose <b>Agent mission control</b>. A direct visit to <b>/agent</b> does not create a simulator campaign or call a model.", LEFT, top, WIDTH)
    screenshot(c, screens / "02-agent-recorded-result-en.png", top, x=LEFT, width=220, max_height=480,
               crop=lambda s: (284, 283, 614, min(s[1], 1003)))
    x, width = LEFT + 242, WIDTH - 242
    for value in [
        "<b>1. State a question.</b><br/>Ask for a historical comparison, a budget tradeoff or the limits of the available evidence. Specific requested quantities make completeness easier to check.",
        "<b>2. Choose a campaign and budget.</b><br/>The equal-campaign view averages six campaigns within each historical seed. A single AID pair uses only that campaign. Read the selected-method roster before running.",
        "<b>3. Choose execution mode.</b><br/>Real model uses the active authorized CPU session through SSH. Deterministic mode computes the table without a model. There is no paid fallback.",
        "<b>4. Choose export intent.</b><br/>Allow a local immutable dossier before starting if you want to export this mission. Then select <b>Run research mission</b> once.",
    ]:
        top = text(c, value, x, top, width, available=top - 90)
    text(c, "CPU responses can take several minutes. Closing the browser tab does not cancel a bounded mission. Use the mission link to follow its actual state.", LEFT, 132, WIDTH, available=70)
    c.showPage()

    top = page(c, 3, "Read values and their provenance")
    top = text(c, "This actual acceptance mission made two model calls and two tool receipts. Its authored question passed a separate direct-CSV task check. This one example is development evidence, not a success-rate estimate.", LEFT, top, WIDTH)
    top = screenshot(c, screens / "03-agent-result-detail-en.png", top, max_height=470)
    top = text(c, "<b>Read the key:</b> b10 means the selected 10% confirmation budget. a0 and a1 refer to the displayed method roster. A delta is a1 minus a0; a budget sweep uses the last selected budget minus the first. Source operands are rounded to three decimals first.", LEFT, top, WIDTH, available=top - 65)
    text(c, "The evidence identity links the answer to its exact source packet. Full source-file SHA-256 identities are retained in the trace and dossier. Open the scope disclosure before using a conclusion.", LEFT, top, WIDTH, available=top - 55)
    c.showPage()

    top = page(c, 4, "Trace actions, failures and fallback")
    top = screenshot(c, screens / "02-agent-recorded-result-en.png", top, max_height=260,
                     crop=lambda s: (638, 283, 1404, 646))
    for value in [
        "<b>Open The evidence trail.</b> Events expand during execution and collapse after completion. The trusted controller performs the initial source read; this is not a tool autonomously chosen by the model. A model can request the fixed compute adapter while it is useful.",
        "<b>Inspect receipts and unverified proposals.</b> A saved model proposal is not a verified scientific result. The release check, raw response and exact call identity are separate records. Model calls and token counters show recorded work; failed calls can have unknown actual token cost.",
        "<b>Keep failed attempts.</b> The controller permits at most three model calls. It can request correction or return an explicitly labeled deterministic abstention after exhaustion. Such fallback is not automatically task success.",
        "<b>Understand the known limitation.</b> In development, the model answered a forbidden final16 request with permitted aggregate numbers. The numerical source check passed, but the task failed. No final16 or private row was accessed. The workbench does not establish unrestricted refusal reliability.",
    ]:
        top = text(c, value, LEFT, top, WIDTH, available=top - 60)
    c.showPage()

    top = page(c, 5, "Export an explicit local dossier")
    top = screenshot(c, screens / "03-agent-result-detail-en.png", top, max_height=230,
                     crop=lambda s: (0, max(0, s[1] - 330), s[0], s[1]))
    top = text(c, "Select <b>Prepare local dossier</b> on a completed mission with export intent. Then open the EN/TH report or download its structured files. The server rechecks the sources and released claims before exporting. Nothing is sent to a team tool or public service.", LEFT, top, WIDTH)
    top = table(c, [
        ("report-en.html / report-th.html", "Bilingual local reports with identical values and source identity."),
        ("dossier.json", "Structured selection, released claims, limitations and recorded cost."),
        ("trace.json", "Actual mission events, requests, responses and tool receipts."),
        ("manifest.json", "File lengths and SHA-256 identities for the four content files."),
    ], top, [170, WIDTH - 170], ["File", "Purpose"])
    text(c, "Application immutability means no silent overwrite: an altered existing bundle is rejected. This is not a cryptographic signature, trusted external timestamp or protection from an administrator who can replace every file.", LEFT, top, WIDTH, available=top - 55)
    c.showPage()

    top = page(c, 6, "Resume work and respect the boundary")
    for value in [
        "<b>Open Recorded local missions.</b> Choosing a saved mission restores its question and filters. Reading it does not regenerate the response. Actual acceptance included a server restart and confirmed the same completed row with no extra model call.",
        "<b>Interrupted work needs explicit reconciliation.</b> The application marks unfinished work as recoverable after restart. Use Reconcile and resume. A completed response is recovered by its exact call ID; an unresolved generation is not silently repeated as a new attempt. Failed attempts remain recorded.",
        "<b>Live inference needs an active resource session.</b> During locked evaluation the model is reserved and ad-hoc model missions are disabled. After research-worker cleanup/account closure, recorded evidence and deterministic mode remain available. Do not reopen a closed ledger. A future operator-owned live session requires fresh authorization and configuration.",
        "<b>The admitted data are narrow.</b> Six exposed development campaigns share one annotation-connected component. Missing confirmation is excluded, nonpositive mixes inactive and inconclusive, and the five-seed range is not a biological confidence interval. Round-robin D=H is mechanical at these budgets.",
        "<b>Protected data remain closed.</b> The tools do not expose final16, individual private CF1 compounds, hidden or pending outcomes, simulator mutation, arbitrary code or external write actions. This evidence does not establish prospective discovery, real-user benefit or commercial data clearance.",
    ]:
        top = text(c, value, LEFT, top, WIDTH, available=top - 60)
    top = text(c, "The original screening simulator, Confirmation evidence and local C Workspace remain separate evidence tracks. Their earlier outcomes and negative scientific findings are preserved.", LEFT, top, WIDTH, available=top - 55)
    c.showPage()

    top = page(c, 7, "Quick reference and troubleshooting")
    top = table(c, [
        ("COMPLETED", "An answer was released. Check task completeness and scope; the label alone is not proof of a correct decision."),
        ("ABSTAINED", "No supported answer was released. Inspect the reason and whether abstention was appropriate for the question."),
        ("FAILED", "Execution failed. The partial trace remains; no mock result or alternative paid provider substitutes for it."),
        ("INTERRUPTED_RECOVERABLE", "Review the previous trace, then explicitly reconcile. Do not create a replacement attempt to hide the interrupted one."),
        ("Model session unavailable", "Use saved evidence or deterministic mode. An operator must authorize a new bounded session for later live inference."),
        ("Source or dossier integrity error", "Preserve the original file and error. Do not edit a pinned source or replace its expected hash merely to pass."),
    ], top, [168, WIDTH - 168], ["State / message", "Meaning and next action"])
    top = text(c, "<b>Evidence and reproducibility</b><br/>The repository evidence index links the actual screenshots, original model mission, five-file dossier, failed development canaries, component checks and frozen computational protocol. The locked study reports all planned attempts, fallback and costs. Author checks are not independent expert or user validation.", LEFT, top, WIDTH, available=top - 85)
    text(c, "This guide adds Agent RD to the existing Dashboard Guide v3 and Confirmation Evidence Guide v4. It does not change historical assay results, the sealed-data boundary or the limits of the underlying studies.", LEFT, top, WIDTH, size=9.5, available=top - 55)
    c.save()
    reader = PdfReader(MANUAL)
    assert len(reader.pages) == 7
    extracted = "\n".join(p.extract_text() for p in reader.pages)
    assert all(value in extracted for value in ("From question to evidence", "Quick reference", "final16", "Deterministic", "source-correct"))
    assert "\ufffd" not in extracted
    mirror = ROOT / "output/pdf" / MANUAL.name
    mirror.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(MANUAL, mirror)
    source_pins = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in screens.glob("*.png")}
    write(PUBLIC / "manual-build-v1.json", {"status": "CREATED_AWAITING_RENDERED_PAGE_REVIEW", "pages": 7,
          "path": MANUAL.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(MANUAL.read_bytes()).hexdigest(),
          "source_screenshots": source_pins, "new_model_inference": False, "independent_expert_validation": False})
    print(json.dumps({"status": "CREATED_AWAITING_VISUAL_REVIEW", "pages": 7, "path": str(MANUAL)}))


def render_manual():
    target = TASK / "manual-render-v1"
    target.mkdir(exist_ok=False)
    result = subprocess.run([str(POPPLER), "-r", "110", "-png", str(MANUAL), str(target / "page")], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert len(list(target.glob("page-*.png"))) == 7
    print(json.dumps({"status": "RENDERED_SEVEN_PAGES_REVIEW_PENDING", "folder": str(target)}))


if __name__ == "__main__":
    if sys.argv[1] == "manual":
        manual()
    elif sys.argv[1] == "render-manual":
        render_manual()
    else:
        raise SystemExit("Manuscript authoring follows actual locked analysis, never invented results")
