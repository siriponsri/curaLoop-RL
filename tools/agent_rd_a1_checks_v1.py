"""A1 code/oracle/frontend checks in one bounded local job."""

import subprocess
import sys

from agent_rd_admin_v1 import ROOT

for script, arguments in (("agent_rd_checks_v1.py", ["v3"]), ("agent_rd_ui_fixture_v1.py", []), ("agent_rd_frontend_checks_v1.py", ["v1"])):
    result = subprocess.run([sys.executable, "tools/" + script, *arguments], cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)
