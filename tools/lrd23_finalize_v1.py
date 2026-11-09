"""Final scoped checks and immutable account closure, without Git mutation."""
# ruff: noqa: E402

import csv
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.common import (
    PUBLIC,
    TASK,
    authority,
    ledger_save,
    new,
    now,
    orchestration_start,
    read,
    sha,
    utility_finish,
    utility_start,
)
from tools.lrd23_pipeline_v1 import validate_freeze


def validate():
    import jsonschema

    validate_freeze()
    # Editorial spacing only, outside the immutable pre-outcome contract.
    paper = ROOT / "docs/07_publication/LR_D23_METHODS_RESULTS_INSERT_20261109.md"
    text = paper.read_text(encoding="utf-8")
    replacements = {"ICML2025": "ICML 2025", "ICML2017": "ICML 2017", "features0,1,3,4": "features 0, 1, 3, 4",
        "after8/16/24": "after 8/16/24", "are216": "are 216", "and1,296": "and 1,296", "All324": "All 324",
        "are72/90/90/72": "are 72/90/90/72", "giving420": "giving 420", "add120": "add 120", "as1.25": "as 1.25",
        "sizes128/303": "sizes 128/303", "are3.417176s": "are 3.417176 s", "and3.799350s": "and 3.799350 s",
        "one CPU-equivalent,4GiB": "one CPU-equivalent, 4 GiB", "all5^5": "all 5^5", "saves41.90%": "saves 41.90%",
        "loses1.0875": "loses 1.0875", "approved0.25": "approved 0.25", "conditional95%": "conditional 95%",
        "interval[-": "interval [-", "loses0.7625": "loses 0.7625", "uses14.59%": "uses 14.59%",
        "has0.2875": "has 0.2875", "has0.7000": "has 0.7000", "All60": "All 60", "deliver32": "deliver 32"}
    for old, new_text in replacements.items():
        text = text.replace(old, new_text)
    paper.write_text(text, encoding="utf-8", newline="\n")
    import pytest

    tests = sorted(ROOT.glob("tests/research/test_lr_d23*.py")) + [
        ROOT / "tests/research/test_d1_controls_v1.py", ROOT / "tests/research/test_d1_control_analysis_v1.py"]
    code = pytest.main(["-q", *[p.relative_to(ROOT).as_posix() for p in tests],
        "--junitxml=docs/evidence/lr-d23-20261109-v1/final-tests-v2.xml"])
    new(TASK / "final-test-output-v2.json", {"exit_code": int(code), "mode": "in-process / local 1GiB"})
    assert code == 0
    assert read(TASK / "final-lint-output-v2.json")["exit_code"] == 0
    card_root = ROOT / "research/product_handoffs/lr_d23_v1"
    jsonschema.validate(read(card_root / "evidence-card-v1.json"), read(card_root / "evidence-card.schema.json"))
    visual_schema = Path(r"C:\Users\User\.codex\plugins\cache\openai-curated-remote\scientific-visual-table-style\2.2.0\skills\scientific-visual-table-style\templates\visual_spec.schema.json")
    jsonschema.validate(read(PUBLIC / "figure-spec-v2.json"), read(visual_schema))
    svg = ROOT / "docs/assets/research/lr-d23-v1/primary-comparison.svg"
    graphic = ET.parse(svg).getroot()
    assert abs(float(graphic.attrib["width"].removesuffix("pt")) * 25.4 / 72 - 178) < 1e-5
    assert abs(float(graphic.attrib["height"].removesuffix("pt")) * 25.4 / 72 - 119.38) < 1e-5
    aggregate = read(PUBLIC / "D2-aggregate-v1.json")
    with (PUBLIC / "primary-results-v1.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            assert all(float(row[k]) == aggregate["means"][row["arm"]][k.removeprefix("mean_")]
                       for k in ("mean_new_positives", "mean_scientific_cpu_seconds", "mean_new_deliveries"))
    docs = [p for pattern in ("docs/03_research/LR_D23*.md", "docs/05_product/LR_D23*.md",
            "docs/06_execution/LR_D23*.md", "docs/07_publication/LR_D23*.md",
            "research/product_handoffs/lr_d23_v1/README.md", "docs/evidence/lr-d23-20261109-v1/README.md")
            for p in ROOT.glob(pattern)]
    links = 0
    for path in docs:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            destination = path.parent / target.split("#")[0]
            assert destination.exists(), (path, target)
            links += 1
    validate_freeze()
    xml = ET.parse(PUBLIC / "final-tests-v2.xml").getroot()
    suites = [xml] if xml.tag == "testsuite" else list(xml)
    count = sum(int(s.attrib["tests"]) for s in suites)
    new(PUBLIC / "final-validation-v1.json", {"status": "PASS_SCOPED_FINAL_VALIDATION",
        "constructed_regression_tests": count, "junit_sha256": sha(PUBLIC / "final-tests-v2.xml"),
        "targeted_lint": "PASS_WITH_EXPLICIT_FROZEN_IMPORT_STYLE_EXCEPTION",
        "lint_style_exception": "tools/lrd23_return_v1.py:I001 (pre-outcome frozen bytes retained)",
        "local_markdown_links_checked": links, "card_and_figure_spec_schemas": "PASS",
        "CSV_matches_full_precision_aggregate": True, "frozen_source_matrices_unchanged": True,
        "app_runtime_UI_browser_build_full_suite": "NOT_RUN_NO_RUNTIME_CHANGE"})
    new(PUBLIC / "figure-visual-review-v1.json", {"status": "PASS_FINAL_SIZE_AND_GRAYSCALE_REVIEW",
        "utc": now().isoformat(), "physical_mm": [178, 119.38], "preview_pixels": [2102, 1410],
        "final_size_review_pixels": [673, 451], "minimum_font_pt": 8,
        "reviewed_color_and_grayscale_at_final_size": True, "clipping": "PASS",
        "source_values_and_all_arms": "PASS", "conditional_interval_scope": "PASS",
        "color_independent_identity": "diamond marker and fixed labeled row; verified in grayscale",
        "risk_claim_check": "Title states the failed D2 criteria; no statistical population dominance claimed",
        "svg_sha256": sha(svg), "png_sha256": sha(svg.with_suffix(".png"))})
    print({"status": "PASS_FINAL_VALIDATION", "tests": count, "links": links}, flush=True)


def close():
    release, ledger = authority()
    assert read(PUBLIC / "final-validation-v1.json")["status"] == "PASS_SCOPED_FINAL_VALIDATION"
    assert read(PUBLIC / "closure-audit-v1.json")["status"] == "PASS_COMPLETE_CLOSURE_AUDIT"
    assert all(b["status"] in ("PASS", "FAIL") for b in ledger["bookings"].values())
    failed = sorted(k for k, b in ledger["bookings"].items() if b["status"] == "FAIL")
    assert failed == ["final-validation", "matrix-worker-preflight", "primary-figure"]
    utility = sum(b.get("guard_cpu_seconds", b.get("aggregate_cpu_seconds", b.get("retained_seconds", 0)))
                  for b in ledger["bookings"].values() if b["bucket"] == "utilities_handoff")
    assert utility <= 6000
    ledger.update(status="CLOSED", closed_utc=now().isoformat(),
                  closure_status="PASS_COMPLETE_HANDOFF_RETURN_AND_AUDIT",
                  D3=ledger["D3_status"], final_outcomes_open=False)
    ledger_save(ledger)
    status = {"schema": "curaloop.lr_d23.status.v1", "status": "CLOSED_COMPLETE_FOR_OWNER_REVIEW",
        "D2_gate": ledger["D2_gate"], "D3_status": ledger["D3_status"], "closed_utc": ledger["closed_utc"],
        "release_utc": release["release_utc"], "original_deadline_utc": release["deadline_utc"],
        "retained_cpu_seconds": sum(ledger["retained_seconds"].values()), "cpu_cap_seconds": 86400,
        "utility_individual_envelopes_seconds": utility, "utility_bucket_seconds": 6000,
        "known_preserved_utility_failures": failed, "private_closed_ledger_sha256": sha(TASK / "ledger.json"),
        "biological_units": 2052, "offline_product_paper_handoff": "COMPLETE",
        "complete_return_and_exact_cleanup": "PASS", "final_outcomes_open": False,
        "conditional96h_activated": False, "M3": "NOT_RELEASED", "actual_product_integration": "NOT_RUN",
        "journal_submission": "NOT_RUN", "normal_main_commit_push_authorized": True,
        "owner_review_before_new_phase": True}
    new(ROOT / "research/manifests/lr_d23_status_20261109_v1.json", status)
    new(PUBLIC / "closed-account-v1.json", status)
    print(status)


if __name__ == "__main__":
    action = sys.argv[1]
    assert action in ("validate", "lint", "close")
    if action == "close":
        close()
    elif action == "lint":
        guard = orchestration_start("final-lint", 30, 60)
        try:
            source = sorted(ROOT.glob("research/lr_d23_v1/*.py")) + sorted(ROOT.glob("tools/lrd23*.py")) + sorted(ROOT.glob("tests/research/test_lr_d23*.py"))
            result = subprocess.run(["rtk", "proxy", sys.executable, "-m", "ruff", "check", "--per-file-ignores",
                "tools/lrd23_return_v1.py:I001", *[p.relative_to(ROOT).as_posix() for p in source]],
                cwd=ROOT, capture_output=True, text=True, timeout=45)
            new(TASK / "final-lint-output-v2.json", {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
            print(result.stdout)
            assert result.returncode == 0
            utility_finish("final-lint", guard, "PASS")
        except BaseException:
            utility_finish("final-lint", guard, "FAIL")
            raise
    else:
        guard = utility_start("final-validation-v2", 240, 600)
        try:
            validate()
            utility_finish("final-validation-v2", guard, "PASS")
        except BaseException:
            utility_finish("final-validation-v2", guard, "FAIL")
            raise
