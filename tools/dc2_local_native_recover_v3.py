"""One bounded mount/dependency repair; preserve the never-started reference attempt."""

import base64
import json
import subprocess

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write
from dc2_local_native_v1 import reserve, settle

WORKER = ROOT / "tools/dc2_local_native_worker_v2.py"
INSTALL = "\nimport base64,hashlib,importlib.util,json\nfrom pathlib import Path\nroot=Path.home()/'curaloop-tasks/lr-dc2-local-20261113-v1'\np=json.load(__import__('sys').stdin)\nraw=base64.b64decode(p['source_b64'],validate=True)\nassert hashlib.sha256(raw).hexdigest()==p['source_sha256']\nassert hashlib.sha256((root/'native-worker-v1.py').read_bytes()).hexdigest()==p['previous_sha256']\nassert not (root/'native-worker-v2.py').exists()\nspec=importlib.util.spec_from_file_location('owned_io',root/'worker.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.authority()\nname='curaloop-dc2-local-native-20261113-v1'\nassert not any('/'+name in r['Names'] for r in m.api('GET','/containers/json?all=1'))\ntarget=root/'native-v1/control/2/failed-start-container-inspection.json'\nv=json.loads(target.read_text())\nassert v['Config']['Labels']['curaloop.task']=='lr-dc2-local-20261113-v1'\nassert v['Config']['Labels']['curaloop.purpose']=='native-reference'\nassert v['Image']=='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d'\nassert not v['State']['Running'] and v['State']['StartedAt'].startswith('0001-')\n(root/'native-worker-v2.py').write_bytes(raw)\nassert hashlib.sha256((root/'native-worker-v2.py').read_bytes()).hexdigest()==p['source_sha256']\nprint(json.dumps({'status':'PASS_BYTE_EXACT_VERSIONED_TRANSPORT_AND_PRIOR_OWNED_ABSENCE','original_state':v['State'],'reference_process_started':False,'original_worker_preserved':True,'prior_exact_removal_had_already_occurred':True,'new_worker_sha256':p['source_sha256']}))\n"


def invoke(command, payload, timeout):
    r = subprocess.run(
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
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if r.returncode:
        raise RuntimeError(
            "Bounded native v2 operation failed: " + r.stderr[-1800:] + r.stdout[-800:]
        )
    return json.loads(r.stdout)


def call(action, payload=None, timeout=700):
    assert action in ("dependency-repair", "qualify")
    return invoke(
        "python3 /home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1/native-worker-v2.py " + action,
        payload or {},
        timeout,
    )


def main():
    authority()
    folder = TASK / "native-qualification-v3"
    folder.mkdir(exist_ok=False)
    encoded = base64.b64encode(INSTALL.encode()).decode()
    command = "python3 -c \"import base64;exec(base64.b64decode('" + encoded + "'))\""
    repaired = invoke(
        command,
        {
            "previous_sha256": sha(ROOT / "tools/dc2_local_native_worker_v1.py"),
            "source_b64": base64.b64encode(WORKER.read_bytes()).decode("ascii"),
            "source_sha256": sha(WORKER),
        },
        60,
    )
    write(folder / "failed-start-recovery.json", repaired)
    ledger = read(TASK / "ledger.json")
    prior = ledger["bookings"]["native-reference-002-v1"]
    assert prior["status"] == "RESERVED"
    prior.update(
        status="FAIL_CONTAINER_START_REFERENCE_NOT_RUN_RETAINED",
        recovery_receipt_sha256=sha(folder / "failed-start-recovery.json"),
    )
    save(ledger)
    write(PUBLIC / "native-mount-failure-repair-v3.json", repaired)
    reserve("native-dependency-repair-v3", 300)
    deps = call("dependency-repair", timeout=650)
    settle("native-dependency-repair-v3", deps, folder / "dependency-repair.json")
    write(PUBLIC / "native-dependency-repair-v3.json", deps)
    rows = read(TASK / "catalog-v1/public-task-and-evaluator-metadata.json")
    inventory = read(TASK / "native-assets-v1/role-and-import-inventory.json")
    results = []
    for item in inventory:
        identity = item["instance_id"]
        row = next(r for r in rows if r["instance_id"] == identity)
        name = f"native-reference-{identity:03d}-v3"
        reserve(name, 620)
        result = call(
            "qualify",
            {"case": {k: row[k] for k in ("instance_id", "gold_program_name", "eval_script_name")}},
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
    result = {
        "status": "PASS_NATIVE_PILOT_COHORT"
        if admitted
        else "DATA_NOT_READY_USE_APPROVED_BOUNDED_FALLBACK",
        "development_ids": [r["instance_id"] for r in development],
        "locked_candidate_ids": [r["instance_id"] for r in locked],
        "locked_repository_lineage_groups": groups,
        "results": results,
        "minimum_rules_unchanged": {
            "locked_tasks": 6,
            "repository_lineage_groups": 4,
            "qualified_development_task": 1,
        },
        "candidate_model_evaluation": "NOT_RUN",
        "matrix_frozen": False,
        "reference_outcome_driven_retry": False,
        "repair": "First v1 reference never started; nested mountpoint fixed, one dependency-only repair; all original bytes and charges retained",
        "wrapper": "Unmodified native eval() criterion in isolated containers; no paid rubric/image/CodeBERT grading; not full upstream harness reproduction",
    }
    write(PUBLIC / "native-reference-qualification-v3.json", result)
    ledger = read(TASK / "ledger.json")
    ledger["gates"]["native_cohort"] = {
        "decision": "PASS" if admitted else "FALLBACK_NATIVE_INFEASIBLE",
        "receipt_sha256": sha(PUBLIC / "native-reference-qualification-v3.json"),
    }
    save(ledger)
    print(json.dumps({k: v for k, v in result.items() if k != "results"}, indent=2))


if __name__ == "__main__":
    main()
