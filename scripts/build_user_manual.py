"""Build the English operator PDF from genuine loaded application captures.

Requires optional requirements-docs.txt; run screenshot capture before authoring.
"""

import json
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/readme-manual-v1/browser"
CAPTURES = EVIDENCE / "manual"
OUT = ROOT / "docs/manual/CuraLoop-RL-User-Manual-EN.pdf"
W, H = landscape(A4)
INK = colors.HexColor("#16333B")
TEAL = colors.HexColor("#087F72")
MUTED = colors.HexColor("#526653")
PAPER = colors.HexColor("#F7F9F8")
MINT = colors.HexColor("#E6F3EB")
RULE = colors.HexColor("#DCE5E1")
REPO = "https://github.com/siriponsri/curaLoop-RL/blob/main/"

PAGES = [
    ("Start locally", "quickstart", None),
    ("Read the workbench", "overview", "01-overview"),
    ("Configure a campaign", "scenario", "02-scenario"),
    ("Select and reserve", "pending", "04-pending-ledger"),
    ("Advance and receive results", "delivered", "05-delivered-ledger"),
    ("Inspect decisions", "decisions", "05-decisions"),
    ("Explore compounds", "compounds", "06-compound-explorer"),
    ("Compare independent policies", "compare", "07-comparison-results"),
    ("Check research evidence", "evidence", "08-evidence"),
    ("Export and resume JSON", "exports", "08-export-resume"),
    ("Open saved campaigns", "saved", "09-saved-campaigns"),
    ("Recover a saved revision", "revisions", "09-revision-recovery"),
    ("Understand the screening loop", "loop", None),
    ("Understand the architecture", "architecture", None),
    ("Present the project", "presentation", "10-presentation"),
    ("Interpret historical and synthetic data", "science", None),
    ("Back up and troubleshoot", "recovery", None),
    ("Verification and reference", "reference", None),
]

CONTENT = {
    "overview": (
        "Begin with the data-origin badge, the active scenario and the live campaign counts.",
        [
            "Historical assay data and synthetic fixtures have different meanings.",
            "Only delivered new active outcomes count as confirmed hits.",
            "Enter Simulation lab or design a scenario; both use the same campaign.",
        ],
    ),
    "scenario": (
        "Use Scenario builder to create a fresh independent campaign. The tutorial keeps seed 42 unchanged.",
        [
            "Choose HIV or a synthetic dataset and a selection policy.",
            "Set budget, queue capacity, feedback delay, jitter and missingness.",
            "Scroll down and select Create campaign to apply changes; editing alone does not.",
        ],
    ),
    "pending": (
        "Select next batch proposes candidates and accepts valid assay requests. Pending labels stay hidden.",
        [
            "With budget 5 and batch capacity 5, this batch reserves all 5 units.",
            "Spent stays 0; reserved is 5; available is 0 until feedback settles.",
            "Inspect due steps and selection explanations. Predictions are not outcomes.",
        ],
    ),
    "delivered": (
        "Advance +1 step moves simulated time. With delay 2, two advances deliver the selected batch.",
        [
            "The historical example delivered 5 assays and found 0 new active hits.",
            "Reserved returns to 0 and spent becomes 5. Budget is never charged twice.",
            "Complete run finishes remaining work; Reset creates a fresh state with revisions retained.",
        ],
    ),
    "decisions": (
        "Read predicted probabilities, observed status and explanations separately. They answer different questions.",
        [
            "Unrevealed, pending, observed active, observed inactive and missing are distinct.",
            "Probabilities are uncalibrated model estimates, not confirmed biological activity.",
            "Verify replay checks public history; the event timeline records accepted actions and outcomes.",
        ],
    ),
    "compounds": (
        "Compound explorer uses public descriptors and revealed results. Genuine structures come from historical SMILES.",
        [
            "Search by compound ID, filter status, choose sorting and move between pages.",
            "Inspect opens details; Escape closes the dialog and returns focus.",
            "Synthetic fixtures have numerical descriptors and no invented molecular drawings.",
        ],
    ),
    "compare": (
        "Benchmark arena executes fresh independent campaigns under matched conditions, including the active scenario seed.",
        [
            "Select policies and run the comparison; wait for actual completion.",
            "Read new hits, spent units and actual controller fallback / learned-request usage.",
            "Saved comparisons survive restart. Recorded HIV charts are separate historical evidence.",
        ],
    ),
    "evidence": (
        "Research evidence exposes provenance, implementation identity, model limitations and recovery tools.",
        [
            "Check dataset release, hashes, label semantics and seed-selection rules.",
            "Review weak held-out performance and synthetic-only controller training.",
            "Use the cited primary sources; current simulation output is not clinical validation.",
        ],
    ),
    "exports": (
        "A single-run JSON is portable recovery. Comparison JSON and CSV have different purposes.",
        [
            "Download JSON for the current campaign; CSV is its public event ledger.",
            "Choose the single-run JSON and select Validate & resume.",
            "Validation reconstructs pending requests and event history; invalid imports preserve the active run.",
        ],
    ),
    "saved": (
        "The primary web app saves accepted actions automatically in local SQLite. No cloud account is required.",
        [
            "Use Saved campaigns & recovery to open a previous campaign.",
            "Refresh saved campaigns updates the list; current campaigns are labelled.",
            "Export before explicit deletion. Deletion permanently removes the saved campaign and revisions.",
        ],
    ),
    "revisions": (
        "Inspect saved revisions lets you recover earlier validated state, including after Reset or a damaged current row.",
        [
            "Choose a campaign, then select a saved revision.",
            "Recover selected revision creates a new independent campaign.",
            "The original record remains intact. Recovery and active campaign actions are serialized.",
        ],
    ),
    "presentation": (
        "Guided presentation uses the live campaign. It provides a 5-7 minute story rather than scripted success metrics.",
        [
            "Explain the decision and distinguish historical labels from simulated operations.",
            "Demonstrate selection, delayed feedback and the public audit trail.",
            "Finish with matched comparisons, exports and the recorded controller fallback limitation.",
        ],
    ),
}


def para(c, value, x, top, width, size=11, color=INK, leading=None):
    style = ParagraphStyle(
        "p",
        fontName="Helvetica",
        fontSize=size,
        leading=leading or size * 1.42,
        textColor=color,
        alignment=TA_LEFT,
    )
    p = Paragraph(value, style)
    _, height = p.wrap(width, 1000)
    p.drawOn(c, x, top - height)
    return top - height


def footer(c, number):
    c.setStrokeColor(RULE)
    c.line(44, 43, W - 44, 43)
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawString(44, 26, "CURALOOP-RL  /  ENGLISH USER MANUAL  /  v0.3")
    c.drawRightString(W - 44, 26, f"{number:02d} / {len(PAGES) + 2:02d}")


def header(c, title, key, number, subtitle=""):
    c.bookmarkPage(key)
    c.addOutlineEntry(title, key, level=0)
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(44, H - 32, "OPERATOR GUIDE / RESEARCH WORKBENCH")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(44, H - 68, title)
    if subtitle:
        para(c, escape(subtitle), 44, H - 84, W - 88, 11, MUTED)
    footer(c, number)


def picture(c, path, x=44, y=108, width=None, height=350, frame=True):
    width = width or W - 88
    reader = ImageReader(str(path))
    iw, ih = reader.getSize()
    ratio = min(width / iw, height / ih)
    dw, dh = iw * ratio, ih * ratio
    if frame:
        c.setFillColor(colors.white)
        c.setStrokeColor(RULE)
        c.roundRect(x, y, width, height, 6, fill=1, stroke=1)
    c.drawImage(reader, x + (width - dw) / 2, y + (height - dh) / 2, dw, dh, mask="auto")


def instructions(c, steps):
    col = (W - 112) / 3
    for k, value in enumerate(steps):
        para(
            c,
            f'<font color="#087F72"><b>{k + 1:02d}</b></font>  {escape(value)}',
            44 + k * (col + 12),
            89,
            col,
            9,
        )


def bullets(c, items, x, top, width, size=12, gap=12):
    for index, item in enumerate(items):
        top = (
            para(
                c,
                f'<font color="#087F72"><b>{index + 1:02d}</b></font>  {item}',
                x,
                top,
                width,
                size,
            )
            - gap
        )
    return top


def main():
    result = json.loads((EVIDENCE / "browser-result.json").read_text())
    assert result["status"] == "PASS"
    assert result["axe_violation_count"] == 0
    assert not any(
        result[k] for k in ("browser_errors", "horizontal_overflow", "blocked_external_requests")
    )
    for _, key, name in PAGES:
        if name:
            assert (CAPTURES / f"{name}.png").is_file(), key
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
    c.setTitle("CuraLoop-RL - English User Manual")
    c.setAuthor("CuraLoop-RL independent research project")
    c.setSubject("Local retrospective screening simulator: operation, evidence and recovery")
    c.setKeywords("CuraLoop-RL, user manual, retrospective screening, localhost, English")
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    picture(c, ROOT / "assets/branding/curaloop-logo-v2.png", 44, H - 156, 350, 112, False)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(48, H - 188, "ENGLISH USER MANUAL  /  LOCALHOST POC  /  v0.3")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 42)
    c.drawString(44, H - 252, "Screening decisions.")
    c.drawString(44, H - 302, "Traceable evidence.")
    para(
        c,
        "Operate the research workbench, follow delayed assay feedback and recover your campaigns with confidence.",
        44,
        H - 333,
        650,
        16,
        MUTED,
    )
    c.setFillColor(MINT)
    c.roundRect(44, 96, W - 88, 54, 7, fill=1, stroke=0)
    para(
        c,
        "<b>LOCAL CPU</b> &nbsp;&nbsp; / &nbsp;&nbsp; <b>HISTORICAL + SYNTHETIC</b> &nbsp;&nbsp; / &nbsp;&nbsp; <b>DURABLE PUBLIC STATE</b>",
        62,
        129,
        W - 124,
        10,
        TEAL,
    )
    para(
        c,
        "Independent personal research portfolio. Not an official GPO system or a validated Digital Twin.\nPrepared 4 November 2026. Screenshots come from the actual English application.",
        44,
        76,
        W - 88,
        9,
        MUTED,
    )
    footer(c, 1)
    c.showPage()

    header(
        c,
        "Your path through the workbench",
        "contents",
        2,
        "Click a section to jump to it. Use your PDF viewer's bookmarks to return.",
    )
    for index, (title, key, _) in enumerate(PAGES):
        col = index // 9
        row = index % 9
        x = 44 + col * 392
        y = H - 146 - row * 42
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, f"{index + 3:02d}")
        c.setFillColor(INK)
        c.setFont("Helvetica", 12)
        c.drawString(x + 32, y, title)
        c.linkRect("", key, (x, y - 7, x + 365, y + 18), relative=0, thickness=0)
    c.showPage()

    for number, (title, key, name) in enumerate(PAGES, start=3):
        if key in CONTENT:
            summary, steps = CONTENT[key]
            header(c, title, key, number, summary)
            picture(c, CAPTURES / f"{name}.png")
            instructions(c, steps)
        elif key == "quickstart":
            header(
                c,
                title,
                key,
                number,
                "Windows first. One address for the interface and API. No Node.js is needed for the bundled release.",
            )
            bullets(
                c,
                [
                    "Install 64-bit Python 3.12 if needed. The verified release ran on Windows 11 / Python 3.12.10.",
                    "Open the project folder and double-click <b>Start-CuraLoop-Web.cmd</b>. First use installs project-local dependencies.",
                    "Open <b>http://127.0.0.1:8000</b>. Keep the launcher terminal open; Ctrl+C stops the service.",
                ],
                44,
                H - 143,
                350,
                13,
                20,
            )
            c.setFillColor(MINT)
            c.roundRect(438, 180, 360, 248, 8, fill=1, stroke=0)
            para(c, "<b>Manual PowerShell alternative</b>", 458, 402, 320, 14)
            para(c, "From the source folder:", 458, 365, 320, 11, MUTED)
            para(
                c,
                "<font name='Courier'>.\\Setup-CuraLoop-Web.cmd<br/><br/>.\\Start-CuraLoop-Web.cmd</font>",
                458,
                334,
                320,
                12,
            )
            para(
                c,
                "Subsequent startup uses local data, models, fonts and built UI assets offline.",
                458,
                248,
                320,
                11,
            )
            para(
                c,
                "The illustrated tutorial uses budget 5 for a compact walkthrough; application defaults use budget 30. Both retain seed 42. Python 3.11 is supported by configuration but was not executed in this verification.",
                44,
                122,
                W - 88,
                10,
                MUTED,
            )
        elif key in ("loop", "architecture"):
            header(c, title, key, number)
            figure = "screening-loop" if key == "loop" else "architecture"
            picture(c, ROOT / f"docs/diagrams/{figure}.png", 44, 62, W - 88, 450, False)
        elif key == "science":
            header(
                c,
                title,
                key,
                number,
                "A source label changes what a result means. Simulated operational settings never become measured laboratory evidence.",
            )
            bullets(
                c,
                [
                    "<b>Historical HIV:</b> real retrospective assay labels and genuine molecular structures; simulated budget, capacity and timing.",
                    "<b>Synthetic fixture:</b> fictional descriptors and labels for engineering checks. No biological assay or molecular-structure claim.",
                    "<b>Missing outcome:</b> settles cost, but is neither an inactive label nor an active hit. It is excluded from training labels.",
                    "<b>Model limits:</b> uncalibrated probabilities and heuristic uncertainty. Recorded learned controllers used Greedy fallback on 300/300 historical requests each.",
                ],
                44,
                H - 143,
                W - 88,
                13,
                18,
            )
            observed = result["observed_status_checks"]["observed"]
            missing = result["observed_status_checks"]["missing"]
            c.setFillColor(MINT)
            c.roundRect(44, 85, W - 88, 84, 8, fill=1, stroke=0)
            para(
                c,
                f"<b>Actual synthetic verification examples:</b> observed fixture: {observed['confirmed_hits']} new hits / {observed['delivered_assays']} delivered; missing fixture: {missing['missing_assays']} missing / {missing['confirmed_hits']} hits. Both spent 18 simulated units. These are labelled fixtures, not new biological benchmarks.",
                62,
                145,
                W - 124,
                12,
            )
        elif key == "recovery":
            header(
                c,
                title,
                key,
                number,
                "Keep portable recovery copies and preserve damaged data. The primary web API uses one active server and one worker.",
            )
            bullets(
                c,
                [
                    "<b>Portable backup:</b> export single-run JSON. Comparison JSON has multiple reports; CSV is an event ledger. Neither resumes one campaign.",
                    "<b>Database backup:</b> stop the server cleanly, then copy <font name='Courier'>.local</font> with its database and any sidecar files.",
                    "<b>Interrupted comparison:</b> the saved job is marked interrupted, never silently rerun. Start a new comparison explicitly.",
                    "<b>Corrupt database:</b> stop and copy it before investigation. Point CURALOOP_STORAGE_PATH to a new file and validate a portable JSON; keep the original.",
                    "<b>Startup issues:</b> retry Setup after a download failure. Reconnect if the server is unavailable. A port conflict never authorizes killing another application.",
                ],
                44,
                H - 144,
                W - 88,
                13,
                15,
            )
            para(
                c,
                f'<a href="{REPO}START_WINDOWS.md" color="#087F72">Windows operator guide</a> &nbsp; | &nbsp; <a href="{REPO}docs/PERSISTENCE.md" color="#087F72">Persistence and recovery reference</a>',
                44,
                96,
                W - 88,
                11,
            )
        elif key == "reference":
            header(
                c,
                title,
                key,
                number,
                "The manual documents software operation. Its screenshots and verification are separate from frozen research benchmark evidence.",
            )
            bullets(
                c,
                [
                    "<b>Scientific scope:</b> retrospective research simulator. No clinical efficacy, GMP suitability, real savings or operational Digital Twin validation.",
                    "<b>Capture provenance:</b> actual Windows Chromium, 1440x1000 desktop and 390x844 mobile. New branding screenshots use isolated local test storage.",
                    "<b>Independent runs:</b> comparison policies share conditions but never share new outcomes. The example historical campaign retains its zero-hit result.",
                    "<b>Accessibility and limits:</b> keyboard/dialog/overflow and automated accessibility checks are exercised. Manual screenreader and physical-device checks remain unrun.",
                ],
                44,
                H - 144,
                W - 88,
                12,
                16,
            )
            links = [
                ("Installation and troubleshooting", "START_WINDOWS.md"),
                ("Evaluation and limitations", "docs/EVALUATION.md"),
                ("Research sources and dataset provenance", "docs/RESEARCH_BENCHMARKS.md"),
                ("Release verification", "docs/RELEASE_VERIFICATION.md"),
                ("Licenses and third-party attribution", "THIRD_PARTY_NOTICES.md"),
            ]
            y = 200
            for label, path in links:
                y = (
                    para(
                        c, f'<a href="{REPO}{path}" color="#087F72">{label}</a>', 44, y, W - 88, 11
                    )
                    - 8
                )
        else:
            raise AssertionError(key)
        c.showPage()
    c.save()
    manifest = {
        "pdf": str(OUT.relative_to(ROOT)),
        "page_count": len(PAGES) + 2,
        "capture_source": str(EVIDENCE.relative_to(ROOT)),
        "browser": result["browser_version"],
        "frontend_build_sha256": result["frontend_build_sha256"],
        "screenshots": "Actual program output; no generated UI mockups.",
        "sections": [title for title, _, _ in PAGES],
    }
    (OUT.parent / "manual-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Created {OUT.name}: {len(PAGES) + 2} pages with linked contents.")


if __name__ == "__main__":
    main()
