"""Fixed local SSH model transport. No API key, paid endpoint or fallback."""

import json
import os
import re
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from .contracts import ANSWER_SCHEMA, REPORT_SCHEMA

ROOT = Path(__file__).resolve().parents[3]
RELEASE = Path(os.environ.get("CURALOOP_AGENT_SESSION", str(ROOT / ".local/agent-rd-run-20261110-v1/release.json")))


class ProviderUnavailable(RuntimeError):
    pass


class SSHModel:
    """The host/operator owns configuration; a mission cannot change it."""

    def generate(self, call_id, messages, seed, max_tokens=256, final_only=False, value_keys=None):
        if os.environ.get("CURALOOP_AGENT_INFERENCE_DISABLED") == "1":
            raise ProviderUnavailable("Model execution is disabled in this process")
        if not RELEASE.exists():
            raise ProviderUnavailable("Start an authorized local model session; recorded missions remain available")
        release = json.loads(RELEASE.read_text(encoding="utf-8"))
        ledger = json.loads(RELEASE.with_name("ledger.json").read_text(encoding="utf-8"))
        if ledger["status"] != "ACTIVE":
            raise ProviderUnavailable("This research resource account is closed; no implicit reuse or provider fallback")
        if datetime.now(timezone.utc) >= datetime.fromisoformat(release["deadline_utc"]):
            raise ProviderUnavailable("The authorized model session deadline has passed")
        answer = json.loads(json.dumps(ANSWER_SCHEMA))
        answer["properties"]["action"] = {"const": "answer"}
        answer["properties"]["values"] = {"type": "object", "properties": {key: {"type": "number"} for key in (value_keys or [])}, "additionalProperties": False}
        answer["properties"]["evidence_id"] = {"type": "string", "pattern": "^[0-9a-f]{16}$"}
        answer["required"] = ["action", "values", "limitations", "evidence_id"]
        abstain = {"type": "object", "additionalProperties": False, "properties": {
            "action": {"const": "abstain"}, "reason": {"type": "string", "enum": ["forbidden_scope", "insufficient_evidence", "source_unavailable"]},
            "values": {"type": "object", "additionalProperties": False},
            "limitations": ANSWER_SCHEMA["properties"]["limitations"]}, "required": ["action", "reason"]}
        permitted = {"oneOf": [answer, abstain] + ([] if final_only else [REPORT_SCHEMA["oneOf"][2]])}
        payload = {"call_id": call_id, "messages": messages, "seed": seed, "max_tokens": max_tokens,
                   "format": permitted}
        if len(json.dumps(payload).encode()) > 131072:
            raise ProviderUnavailable("Model request exceeds its admitted size")
        host = release.get("ssh_host", "100.77.149.83")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,252}", host):
            raise ProviderUnavailable("Operator SSH host is invalid")
        worker = release.get("remote_worker", "worker-v2.py")
        if worker not in ("worker.py", "worker-v2.py"):
            raise ProviderUnavailable("Operator worker is not a registered transport")
        command = "python3 " + shlex.quote(release["remote_root"] + "/" + worker) + " infer"
        started = time.monotonic()
        try:
            result = subprocess.run(["rtk", "proxy", "ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                                     "-o", "ConnectTimeout=15", host, command],
                                    input=json.dumps(payload, ensure_ascii=False), capture_output=True, text=True,
                                    encoding="utf-8", timeout=660)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ProviderUnavailable("Owned model transport unavailable: " + type(exc).__name__) from exc
        if result.returncode:
            raise ProviderUnavailable("Owned model call failed; retained call id " + call_id + ": " + result.stderr[-500:])
        receipt = json.loads(result.stdout)
        if receipt.get("status") != "PASS_PROVIDER_RESPONSE":
            raise ProviderUnavailable("Model call has no completed provider response")
        if receipt.get("model") != release["model"] or receipt.get("model_digest") != release["model_digest"]:
            raise ProviderUnavailable("Model identity differs from the released session")
        if any(model.get("size_vram") != 0 for model in receipt.get("running_model_metadata", {}).get("models", [])):
            raise ProviderUnavailable("Provider did not remain CPU-only")
        raw = receipt["response"]["message"]["content"]
        return {"raw": raw, "receipt": receipt, "transport_wall_seconds": time.monotonic() - started,
                "paid_cost_usd": 0, "provider_fallback": False}
