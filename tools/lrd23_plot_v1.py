"""Publication-size absolute discovery/compute comparison from frozen D2 rows."""
# ruff: noqa: E402

import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.common import PUBLIC, TASK, new, read, sha, utility_finish, utility_start


def plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import FuncFormatter, LogLocator, MaxNLocator
    from PIL import Image

    from research.lr_d23_v1.analysis import estimate

    source = TASK / "D2-rows-private.json"
    rows, aggregate = read(source), read(PUBLIC / "D2-aggregate-v1.json")
    order = ["G1", "Gk2", "Gk4", "T_k4_tau0.05", "frozen_cache_greedy", "nearest_hit",
             "candidate_v0", "no_history_v1", "candidate_v1"]
    labels = ["G1", "Gk2", "Gk4", "T (k4, tau 0.05)", "Frozen-cache greedy", "Nearest-hit",
              "Residual v0", "No-history v1", "Residual v1"]
    spec = {"claim": "Residual scheduling " + ("met" if aggregate["status"] == "PASS_D2" else "did not meet") + " D2 criteria",
            "visual_form": "dot_interval", "metric": {"name": "new assay positives", "unit": "count", "direction": "higher",
            "aggregation": "equal components, equal assays within component, matched n0/seed", "denominator": "6 exposed assays / 4 annotation components"},
            "secondary_metric": {"name": "scientific CPU", "unit": "seconds", "direction": "lower", "scale": "log10"},
            "data_source": {"path_or_identifier": "private D2-rows-private.json; public D2-aggregate-v1.json", "checksum": sha(source)},
            "focal_series": "candidate_v1", "required_baselines": order[:-1], "series_order": order,
            "uncertainty": {"available": True, "type": "bootstrap_interval", "level": .95, "sample_or_seed_count": 5,
                            "note": "all5^5 joint-seed resamples, conditional on the exposed assays, not biological population uncertainty"},
            "target": {"medium": "paper", "width": 178, "height": 119.38, "unit": "mm", "minimum_text_size_pt": 8},
            "output_formats": ["svg", "png"], "selected_reference_ids": ["OAI-VIS-002", "OAI-VIS-001", "OAI-VIS-087"],
            "exceptions": [{"rule": "focal teal", "reason": "Use the owner's approved wine accent instead of the rejected green/teal direction."}]}
    new(PUBLIC / "figure-spec-v2.json", spec)
    table = {}
    seeds = sorted({r["spec"]["seed"] for r in rows})
    indices = np.asarray(list(itertools.product(range(5), repeat=5)))
    for arm in order:
        selected = [r for r in rows if r["spec"]["control"] == arm]
        table[arm] = {}
        for metric in ("new_positives", "scientific_cpu_seconds"):
            means = np.array([estimate(selected, metric, seed=s) for s in seeds])
            point = estimate(selected, metric)
            assert abs(point - aggregate["means"][arm][metric]) < 1e-12
            point = aggregate["means"][arm][metric]
            table[arm][metric] = {"mean": point, "conditional_seed_95_percentile_interval": np.quantile(means[indices].mean(axis=1), [.025, .975]).tolist()}
    new(PUBLIC / "figure-data-v2.json", {"order": order, "data": table, "source_sha256": sha(source)})
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.labelsize": 9,
                         "xtick.labelsize": 8, "ytick.labelsize": 9, "axes.linewidth": .6,
                         "text.color": "#171717", "axes.labelcolor": "#171717", "svg.fonttype": "none"})
    fig = plt.figure(figsize=(178 / 25.4, 4.7), facecolor="white")
    grid = fig.add_gridspec(1, 2, left=.29, right=.98, bottom=.23, top=.82, wspace=.38)
    axes = [fig.add_subplot(grid[0, i]) for i in range(2)]
    for axis, metric, title in zip(axes, ("new_positives", "scientific_cpu_seconds"),
                                   ("New assay positives", "Scientific CPU (s, log)"), strict=True):
        for y, arm in enumerate(order):
            item = table[arm][metric]
            low, high = item["conditional_seed_95_percentile_interval"]
            color = "#7B233F" if arm == "candidate_v1" else "#656562"
            axis.errorbar(item["mean"], y, xerr=[[max(0., item["mean"] - low)], [max(0., high - item["mean"])]],
                          fmt="D" if arm == "candidate_v1" else "o", markersize=4.5,
                          color=color, capsize=2, elinewidth=.8, markeredgewidth=.6)
        axis.set_ylim(8.65, -.65)
        axis.set_yticks(range(9), labels if axis is axes[0] else [])
        axis.tick_params(axis="y", length=0, pad=8)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.spines["bottom"].set_color("#999995")
        axis.set_title(title, fontsize=9, loc="left", pad=10)
        axis.set_xlabel("Higher is better" if metric == "new_positives" else "Lower is better", labelpad=7)
        if metric == "scientific_cpu_seconds":
            axis.set_xscale("log")
            axis.xaxis.set_major_locator(LogLocator(base=10, numticks=4))
            axis.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:g}"))
            axis.minorticks_off()
        else:
            axis.xaxis.set_major_locator(MaxNLocator(4))
        # Locators include off-view ticks; exclude these before bounding-box QA.
        low, high = axis.get_xlim()
        axis.set_xticks([t for t in axis.get_xticks() if low <= t <= high])
    fig.text(.035, .955, spec["claim"], fontsize=11, weight="bold", va="top")
    fig.text(.035, .900, "RF / B32 / Cref / n0 0 or 16 / six exposed development assays", fontsize=8.5, va="top")
    fig.text(.035, .103, "Equal component/assay means; whiskers: 95% joint-seed percentile intervals (5 seeds).\n"
             "Intervals are conditional on these assays; no population or clinical inference.\n"
             "dr-train: three assigned cores, one CPU-equivalent per worker; offline training excluded.",
             fontsize=8, va="top", linespacing=1.35)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in fig.findobj(matplotlib.text.Text):
        if text.get_visible() and text.get_text():
            bounds = text.get_window_extent(renderer)
            assert bounds.x0 >= -1 and bounds.y0 >= -1 and bounds.x1 <= fig.bbox.width + 1 and bounds.y1 <= fig.bbox.height + 1, text.get_text()
    output = ROOT / "docs/assets/research/lr-d23-v1"
    output.mkdir(parents=True, exist_ok=False)
    fig.savefig(output / "primary-comparison.svg")
    fig.savefig(output / "primary-comparison.png", dpi=300)
    with Image.open(output / "primary-comparison.png") as im:
        im.convert("L").save(TASK / "primary-comparison-grayscale.png")
    plt.close(fig)
    print({"status": "PASS_RENDER_AND_GEOMETRY_PENDING_VISUAL_REVIEW", "figure": str(output)})


if __name__ == "__main__":
    guard = utility_start("primary-figure-repair", 180, 300)
    try:
        plot()
        utility_finish("primary-figure-repair", guard, "PASS")
    except BaseException:
        utility_finish("primary-figure-repair", guard, "FAIL")
        raise
