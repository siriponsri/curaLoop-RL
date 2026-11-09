# Visual-only v2: preserve all values; shared y limit includes every seed maximum.
"""Aggregate-only EN/TH offline handoff and restrained, editable research figures."""
# ruff: noqa: E402

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, now, read, sha, start
from research.confirmation_v1.contracts import GATE_NAMES, validate_report

HANDOFF = ROOT / "research/product_handoffs/lr_cf1_v1"
RANKERS = ("random", "primary_score", "mvsa", "gbm", "rf", "nearest_primary")
NAMES = ("Random", "Primary Score", "MVS-A", "GBM", "RF", "Nearest primary hit")
OPERATORS = ("top_ranked", "cluster_round_robin", "classical_max_min")


def offline():
    data = read(PUBLIC / "results-summary-v1.json")
    assert data["status"] == "PASS_INDEPENDENT_AGGREGATE_RECALCULATION"
    HANDOFF.mkdir(exist_ok=False)
    card = {"schema": "curaloop.confirmation.offline-report.v1", "status": "FEASIBILITY_COMPLETE",
        "created_utc": now().isoformat(), "estimand": "OBSERVATION_SUPPORTED_PRIMARY_HITS_ONLY",
        "final16_access": False, "new_selector_training": False, "gates": dict.fromkeys(GATE_NAMES, True),
        "campaigns": 6, "source_experiment_blocks": 4, "annotation_connected_components": 1,
        "metrics": {"confirmed_positives": sum(r["source_confirmed_positive_count"] for r in data["campaigns"]),
                    "positive_structure_groups": sum(r["source_positive_structure_groups"] for r in data["campaigns"])},
        "metric_context": "Sum across six complete admitted observation-supported universes; assay-specific observations/groups, not unique cross-assay compounds or a selected policy's output",
        "uncertainty": {"estimated": True, "type": "five-seed observed range and SD", "seed_intervals_are_biological_uncertainty": False},
        "integration_status": "OFFLINE_HANDOFF_ONLY", "publication_ready": False,
        "data_use_scope": "Bounded noncommercial reanalysis and derived aggregate report preparation; raw redistribution and commercial data clearance are not established",
        "source_snapshot": "04c58e85188e724ec5ff44cbed2e7b960f6f3df3",
        "source_name_conflicts": "13 of 17 SI/repository aliases conflict; numeric AID pairs and pinned repository govern",
        "evidence": {"results": "../../../docs/evidence/lr-cf1-20261109-v1/results-summary-v1.json",
                     "cells": "../../../docs/evidence/lr-cf1-20261109-v1/portfolio-cells-v1.csv"},
        "labels": {"en": {"title": "Confirmation portfolio evidence", "status": "Development feasibility complete",
            "scope": "Published processed-repository reproduction; observation-supported primary hits only",
            "confirmation_zero": "Source nonpositive includes inactive or inconclusive; missing is never imputed",
            "next_step": "Owner reviews contribution and study design before any new selector or independent evaluation"},
            "th": {"title": "หลักฐานการจัดชุดสารเพื่อยืนยันผล", "status": "ตรวจความเป็นไปได้บนชุดพัฒนาเสร็จแล้ว",
            "scope": "ทดสอบจากข้อมูลที่ผู้เขียนประมวลผลและเผยแพร่ เฉพาะสาร primary hit ที่มีผลยืนยันบันทึกไว้",
            "confirmation_zero": "ค่า 0 รวมผลไม่ออกฤทธิ์และผลที่ยังสรุปไม่ได้ ส่วนผลที่หายไปไม่เติมเป็น 0",
            "next_step": "เจ้าของโครงการร่วมตัดสินใจ contribution และแบบการศึกษาก่อนพัฒนาวิธีใหม่หรือประเมินชุดอิสระ"}}}
    validate_report(card)
    import jsonschema
    schema_path = ROOT / "research/confirmation_v1/offline-card.schema.json"
    schema = read(schema_path)
    jsonschema.validate(card, schema)
    for forbidden in ("raw_labels", "compound_rows", "pending_assay_results"):
        try:
            jsonschema.validate({**card, forbidden: [1]}, schema)
        except jsonschema.ValidationError:
            continue
        raise AssertionError("PRIVATE_FIELD_ACCEPTED_BY_OFFLINE_SCHEMA")
    new(HANDOFF / "evidence-card-v1.json", card)
    new(HANDOFF / "evidence-card.schema.json", schema)
    payload = {"global": data["equal_campaign_summary"], "campaigns": data["campaigns"]}
    import csv
    with (PUBLIC / "campaign-summary-v1.csv").open(newline="") as file:
        campaign_rows = list(csv.DictReader(file))
    payload["rows"] = [{k: float(v) if k.endswith(("_mean", "_min", "_max", "_sd")) else int(v)
                         if k in ("budget_percent", "confirmation_count", "conditional_seed_count") else v
                         for k, v in r.items()} for r in campaign_rows]
    template = Path(__file__).with_name("cf1_offline_report_v1.html").read_text(encoding="utf-8")
    content = template.replace("__AGGREGATE_PAYLOAD__", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
    with (HANDOFF / "report.html").open("x", encoding="utf-8", newline="\n") as file:
        file.write(content)
    new(PUBLIC / "offline-product-validation-v1.json", {"status": "PASS_GATED_OFFLINE_CARD",
        "card_sha256": sha(HANDOFF / "evidence-card-v1.json"), "report_sha256": sha(HANDOFF / "report.html"),
        "schema_validation": "semantic contract + Draft2020-12 strict schema; three private-field injection rejections",
        "actual_product_integration": False, "raw_records_or_structures_published": False,
        "browser_check": "NOT_RUN_AT_GENERATION"})


def figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = read(PUBLIC / "results-summary-v1.json")["equal_campaign_summary"]
    directory = PUBLIC / "figures"
    directory.mkdir(exist_ok=False)
    new(directory / "visual-spec-v2.json", {
        "claim": "All fixed ranking controls have budget-dependent hit and structural-coverage curves; every operator and seed range remains visible",
        "visual_form": "six ranker facets; three ordered operator curves per facet; separate H and D figures",
        "metric": ["mean source-confirmed positives H", "mean positive structure groups D"], "unit": "counts per campaign",
        "direction": "higher", "aggregation": "equal weight to the same six development campaigns within each seed",
        "focal_series": "no proposed new method; top-ranked anchor", "required_baselines": list(RANKERS),
        "stable_series_order": list(OPERATORS), "width_mm": 178, "height_mm": 145,
        "uncertainty": "observed min/max across five conditional seeds; not a biological population interval",
        "annotation_plan": "shared operator legend and ranker facet titles; no outcome-selected callout",
        "palette_override": "burgundy accent follows owner preference against green/teal",
        "references": ["gpt6_astra_north_star.md figures 1/2/5; final-size small-multiple grammar",
                       "top_reference_set.md ranks 6/7/13: sparse comparisons and explicit variation"],
        "output_formats": ["svg", "pdf", "png"], "source": "../results-summary-v1.json"})
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.2, "axes.titlesize": 8.8,
        "axes.labelsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .6,
        "axes.edgecolor": "#767676", "text.color": "#171717", "axes.labelcolor": "#171717",
        "svg.fonttype": "none", "pdf.fonttype": 42})
    styles = [("#7B2840", "-", "o"), ("#565656", "--", "s"), ("#848484", ":", "^")]
    for metric, name, label in (("confirmed_positives", "hits", "Mean source-positive hits H"),
                                 ("positive_structure_groups", "groups", "Mean positive structure groups D")):
        fig, axes = plt.subplots(2, 3, figsize=(178 / 25.4, 145 / 25.4), sharex=True, sharey=True)
        for axis, ranker, title in zip(axes.flat, RANKERS, NAMES):
            for operator, (color, line, marker) in zip(OPERATORS, styles):
                values = sorted([r for r in rows if r["ranker"] == ranker and r["operator"] == operator], key=lambda r: r["budget_percent"])
                x = [r["budget_percent"] for r in values]
                y = [r[metric + "_mean"] for r in values]
                lower = [r[metric + "_min"] for r in values]
                upper = [r[metric + "_max"] for r in values]
                axis.fill_between(x, lower, upper, color=color, alpha=.10, linewidth=0)
                axis.plot(x, y, color=color, linestyle=line, marker=marker, markersize=3,
                          linewidth=1.2, label=operator.replace("_", " "))
            axis.set_title(title, loc="left", fontweight="semibold")
            axis.set_xticks([1, 5, 10, 20])
            axis.set_xlim(0, 21)
            axis.set_ylim(0, max(r[metric + "_max"] for r in rows) * 1.08)
            axis.grid(axis="y", color="#e7e7e7", linewidth=.45)
            axis.set_axisbelow(True)
        fig.suptitle("Fixed confirmation portfolios: " + ("hit recovery" if name == "hits" else "structural coverage"),
                     x=.105, y=.985, ha="left", fontsize=10.2, fontweight="semibold")
        fig.supxlabel("Nominal confirmation budget (% of each campaign's supported universe)", y=.13, fontsize=8.5)
        fig.supylabel(label + " (higher is better)", x=.012, fontsize=8.5)
        handles, labels = axes.flat[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.53, .065), ncol=3, frameon=False, fontsize=8)
        fig.text(.105, .025, "Six fixed campaigns; five seeds. Bands: observed conditional seed range.\nNo biological population interval; final16 sealed.",
                 fontsize=8, color="#4a4a4a")
        fig.subplots_adjust(left=.105, right=.985, bottom=.22, top=.91, wspace=.20, hspace=.31)
        for suffix in ("svg", "pdf", "png"):
            fig.savefig(directory / (name + "-budget-curves-v2." + suffix), dpi=240, facecolor="white")
        qa = TASK / "figure-qa"
        qa.mkdir(exist_ok=True)
        fig.savefig(qa / (name + "-color-final-size-v2.png"), dpi=96, facecolor="white")
        for axis in axes.flat:
            for line, color in zip(axis.lines, ("#202020", "#555555", "#808080")):
                line.set_color(color)
            for band, color in zip(axis.collections, ("#202020", "#555555", "#808080")):
                band.set_facecolor(color)
        for line, color in zip(fig.legends[0].get_lines(), ("#202020", "#555555", "#808080")):
            line.set_color(color)
        fig.savefig(qa / (name + "-grayscale-v2.png"), dpi=96, facecolor="white")
        plt.close(fig)


if __name__ == "__main__":
    action = sys.argv[1]
    assert action in ("offline", "figures")
    guard = start("deliverables-" + action + "-v2", 180, 600, bucket="utilities_return_handoff_delivery")
    try:
        offline() if action == "offline" else figures()
        finish("deliverables-" + action + "-v2", guard, "PASS_GENERATED_" + action.upper())
    except BaseException:
        finish("deliverables-" + action + "-v2", guard, "FAIL")
        raise
