"""Source-locked diagram and figure plan; never invents experiment results."""

import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/agent-rd-run-20261110-v1"
PUBLIC = ROOT / "docs/evidence/agent-rd-20261110-v1"
BUNDLED = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
SKILL = Path.home() / ".codex/plugins/cache/openai-curated-remote/scientific-visual-table-style/2.2.0/skills/scientific-visual-table-style"
PLOTDEPS = TASK / "plotdeps-v1"
FIG_VERSION = "v2"


def ensure_plot_dependencies():
    receipt = TASK / "plotdeps-install-v1.json"
    if receipt.exists():
        assert json.loads(receipt.read_text())["exit_code"] == 0
        return
    environment = {**os.environ, "PIP_CONFIG_FILE": os.devnull, "PIP_NO_CACHE_DIR": "1"}
    environment.pop("PIP_EXTRA_INDEX_URL", None)
    command = [str(BUNDLED), "-m", "pip", "install", "--target", str(PLOTDEPS), "--only-binary=:all:",
               "--index-url", "https://pypi.org/simple", "--no-input", "--disable-pip-version-check", "--no-compile",
               "--report", str(TASK / "plotdeps-pip-report-v1.json"), "matplotlib==3.10.8", "numpy<3"]
    result = subprocess.run(command, env=environment, capture_output=True, text=True, encoding="utf-8")
    (TASK / "plotdeps-install-v1.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (TASK / "plotdeps-install-v1.stderr.txt").write_text(result.stderr, encoding="utf-8")
    write(receipt, {"exit_code": result.returncode, "scope": "Isolated document plotting dependencies only; no change to frozen evaluation or project environment", "target": str(PLOTDEPS)})
    assert result.returncode == 0, result.stderr[-1000:]
    report = json.loads((TASK / "plotdeps-pip-report-v1.json").read_text())
    write(PUBLIC / "plotting-dependencies-v1.json", {"status": "INSTALLED_IN_OWNED_DOCUMENT_ONLY_TARGET", "model_download": False,
          "frozen_evaluation_environment_changed": False, "packages": [{"name": p["metadata"]["name"], "version": p["metadata"]["version"],
          "hashes": p["download_info"]["archive_info"].get("hashes", {})} for p in report["install"]]})


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2, ensure_ascii=False, allow_nan=False)
        output.write("\n")


def plan():
    freeze = json.loads((ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json").read_text(encoding="utf-8"))
    assert all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == value for path, value in freeze["pins"].items())
    if (TASK / "document-next-action-v1.json").exists():
        # A bounded operator helper, never an inference tool or second resource Job.
        raise SystemExit(subprocess.run([sys.executable, str(ROOT / "tools/agent_rd_document_dispatch_v1.py")], cwd=ROOT).returncode)
    if not (PUBLIC / "python-environment-observed-v1.json").exists():
        packages = {}
        for package in ("pydantic", "pydantic-core", "fastapi", "uvicorn", "pytest", "ruff", "jsonschema", "numpy"):
            try:
                packages[package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                packages[package] = None
        write(PUBLIC / "python-environment-observed-v1.json", {"utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "executable": sys.executable, "packages": packages,
              "scope": "Observed during locked execution; not a pre-execution whole-environment byte seal. Plotting dependencies use an isolated target."})
    if (PUBLIC / "visual-spec-v1.json").exists():
        previous = json.loads((PUBLIC / "visual-spec-v1.json").read_text(encoding="utf-8"))
        assert previous["freeze_sha256"] == hashlib.sha256((ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json").read_bytes()).hexdigest()
        ensure_plot_dependencies()
        if (PUBLIC / ("figures-" + FIG_VERSION) / "01-control-flow.svg").exists():
            raise SystemExit(subprocess.run([sys.executable, str(ROOT / "tools/agent_rd_delivery_check_v1.py")], cwd=ROOT).returncode)
        raise SystemExit(subprocess.run([str(BUNDLED), __file__, "render-flow"], cwd=ROOT).returncode)
    references = []
    for query in ("workflow architecture diagram append only context", "accuracy uncertainty horizontal model comparison", "score latency inference cost scatter"):
        result = subprocess.run([str(BUNDLED), str(SKILL / "scripts/select_references.py"), "--query", query,
                                 "--limit", "4", "--max-tier", "2"], capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 0, result.stderr
        references.append({"query": query, "selector_output": result.stdout})
    value = {"status": "DESIGN_SPEC_NO_EXPERIMENT_VALUES", "series_order": ["B0", "B1", "B2", "P"],
             "focal": "P", "palette": {"ink": "#29282b", "baseline": "#777777", "focal": "#a6492d", "background": "#ffffff"},
             "palette_reason": "Owner-approved graphite/copper brand; replaces the skill's default green accent",
             "global_references": [
                 "GPT-6 Astra governing system-card grammar: tables1/2/4/6/7/8, figures1/2/5/6/9/12/13/14/17/19",
                 "Append-only context: aligned near-monochrome workflow with one accent",
                 "Professional benchmark table: sparse rules, exact values, consistent model order"],
             "form_matched_retrieval": references,
             "figures": [
                 {"id": "01-control-flow", "claim": "Matched B2/P input and tool flow differ at the source gate and bounded repair",
                  "form": "minimal workflow diagram", "width_mm": 178, "height_mm": 122,
                  "source": "frozen protocol and engine", "numeric_results": False},
                 {"id": "02-task-completion", "claim": "Show actual task completion and every required baseline, including a strong deterministic reference",
                  "form": "horizontal dots with actual three-decoding-seed range; companion family matrix only if legible",
                  "source": "actual locked receipts after complete analysis", "metric": "task success", "unit": "% of32 authored cases per decoding seed",
                  "direction": "higher is better", "uncertainty": "three-seed min/max, not a biological CI", "width_mm": 178, "height_mm": 108},
                 {"id": "03-cost-completion", "claim": "Show observed completion against actual runtime without hiding deterministic cost",
                  "form": "direct-labeled scatter; log latency only if its range warrants it; no lines between model families",
                  "source": "actual locked receipts", "x": "median unit wall seconds", "y": "all-planned task success %",
                  "timing_scope": "single CPU runtime/order/prompt-cache conditions; all attempt costs retained", "width_mm": 178, "height_mm": 108}],
             "tables": ["Completion, abstention, fallback, malformed response and numeric errors with actual denominators",
                        "Actual compute/calls/tokens/wall; unknown failed-call costs are not zero",
                        "Eight matched no-repair anchors, compared with P on the same cases only"],
             "rules": ["No fabricated missing values or intervals", "No baseline omission if P loses", "No biological independence claim",
                       "No significance stars or Pareto claim without a computed estimand", "SVG plus300dpi PNG and editable code",
                       "At least8.5pt text at final size; inspect color, grayscale, clipping and manuscript insertion"],
             "freeze_sha256": hashlib.sha256((ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json").read_bytes()).hexdigest()}
    write(PUBLIC / "visual-spec-v1.json", value)
    ensure_plot_dependencies()
    result = subprocess.run([str(BUNDLED), __file__, "render-flow"], cwd=ROOT)
    raise SystemExit(result.returncode)


def render_flow():
    sys.path.insert(0, str(PLOTDEPS))
    os.environ["MPLCONFIGDIR"] = str(TASK / "mpl-cache-v1")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    from PIL import Image

    output = PUBLIC / ("figures-" + FIG_VERSION)
    output.mkdir(exist_ok=True)
    assert not (output / "01-control-flow.svg").exists()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.fonttype": "none",
                         "axes.facecolor": "white", "figure.facecolor": "white", "savefig.facecolor": "white"})
    fig = plt.figure(figsize=(178 / 25.4, 122 / 25.4), dpi=300)
    ax = fig.add_axes([.02, .13, .96, .70])
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    ink, copper, line = "#29282b", "#a6492d", "#777777"

    def box(x, y, width, height, label, focal=False):
        ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.006,rounding_size=0.01",
                                   facecolor="#fcf5f1" if focal else "white", edgecolor=copper if focal else "#c8c1ba", linewidth=.75))
        ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=9, color=ink, linespacing=1.35)

    def arrow(start, end, focal=False):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=8, linewidth=.8,
                                    color=copper if focal else line, shrinkA=2, shrinkB=3))

    fig.text(.04, .94, "Matched controls locate the source-checking step", fontsize=11, weight="semibold", color=ink)
    fig.text(.04, .885, "One fixed public corpus. Same model observations and decoding seeds.", fontsize=9, color="#655e57")
    box(.015, .40, .19, .31, "Fixed mission,\nsource packet,\ndecoding seed\n(no oracle)")
    ax.plot([.205, .25], [.555, .555], color=line, linewidth=.8)
    ax.plot([.25, .25], [.245, .875], color=line, linewidth=.8)
    rows = [(.82, "B0 / Deterministic", "Exact table +\nscope rules", "Deterministic report"),
            (.62, "B1 / LLM only", "LLM\n(no executable tools)", "Ungated report"),
            (.42, "B2 / LLM + tools", "Same LLM +\npreflight read / compute", "Ungated report")]
    for y, heading, model, result in rows:
        ax.text(.305, y + .132, heading, fontsize=9, color=ink, weight="semibold")
        arrow((.25, y + .055), (.305, y + .055))
        box(.305, y, .325, .11, model)
        arrow((.63, y + .055), (.68, y + .055))
        box(.68, y, .30, .11, result)
    y = .19
    ax.text(.305, y + .132, "P / Guarded", fontsize=9, color=ink, weight="semibold")
    arrow((.25, y + .055), (.305, y + .055))
    box(.305, y, .325, .11, "Same LLM +\npreflight read / compute")
    arrow((.63, y + .055), (.665, y + .055), True)
    box(.665, y, .115, .11, "Source\ncheck", True)
    arrow((.78, y + .055), (.815, y + .055), True)
    box(.815, y, .165, .11, "Checked report\nor abstention")
    ax.plot([.72, .72, .47, .47], [.30, .35, .35, .305], color=copper, linewidth=.8)
    arrow((.47, .325), (.47, .30), True)
    ax.text(.59, .36, "bounded repair", fontsize=8.5, ha="center", color=copper)
    fig.text(.04, .075, "All model arms: at most 3 calls x 256 output tokens; fixed read/compute adapters.", fontsize=8.5, color="#655e57")
    fig.text(.04, .035, "The separate offline scorer uses the CSV oracle. Source checking is not task-completeness scoring.", fontsize=8.5, color="#655e57")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in fig.findobj(match=matplotlib.text.Text):
        if not item.get_text():
            continue
        assert item.get_fontsize() >= 8.5
        bounds = item.get_window_extent(renderer)
        assert bounds.x0 >= 0 and bounds.y0 >= 0 and bounds.x1 <= fig.bbox.width and bounds.y1 <= fig.bbox.height, item.get_text()
    for suffix in ("svg", "png"):
        fig.savefig(output / ("01-control-flow." + suffix), dpi=300)
    plt.close(fig)
    review = TASK / ("visual-qa-" + FIG_VERSION)
    review.mkdir(exist_ok=True)
    Image.open(output / "01-control-flow.png").convert("L").save(review / "01-control-flow-gray.png")
    write(PUBLIC / ("control-flow-build-" + FIG_VERSION + ".json"), {"status": "RENDERED_AWAITING_VISUAL_REVIEW", "width_mm": 178, "height_mm": 122,
          "min_text_pt": 8.5, "formats": ["svg", "png"], "numeric_results": False,
          "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob("01-control-flow.*")}})
    print("Rendered protocol-derived control flow; visual review pending; no experiment result was created")


if __name__ == "__main__":
    render_flow() if sys.argv[1:] == ["render-flow"] else plan()
