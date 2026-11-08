"""Build the English four-screen guide from verified real application captures."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'docs/evidence/four-screen-dashboard-20261108-v1'
OUTPUT = ROOT / 'docs/manual/CuraLoop-RL-Dashboard-Guide-EN-v3.pdf'
INK = colors.HexColor('#28282b')
COPPER = colors.HexColor('#a6492d')
MUTED = colors.HexColor('#6a6661')
STYLES = {
    'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=30, leading=36, textColor=INK, spaceAfter=12),
    'heading': ParagraphStyle('heading', fontName='Helvetica-Bold', fontSize=20, leading=25, textColor=INK, spaceAfter=8),
    'body': ParagraphStyle('body', fontName='Helvetica', fontSize=11, leading=17, textColor=MUTED, spaceAfter=8, alignment=TA_LEFT),
    'small': ParagraphStyle('small', fontName='Helvetica', fontSize=9, leading=13, textColor=MUTED, spaceAfter=6),
    'label': ParagraphStyle('label', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=COPPER, spaceAfter=10),
}


def para(text, style='body'):
    return Paragraph(text, STYLES[style])


def image(name):
    # A real 1440x1000 viewport, with no screenshot-content substitutions.
    path = MEDIA / name
    assert path.exists(), path
    return Image(str(path), width=510, height=510 * 1000 / 1440, kind='direct', hAlign='LEFT')


def footer(canvas, doc):
    width, _ = landscape(A4)
    canvas.setStrokeColor(colors.HexColor('#ded8d0'))
    canvas.line(36, 33, width - 36, 33)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(36, 20, 'CuraLoop-RL | English operator guide | 8 November 2026 | Research prototype')
    canvas.drawRightString(width - 36, 20, str(doc.page))


def main():
    OUTPUT.parent.mkdir(exist_ok=True, parents=True)
    story = [para('CURALOOP-RL / OPERATOR GUIDE', 'label'), para('A clearer view of screening decisions.', 'title'),
             para('Four connected screens. Actual Python-engine state. English and Thai interfaces.'), Spacer(1, 16)]
    rows = [
        ['01  Discovery Overview', 'Understand the current pool, simulated budget and observed results.'],
        ['02  Digital Twin Simulation Lab', 'Select, queue, deliver and inspect the next decision. Retrospective Simulator.'],
        ['03  Benchmark Arena', 'Compare existing policies; distinguish single-seed output from recorded variability.'],
        ['04  Compound Explorer', 'Search structures, status and selection history without seeing hidden labels.'],
    ]
    table = Table([[para(a, 'label'), para(b)] for a, b in rows], colWidths=[240, 520])
    table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
                               ('LINEBELOW', (0, 0), (-1, -1), .5, colors.HexColor('#e4e0da'))]))
    story += [table, Spacer(1, 20), para('Before you begin', 'heading'),
              para('Start the local application using the repository quick-start instructions. The default historical HIV campaign contains 1,200 compounds and a budget of 30 simulated cost units. Synthetic fixtures are explicitly labeled. These are prototype settings, not recommended laboratory budgets.'),
              para('Historical assay labels are distinct from simulated operations. This application is not a validated digital twin, a live laboratory controller, or evidence of pharmaceutical efficacy. No authentication or sample customer accounts are required.'), PageBreak()]
    screens = [
        ('01', 'Discovery Overview', '01-overview-desktop-en.png', [
            ('Read the current campaign', 'The four headline figures come from the current engine state. Initial observations are included in the compound pool, but initial seed hits are excluded from new discoveries.'),
            ('Inspect chemistry', 'Use Previous compound and Next compound to browse eligible public structures. Zoom changes the structure view only; it does not select an assay.'),
            ('Follow the evidence', 'The performance chart uses delivered hits and simulated cost. Zero observed hits remain zero. Open the Lab to run the next operation.')]),
        ('02', 'Digital Twin Simulation Lab', '02-lab-desktop-en.png', [
            ('Select a batch', 'Accepted requests reserve budget and enter the queue. Capacity and available budget govern whether selection is enabled.'),
            ('Advance simulated time', 'Advance +1 step moves time forward. Labels remain hidden until the due step. Delivered outcomes settle cost; missing outcomes are reported separately.'),
            ('Inspect the four stages', 'Stage buttons inspect data only. Model Update shows observations available to the next decision and the last recorded model status. Predictions are not observations.'),
            ('Export and recover', 'JSON/CSV exports contain public state. Verify replay checks the ledger. Reset is explicit and starts a fresh local campaign; save an export first when needed.')]),
        ('03', 'Benchmark Arena', '03-arena-desktop-en.png', [
            ('Two kinds of evidence', 'The recorded HIV block shows an existing ten-seed benchmark with its own budget, capacity and delay. Opening the page does not rerun that benchmark.'),
            ('Run a matched comparison', 'Choose Random, Greedy, Uncertainty (the active-learning comparator), Q-learning and/or Contextual bandit. The active scenario and unchanged seed are shared; campaigns are independent.'),
            ('Interpret cost and variation', 'Hits / cost unit is confirmed new hits divided by spent simulated units. An unspent budget has no ratio. One seed has no empirical across-seed variance. Recorded error bars are seed SD, not cross-target confidence intervals.'),
            ('Read controller limitations', 'The learned controllers were trained on synthetic tasks and can use Greedy fallback. Recorded equality does not establish successful RL transfer or superiority.')]),
        ('04', 'Compound Explorer', '04-explorer-desktop-en.png', [
            ('Search and filter', 'Search compound IDs; filter by eligible, seed, pending, delivered or missing. Sort and paginate the public catalogue. Table and grid views show the same public records.'),
            ('Open a compound record', 'Click its ID for the public 2D structure, SMILES, descriptors, selection rationale and actual request history. Synthetic numerical fixtures have no invented molecular drawing.'),
            ('Respect outcome visibility', 'Eligible and pending records show Unrevealed. Delivered activity is separate from predicted probability. Missing outcomes are not inactive results.'),
            ('On a narrow screen', 'Scroll the table horizontally to see status, outcome and history, or switch to grid view. Tap a compound ID for the full record.')]),
    ]
    for index, title, filename, notes in screens:
        story += [para(index + ' / WORKSPACE', 'label'), para(title, 'heading')]
        right = []
        for label, text in notes:
            right.extend([para(label, 'label'), para(text, 'small'), Spacer(1, 5)])
        layout = Table([[image(filename), right]], colWidths=[530, 230])
        layout.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0)]))
        story += [layout, Spacer(1, 8), para('Actual application capture. Scroll within the app for the remaining ledger and details; full-page EN/TH captures are linked from the README.', 'small'), PageBreak()]
    story += [para('READING RESULTS RESPONSIBLY', 'label'), para('What the interface can and cannot establish', 'title'),
              para('A useful demonstration'), para('Select a batch, inspect its pending queue, advance to the due step, and check the delivered record. Then compare policies under a common scenario. Keep the exported public ledger alongside the report.'),
              para('Research boundaries', 'heading'), para('A single HIV assay and synthetic operating assumptions do not establish cross-target generalization, laboratory savings or clinical value. Uncalibrated logistic probabilities and synthetic-trained controllers have specific limitations. Review the Research evidence screen before presenting performance claims.'),
              para('Language and recovery', 'heading'), para('EN / Thai changes interface labels without resetting the campaign, filters or canonical API values. Original engine diagnostics remain English and are labeled as such. A stale action is rejected rather than charged twice; Reconnect refreshes server state. Saved campaigns and comparisons are local, not a cloud service.'),
              para('Scope of this guide', 'heading'), para('This guide documents the four-screen frontend checkpoint. It does not release M2, open protected final outcomes, or establish a new scientific contribution. The existing C Workspace remains a separate local metadata and reporting tool.'),
              para('Design reference: ui.shadcn.com/blocks/dashboard. Existing Radix/shadcn-style primitives are reused; authentication, demo teams and template data are not imported.', 'small')]
    SimpleDocTemplate(str(OUTPUT), pagesize=landscape(A4), rightMargin=36, leftMargin=36,
                      topMargin=30, bottomMargin=48, title='CuraLoop-RL English Dashboard Operator Guide',
                      author='CuraLoop-RL').build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == '__main__':
    main()
