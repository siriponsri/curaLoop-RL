"""Post-hoc descriptive replay of gate opportunities in fixed actual traces.

No new task, inference, score definition or primary result is introduced.
The unchanged verifier is replayed on recorded terminal proposals only.
"""

import json
from collections import Counter
from pathlib import Path

from agent_rd_admin_v1 import PUBLIC, ROOT, read, sha, write

from curaloop_rd.agent_rd.verifier import verify


def main():
    analysis_path = PUBLIC / "analysis-v1/analysis.json"
    analysis = read(analysis_path)
    replay = read(PUBLIC / "reproducibility-replay-v1.json")
    assert replay["status"] == "PASS_READ_ONLY_FROZEN_SCORE_AND_ANALYSIS_REPLAY"
    assert replay["analysis_sha256"] == sha(analysis_path)
    source_path = PUBLIC / "analysis-v1/source-pins.json"
    source_pins = read(source_path)
    assert all(sha(ROOT / path) == value for path, value in source_pins.items())
    rows, paired = [], {}
    for system in ("B1", "B2", "P", "A-NOREPAIR"):
        counts = Counter()
        error_types = Counter()
        for path in sorted((PUBLIC / "locked-results-v1").glob("*.json")):
            if path.name.endswith("-trace.json"):
                continue
            result = read(path)
            unit = result["unit"]
            if unit["system"] != system:
                continue
            trace = read(path.with_name(unit["unit_id"] + "-trace.json"))["payload"]
            counts["missions"] += 1
            for call in trace["calls"]:
                if call["status"] != "PASS":
                    continue
                try:
                    proposal = json.loads(call["output"])
                except (ValueError, TypeError):
                    continue
                if not isinstance(proposal, dict) or proposal.get("action") not in ("answer", "abstain"):
                    continue
                counts["terminal_proposals"] += 1
                verdict = verify(proposal, trace["evidence"], trace["derived"])
                if not verdict["valid"]:
                    counts["verifier_invalid_terminal_proposals"] += 1
                    error_types.update(str(error) for error in verdict["errors"])
            if system in ("B2", "P"):
                paired[(unit["case_id"], unit["seed"], system)] = {
                    "outputs": [call.get("output") for call in trace["calls"]],
                    "task_success": result["score"]["success"]}
        rows.append({"system": system, "missions": counts["missions"],
                     "terminal_proposals": counts["terminal_proposals"],
                     "verifier_invalid_terminal_proposals": counts["verifier_invalid_terminal_proposals"],
                     "verification_error_types": dict(error_types)})
    pairs = {(case, seed) for case, seed, _ in paired}
    comparable = [(paired[(case, seed, "B2")], paired[(case, seed, "P")]) for case, seed in sorted(pairs)
                  if (case, seed, "B2") in paired and (case, seed, "P") in paired]
    assert all(sha(ROOT / path) == value for path, value in source_pins.items())
    write(PUBLIC / "mechanism-audit-v1.json", {
        "status": "DESCRIPTIVE_FIXED_TRACE_VERIFIER_REPLAY_NO_SCORE_CHANGE",
        "arms": rows, "comparable_B2_P_seed_case_pairs": len(comparable),
        "B2_P_identical_recorded_output_sequences": sum(left["outputs"] == right["outputs"] for left, right in comparable),
        "B2_P_equal_task_success_pairs": sum(left["task_success"] == right["task_success"] for left, right in comparable),
        "all_case_averaged_primary_differences_zero": all(row["difference_pp"] == 0 for row in analysis["paired_cases"]),
        "source_pins": {"analysis": sha(analysis_path), "all_unit_source_pins": sha(source_path),
                        "frozen_verifier": sha(ROOT / "src/curaloop_rd/agent_rd/verifier.py"),
                        "descriptive_audit_source": sha(Path(__file__))},
        "new_model_calls": 0, "new_scientific_score": False, "independent_expert_validation": False,
        "interpretation": "Replay describes verifier opportunities in observed proposals, not general gate efficacy or semantic task correctness. Identical observed paired scores and a degenerate resampling interval do not establish external-population equivalence."
    }, True)
    print("Created post-hoc mechanism description from fixed actual traces; no scores or outputs changed")


if __name__ == "__main__":
    main()
