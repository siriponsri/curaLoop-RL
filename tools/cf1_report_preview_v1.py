"""Loopback-only allowlisted aggregate report preview for browser QA."""
# ruff: noqa: E402

import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, start

HANDOFF = ROOT / "research/product_handoffs/lr_cf1_v1"
ALLOWED = {"/": HANDOFF / "report.html", "/report.html": HANDOFF / "report.html",
           "/evidence-card-v1.json": HANDOFF / "evidence-card-v1.json",
           "/evidence-card.schema.json": HANDOFF / "evidence-card.schema.json",
           "/docs/evidence/lr-cf1-20261109-v1/portfolio-cells-v1.csv": PUBLIC / "portfolio-cells-v1.csv"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = ALLOWED.get(urlsplit(self.path).path)
        if path is None:
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", (mimetypes.guess_type(path)[0] or "application/octet-stream") + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/__stop":
            self.send_error(404)
            return
        self.send_response(200)
        self.end_headers()
        self.server.should_exit = True

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    guard = start("offline-report-browser-preview-v1", 180, 1200, bucket="utilities_return_handoff_delivery")
    try:
        server = HTTPServer(("127.0.0.1", 0), Handler)
        server.timeout, server.should_exit = .5, False
        state = {"status": "RUNNING_LOOPBACK_AGGREGATE_ONLY", "url": "http://127.0.0.1:" + str(server.server_port) + "/report.html",
                 "port": server.server_port, "allowed_paths": list(ALLOWED), "engine_integration": False}
        new(TASK / "preview-server-v1.json", state)
        print(json.dumps(state), flush=True)
        while not server.should_exit:
            server.handle_request()
        server.server_close()
        finish("offline-report-browser-preview-v1", guard, "PASS_PREVIEW_CLOSED")
    except BaseException:
        finish("offline-report-browser-preview-v1", guard, "FAIL")
        raise
