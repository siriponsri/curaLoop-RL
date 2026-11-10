"""Actual local stdio round trip for the additive C tools; no external agent."""

import json
import subprocess
import sys
from pathlib import Path

from cf2p_admin_v1 import PUBLIC, ROOT, TASK, write


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    assert tag in ("v1", "v2")
    selection = {"campaign": "628/677", "budget_percent": 5, "ranker": "rf", "operator": "cluster_round_robin"}
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "bounded-native-check", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "confirmation_inspect", "arguments": selection}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "confirmation_export", "arguments": selection}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "confirmation_export", "arguments": {**selection, "locale": "th"}}},
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "confirmation_export", "arguments": {"path": "../outside"}}},
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "confirmation_inspect", "arguments": {"budget_percent": 3}}},
    ]
    result = subprocess.run([sys.executable, "-m", "curaloop_rd.confirmation_mcp_v3", "--workspace", str(TASK / ("c-workspace" if tag == "v1" else "c-workspace-v2"))],
                            cwd=ROOT, input="\n".join(json.dumps(m) for m in messages) + "\n", capture_output=True, text=True, timeout=60)
    write(TASK / f"c-stdio-response-{tag}.json", {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, True)
    assert result.returncode == 0, result.stderr
    responses = [json.loads(line) for line in result.stdout.splitlines()]
    assert [r["id"] for r in responses] == list(range(1, 8))
    assert len(responses[1]["result"]["tools"]) == 2
    values = {r["id"]: json.loads(r["result"]["content"][0]["text"]) for r in responses if r["id"] in (3, 4, 5)}
    assert values[3]["selection"] == selection and values[4] == values[5]
    assert values[4]["external_delivery"] is False
    assert all("error" in r for r in responses if r["id"] in (6, 7))
    folder = Path(values[4]["local_folder"])
    assert len(list(folder.iterdir())) == 5
    write(PUBLIC / f"native-c-workspace-{tag}.json", {"status": "PASS_ACTUAL_LOCAL_STDIO", "requests": len(messages),
          "responses": len(responses), "bilingual_export_files": 5, "selection": selection,
          "export_relative_to_private_root": folder.relative_to(TASK).as_posix(), "external_delivery": False,
          "live_agent_reasoning_evaluated": False, "manifest": values[4]["manifest"]}, True)
    print("PASS actual C Workspace stdio: eight messages, seven responses, bilingual local export, invalid fields rejected")


if __name__ == "__main__":
    main()
