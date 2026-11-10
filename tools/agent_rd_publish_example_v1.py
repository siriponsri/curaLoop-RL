"""Publish the actual aggregate-only acceptance record and immutable dossier."""

import shutil

from agent_rd_admin_v1 import PUBLIC, TASK, read, sha, write

row = read(TASK / "browser-real-mission-v1.json")
root = TASK / "jobs/actual-browser-model-acceptance-v1/disposable-api-agent-rd"
source = root / "missions" / (row["mission_id"] + ".json")
target = PUBLIC / "example-mission-v1.json"
assert not target.exists()
shutil.copyfile(source, target)
assert sha(source) == sha(target)
folders = list((root / "dossiers").glob(row["mission_id"] + "-*"))
assert len(folders) == 1
destination = PUBLIC / "example-dossier-v1"
assert not destination.exists()
shutil.copytree(folders[0], destination)
assert {p.name for p in destination.iterdir()} == {"manifest.json", "dossier.json", "trace.json", "report-en.html", "report-th.html"}
assert all(sha(path) == sha(destination / path.name) for path in folders[0].iterdir())
write(PUBLIC / "example-publication-v1.json", {"status": "PASS_EXACT_COPY_OF_ACTUAL_MODEL_ACCEPTANCE", "mission_id": row["mission_id"],
      "mission_sha256": sha(target), "files": {p.name: sha(p) for p in destination.iterdir()},
      "new_inference": False, "private_compound_rows": False, "final16_access": False,
      "note": "Historical author computation, not a live run or independent expert validation"}, True)
print("Published one original real mission and five exact dossier files; no new inference")
