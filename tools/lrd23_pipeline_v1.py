"""Frozen LR-D23 sequence, at most one remote batch on each admitted core."""
# ruff: noqa: E402

import json
import sys
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.analysis import analyze
from research.lr_d23_v1.common import (
    PUBLIC,
    REMOTE,
    TASK,
    authority,
    ledger_save,
    new,
    now,
    orchestration_start,
    read,
    sha,
    utility_finish,
)
from research.lr_d23_v1.matrix import batches, evaluation, training
from tools.lrd23_remote_v1 import book, dispatch, remote, settle

CPUS = (69, 70, 71)


def upload(path, relative):
    assert relative.startswith("matrices/") and ".." not in relative and relative.endswith(".json")
    code = '''import hashlib,json,os,resource,signal,sys
from pathlib import Path
os.sched_setaffinity(0,{69});resource.setrlimit(resource.RLIMIT_CPU,(10,10));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(30)
root=Path(__ROOT__);assert root.resolve()==root and root.is_dir() and not root.is_symlink()
data=sys.stdin.buffer.read(__SIZE__+1);assert len(data)==__SIZE__ and hashlib.sha256(data).hexdigest()==__SHA__
p=root/__REL__;p.parent.mkdir(exist_ok=True)
with p.open('xb') as f:f.write(data)
print(json.dumps({'status':'PASS','sha256':hashlib.sha256(data).hexdigest()}))
'''.replace("__ROOT__", repr(REMOTE)).replace("__SIZE__", str(path.stat().st_size)).replace("__SHA__", repr(sha(path))).replace("__REL__", repr(relative))
    with path.open("rb") as stream:
        response = remote(code, stdin=stream, timeout=40)
    new(TASK / "transport" / (path.stem + "-receipt.json"),
        {"exit_code": response.returncode, "stdout": response.stdout.decode(), "stderr": response.stderr.decode()})
    assert response.returncode == 0 and json.loads(response.stdout)["sha256"] == sha(path)


def freeze():
    authority()
    sources = read(TASK / "sources.json")
    matrices = {"round0": training(sources, CPUS, 0), "round1": training(sources, CPUS, 1),
                "primary": evaluation(sources, CPUS), "attribution": evaluation(sources, CPUS, attribution=True)}
    for predictor in ("rf", "neighbor"):
        for budget in (16, 32):
            for multiplier in (1., .5):
                if (predictor, budget, multiplier) != ("rf", 32, 1.):
                    key = f"transfer-{predictor}-{budget}-{multiplier}"
                    matrices[key] = evaluation(sources, CPUS, predictor, budget, multiplier)
    for key, value in matrices.items():
        new(TASK / "matrices" / (key + ".json"), value)
    pins = {}
    for pattern in ("research/lr_d23_v1/*.py", "tools/lrd23*.py", "tests/research/test_lr_d23*.py"):
        pins.update({p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob(pattern)})
    contract = "docs/03_research/LR_D23_ALGORITHM_AND_FREEZE_20261109.md"
    pins[contract] = sha(ROOT / contract)
    value = {"status": "PASS_PRE_OUTCOME_FREEZE", "utc": now().isoformat(), "source_pins": pins,
             "matrices": {k: sha(TASK / "matrices" / (k + ".json")) for k in matrices},
             "sources_sha256": sha(TASK / "sources.json"), "biological_labels_decoded": False,
             "final_outcomes_open": False, "code_pins": read(TASK / "code-pins.json")}
    new(TASK / "execution-freeze-v1.json", value)
    new(PUBLIC / "execution-freeze-v1.json", value)
    for key in ("round0", "round1"):
        upload(TASK / "matrices" / (key + ".json"), "matrices/" + key + ".json")
    print({"stage": "freeze", "status": "PASS", "matrices": len(matrices)}, flush=True)


def validate_freeze():
    frozen = read(TASK / "execution-freeze-v1.json")
    assert all(sha(ROOT / name) == digest for name, digest in frozen["source_pins"].items())
    assert all(sha(TASK / "matrices" / (key + ".json")) == digest for key, digest in frozen["matrices"].items())
    return frozen


def profiles():
    contexts = [dict(n=n, predictor=p, n0=n0, budget=b) for n in (128, 303)
                for p in ("rf", "neighbor") for n0 in (0, 16) for b in (16, 32)]
    names = []
    for cpu in CPUS:
        name = "profiles-c" + str(cpu)
        book(name, "profiles", cpu, "synthetic_admission", 24, 15, {"contexts": contexts})
        names.append(name)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(dispatch, n): n for n in names}
        for future in futures:
            result = future.result()
            settle(futures[future], result)
    caps = {}
    all_results = [r for n in names for r in read(TASK / "jobs" / n / "result.json")["contexts"]]
    assert len(all_results) == 48
    for kind in ("rf", "neighbor"):
        for n0 in (0, 16):
            for budget in (16, 32):
                selected = [r for r in all_results if (r["spec"]["predictor"], r["spec"]["n0"], r["spec"]["budget"]) == (kind, n0, budget)]
                assert len(selected) == 6 and all(r["status"] == "PASS" for r in selected)
                cap = 1.25 * max(r["scientific_cpu_seconds"] for r in selected)
                assert cap <= (5 if kind == "rf" else 1)
                fit = max(r["last_fit_cpu_seconds"] for r in selected)
                caps[f"{kind}:{n0}:{budget}"] = {"C_ref": cap,
                    "cost_priors": {"UPDATE": max(.00001, fit), "REUSE": .00001, "PLAN": .1}}
    value = {"status": "PASS_TECHNICAL_ADMISSION", "utc": now().isoformat(), "admission_contexts": 72,
             "complete_G1_campaigns": 48, "constructed_checks": 24, "cpus": list(CPUS), "caps": caps,
             "biological_labels_decoded": False, "final_outcomes_open": False}
    new(TASK / "technical-admission.json", value)
    new(PUBLIC / "technical-admission-v1.json", value)
    print({"stage": "technical-admission", "status": "PASS", "caps": {k: v["C_ref"] for k, v in caps.items()}}, flush=True)


def stage(key, stage_name, artifacts, paths, pins, sequence):
    validate_freeze()
    matrix = read(TASK / "matrices" / (key + ".json"))
    bucket = "D3_additional_cells" if key.startswith("transfer-") else stage_name
    queues = {cpu: [] for cpu in CPUS}
    for cpu, units in batches(matrix, CPUS, stage_name):
        queues[cpu].append(units)
    sources = read(TASK / "sources.json")
    caps = read(TASK / "technical-admission.json")["caps"]
    with ThreadPoolExecutor(max_workers=3) as executor:
        pending = {}
        def submit(cpu):
            if not queues[cpu]:
                return
            units = queues[cpu].pop(0)
            name = f"{sequence}-{cpu}-{len(queues[cpu]):03d}"
            needs = {u["prefix"] for u in units if "prefix" in u}
            book(name, "campaigns", cpu, bucket, len(units), 10,
                 {"technical_admission": "PASS", "units": units, "sources": sources, "caps": caps,
                  "artifacts": artifacts, "unit_paths": {n: paths[n] for n in needs},
                  "unit_pins": {n: pins[n] for n in needs}, "matrix_sha256": sha(TASK / "matrices" / (key + ".json"))})
            pending[executor.submit(dispatch, name)] = (name, cpu)
        for cpu in CPUS:
            submit(cpu)
        while pending:
            ready, _ = wait(pending, timeout=30, return_when=FIRST_COMPLETED)
            if not ready:
                print({"stage": sequence, "active_cores": len(pending), "utc": now().isoformat()}, flush=True)
            for future in ready:
                name, cpu = pending.pop(future)
                result = future.result()
                settle(name, result)
                for unit in result["result"]["units"]:
                    assert unit["unit"] not in paths
                    paths[unit["unit"]], pins[unit["unit"]] = unit["path"], unit["sha256"]
                print({"batch": name, "status": "PASS", "units": result["result"]["count"]}, flush=True)
                submit(cpu)
    new(TASK / (sequence + "-index.json"), {"paths": paths, "pins": pins})


def fit(round_index, artifacts, paths, pins):
    validate_freeze()
    key = "round" + str(round_index)
    matrix_path = TASK / "matrices" / (key + ".json")
    matrix = read(matrix_path)
    groups = matrix["components"]
    needs = {u["name"] for u in matrix["units"] if u["stage"] == "paired_branches"}
    name = "fit-r" + str(round_index)
    book(name, "fit", 69, "gate_fits", 4 if round_index == 0 else 8, 120,
         {"technical_admission": "PASS", "round": round_index, "matrix_path": "matrices/" + key + ".json",
          "matrix_sha256": sha(matrix_path), "folds": {g: [v for v in groups if v != g] for g in groups},
          "unit_paths": {n: paths[n] for n in needs}, "unit_pins": {n: pins[n] for n in needs},
          "behavior_artifacts": artifacts})
    result = dispatch(name)
    settle(name, result)
    return dict(artifacts, **result["result"]["artifacts"])


def collect(keys, paths, pins, tag):
    names = [u["name"] for key in keys for u in read(TASK / "matrices" / (key + ".json"))["units"]]
    assert len(names) == len(set(names))
    rows = []
    for start in range(0, len(names), 60):
        selected = {name: {"path": paths[name], "sha256": pins[name]} for name in names[start:start + 60]}
        code = '''import hashlib,json,os,resource,signal
from pathlib import Path
os.sched_setaffinity(0,{69});resource.setrlimit(resource.RLIMIT_CPU,(10,10));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(30)
root=Path(__ROOT__);out=[]
for name,meta in __SELECTED__.items():
 p=root/meta['path']/'result.json';assert p.resolve().is_relative_to(root) and not p.is_symlink()
 b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==meta['sha256'];out.append(json.loads(b))
print(json.dumps(out))
'''.replace("__ROOT__", repr(REMOTE)).replace("__SELECTED__", repr(selected))
        response = remote(code, timeout=40)
        assert response.returncode == 0
        rows.extend(json.loads(response.stdout))
    expected = {u["name"]: u for key in keys for u in read(TASK / "matrices" / (key + ".json"))["units"]}
    assert all(r["spec"] == expected[r["spec"]["name"]] for r in rows)
    new(TASK / (tag + "-rows-private.json"), rows)
    result = analyze(rows, require_attribution=tag == "D2", budget=rows[0]["spec"]["budget"])
    new(TASK / (tag + "-aggregate.json"), result)
    new(PUBLIC / (tag + "-aggregate-v1.json"), result)
    return result


def pipeline():
    profiles()
    validate_freeze()
    paths, pins, artifacts = {}, {}, {}
    ledger = read(TASK / "ledger.json")
    ledger["development_labels_decoded"] = True
    ledger_save(ledger)
    for round_index in (0, 1):
        key = "round" + str(round_index)
        stage(key, "training_prefixes", artifacts, paths, pins, "r" + str(round_index) + "-prefix")
        stage(key, "paired_branches", artifacts, paths, pins, "r" + str(round_index) + "-branch")
        artifacts = fit(round_index, artifacts, paths, pins)
    new(TASK / "final-artifacts-private.json", artifacts)
    stage("primary", "D2_primary", artifacts, paths, pins, "D2-primary")
    stage("attribution", "attribution", artifacts, paths, pins, "D2-attr")
    result = collect(["primary", "attribution"], paths, pins, "D2")
    ledger = read(TASK / "ledger.json")
    ledger["D2_gate"] = result["status"]
    ledger_save(ledger)
    if result["status"] == "PASS_D2":
        for key in read(TASK / "execution-freeze-v1.json")["matrices"]:
            if key.startswith("transfer-"):
                stage(key, "D2_primary", artifacts, paths, pins, key)
                collect([key], paths, pins, key)
        ledger = read(TASK / "ledger.json")
        ledger["D3_status"] = "COMPLETE_PRESPECIFIED_CELLS"
        ledger_save(ledger)
    else:
        ledger = read(TASK / "ledger.json")
        ledger["D3_status"] = "NOT_RUN_D2_GATE_NOT_MET"
        ledger_save(ledger)
    new(TASK / "pipeline-terminal.json", {"status": "PASS_EXECUTION", "D2_gate": result["status"],
                                          "D3_status": ledger["D3_status"], "utc": now().isoformat()})


if __name__ == "__main__":
    action = sys.argv[1]
    assert action in ("freeze", "run")
    name = "local-" + action
    guard = orchestration_start(name, 120 if action == "freeze" else 1200, 300 if action == "freeze" else 24000)
    try:
        freeze() if action == "freeze" else pipeline()
        utility_finish(name, guard, "PASS")
    except BaseException:
        utility_finish(name, guard, "FAIL")
        raise
