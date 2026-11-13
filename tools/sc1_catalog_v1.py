"""Create agent-safe views and fixed development IDs before any model outcome."""
import ast
import hashlib
import importlib.util
import json
from tools.sc1_control_v1 import ACCOUNT, ROOT, digest, write_new


def main():
    root = ROOT / "research/raw_data/external-benchmarks/scicode-2024"
    public = root / "agent-public-v1"
    catalog = {}
    modules = set()
    for split in ("dev", "test"):
        source = root / "upstream-hf" / f"problems_{split}.jsonl"
        rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
        safe_rows, entries = [], []
        for row in rows:
            safe = {key: row[key] for key in ("problem_id", "problem_name", "problem_description_main", "problem_background_main", "problem_io", "required_dependencies")}
            safe["sub_steps"] = [{key: step[key] for key in ("step_number", "function_header", "return_line", "step_description_prompt", "step_background")} for step in row["sub_steps"]]
            safe_rows.append(safe)
            imports = set()
            try:
                tree = ast.parse(row["required_dependencies"])
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module.split(".")[0])
            except SyntaxError:
                imports.add("UNPARSEABLE_DEPENDENCIES")
            modules.update(imports)
            entries.append({"main_id": row["problem_id"], "subproblem_count": len(row["sub_steps"]),
                            "required_import_roots": sorted(imports),
                            "native_test_counts": {step["step_number"]: len(step["test_cases"]) for step in row["sub_steps"]}})
        public.mkdir(parents=True, exist_ok=True)
        path = public / f"problems_{split}.jsonl"
        with path.open("x", encoding="utf-8", newline="\n") as output:
            for row in safe_rows:
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
        catalog[split] = {"source_sha256": digest(source), "agent_view_sha256": digest(path), "metadata": entries}
    ordered = sorted((row["main_id"] for row in catalog["dev"]["metadata"]), key=lambda identity: hashlib.sha256(("LR-SC1-fixed-development-v1:" + identity).encode()).hexdigest())
    chosen = ordered[:6]
    write_new(ACCOUNT / "catalog-v1.json", {"catalog": catalog, "development_selection": {"rule": "ascending SHA256 of LR-SC1-fixed-development-v1: plus official validation main id; first six", "selected": chosen},
                                         "package_presence_only": {name: importlib.util.find_spec(name) is not None for name in ("numpy", "scipy", "sympy", "h5py", "pandas")}})
    write_new(ROOT / "docs/evidence/lr-sc1-20261113-v1/development-selection-v1.json", {"selected_main_ids": chosen, "selection_seed_prefix": "LR-SC1-fixed-development-v1:", "outcome_based_selection": False,
                                                                                  "hf_revision": "4510f6a6aa27c43fad7b43da2c59602a86e88480"})
    print(json.dumps({"development_ids": chosen, "imports": sorted(modules), "package_presence": {name: importlib.util.find_spec(name) is not None for name in ("numpy", "scipy", "sympy", "h5py", "pandas")},
                      "test_main_count": len(catalog["test"]["metadata"]), "forbidden_fields_stripped": ["ground_truth_code", "general_solution", "test_cases", "general_tests"]}))


if __name__ == "__main__":
    main()
