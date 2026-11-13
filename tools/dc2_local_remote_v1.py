"""Fixed SSH transport, conservative lease bookings and real provider canary."""

import base64
import hashlib
import json
import subprocess

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write

WORKER = ROOT / "tools/dc2_local_model_worker_v1.py"
MODEL = "hf.co/scb10x/typhoon2.1-gemma3-12b-gguf:Q4_K_M"
DIGEST = "ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b"


def call(action, payload, *, timeout=180):
    assert action in ("bootstrap", "start", "infer", "stop", "watchdog-probe", "verify-model-bytes")
    if action == "bootstrap":
        source = WORKER.read_text(encoding="utf-8")
        program = base64.b64encode(source.encode()).decode()
        command = "python3 -c \"import base64;exec(base64.b64decode('" + program + "'))\" bootstrap"
    else:
        command = "python3 /home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1/worker.py " + action
        if payload.get("lease_id", "").startswith("product-"):
            device = read(PUBLIC / "product-device-selection-v1.json")
            assert sha(ROOT / "tools/dc2_local_product_worker_v1.py") == device["product_worker_sha256"]
            command = "python3 /home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1/worker-product-v1.py " + action
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
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if result.returncode:
        raise RuntimeError(
            "Owned SSH operation failed: " + result.stderr[-1600:] + result.stdout[-800:]
        )
    return json.loads(result.stdout)


def reserve_lease(identity, bucket, cpu, gpu):
    release, ledger = authority()
    if ledger["status"] == "ACTIVE_PRODUCT_FALLBACK":
        assert bucket == "development" and identity.startswith("product-")
    assert identity not in ledger["bookings"]
    assert not any(
        b["status"] == "RESERVED" and b["gpu_cap"] > 0 for b in ledger["bookings"].values()
    )
    for kind, value, total_key in (
        ("cpu", cpu, "cpu_cap_seconds"),
        ("gpu", gpu, "gpu_allocated_cap_seconds"),
    ):
        ledger[f"retained_{kind}_seconds"][bucket] += value
        assert (
            ledger[f"retained_{kind}_seconds"][bucket]
            <= ledger[f"stage_{kind}_caps_seconds"][bucket]
        )
        assert sum(ledger[f"retained_{kind}_seconds"].values()) <= release[total_key]
    ledger["bookings"][identity] = {
        "status": "RESERVED",
        "host": "dr-train-model",
        "bucket": bucket,
        "cpu_cap": cpu,
        "gpu_cap": gpu,
    }
    save(ledger)
    payload = {"lease_id": identity, "cpu_cap_seconds": cpu, "gpu_cap_seconds": gpu}
    return call("start", payload)


def settle_lease(identity):
    receipt = call("stop", {"lease_id": identity})
    write(TASK / (identity + "-stop-receipt.json"), receipt)
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][identity].update(
        status="PASS_STOPPED_RETAINED_ALLOCATION",
        stop_receipt_sha256=sha(TASK / (identity + "-stop-receipt.json")),
    )
    save(ledger)
    return receipt


def generate(payload, *, development=True):
    release, ledger = authority()
    if ledger["status"] == "ACTIVE_PRODUCT_FALLBACK":
        assert development and payload["call_id"].startswith("product-")
    identity = payload["call_id"]
    attempts = ledger.setdefault("provider_attempts", {})
    assert identity not in attempts
    if development:
        count = ledger.get("development_provider_attempts", 0) + 1
        assert count <= release["development_provider_call_cap"]
        ledger["development_provider_attempts"] = count
    attempts[identity] = {"status": "ATTEMPT_STARTED", "development": development}
    save(ledger)
    folder = TASK / "provider-calls" / identity
    folder.mkdir(parents=True, exist_ok=False)
    write(folder / "request.json", payload)
    try:
        result = call("infer", payload, timeout=650)
        write(folder / "response.json", result)
        ledger = read(TASK / "ledger.json")
        ledger["provider_attempts"][identity]["status"] = "PASS_REAL_RESPONSE"
        ledger["model_calls"] += 1
        ledger["generated_tokens"] += result["response"].get("eval_count", 0)
        if development:
            ledger["development_model_calls"] += 1
        save(ledger)
        return result
    except BaseException as error:
        write(
            folder / "transport-failure.json",
            {
                "status": "FAIL_OR_UNKNOWN_PROVIDER_ATTEMPT",
                "error": type(error).__name__ + ":" + str(error)[:1800],
            },
        )
        ledger = read(TASK / "ledger.json")
        ledger["provider_attempts"][identity]["status"] = "FAIL_OR_UNKNOWN_DO_NOT_REPLAY"
        save(ledger)
        raise


def main():
    release, _ = authority()
    selected = {
        "schema": "curaloop.lr-dc2-local.model-selection.v1",
        "status": "FIXED_BEFORE_COMPARATIVE_MODEL_OUTCOMES",
        "model": MODEL,
        "model_digest": DIGEST,
        "selection_basis": "Existing complete checkpoint; free V100 32GB; no model download or search",
        "model_count": 1,
        "gpu_uuid": "GPU-277ccc57-c3e5-0731-cd49-f4f8695f7089",
    }
    write(ROOT / "research/manifests/lr_dc2_local_model_selection_20261113_v1.json", selected)
    remote_release = {**release, "model": MODEL, "model_digest": DIGEST}
    source = WORKER.read_text(encoding="utf-8")
    receipt = call(
        "bootstrap",
        {
            "release": remote_release,
            "worker_source": source,
            "worker_sha256": hashlib.sha256(source.encode()).hexdigest(),
        },
    )
    write(TASK / "remote-bootstrap-receipt-v1.json", receipt)
    probes = []
    for kind, cpu, gpu in (("cpu", 30, 60), ("wall", 120, 30)):
        identity = "guard-probe-" + kind + "-v1"
        ready = reserve_lease(identity, "admission", cpu, gpu)
        try:
            result = call("watchdog-probe", {"lease_id": identity, "kind": kind}, timeout=90)
            probes.append({"ready": ready, "probe": result})
        finally:
            stopped = settle_lease(identity)
        probes[-1]["stop"] = stopped
    write(
        PUBLIC / "actual-model-watchdog-probes-v1.json",
        {"status": "PASS_ACTUAL_CPU_AND_WALL_TERMINATION", "probes": probes},
    )
    identity = "model-format-canary-v1"
    ready = reserve_lease(identity, "admission", 1200, 600)
    try:
        model_bytes = call("verify-model-bytes", {"lease_id": identity}, timeout=150)
        payload = {
            "lease_id": identity,
            "call_id": "technical-canary-0001",
            "seed": 20261113,
            "max_tokens": 128,
            "messages": [
                {
                    "role": "user",
                    "content": "Return exactly a JSON object with status equal to ready. This is a technical format check, not a scientific task.",
                }
            ],
            "format": {
                "type": "object",
                "properties": {"status": {"const": "ready"}},
                "required": ["status"],
                "additionalProperties": False,
            },
        }
        response = generate(payload)
        assert json.loads(response["response"]["message"]["content"]) == {"status": "ready"}
        assert any(m["size_vram"] > 0 for m in response["running_model_metadata"]["models"])
    finally:
        stopped = settle_lease(identity)
    write(
        PUBLIC / "real-gpu-format-canary-v1.json",
        {
            "status": "PASS_REAL_GPU_FORMAT_CANARY_NOT_AGENT_EVALUATION",
            "ready": ready,
            "full_model_blob": model_bytes,
            "provider_response": response,
            "stop": stopped,
            "scientific_task_success": "NOT_RUN",
            "mock_used": False,
        },
    )
    print(
        json.dumps(
            {
                "status": "PASS_REAL_GPU_CANARY",
                "provider_calls": 1,
                "generated_tokens": response["response"].get("eval_count"),
                "gpu_allocation_retained_seconds": 690,
                "watchdog_probes": 2,
            }
        )
    )


if __name__ == "__main__":
    main()
