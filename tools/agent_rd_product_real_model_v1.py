"""One actual current-product model mission after the frozen matrix exits.

Uses only the remaining already-retained remote envelope, unchanged model/data
and original deadline. No new phase, cap, trial replacement or comparative score.
The research lock is archived only after its fixed disposition is verified.
"""

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write
from agent_rd_remote_v1 import call
from playwright.sync_api import sync_playwright

from research.agent_rd_eval_v1.oracle import expected_values


def main():
    release, _ = authority()
    work = TASK / "product-real-model-v1"
    work.mkdir(exist_ok=False)
    receipt = {"status": "NOT_STARTED", "scope": "One post-study product lifecycle mission, never a comparative study unit",
               "scientific_trial_added_or_replaced": False, "model_phase_or_cpu_cap_reset": False,
               "new_model_download": False, "paid_api": False, "mission_id": None}
    completion = read(TASK / "evaluation-completion-v1.json")
    assert completion["evaluation_exit_code"] == 0 and completion["disposition_sha256"] == sha(PUBLIC / "locked-progress-v1.json")
    assert read(PUBLIC / "product-policy-acceptance.json")["status"] == "PASS_CURRENT_PRODUCT_POLICY_NOT_FROZEN_STUDY"
    freeze_path = ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json"
    freeze = read(freeze_path)
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    before = {p.name: sha(p) for p in (PUBLIC / "locked-results-v1").glob("*.json")}
    try:
        status = call("status", timeout=45)
    except Exception as exc:
        receipt.update(status="NOT_RUN_RUNTIME_UNAVAILABLE", error=type(exc).__name__ + ": " + str(exc)[-1000:])
        write(PUBLIC / "product-current-model-acceptance-v1.json", receipt, True)
        print(json.dumps(receipt))
        return
    original = read(sorted((TASK / "locked-evaluation-v1").glob("invocation-*.json"))[0])["phase"]
    assert status["phase"] == original["phase"] and status["admission"]["container_id"] == original["admission"]["container_id"]
    remaining = status["phase"]["cpu_base"] + status["phase"]["cpu_cap"] - status["container_cpu_seconds"]
    receipt["unchanged_remaining_phase_cpu_seconds_before"] = remaining
    deadline_left = (datetime.fromisoformat(release["deadline_utc"]) - datetime.now(timezone.utc)).total_seconds()
    if remaining < 6000 or deadline_left < 3600:
        receipt.update(status="NOT_RUN_RESOURCE_HEADROOM", explanation="Require 6000 remaining remote CPU seconds and one hour before the original deadline")
        write(PUBLIC / "product-current-model-acceptance-v1.json", receipt, True)
        print(json.dumps(receipt))
        return
    lock = TASK / "evaluation.lock"
    archived = work / "completed-research-lock-original.json"
    assert lock.resolve().parent == TASK.resolve() and archived.resolve().is_relative_to(TASK.resolve())
    assert read(lock)["freeze_sha256"] == sha(freeze_path) and not archived.exists()
    lock.rename(archived)
    write(work / "lock-release.json", {"reason": "Fixed matrix finished; one engineering acceptance under original active limits",
          "lock_original_sha256": sha(archived), "disposition_sha256": sha(PUBLIC / "locked-progress-v1.json"),
          "global_budget_or_phase_reset": False}, True)
    captures = PUBLIC / "product-current-model-screens-v1"
    captures.mkdir(exist_ok=False)
    database = work / "local-api.sqlite3"
    port = None
    for candidate in (5173, 8000, 8771):
        try:
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", candidate))
            port = candidate
            break
        except OSError:
            pass
    assert port is not None
    base = f"http://127.0.0.1:{port}"
    environment = {**os.environ, "CURALOOP_STORAGE_PATH": str(database), "CURALOOP_AGENT_INFERENCE_DISABLED": "0"}
    out, err = (work / "server.stdout.txt").open("wb"), (work / "server.stderr.txt").open("wb")
    server = None

    def get(path):
        with urllib.request.urlopen(base + path, timeout=30) as response:
            return json.load(response)

    def start():
        nonlocal server
        server = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
                                  cwd=ROOT, env=environment, stdout=out, stderr=err)
        for _ in range(100):
            assert server.poll() is None
            try:
                get("/api/v1/health")
                return
            except OSError:
                time.sleep(.2)
        raise RuntimeError("Owned current-product preview did not become ready")

    def stop():
        if server is not None and server.poll() is None:
            server.terminate()
            server.wait(timeout=30)

    try:
        start()
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--disable-gpu", "--disable-webgl", "--disable-vulkan",
                                                              "--use-gl=disabled", "--disable-background-networking"])
            page = browser.new_page(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce")
            page_errors, external = [], []
            page.on("pageerror", lambda error: page_errors.append(str(error)))

            def boundary(route):
                if route.request.url.startswith(base + "/") or route.request.url.startswith(("data:", "blob:")):
                    route.continue_()
                else:
                    external.append(route.request.url)
                    route.abort()
            page.route("**/*", boundary)
            page.goto(base + "/agent", wait_until="networkidle")
            page.locator("#agent-campaign").select_option("628/677")
            page.locator("#agent-goal").fill("Report only b10:a0:H and b10:a0:D. Include development_only and seed_range_not_ci.")
            page.get_by_role("button", name="Run research mission", exact=True).click()
            started = time.monotonic()
            row = None
            while time.monotonic() - started < 2050:
                items = get("/api/v1/agent/missions")["items"]
                assert len(items) <= 1, "No replacement or second acceptance mission"
                if items:
                    receipt["mission_id"] = items[0]["mission_id"]
                    row = get("/api/v1/agent/missions/" + receipt["mission_id"])
                    if row["state"] in ("COMPLETED", "ABSTAINED", "FAILED"):
                        break
                time.sleep(2)
            assert row and row["state"] in ("COMPLETED", "ABSTAINED"), "Actual current-product model lifecycle did not finish"
            assert row["product_preflight"]["decision"] == "ALLOW" and 1 <= row["cost"]["model_calls"] <= 3
            assert any(c["status"] == "PASS" for c in row["calls"]), "A real provider response is required"
            gold = expected_values(row["spec"])
            values = row["released"].get("values", {})
            task_pass = row["released"]["action"] == "answer" and all(
                key in values and type(values[key]) in (int, float) and abs(values[key] - gold[key]) <= .0005000001
                for key in ("b10:a0:H", "b10:a0:D"))
            task_pass = bool(task_pass and {"development_only", "seed_range_not_ci"}.issubset(row["released"].get("limitations", [])))
            receipt.update(task_required_fields_and_scope_pass=task_pass, actual_cost=row["cost"], terminal_state=row["state"])
            page.locator(".agent-result").wait_for(timeout=15000)
            page.locator(".agent-result").screenshot(path=str(captures / "01-current-product-actual-model-result-en.png"))
            page.get_by_role("button", name="Prepare local dossier", exact=True).click()
            page.get_by_role("link", name="Open dossier", exact=True).wait_for()
            stop()
            start()
            assert get("/api/v1/agent/missions/" + row["mission_id"]) == row
            assert get("/api/v1/runs")["items"] == []
            assert not page_errors and not external
            mission = work / "local-api-agent-rd/missions" / (row["mission_id"] + ".json")
            target = PUBLIC / "product-current-model-mission-v1.json"
            assert not target.exists()
            target.write_bytes(mission.read_bytes())
            receipt.update(status="PASS_ACTUAL_CURRENT_PRODUCT_MODEL_LIFECYCLE", actual_restart_without_regeneration=True,
                           model_mission_sha256=sha(target), screenshots=[(captures / "01-current-product-actual-model-result-en.png").relative_to(ROOT).as_posix()],
                           primary_comparative_efficacy_claim=False)
            browser.close()
    except BaseException as exc:
        receipt.update(status="FAIL", error=type(exc).__name__ + ": " + str(exc))
        if receipt["mission_id"]:
            try:
                failed_row = get("/api/v1/agent/missions/" + receipt["mission_id"])
                receipt.update(actual_cost=failed_row.get("cost"), terminal_state=failed_row.get("state"))
                write(work / "failed-mission-observation.json", failed_row, True)
            except Exception as observation_error:
                receipt["failure_observation_error"] = str(observation_error)
        raise
    finally:
        stop()
        assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
        assert {p.name: sha(p) for p in (PUBLIC / "locked-results-v1").glob("*.json")} == before
        write(PUBLIC / "product-current-model-acceptance-v1.json", receipt, True)
        print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
