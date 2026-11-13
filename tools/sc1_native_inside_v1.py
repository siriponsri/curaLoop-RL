"""Task-owned container entrypoint for one fixed SciCode admission recipe."""
import ast
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

WORK = Path("/control")


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def watchdog(limits):
    os.sched_setaffinity(0, {limits["initial_cpu"]})
    while True:
        usage = dict(line.split() for line in Path("/sys/fs/cgroup/cpu.stat").read_text().splitlines())
        if time.time() >= limits["deadline_epoch"] or int(usage["usage_usec"]) / 1e6 >= limits["cpu_seconds"] - 1:
            write(WORK / "limit-stop.json", {"status": "FAIL_RESOURCE_LIMIT", "usage": usage, "time_epoch": time.time()})
            os._exit(124)
        time.sleep(.2)


def setup():
    pins = ["numpy==1.26.4", "scipy==1.11.4", "sympy==1.12", "h5py==3.10.0", "matplotlib==3.8.4"]
    p = subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-cache-dir", "--only-binary=:all:", "--target=/env", *pins], capture_output=True, text=True, timeout=850)
    (WORK / "pip.stdout.txt").write_text(p.stdout)
    (WORK / "pip.stderr.txt").write_text(p.stderr)
    write(WORK / "result.json", {"status": "PASS" if p.returncode == 0 else "FAIL", "returncode": p.returncode, "pins": pins})
    return p.returncode


def qualify():
    import h5py
    import numpy
    import scipy
    import sympy
    import matplotlib
    root = Path("/assets")
    raw = {name: [json.loads(line) for line in (root / f"problems_{name}.jsonl").read_text().splitlines() if line.strip()] for name in ("dev", "test")}
    selected = json.loads((root / "development-selection.json").read_text())["selected_main_ids"]
    # Strip only the optional Hub-loader import. Native parser function bodies,
    # test predicates, fixture loader semantics and tolerances remain unchanged.
    source = (root / "code/src/scicode/parse/parse.py").read_text()
    tree = ast.parse(source)
    nodes = [n for n in tree.body if not (isinstance(n, ast.ImportFrom) and n.module == "datasets")]
    adapted = ast.unparse(ast.Module(body=nodes, type_ignores=[]))
    original_functions = {n.name: ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    adapted_functions = {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(adapted).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if original_functions != adapted_functions:
        raise RuntimeError("Native fixture parser function changed")
    package = WORK / "native-support/scicode/parse"
    package.mkdir(parents=True, exist_ok=False)
    (package.parent / "__init__.py").write_text("")
    (package / "__init__.py").write_text("")
    (package / "parse.py").write_text(adapted)
    metadata = []
    skipped = {"13.6", "62.1", "76.3"}
    with h5py.File(root / "test_data.h5", "r") as data:
        for row in raw["test"]:
            missing = []
            for step in row["sub_steps"]:
                if step["step_number"] in skipped:
                    continue
                for i in range(len(step["test_cases"])):
                    group = f'{step["step_number"]}/test{i+1}'
                    if group not in data:
                        missing.append(group)
            metadata.append({"main_id": row["problem_id"], "fixture_groups_complete": not missing, "missing_groups": missing,
                             "native_skipped_substeps": [s["step_number"] for s in row["sub_steps"] if s["step_number"] in skipped]})
    results = []
    env = dict(os.environ, PYTHONPATH="/control/native-support:/env", MPLCONFIGDIR="/tmp/matplotlib", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    for identity in selected:
        row = next(r for r in raw["dev"] if r["problem_id"] == identity)
        previous = row["required_dependencies"] + "\n"
        for step in row["sub_steps"]:
            code = previous + "\n" + step["ground_truth_code"]
            previous = code
            body = code + "\nfrom scicode.parse.parse import process_hdf5_to_tuple\n"
            body += f"targets = process_hdf5_to_tuple({step['step_number']!r}, {len(step['test_cases'])}, '/assets/test_data.h5')\n"
            for i, case in enumerate(step["test_cases"]):
                body += f"target = targets[{i}]\n" + case + "\n"
            path = WORK / f'gold-{step["step_number"]}.py'
            path.write_text(body)
            begin = time.monotonic()
            try:
                p = subprocess.run([sys.executable, str(path)], env=env, capture_output=True, text=True, timeout=90)
                (WORK / f'gold-{step["step_number"]}.stdout.txt').write_text(p.stdout)
                (WORK / f'gold-{step["step_number"]}.stderr.txt').write_text(p.stderr)
                result = {"step_id": step["step_number"], "status": "PASS" if p.returncode == 0 else "FAIL", "returncode": p.returncode}
            except subprocess.TimeoutExpired:
                result = {"step_id": step["step_number"], "status": "FAIL_TIMEOUT"}
            result["wall_seconds"] = time.monotonic() - begin
            results.append(result)
    status = "PASS" if all(r["status"] == "PASS" for r in results) and sum(r["fixture_groups_complete"] for r in metadata) >= 50 else "FAIL"
    write(WORK / "result.json", {"status": status, "selected_validation_ids": selected, "validation_native_results": results,
          "test_fixture_metadata": metadata, "test_expected_numeric_values_inspected": False,
          "test_reference_programs_executed": False, "native_parser_functions_ast_identical": True,
          "environment": {"numpy": numpy.__version__, "scipy": scipy.__version__, "sympy": sympy.__version__, "h5py": h5py.__version__, "matplotlib": matplotlib.__version__},
          "known_upstream_skips": sorted(skipped), "native_scoring_limit": "Inspected upstream inspect integration skips these three steps but retains len(sub_steps) as its denominator; do not silently repair or claim exact leaderboard reproduction"})
    return 0 if status == "PASS" else 2


def main():
    limits = json.loads((WORK / "limits.json").read_text())
    os.sched_setaffinity(0, {limits["initial_cpu"]})
    threading.Thread(target=watchdog, args=(limits,), daemon=True).start()
    if sys.argv[1] == "setup":
        return setup()
    if sys.argv[1] == "qualify":
        return qualify()
    if sys.argv[1] == "probe":
        while True:
            sum(i*i for i in range(10000))
    raise ValueError("Unsupported action")


if __name__ == "__main__":
    sys.exit(main())
