"""Validate documentation identity, active links, references and calculations.

Uses only the Python standard library. Does not run the scientific benchmark.
"""

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


def protected_match(root: Path, record: dict, source_commit: str) -> str | None:
    """Retain raw-byte evidence; accept only proven Git checkout CRLF differences."""
    path = root / record["path"]
    if not path.is_file():
        return None
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() == record["sha256"]:
        return "raw"
    if b"\0" in raw or hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() != record["sha256"]:
        return None
    try:
        original = subprocess.check_output(
            ["git", "show", source_commit + ":" + record["path"]],
            cwd=root,
            stderr=subprocess.DEVNULL,
        )
        unchanged = (
            subprocess.run(
                ["git", "diff", "--quiet", source_commit, "--", record["path"]],
                cwd=root,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if unchanged and hashlib.sha256(original).hexdigest() == record["sha256"]:
        return "git_verified_crlf_only"
    return None


def active_markdown(root: Path) -> list[Path]:
    """Inspect repository files, excluding ignored dependencies and old snapshots."""
    names = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
        )
        .decode("utf-8")
        .split("\0")
    )
    excluded = {"archive", "requirements_v3", "requirements", "evidence"}
    return sorted(
        {
            root / name
            for name in names
            if name.endswith(".md")
            and not excluded.intersection(Path(name).parts)
            and (root / name).is_file()
        }
    )


def validate(root: Path) -> dict:
    failures = []
    checks = {}
    protected = json.loads((root / "docs/07_audit/protected_source_manifest.json").read_text())
    modes = {"raw": 0, "git_verified_crlf_only": 0}
    newline_paths = []
    for record in protected["files"]:
        mode = protected_match(root, record, protected["source_commit"])
        if mode is None:
            failures.append("Protected source differs: " + record["path"])
        else:
            modes[mode] += 1
            if mode == "git_verified_crlf_only":
                newline_paths.append(record["path"])
    checks["protected_files"] = len(protected["files"])
    checks["protected_raw_byte_matches"] = modes["raw"]
    checks["protected_git_verified_crlf_only"] = newline_paths

    archive = root / "docs/archive/pre_academic_20261104"
    snapshot = json.loads((archive / "snapshot_manifest.json").read_text())
    for record in snapshot["files"]:
        path = archive / record["path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            failures.append("Archived document differs: " + record["path"])
    checks["archived_originals"] = len(snapshot["files"])

    active = active_markdown(root)
    links = 0
    anchors = 0
    for path in active:
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip().split(' "')[0].strip("<>")
            if re.match(r"^(https?://|mailto:|data:)", target):
                continue
            file_target, _, fragment = unquote(target).partition("#")
            target = file_target
            linked = (path.parent / target).resolve() if target else path
            links += 1
            if not linked.exists():
                failures.append(f"Broken active link: {path.relative_to(root)} -> {target}")
            elif fragment and linked.suffix == ".md":
                headings = re.findall(
                    r"^#{1,6}\s+(.+?)\s*#*$", linked.read_text(encoding="utf-8"), flags=re.M
                )
                slugs = set()
                for heading in headings:
                    slug = re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")
                    slugs.add(slug)
                anchors += 1
                if fragment not in slugs:
                    failures.append(
                        f"Unresolved heading anchor: {path.relative_to(root)} -> {target}#{fragment}"
                    )
    checks["active_markdown_files"] = len(active)
    checks["active_local_links"] = links
    checks["markdown_heading_anchors"] = anchors
    checks["active_words"] = sum(len(p.read_text(encoding="utf-8").split()) for p in active)

    manifest = json.loads((root / "docs/02_literature/literature_manifest.json").read_text())
    records = manifest["records"]
    ids = {r["id"] for r in records}
    if len(records) != 28 or ids != {f"R{i:02d}" for i in range(1, 29)}:
        failures.append("Reference set is not the declared R01-R28")
    bib = (root / "docs/02_literature/references.bib").read_text()
    for rid in ids:
        if not re.search(r"@\w+\{" + rid + ",", bib):
            failures.append("Missing BibTeX entry: " + rid)
    for r in records:
        if r["public_repository_pdf_included"]:
            failures.append("Reading PDF incorrectly marked public: " + r["id"])
        if not r["authors"]:
            failures.append("Missing author metadata: " + r["id"])
    for p in active:
        if "archive" in p.parts:
            continue
        for rid in re.findall(r"\bR\d{2}\b", p.read_text()):
            if rid not in ids:
                failures.append("Unknown reference: " + rid)
    checks["references"] = len(records)
    checks["package_declared_verified_private_pdf_records"] = sum(
        r["status"] == "PDF_VERIFIED" for r in records
    )
    checks["link_only_records"] = sum(r["status"] != "PDF_VERIFIED" for r in records)
    supplements = manifest.get("supplemental_records", [])
    if manifest.get("verified_pdfs") != checks["package_declared_verified_private_pdf_records"]:
        failures.append("Declared main PDF count differs from records")
    if len(supplements) != 1 or supplements[0].get("id") != "R05_SI":
        failures.append("Missing or unexpected supplementary source identity")
    for record in records + supplements:
        if not re.fullmatch(r"[0-9a-f]{64}", record.get("pdf_sha256", "")):
            failures.append("Missing PDF identity hash: " + record["id"])
        if not isinstance(record.get("pages"), int) or record["pages"] <= 0:
            failures.append("Invalid PDF page count: " + record["id"])
        if record.get("public_repository_pdf_included") is not False:
            failures.append("PDF incorrectly marked public: " + record["id"])
    checks["supplementary_pdf_records"] = len(supplements)
    checks["package_declared_total_reading_pdfs"] = len(records) + len(supplements)
    checks["package_declared_reading_pdf_pages"] = sum(r["pages"] for r in records + supplements)
    if manifest.get("total_reading_pdf_pages") != checks["package_declared_reading_pdf_pages"]:
        failures.append("Declared total reading pages differs from records")
    r05 = next(r for r in records if r["id"] == "R05")
    if (
        r05.get("reviewed_version_id") != "chemrxiv-2023-wgl32-v3"
        or r05.get("associated_publication_full_text_inspected") is not False
    ):
        failures.append("R05 preprint/journal version boundary is inaccurate")

    with (root / "docs/02_literature/extraction_matrix.csv").open(
        newline="", encoding="utf-8"
    ) as f:
        matrix = list(csv.DictReader(f))
    if {r["reference_id"] for r in matrix} != ids:
        failures.append("Extraction matrix source IDs differ")
    by_id = {r["id"]: r for r in records}
    for row in matrix:
        r = by_id.get(row["reference_id"])
        if r and any(
            row[k] != r[v]
            for k, v in [
                ("title", "title"),
                ("source", "landing"),
                ("read_level", "read_level"),
                ("pdf_status", "status"),
            ]
        ):
            failures.append("Stale extraction matrix: " + row["reference_id"])
    for name in ("catalogue_audit.csv", "papers_manifest.json"):
        if (root / "papers" / name).read_bytes() != (archive / "papers" / name).read_bytes():
            failures.append("Frozen historical catalogue differs: " + name)
    checks["active_literature_matrix_consistent"] = True
    checks["frozen_historical_catalogues_preserved"] = 2

    economic = root / "docs/04_business/illustrative_unit_economics.csv"
    with economic.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        cost = (
            float(r["delivery_hours"]) * float(r["labor_rate"])
            + float(r["infrastructure"])
            + float(r["support_other"])
        )
        contribution = float(r["fee"]) - cost
        if (
            abs(cost - float(r["direct_cost"])) > 1e-8
            or abs(contribution - float(r["contribution"])) > 1e-8
            or abs(contribution / float(r["fee"]) - float(r["contribution_margin"])) > 1e-8
        ):
            failures.append("Unit-economics calculation mismatch: " + r["scenario"])
    checks["economic_scenarios"] = len(rows)

    cfg = json.loads((root / "research/configs/development_protocol.json").read_text())
    if (
        cfg["status"] != "SPECIFICATION_NOT_EXECUTABLE_BY_CURRENT_CLI"
        or cfg["paid_compute_authorized"]
    ):
        failures.append("Protocol execution/spending status is inaccurate")
    for name in (
        "frozen_model_greedy",
        "nearest_delivered_hit_similarity",
        "objective_matched_async_probabilistic_comparator",
    ):
        if name not in cfg["methods"]["planned"]:
            failures.append("Missing planned comparison: " + name)
    if (
        cfg.get("initialization_regimes", {}).get("primary")
        != "uniform_without_label_inspection_including_zero_active_starts"
    ):
        failures.append("Uniform primary initialization contract is missing")
    freeze = json.loads((root / "research/manifests/protocol_freeze.json").read_text())
    if freeze["status"] != "NOT_FROZEN" or freeze["final_outcomes_inspected"]:
        failures.append("Unexecuted study incorrectly marked frozen/evaluated")
    checks["declarative_configs"] = 2

    preserved = json.loads((root / "docs/evidence/hiv-benchmark/summary.json").read_text())
    expected = {
        "random": 0.7,
        "greedy": 3.8,
        "uncertainty": 0.9,
        "q_learning": 3.8,
        "contextual_bandit": 3.8,
    }
    if {r["policy"]: r["mean_hits"] for r in preserved["statistics"]["summary"]} != expected:
        failures.append("Historical result summary mismatch")
    checks["historical_policy_means"] = len(expected)

    chapter_paths = sorted((root / "docs/01_paper").glob("[0-9][0-9]_*.md"))
    manuscript = (root / "docs/01_paper/MANUSCRIPT.md").read_text()
    for chapter in chapter_paths:
        transformed = re.sub(r"^(#{1,5}) ", r"#\1 ", chapter.read_text(), flags=re.M).rstrip()
        if transformed not in manuscript:
            failures.append("Assembled manuscript is stale: " + chapter.name)
    checks["assembled_manuscript_chapters"] = len(chapter_paths)

    # Binary inputs are distributed separately; this check works for full and overlay checkouts.
    reading_room = root.parent / "reading_room_private"
    if reading_room.is_dir():
        for record in records + supplements:
            path = reading_room / record["private_reading_filename"]
            if (
                not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != record["pdf_sha256"]
            ):
                failures.append("Private reading PDF differs: " + record["id"])
        checks["private_pdf_hashes_verified_here"] = len(records) + len(supplements)
    else:
        checks["private_pdf_hashes_verified_here"] = (
            "NOT_PRESENT_IN_PUBLIC_PAYLOAD; see PDF receipt"
        )

    return {
        "status": "PASS" if not failures else "FAIL",
        "source_commit": protected["source_commit"],
        "checks": checks,
        "failures": failures,
        "not_run": [
            "final multi-target confirmatory study (NCATS development pilot recorded separately)",
            "new controller training",
            "full application Python/frontend/browser suites",
            "customer validation",
            "journal submission",
            "remote Git push",
            "provided bulk apply-helper writes on Windows (newer HEAD correctly rejected in dry run)",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(Path(__file__).resolve().parents[1])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["status"] == "PASS" else 1)
