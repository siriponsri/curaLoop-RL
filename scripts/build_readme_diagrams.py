"""Build editable, offline diagrams for the README and operator manual."""

import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/diagrams"
PAPER, INK, MUTED, TEAL = "#F7F9F8", "#16333B", "#526653", "#087F72"


def text(x, y, value, size=16, fill=INK, weight=400, anchor="start", mono=False):
    family = "Consolas,monospace" if mono else "Segoe UI,Arial,sans-serif"
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def arrow(path, color=MUTED, dashed=False):
    dash = ' stroke-dasharray="5 5"' if dashed else ""
    marker = "teal" if color == TEAL else "muted"
    return (
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"'
        f'{dash} marker-end="url(#{marker})"/>'
    )


def label(x, y, value, width=128):
    return (
        f'<rect x="{x - width / 2}" y="{y - 15}" width="{width}" height="22" fill="{PAPER}"/>'
        + text(x, y, value, 11, MUTED, 500, "middle", True)
    )


def box(x, y, title, lines, tag, focal=False, width=248, height=112):
    stroke, fill = (TEAL, "#E6F3EB") if focal else ("#B5C7BF", "#FFFFFF")
    parts = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
        text(x + 20, y + 24, tag, 10, TEAL if focal else MUTED, 600, mono=True),
        text(x + 20, y + 52, title, 19, INK, 600),
    ]
    parts += [text(x + 20, y + 76 + i * 18, line, 12, MUTED) for i, line in enumerate(lines)]
    return "".join(parts)


def write(slug, title, description, body):
    defs = "".join(
        f'<marker id="{name}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L8 4L0 8Z" fill="{color}"/></marker>'
        for name, color in [("muted", MUTED), ("teal", TEAL)]
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 792" role="img" aria-labelledby="{slug}-title {slug}-desc">'
        f'<title id="{slug}-title">{escape(title)}</title><desc id="{slug}-desc">{escape(description)}</desc>'
        f'<defs>{defs}</defs><rect width="1120" height="792" fill="{PAPER}" rx="12"/>'
        + text(64, 40, "CURALOOP-RL / RESEARCH WORKBENCH", 11, TEAL, 600, mono=True)
        + text(64, 88, title, 32, INK, 600)
        + body
        + "</svg>"
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>
*{{box-sizing:border-box}}body{{margin:0;padding:24px;background:{PAPER};font-family:Segoe UI,Arial,sans-serif;color:{INK}}}main{{max-width:1120px;min-width:0;margin:auto}}.diagram-container{{width:100%;overflow-x:auto}}svg{{display:block;width:100%;min-width:1120px}}h1{{font-size:20px;font-weight:600}}p{{color:{MUTED};line-height:1.6}}@media print{{body{{padding:0}}.diagram-container{{overflow-x:visible}}svg{{min-width:0}}.source-note{{display:none}}}}
</style></head><body><main><div class="diagram-container">{svg}</div><p class="source-note">{escape(description)} Project-local brand tokens and source mapping: docs/design/diagram-style.md.</p></main></body></html>"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.html").write_text(html, encoding="utf-8")


def architecture():
    parts = [
        text(64, 120, "One local address. One Python authority for scientific state.", 14, MUTED),
        arrow("M312 260H436", "#176C83"),
        arrow("M684 260H808"),
        arrow("M436 288H376Q368 288 368 296V432Q368 440 360 440H196Q188 440 188 448V516", TEAL),
        arrow("M872 316V392Q872 400 864 400H568Q560 400 560 408V516"),
        arrow("M936 316V516"),
        label(374, 244, "LOCAL HTTP", 112),
        label(746, 244, "CALLS", 72),
        label(302, 404, "PUBLIC JSON", 116),
        label(716, 385, "PUBLIC INPUT", 136),
        label(1012, 416, "VALIDATED ONLY", 136),
        box(
            64,
            204,
            "Research interface",
            ["React / TypeScript", "Seven connected workflows"],
            "LOCAL BROWSER",
        ),
        box(
            436,
            204,
            "Local API",
            ["Validation and revisions", "Loopback: 127.0.0.1:8000"],
            "FASTAPI",
        ),
        box(
            808,
            204,
            "Scientific core",
            ["RunService + Campaign", "Selection, time and budget"],
            "PYTHON",
            True,
        ),
        box(
            64,
            516,
            "Durable public state",
            ["Snapshots / revisions / jobs", "Atomic commit and recovery"],
            "SQLITE",
            True,
        ),
        box(
            436,
            516,
            "Policy worker",
            ["Separate built-in process", "Public observations only"],
            "ISOLATED PROCESS",
        ),
        box(
            808,
            516,
            "Private assay oracle",
            ["Unrevealed labels stay here", "Results only when due"],
            "TRUTHSTORE",
        ),
        '<rect x="64" y="664" width="992" height="48" rx="8" fill="#E6F3EB"/>',
        text(
            84,
            694,
            "Only seed labels and delivered outcomes can inform policy decisions.",
            16,
            INK,
            600,
        ),
        text(
            64,
            750,
            "Arrows show permitted calls. Responses return through the scientific core and API.",
            12,
            MUTED,
        ),
        text(
            64,
            774,
            "Local process separation is an engineering boundary, not an OS sandbox for hostile code.",
            11,
            MUTED,
        ),
    ]
    write(
        "architecture",
        "A local workbench, one scientific core",
        "The browser uses a local API; Python owns scientific transitions, SQLite stores public snapshots and the private oracle never supplies hidden labels to policies.",
        "".join(parts),
    )


def loop():
    cx, cy, radius, width, height = 560, 416, 240, 192, 80
    stations = [
        ("Observe", "Public descriptors and labels"),
        ("Select", "A policy proposes candidates"),
        ("Reserve", "Accept once; reserve budget"),
        ("Wait", "Configured feedback delay"),
        ("Deliver", "Active / inactive / missing"),
        ("Update", "Use newly delivered labels"),
    ]
    rects = []
    for k in range(6):
        angle = -math.pi / 2 + k * math.pi / 3
        x = round((cx + radius * math.cos(angle) - width / 2) / 4) * 4
        y = round((cy + radius * math.sin(angle) - height / 2) / 4) * 4
        rects.append((x, y, angle))

    def endpoints(k):
        x, y, theta = rects[k]
        points = []
        for edge in (x, x + width):
            q = radius**2 - (edge - cx) ** 2
            if q >= 0:
                for yy in (cy - math.sqrt(q), cy + math.sqrt(q)):
                    if y <= yy <= y + height:
                        points.append((edge, yy))
        for edge in (y, y + height):
            q = radius**2 - (edge - cy) ** 2
            if q >= 0:
                for xx in (cx - math.sqrt(q), cx + math.sqrt(q)):
                    if x <= xx <= x + width:
                        points.append((xx, edge))
        return sorted(
            points,
            key=lambda p: (
                (math.atan2(p[1] - cy, p[0] - cx) - theta + math.pi) % (2 * math.pi) - math.pi
            ),
        )

    parts = [
        text(
            64,
            120,
            "An auditable screening cycle with delayed feedback and bounded resources.",
            14,
            MUTED,
        )
    ]
    for k in range(6):
        start = endpoints(k)[-1]
        end = endpoints((k + 1) % 6)[0]
        phi = math.atan2(end[1] - cy, end[0] - cx) - 2 / radius
        end = (cx + radius * math.cos(phi), cy + radius * math.sin(phi))
        parts.append(
            arrow(
                f"M{start[0]:.3f} {start[1]:.3f}A240 240 0 0 1 {end[0]:.3f} {end[1]:.3f}",
                TEAL if k == 3 else MUTED,
            )
        )
    for k, (x, y, theta) in enumerate(rects):
        if k not in (0, 2, 3, 4):
            continue
        vx, vy = math.cos(theta), math.sin(theta)
        d = min(
            width / 2 / abs(vx) if abs(vx) > 1e-8 else 1e9,
            height / 2 / abs(vy) if abs(vy) > 1e-8 else 1e9,
        )
        h = (
            min(112 / abs(vx) if abs(vx) > 1e-8 else 1e9, 56 / abs(vy) if abs(vy) > 1e-8 else 1e9)
            + 8
        )
        sx, sy = x + width / 2 - d * vx, y + height / 2 - d * vy
        ex, ey = cx + h * vx, cy + h * vy
        route = (
            f"M{ex:.3f} {ey:.3f}L{sx:.3f} {sy:.3f}"
            if k == 0
            else f"M{sx:.3f} {sy:.3f}L{ex:.3f} {ey:.3f}"
        )
        parts.append(arrow(route, dashed=True))
    parts.append(
        '<rect x="448" y="360" width="224" height="112" rx="8" fill="#E6F3EB" stroke="#087F72" stroke-width="1.5"/>'
    )
    parts += [
        text(cx, 392, "PUBLIC EVIDENCE", 10, TEAL, 600, "middle", True),
        text(cx, 422, "Event ledger", 22, INK, 600, "middle"),
        text(cx, 448, "Metrics / budgets / revisions", 12, MUTED, anchor="middle"),
    ]
    for k, ((x, y, _), (title, caption)) in enumerate(zip(rects, stations)):
        focal = k == 4
        parts += [
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{"#E6F3EB" if focal else "#FFFFFF"}" stroke="{TEAL if focal else "#B5C7BF"}" stroke-width="1.5"/>',
            text(x + 16, y + 23, f"0{k + 1}", 10, TEAL if focal else MUTED, 600, mono=True),
            text(x + 16, y + 46, title, 19, INK, 600),
            text(x + 16, y + 67, caption, 11, MUTED),
        ]
    parts += [
        text(
            64,
            750,
            "Solid: next step. Dashed: record accepted actions and due results; read public state.",
            12,
            MUTED,
        ),
        text(
            64,
            774,
            "Repeat while budget and candidates permit. Pending predictions and seed hits are not new confirmed hits.",
            11,
            MUTED,
        ),
    ]
    write(
        "screening-loop",
        "From candidates to traceable evidence",
        "Observe public state, select candidates, reserve resources, wait for due feedback, deliver outcomes and update decisions; every pass contributes to the public event ledger.",
        "".join(parts),
    )


if __name__ == "__main__":
    architecture()
    loop()
    print("Built architecture and screening-loop HTML diagram sources.")
