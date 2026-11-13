"""One actual attempt per frozen author case; preserve failures and never substitute."""
import json
import time
from datetime import datetime, timedelta, timezone

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write
from dc2_local_product_service_v1 import await_job, service
from dc2_local_remote_v1 import reserve_lease, settle_lease


def main():
    release, _ = authority()
    freeze = read(PUBLIC / "product-acceptance-freeze-v1.json")
    for path, expected in freeze["source_sha256"].items():
        assert sha(ROOT / path) == expected, path
    assert sha(PUBLIC / "product-acceptance-freeze-v1.json") == read(TASK / "product-acceptance-freeze-pin-v1.json")["sha256"]
    report = {"status": "RUNNING", "scope": "Frozen author engineering acceptance; no scientific comparison or independent validation", "cases": [], "deterministic_cases": [], "mock_used": False, "outcome_driven_repeats": False}
    identity = "product-acceptance-v1"
    session = TASK / "product-session-v1.json"
    started = False
    try:
        ready = reserve_lease(identity, "development", 2400, 1200)
        started = True
        report["ready"] = ready
        expiry = min(datetime.now(timezone.utc) + timedelta(seconds=1100), datetime.fromisoformat(release["deadline_utc"]))
        write(session, {"lease_id": identity, "seed": 20261113, "expires_utc": expiry.isoformat()})
        with service(TASK / "product-model-v1", session=session) as (_, request):
            assert request("/api/v1/local-workflow/runtime")["model_session_authorized"]
            # Type-controlled RDKit executions confirm the independently specified set.
            for case in freeze["cases"][::2]:
                spec = {"csv_text": freeze["csv_text"], "goal": "Apply the explicit recorded descriptor limits", "parameters": case["expected_parameters"], "mode": "deterministic", "locale": "en"}
                row = request("/api/v1/local-workflow/jobs", spec)
                result = await_job(request, row["job_id"], seconds=60)
                actual = sorted(c["compound_id"] for c in result.get("data", {}).get("compounds", []) if c["selected"])
                passed = result["state"] == "COMPLETED" and actual == sorted(case["expected_selected_ids"])
                report["deterministic_cases"].append({"id": case["id"], "pass": passed, "result": result})
                write(TASK / ("product-deterministic-" + case["id"] + ".json"), result)
            if not all(c["pass"] for c in report["deterministic_cases"]):
                raise RuntimeError("Frozen deterministic conformance did not pass; no model cases started")
            for case in freeze["cases"]:
                began = time.monotonic()
                row = request("/api/v1/local-workflow/jobs", {"csv_text": freeze["csv_text"], "goal": case["goal"], "parameters": freeze["defaults"], "mode": "agent", "locale": case["locale"]})
                result = await_job(request, row["job_id"], seconds=180)
                actual = sorted(c["compound_id"] for c in (result.get("data") or {}).get("compounds", []) if c["selected"])
                checks = {"completed": result["state"] == "COMPLETED", "parameters_exact": result["parameters"] == case["expected_parameters"], "selected_ids_exact": actual == sorted(case["expected_selected_ids"]), "two_real_provider_responses": len(result["provider_calls"]) == 2 and all(c["status"] == "PASS_REAL_RESPONSE" for c in result["provider_calls"])}
                if checks["completed"]:
                    request(f"/api/v1/local-workflow/jobs/{row['job_id']}/artifacts/bundle.zip", binary=True)
                observed = {"id": case["id"], "pass": all(checks.values()), "checks": checks, "wall_seconds": time.monotonic() - began, "actual_selected_ids": actual, "result": result}
                report["cases"].append(observed)
                write(PUBLIC / ("product-case-" + case["id"] + ".json"), observed)
            report["status"] = "PASS_FROZEN_AUTHOR_CASES" if all(c["pass"] for c in report["cases"]) else "FAIL_SOME_FROZEN_AUTHOR_CASES"
            report["passed"] = sum(c["pass"] for c in report["cases"])
            report["total"] = len(report["cases"])
    except BaseException as error:
        report.update(status="FAIL_PRODUCT_ACCEPTANCE_ATTEMPT_RETAINED", error=type(error).__name__ + ": " + str(error)[:1800])
        raise
    finally:
        if started:
            report["stop"] = settle_lease(identity)
        write(PUBLIC / "product-model-acceptance-v1.json", report)
    print(json.dumps({k: report[k] for k in ("status", "passed", "total")}))

if __name__ == "__main__":
    main()
