"""Stream a private minimal bundle, qualify native references once, retain failures."""

import base64
import json
import subprocess
import tarfile

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write

WORKER = ROOT / "tools/dc2_local_native_worker_v1.py"


def call(action, payload=None, timeout=180):
    assert action in ("install", "receive", "setup", "qualify", "guard-probe")
    if action == "install":
        encoded = base64.b64encode(WORKER.read_bytes()).decode()
        command = "python3 -c \"import base64;exec(base64.b64decode('" + encoded + "'))\" install"
    else:
        command = (
            "python3 /home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1/native-worker-v1.py "
            + action
        )
    result = subprocess.run(
        [
            "rtk",
            "proxy",
            "ssh",
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=yes",
            "-o",
            "ConnectTimeout=15",
            "100.77.149.83",
            command,
        ],
        input=json.dumps(payload or {}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if result.returncode:
        raise RuntimeError(
            "Native operation failed: " + result.stderr[-1600:] + result.stdout[-800:]
        )
    return json.loads(result.stdout)


def reserve(name, cpu):
    release, ledger = authority()
    assert name not in ledger["bookings"]
    assert not any(
        b["status"] == "RESERVED" and b["host"] == "dr-train-native"
        for b in ledger["bookings"].values()
    )
    ledger["retained_cpu_seconds"]["admission"] += cpu
    assert (
        ledger["retained_cpu_seconds"]["admission"] <= ledger["stage_cpu_caps_seconds"]["admission"]
    )
    assert sum(ledger["retained_cpu_seconds"].values()) <= release["cpu_cap_seconds"]
    ledger["bookings"][name] = {
        "status": "RESERVED",
        "host": "dr-train-native",
        "bucket": "admission",
        "cpu_cap": cpu,
        "gpu_cap": 0,
    }
    save(ledger)


def settle(name, receipt, path):
    write(path, receipt)
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][name].update(
        status="SETTLED_ORIGINAL_OUTCOME_RETAINED", receipt_sha256=sha(path)
    )
    save(ledger)


def bundle():
    source = TASK / "native-assets-v1"
    entries = {}
    for p in sorted((source / "candidate-inputs").rglob("*")):
        if p.is_file():
            entries["assets/inputs/" + p.relative_to(source / "candidate-inputs").as_posix()] = p
    for row in read(TASK / "catalog-v1/public-task-and-evaluator-metadata.json"):
        identity = str(row["instance_id"])
        prefix = source / "evaluator-only" / identity
        if not prefix.exists():
            continue
        for rel in (
            "benchmark/gold_programs/" + row["gold_program_name"],
            "benchmark/eval_programs/" + row["eval_script_name"],
        ):
            entries["assets/evaluators/" + identity + "/" + rel] = prefix / rel
    gold = source / "evaluator-only/2/benchmark/eval_programs/gold_results"
    for p in sorted(gold.rglob("*")):
        if p.is_file():
            entries["assets/gold-results/" + p.relative_to(gold).as_posix()] = p
    manifest = {n: {"bytes": p.stat().st_size, "sha256": sha(p)} for n, p in entries.items()}
    target = TASK / "native-assets-v1.tar.gz"
    assert not target.exists()
    with tarfile.open(target, "w:gz", compresslevel=1) as archive:
        for name, path in entries.items():
            archive.add(path, arcname=name, recursive=False)
    assert target.stat().st_size <= 128 * 1024**2
    result = {"sha256": sha(target), "bytes": target.stat().st_size, "members": manifest}
    write(TASK / "native-bundle-identity-v1.json", result)
    return target, result


def main():
    authority()
    folder = TASK / "native-qualification-v1"
    folder.mkdir(exist_ok=False)
    target, metadata = bundle()
    source = WORKER.read_text(encoding="utf-8")
    installed = call(
        "install", {"source": source, "source_sha256": sha(WORKER), "bundle": metadata}
    )
    write(folder / "installed.json", installed)
    result = subprocess.run(
        [
            "rtk",
            "proxy",
            "scp",
            "-q",
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=yes",
            "-o",
            "ConnectTimeout=15",
            str(target),
            "100.77.149.83:/home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1/native-assets-v1.tar.gz",
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    write(
        folder / "transfer.json",
        {
            "exit_code": result.returncode,
            "stderr": result.stderr,
            "bytes": metadata["bytes"],
            "sha256": metadata["sha256"],
        },
    )
    assert result.returncode == 0, "Private native bundle transfer failed; do not repeat blindly"
    received = call("receive", timeout=180)
    write(folder / "received.json", received)
    reserve("native-wall-watchdog-probe-v1", 30)
    probe = call("guard-probe", timeout=60)
    settle("native-wall-watchdog-probe-v1", probe, folder / "watchdog-probe.json")
    write(PUBLIC / "actual-native-watchdog-probe-v1.json", probe)
    reserve("native-dependency-setup-v1", 900)
    setup = call("setup", timeout=1550)
    settle("native-dependency-setup-v1", setup, folder / "setup.json")
    write(PUBLIC / "native-dependency-setup-v1.json", setup)
    rows = read(TASK / "catalog-v1/public-task-and-evaluator-metadata.json")
    inventory = read(TASK / "native-assets-v1/role-and-import-inventory.json")
    results = []
    for item in inventory:
        identity = item["instance_id"]
        row = next(r for r in rows if r["instance_id"] == identity)
        name = f"native-reference-{identity:03d}-v1"
        reserve(name, 620)
        result = call(
            "qualify",
            {"case": {k: row[k] for k in ("instance_id", "gold_program_name", "eval_script_name")}},
            timeout=700,
        )
        result.update(role=item["role"], lineage_group=item["lineage_group"])
        settle(name, result, folder / f"reference-{identity:03d}.json")
        results.append(result)
        print(
            json.dumps(
                {
                    "reference_qualified": identity,
                    "native_success": result["native_success"],
                    "reference_exit_code": result.get("reference_exit_code"),
                    "missing_module": result.get("missing_module"),
                }
            ),
            flush=True,
        )
    locked = [r for r in results if r["role"] == "locked_candidate" and r["native_success"]]
    development = [r for r in results if r["role"] == "development" and r["native_success"]]
    groups = sorted({r["lineage_group"] for r in locked})
    admitted = bool(development) and len(locked) >= 6 and len(groups) >= 4
    receipt = {
        "status": "PASS_NATIVE_PILOT_COHORT"
        if admitted
        else "DATA_NOT_READY_USE_APPROVED_BOUNDED_FALLBACK",
        "development_ids": [r["instance_id"] for r in development],
        "locked_candidate_ids": [r["instance_id"] for r in locked],
        "locked_repository_lineage_groups": groups,
        "results": results,
        "minimum_rules_fixed_before_reference_runs": {
            "locked_tasks": 6,
            "repository_lineage_groups": 4,
            "qualified_development_task": 1,
        },
        "matrix_frozen": False,
        "candidate_model_evaluation": "NOT_RUN",
        "wrapper": "Unmodified native eval() success criterion; no paid rubric/image/CodeBERT assessment; not full upstream harness reproduction",
    }
    write(PUBLIC / "native-reference-qualification-v1.json", receipt)
    ledger = read(TASK / "ledger.json")
    ledger["gates"]["native_cohort"] = {
        "decision": "PASS" if admitted else "FALLBACK_NATIVE_INFEASIBLE",
        "receipt_sha256": sha(PUBLIC / "native-reference-qualification-v1.json"),
    }
    save(ledger)
    print(json.dumps({k: v for k, v in receipt.items() if k != "results"}, indent=2))


if __name__ == "__main__":
    main()
