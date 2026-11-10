"""Read-only replay of frozen scoring/analysis and matched-input assertions."""

import argparse
import hashlib
import json
from pathlib import Path

from research.agent_rd_eval_v1.analysis import summarize
from research.agent_rd_eval_v1.scoring import score

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/evidence/agent-rd-20261110-v1"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true", help="Create a new evidence receipt; default is read-only")
    args = parser.parse_args()
    freeze_path = ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json"
    freeze = read(freeze_path)
    assert sha(freeze_path) == "5b70e5f1454e9062441b3e292a50fab45f9aebe73ed7994971c6a88de2ad4c8e"
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    frozen = ROOT / "research/agent_rd_eval_v1/frozen"
    plan, cards = read(frozen / "schedule.json"), read(frozen / "locked-cases.json")
    gold = read(frozen / "locked-oracle.json")
    card_map = {c["case_id"]: c for c in cards}
    results, traces = [], {}
    calls, provider_responses = set(), 0
    for path in sorted((PUBLIC / "locked-results-v1").glob("*.json")):
        if path.name.endswith("-trace.json"):
            continue
        receipt = read(path)
        unit = receipt["unit"]
        assert unit in plan and receipt["freeze_sha256"] == sha(freeze_path)
        envelope = read(path.with_name(unit["unit_id"] + "-trace.json"))
        assert canonical(envelope) == receipt["mission_file_sha256"]
        assert canonical(envelope["payload"]) == envelope["sha256"]
        row = envelope["payload"]
        assert row["mission_id"] == receipt["mission_id"]
        assert row["system"] == unit["system"] and row["seed"] == unit["seed"]
        assert score(card_map[unit["case_id"]], gold[unit["case_id"]], row) == receipt["score"]
        assert len(row["calls"]) <= 3 and row["cost"]["model_calls"] == len(row["calls"])
        for call in row["calls"]:
            assert call["call_id"] not in calls
            calls.add(call["call_id"])
            if call["status"] == "PASS":
                provider_responses += 1
                response = call["receipt"]
                assert response["model_digest"] == freeze["model_digest"]
                assert all(m.get("size_vram") == 0 for m in response["running_model_metadata"]["models"])
                assert response["request"]["max_tokens"] == 256 and response["request"]["seed"] == unit["seed"]
        results.append(receipt)
        traces[unit["unit_id"]] = row
    replay = summarize(plan, results, cards)
    assert replay == read(PUBLIC / "analysis-v1/analysis.json")
    matched, unavailable = 0, 0
    for case in cards:
        for seed in freeze["decoding_seeds"]:
            identities = [f"{case['case_id']}--{seed}--{system}" for system in ("B2", "P")]
            pair = [traces.get(identity) for identity in identities]
            if not all(row and row["calls"] and row["calls"][0]["status"] == "PASS" for row in pair):
                unavailable += 1
                continue
            first, second = [row["calls"][0]["receipt"]["request"] for row in pair]
            for key in ("messages", "seed", "max_tokens", "format"):
                assert first[key] == second[key], f"Primary inputs differ: {case['case_id']} {seed} {key}"
            matched += 1
    receipt = {"status": "PASS_READ_ONLY_FROZEN_SCORE_AND_ANALYSIS_REPLAY", "planned": len(plan), "attempted": len(results),
               "successful_provider_responses": provider_responses, "unique_attempt_call_ids": len(calls),
               "B2_P_identical_initial_input_pairs_checked": matched,
               "B2_P_pairs_without_two_successful_initial_responses": unavailable,
               "analysis_sha256": sha(PUBLIC / "analysis-v1/analysis.json"), "frozen_pins_preserved": len(freeze["pins"]),
               "model_inference": False, "new_data_download": False, "score_changes": False,
               "independent_expert_validation": False}
    if args.write_receipt:
        with (PUBLIC / "reproducibility-replay-v1.json").open("x", encoding="utf-8", newline="\n") as output:
            json.dump(receipt, output, indent=2)
            output.write("\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
