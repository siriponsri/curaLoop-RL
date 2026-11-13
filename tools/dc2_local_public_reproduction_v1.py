"""Publish author-example prompts/real responses; never read external gold or private CF1."""
import importlib.metadata
import platform
import subprocess
from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write


def main():
    model = read(PUBLIC / "product-model-acceptance-v1.json")
    calls = []
    for case in model["cases"]:
        for call in case["result"]["provider_calls"]:
            folder = TASK / "provider-calls" / call["call_id"]
            request, response = read(folder / "request.json"), read(folder / "response.json")
            assert request["call_id"].startswith("product-") and response["provider_fallback"] is False
            calls.append({"case": case["id"], "request": request, "response": {k:response[k] for k in ("status","call_id","lease_id","utc","model","model_digest","response","wall_seconds","container_cpu_seconds_delta","paid_cost_usd","provider_fallback")}, "model_size_vram_bytes": [m["size_vram"] for m in response["running_model_metadata"]["models"]], "original_response_sha256": sha(folder / "response.json")})
    write(PUBLIC / "product-provider-calls-v1.json", {"scope":"Actual author-example messages/responses; not fabricated or external benchmark rows", "new_inference": False, "calls": calls})
    packages = {name: importlib.metadata.version(name) for name in ("rdkit","numpy","pandas","fastapi","uvicorn","pydantic","playwright","matplotlib","reportlab","pypdf","Pillow")}
    write(PUBLIC / "software-environment-v1.json", {"python":platform.python_version(),"platform":platform.platform(),"packages":packages,"model_manifest_digest":"ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b","model_blob_sha256":"4a1f36682cbeae8153f64a496ebcee10a23378abae631e905865fabfd3b21388","frontend_lock_sha256":sha(ROOT / "frontend/package-lock.json"),"frozen_product_sources_unchanged": all(sha(ROOT/p)==s for p,s in read(PUBLIC / "product-acceptance-freeze-v1.json")["source_sha256"].items())})
    result = subprocess.run(["rtk","proxy","node","node_modules/eslint/bin/eslint.js","src/pages/LocalWorkflow.tsx","src/App.tsx","--max-warnings","0"],cwd=ROOT/"frontend",capture_output=True,text=True)
    write(PUBLIC / "frontend-source-lint-v1.json", {"status":"PASS" if result.returncode==0 else "FAIL","returncode":result.returncode,"stdout":result.stdout,"stderr":result.stderr})
    assert result.returncode==0, result.stdout+result.stderr
    print("PASS_PUBLIC_ACTUAL_RESPONSES_ENVIRONMENT_AND_CHANGED_FRONTEND_LINT")

if __name__ == "__main__":
    main()
