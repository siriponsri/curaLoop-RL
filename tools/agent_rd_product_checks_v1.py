"""Post-study product checks, separate from immutable experimental outcomes.

Only targeted non-frozen lint is used, never the old --fix scientific check.
The actual data/model comparison is not replaced by these engineering tests.
"""

import subprocess
import sys

from agent_rd_admin_v1 import PUBLIC, ROOT, read, sha, write

freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
result_before = {p.name: sha(p) for p in (PUBLIC / "locked-results-v1").glob("*.json")}
paths = ["api/agent_product_scope_v1.py", "api/agent_recorded_example_v1.py", "api/agent_rd_routes.py", "tests/test_agent_product_scope_v1.py",
         "tools/agent_rd_product_checks_v1.py", "tools/agent_rd_product_browser_v1.py",
         "tools/agent_rd_product_real_model_v1.py"]
tag = sys.argv[1] if len(sys.argv) == 2 else "v1"
assert tag in ("v1", "v2", "v3")
checks = []
commands = [[sys.executable, "-m", "ruff", "check", *paths],
            [sys.executable, "-m", "pytest", "-q", "tests/test_agent_product_scope_v1.py", "tests/test_agent_rd.py",
             "tests/test_agent_rd_eval.py", "tests/test_confirmation_study.py"],
            [sys.executable, "tools/agent_rd_frontend_checks_v1.py", "product-scope-" + tag],
            [sys.executable, "tools/agent_rd_product_browser_v1.py", tag]]
for command in commands:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    checks.append({"command": command, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
    print(completed.stdout[-1800:])
    if completed.returncode:
        print(completed.stderr[-2000:])
        break
assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
assert {p.name: sha(p) for p in (PUBLIC / "locked-results-v1").glob("*.json")} == result_before
value = {"status": "PASS_POST_STUDY_PRODUCT_SCOPE_CHECKS" if all(c["exit_code"] == 0 for c in checks) else "FAIL",
         "checks": checks, "changed_product_source_pins": {p: sha(ROOT / p) for p in paths},
         "frozen_27_pins_preserved": True, "new_model_generation": False,
         "locked_result_files_preserved": len(result_before),
         "research_results_replaced_or_rescored": False,
         "interpretation": "Product transport preflight is not the frozen P research condition; no comparative efficacy is inferred from these checks"}
receipt_path = PUBLIC / ("product-scope-checks-" + tag + ".json")
write(receipt_path, value, True)
if value["status"].startswith("PASS"):
    write(PUBLIC / "product-policy-acceptance.json", {"status": "PASS_CURRENT_PRODUCT_POLICY_NOT_FROZEN_STUDY",
          "checks": receipt_path.name, "checks_sha256": sha(receipt_path), "browser": "product-policy-browser-" + tag + ".json",
          "browser_sha256": sha(PUBLIC / ("product-policy-browser-" + tag + ".json")),
          "screens_folder": "product-policy-screens-" + tag, "new_model_generations": 0,
          "frozen_research_condition": False, "previous_failed_attempts_preserved": True}, True)
print(value["status"])
raise SystemExit(0 if value["status"].startswith("PASS") else 1)
