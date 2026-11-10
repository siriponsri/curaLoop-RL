"""Verify the UI refinement without regenerating a successful model answer."""

import subprocess
import sys

from agent_rd_admin_v1 import ROOT

for script, arguments in (("agent_rd_frontend_checks_v1.py", ["v3"]), ("agent_rd_browser_review_v2.py", [])):
    result = subprocess.run([sys.executable, "tools/" + script, *arguments], cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)
