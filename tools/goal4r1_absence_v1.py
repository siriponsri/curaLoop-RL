"""Fresh read-only confirmation after cleanup; never recreates remote paths."""

import json
from pathlib import Path

from tools.remote_goal4_control_v1 import ssh_script

ROOT = Path(__file__).resolve().parents[1]


def main():
    retained = ROOT / ".local/goal4r1-20261105-v1/remote-return/full-v1/files"
    fixture_manifest = retained / ".local/goal4r1-20261105-v1/external-scratch-manifest-v2.json"
    fixtures = [r["source"] for r in json.loads(fixture_manifest.read_text())["sources"]]
    paths = ["/home/chaw/curaloop-rl/" + name for name in (
        "goal2-20261104-v1", "plan-a-20261105-v1", "plan-a-20261105-v1-return",
        "plan-a-20261105-v2", "plan-a-20261105-v2-return",
        "goal4r1-20261105-v1", "goal4r1-20261105-v1-return")]
    script = "from pathlib import Path; import json,socket; from datetime import datetime,timezone; names=" + repr(paths) + "; fixtures=" + repr(fixtures) + "; rows={n:{'exists':Path(n).exists(),'is_symlink':Path(n).is_symlink()} for n in names+fixtures}; ok=all(not r['exists'] and not r['is_symlink'] for r in rows.values()); print(json.dumps({'status':'PASS_ALL_SCOPED_ROOTS_AND_IDENTIFIED_FIXTURES_ABSENT' if ok else 'FAIL','utc':datetime.now(timezone.utc).isoformat(),'host':socket.gethostname(),'paths':rows,'read_only':True},indent=2))"
    result = json.loads(ssh_script(script))
    output = ROOT / "docs/evidence/goal4r1-20261105-v1/remote-absence-v1.json"
    with output.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result, indent=2))
    if not result["status"].startswith("PASS"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
