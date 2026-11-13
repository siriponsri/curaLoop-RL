"""Prepare separate candidate inputs and evaluator assets without displaying gold."""

import ast
import json
import shutil
import stat
import zipfile
from pathlib import PurePosixPath

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write

DEVELOPMENT = [2, 3]
LOCKED_CANDIDATES = [5, 16, 18, 19, 22, 26, 40, 41, 85]


def main():
    authority()
    folder = TASK / "native-assets-v1"
    folder.mkdir(exist_ok=False)
    rows = read(TASK / "catalog-v1/public-task-and-evaluator-metadata.json")
    selected = [r for r in rows if r["instance_id"] in DEVELOPMENT + LOCKED_CANDIDATES]
    assert len(selected) == 11 and not any(r["preliminary_exclusions"] for r in selected)
    prefixes = {}
    for r in selected:
        dataset = r["dataset_folder_tree"].splitlines()[0].removeprefix("|-- ").strip().rstrip("/")
        assert dataset and "/" not in dataset and "\\" not in dataset and ":" not in dataset
        prefixes[r["instance_id"]] = "benchmark/datasets/" + dataset + "/"
    archive = (
        ROOT
        / "research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip"
    )
    inventory = []
    with zipfile.ZipFile(archive) as z:
        infos = {i.filename: i for i in z.infolist()}
        for r in selected:
            identity = r["instance_id"]
            candidate = folder / "candidate-inputs" / str(identity)
            evaluator = folder / "evaluator-only" / str(identity)
            gold_name = "benchmark/gold_programs/" + r["gold_program_name"]
            eval_name = "benchmark/eval_programs/" + r["eval_script_name"]
            # Extract original inputs only for candidates; private evaluator gets a
            # separate tree, never a mount visible to generated programs.
            names = [n for n in infos if n.startswith(prefixes[identity])]
            eval_names = [gold_name, eval_name] + [
                n for n in infos if n.startswith("benchmark/eval_programs/gold_results/")
            ]
            for target_root, members in ((candidate, names), (evaluator, names + eval_names)):
                for name in dict.fromkeys(members):
                    info = infos[name]
                    path = PurePosixPath(name)
                    assert not path.is_absolute() and ".." not in path.parts
                    assert all(":" not in p and "\\" not in p for p in path.parts)
                    assert not stat.S_ISLNK(info.external_attr >> 16)
                    target = target_root.joinpath(*path.parts)
                    assert target.resolve().is_relative_to(folder.resolve())
                    if info.is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                        continue
                    assert info.file_size <= 256 * 1024**2
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(info, pwd=b"scienceagentbench") as src, target.open("xb") as dst:
                        shutil.copyfileobj(src, dst, 65536)
                    assert target.stat().st_size == info.file_size
            gold_path = evaluator / gold_name
            tree = ast.parse(gold_path.read_text(encoding="utf-8-sig"))
            imports = sorted(
                {
                    alias.name.split(".")[0]
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Import)
                    for alias in node.names
                }
                | {
                    node.module.split(".")[0]
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module
                }
            )
            inventory.append(
                {
                    "instance_id": identity,
                    "role": "development" if identity in DEVELOPMENT else "locked_candidate",
                    "lineage_group": r["github_name"],
                    "source_path": r["src_file_or_path"],
                    "dataset_prefix": prefixes[identity],
                    "reference_imports": imports,
                    "reference_sha256": sha(gold_path),
                    "evaluator_sha256": sha(evaluator / eval_name),
                }
            )
    pins = {
        p.relative_to(folder).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)}
        for p in sorted(folder.rglob("*"))
        if p.is_file()
    }
    assert sum(v["bytes"] for v in pins.values()) <= 1024**3
    write(folder / "private-asset-manifest.json", pins)
    write(folder / "role-and-import-inventory.json", inventory)
    receipt = {
        "status": "PASS_SEPARATE_ASSET_TREES_NOT_NATIVE_QUALIFICATION",
        "development_ids": DEVELOPMENT,
        "locked_candidate_ids": LOCKED_CANDIDATES,
        "minimum_locked_tasks_for_pilot": 6,
        "minimum_locked_repository_lineage_groups": 4,
        "group_rule": "Conservative source repository lineage; not certified independent publications",
        "role_rule_frozen_before_reference_body_processing": True,
        "neural_training_tasks_excluded_from_this_cpu_bounded_pool": True,
        "protected_old_outcomes_opened": False,
        "native_success": "NOT_RUN",
        "candidate_gold_access": False,
        "gold_body_displayed_to_model_or_author_context": False,
        "gold_processed_only_for_isolated_reference_syntax_and_later_qualification": True,
        "files": len(pins),
        "expanded_private_bytes": sum(v["bytes"] for v in pins.values()),
        "private_manifest_sha256": sha(folder / "private-asset-manifest.json"),
        "reference_import_inventory": inventory,
    }
    write(PUBLIC / "native-asset-separation-v1.json", receipt)
    print(
        json.dumps(
            {k: v for k, v in receipt.items() if k != "reference_import_inventory"}, indent=2
        )
    )


if __name__ == "__main__":
    main()
