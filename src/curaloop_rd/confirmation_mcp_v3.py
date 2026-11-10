"""Local stdio MCP entry point for the additive CF1 C Workspace tools."""

import argparse
import json
import sys

from .confirmation_study import BUDGETS, CAMPAIGNS, OPERATORS, RANKERS
from .confirmation_workspace_v3 import ConfirmationWorkspace

FILTER_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "campaign": {"type": "string", "enum": ["equal", *CAMPAIGNS]},
    "budget_percent": {"type": "integer", "enum": list(BUDGETS)},
    "ranker": {"type": "string", "enum": list(RANKERS)},
    "operator": {"type": "string", "enum": list(OPERATORS)},
    "locale": {"type": "string", "enum": ["en", "th"]},
}}


def handle(message, workspace):
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or set(message) - {"jsonrpc", "id", "method", "params"}:
        raise ValueError("Invalid JSON-RPC envelope")
    method, params = message.get("method"), message.get("params", {})
    if not isinstance(params, dict):
        raise ValueError("Parameters must be an object")
    if method == "notifications/initialized" and "id" not in message:
        return None
    if "id" not in message:
        raise ValueError("Request id required")
    if method == "initialize":
        if set(params) - {"protocolVersion", "capabilities", "clientInfo"}:
            raise ValueError("Unexpected initialization fields")
        return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                "serverInfo": {"name": "curaloop-confirmation-workspace", "version": "3.0.0"}}
    if method == "tools/list" and not params:
        return {"tools": [{"name": name, "description": description, "inputSchema": FILTER_SCHEMA,
                           "annotations": {"readOnlyHint": name == "confirmation_inspect", "openWorldHint": False,
                                           "destructiveHint": False, "idempotentHint": True}}
                          for name, description in [
                              ("confirmation_inspect", "Inspect fixed historical CF1 aggregates. No simulator or external action."),
                              ("confirmation_export", "Create or verify a local EN/TH comparison brief in the configured workspace. No external delivery.")]]}
    if method == "tools/call" and set(params) == {"name", "arguments"}:
        value = workspace.call(params["name"], params["arguments"])
        return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, allow_nan=False)}], "isError": False}
    raise ValueError("Unsupported method or fields")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()
    workspace = ConfirmationWorkspace(args.workspace)
    for line in sys.stdin:
        message = None
        try:
            if len(line.encode("utf-8")) > 1048576:
                raise ValueError("Request exceeds one MiB")
            message = json.loads(line)
            result = handle(message, workspace)
            if result is None:
                continue
            response = {"jsonrpc": "2.0", "id": message["id"], "result": result}
        except (ValueError, TypeError, KeyError, OSError) as exc:
            response = {"jsonrpc": "2.0", "id": message.get("id") if isinstance(message, dict) else None,
                        "error": {"code": -32602, "message": str(exc)}}
        print(json.dumps(response, ensure_ascii=True, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
