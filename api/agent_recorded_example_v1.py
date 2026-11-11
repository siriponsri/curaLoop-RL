"""Explicit import of one genuine recorded model mission, never regeneration."""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from curaloop_rd.agent_rd.contracts import MissionSpec, digest
from curaloop_rd.agent_rd.evidence import collect, comparisons
from curaloop_rd.agent_rd.verifier import verify

EXAMPLE_ID = "788428ed-b5b2-4743-af1b-6324b4a441ad"
EXAMPLE_SHA = "a2888ec7c33f9982dfc9325147b65479e5a623305899605cbf88a87afa5f0122"
EXAMPLE = Path(__file__).resolve().parents[1] / "docs/evidence/agent-rd-20261110-v1/example-mission-v1.json"


def import_example(store):
    if any(path.is_symlink() for path in (EXAMPLE, *EXAMPLE.parents)) or EXAMPLE.stat().st_nlink != 1:
        raise ValueError("Recorded example source must not follow a symlink or shared hardlink")
    source = EXAMPLE.read_bytes()
    if hashlib.sha256(source).hexdigest() != EXAMPLE_SHA:
        raise ValueError("Original recorded model example identity mismatch")
    envelope = json.loads(source)
    row = envelope["payload"]
    if digest(row) != envelope["sha256"] or row["mission_id"] != EXAMPLE_ID or row["state"] != "COMPLETED":
        raise ValueError("Original recorded model example envelope is invalid")
    evidence = collect(MissionSpec.model_validate(row["spec"]))
    if evidence["evidence_id"] != row["evidence"]["evidence_id"] or not verify(row["released"], evidence, comparisons(evidence))["valid"]:
        raise ValueError("Original example source identity or claims no longer verify")
    target = store.path(EXAMPLE_ID)
    if target.exists():
        if target.read_bytes() != source:
            raise ValueError("Existing mission differs; no import overwrite is allowed")
        return store.read(EXAMPLE_ID)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=".recorded-example-", dir=store.root, delete=False) as output:
            temporary = Path(output.name)
            output.write(source)
            output.flush()
            os.fsync(output.fileno())
        # Atomic no-replace publication. This links only the newly written
        # private temporary copy; it never links/mutates the public original.
        try:
            os.link(temporary, target)
        except FileExistsError:
            if target.read_bytes() != source:
                raise ValueError("Concurrent existing mission differs; preserve it") from None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    if target.read_bytes() != source:
        raise ValueError("Recorded example copy failed byte identity")
    return store.read(EXAMPLE_ID)
