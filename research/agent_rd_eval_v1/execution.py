"""Real missions and real source faults; never synthesizes a model answer."""

import shutil
from pathlib import Path

from curaloop_rd.agent_rd.contracts import MissionSpec
from curaloop_rd.agent_rd.engine import MissionEngine, MissionInterrupted
from curaloop_rd.confirmation_study import INPUTS, ROOT


def source_root(case, destination):
    if not case["fault"]:
        return ROOT
    destination = Path(destination)
    if not destination.exists():
        destination.mkdir(parents=True, exist_ok=False)
        for relative, _, _ in INPUTS.values():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        fault = case["fault"]
        if fault in ("missing_card", "missing_cells"):
            (destination / INPUTS["card" if fault == "missing_card" else "cells"][0]).unlink()
        elif fault == "summary_append":
            with (destination / INPUTS["summary"][0]).open("ab") as stream:
                stream.write(b"\n")
        elif fault == "same_size_cells_tamper":
            path = destination / INPUTS["cells"][0]
            data = bytearray(path.read_bytes())
            data[-10] = (data[-10] + 1) % 128
            path.write_bytes(data)
        else:
            raise ValueError("Unknown constructed source fault")
    return destination


def execute(case, unit, store, work, *, identity=None):
    spec = MissionSpec.model_validate(case["spec"])
    row = store.read(identity) if identity else store.create(spec, system=unit["system"], seed=unit["seed"])
    root = source_root(case, Path(work) / "source-faults" / case["case_id"])
    checkpoint_path = Path(work) / (row["mission_id"] + "-interruption.json")

    def checkpoint(current):
        if not checkpoint_path.exists():
            checkpoint_path.write_text('{"mechanism":"CONTROLLED_EXCEPTION_AFTER_REAL_MODEL_RETURN","reused_model_response":true}\n')
            store.update(current["mission_id"], current["revision"], "INTERRUPTED_RECOVERABLE",
                         "Predeclared constructed interruption after a real recorded response; no process crash claim")
            raise MissionInterrupted("Constructed evaluation checkpoint")

    try:
        return MissionEngine(store, source_root=root, checkpoint=checkpoint if case["recovery"] else None).run(row["mission_id"])
    except MissionInterrupted:
        return MissionEngine(store, source_root=root).run(row["mission_id"])
