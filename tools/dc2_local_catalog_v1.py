"""Inspect public task metadata and evaluator syntax, never reference answers."""

import ast
import json
import zipfile
from collections import Counter
from pathlib import PurePosixPath

import pyarrow.parquet as pq
from dc2_local_admin_v1 import OLD_TASK, PUBLIC, ROOT, TASK, authority, sha, write


def inspect_python(raw):
    tree = ast.parse(raw)
    imports = sorted(
        {
            name.name.split(".")[0]
            for n in ast.walk(tree)
            if isinstance(n, ast.Import)
            for name in n.names
        }
        | {
            n.module.split(".")[0]
            for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom) and n.module
        }
    )
    calls = sorted({ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)})
    arguments = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_argument"
        ):
            arguments.extend(
                a.value
                for a in node.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)
            )
    return {
        "imports": imports,
        "call_names": calls,
        "cli_arguments": arguments,
        "paid_or_image_judge_import": any(n in imports for n in ("openai", "anthropic", "litellm")),
    }


def main():
    authority()
    folder = TASK / "catalog-v1"
    folder.mkdir(exist_ok=False)
    annotation = OLD_TASK / "dataset-intake-v1/verified.parquet"
    cols = [
        "instance_id",
        "domain",
        "github_name",
        "subtask_categories",
        "task_inst",
        "domain_knowledge",
        "dataset_folder_tree",
        "src_file_or_path",
        "gold_program_name",
        "output_fname",
        "eval_script_name",
    ]
    rows = pq.read_table(annotation, columns=cols).to_pylist()
    archive = (
        ROOT
        / "research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip"
    )
    catalog = []
    with zipfile.ZipFile(archive) as z:
        index = {i.filename: i for i in z.infolist()}
        assert all(
            not PurePosixPath(n).is_absolute() and ".." not in PurePosixPath(n).parts for n in index
        )
        for row in rows:
            if row["domain"] not in ("Computational Chemistry", "Bioinformatics"):
                continue
            name = "benchmark/eval_programs/" + row["eval_script_name"]
            assert name in index and index[name].file_size <= 1024**2
            # Scorer bodies remain evaluator-side; emit only syntax/dependency metadata.
            raw = z.read(name, pwd=b"scienceagentbench")
            target = folder / "evaluator-only" / row["eval_script_name"]
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(raw)
            info = inspect_python(raw.decode("utf-8-sig"))
            excluded = []
            if row["instance_id"] == 11:
                excluded.append("REPORTED_BBBC002_REFERENCE_EXPOSURE")
            if info["paid_or_image_judge_import"]:
                excluded.append("NATIVE_SCORER_REQUIRES_EXTERNAL_MODEL_JUDGE")
            if PurePosixPath(row["output_fname"]).suffix.lower() in (
                ".png",
                ".jpg",
                ".jpeg",
                ".pdf",
            ):
                excluded.append("VISUAL_OUTPUT_NATIVE_SCORING_NOT_ADMITTED")
            catalog.append(
                {
                    **row,
                    "evaluator_sha256": sha(target),
                    "evaluator_syntax": info,
                    "preliminary_exclusions": excluded,
                }
            )
    write(folder / "public-task-and-evaluator-metadata.json", catalog)
    receipt = {
        "status": "PASS_STATIC_METADATA_NOT_NATIVE_EXECUTION",
        "annotation_sha256": sha(annotation),
        "tasks_inspected": len(catalog),
        "reference_programs_or_gold_outputs_read": False,
        "candidate_model_calls": 0,
        "evaluator_bodies_exposed_to_model": False,
        "public_task_preview_column_read": False,
        "exclusion_counts": dict(Counter(e for r in catalog for e in r["preliminary_exclusions"])),
        "preliminary_candidate_ids": [
            r["instance_id"] for r in catalog if not r["preliminary_exclusions"]
        ],
        "candidate_cohort_admitted": False,
        "syntax_summary": [
            {
                "instance_id": r["instance_id"],
                "imports": r["evaluator_syntax"]["imports"],
                "cli_arguments": r["evaluator_syntax"]["cli_arguments"],
                "excluded": r["preliminary_exclusions"],
            }
            for r in catalog
        ],
    }
    write(PUBLIC / "static-task-catalog-v1.json", receipt)
    print(json.dumps({k: v for k, v in receipt.items() if k != "syntax_summary"}, indent=2))


if __name__ == "__main__":
    main()
