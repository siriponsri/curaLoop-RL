"""Explicit operator session over the registered SSH transport; no paid fallback."""

import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ACCOUNT = ROOT / ".local/lr-dc2-local-20261113-v1"


class OperatorSessionProvider:
    def __init__(self, session):
        self.session = Path(session).resolve()
        if self.session.parent != ACCOUNT.resolve() or not self.session.name.startswith(
            "product-session-"
        ):
            raise ValueError("Only the registered operator product session is supported")

    def configuration(self):
        session = json.loads(self.session.read_text(encoding="utf-8"))
        release = json.loads((ACCOUNT / "release.json").read_text(encoding="utf-8"))
        ledger = json.loads((ACCOUNT / "ledger.json").read_text(encoding="utf-8"))
        if not isinstance(session.get("lease_id"), str):
            raise ValueError("Invalid product session lease")
        if datetime.now(timezone.utc) >= datetime.fromisoformat(session["expires_utc"]):
            raise ValueError("The product model lease has expired")
        if ledger["status"] != "ACTIVE_PRODUCT_FALLBACK" or datetime.now(
            timezone.utc
        ) >= datetime.fromisoformat(release["deadline_utc"]):
            raise ValueError("The authorized local model window is inactive")
        booking = ledger["bookings"].get(session["lease_id"], {})
        if booking.get("status") != "RESERVED" or booking.get("bucket") != "development":
            raise ValueError("The registered product lease is not active")
        if not session["lease_id"].startswith("product-"):
            raise ValueError("Session is not a product lease")
        return session

    def available(self):
        try:
            self.configuration()
            return True
        except (OSError, ValueError, KeyError):
            return False

    def generate(self, call_id, messages):
        session = self.configuration()
        tools = str(ROOT / "tools")
        if tools not in sys.path:
            sys.path.append(tools)
        transport = importlib.import_module("dc2_local_remote_v1")
        if call_id.endswith("-plan"):
            schema = {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "action": {"const": "compute"},
                    "parameters": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            k: {"type": "number"}
                            for k in ("molecular_weight_max", "logp_max", "tpsa_max")
                        },
                        "required": ["molecular_weight_max", "logp_max", "tpsa_max"],
                    },
                },
                "required": ["action", "parameters"],
            }
        elif call_id.endswith("-export"):
            schema = {
                "type": "object",
                "properties": {"action": {"const": "export"}},
                "required": ["action"],
                "additionalProperties": False,
            }
        else:
            raise ValueError("Unregistered product generation stage")
        response = transport.generate(
            {
                "lease_id": session["lease_id"],
                "call_id": call_id,
                "messages": messages,
                "seed": session["seed"],
                "max_tokens": 256,
                "format": schema,
            },
            development=True,
        )
        return {
            "raw": response["response"]["message"]["content"],
            "model": response["model"],
            "model_digest": response["model_digest"],
            "tokens": response["response"].get("eval_count"),
            "prompt_tokens": response["response"].get("prompt_eval_count"),
            "wall_seconds": response["wall_seconds"],
            "paid_cost_usd": 0,
            "provider_fallback": False,
            "original_receipt": response,
        }


def configured_provider():
    path = os.environ.get("CURALOOP_LOCAL_WORKFLOW_SESSION")
    return OperatorSessionProvider(path) if path else None
