"""Scorer/oracle conformance uses direct arithmetic, never fake model outcomes."""

import copy

from curaloop_rd.agent_rd.contracts import MissionSpec
from curaloop_rd.agent_rd.evidence import collect, compact, comparisons
from curaloop_rd.agent_rd.store import MissionStore
from research.agent_rd_eval_v1.analysis import rate, summarize
from research.agent_rd_eval_v1.cases import cases, schedule
from research.agent_rd_eval_v1.execution import execute
from research.agent_rd_eval_v1.oracle import expected_values, gold
from research.agent_rd_eval_v1.scoring import score


def test_case_schedule_and_independent_csv_oracle():
    assert len(schedule()) == 408 and len({r["unit_id"] for r in schedule()}) == 408
    for card in cases("development") + cases("locked"):
        spec = MissionSpec.model_validate(card["spec"])
        data = collect(spec)
        assert expected_values(card["spec"]) == {**compact(data)["values"], **comparisons(data)["values"]}


def test_strong_deterministic_reference_and_constructed_faults(tmp_path):
    cards = cases("locked")
    truth = gold(cards)
    store = MissionStore(tmp_path / "missions")
    for card in cards:
        unit = {"system": "B0", "seed": 17011}
        row = execute(card, unit, store, tmp_path)
        result = score(card, truth[card["case_id"]], row)
        assert result["success"], (card["case_id"], result)
        assert row["cost"]["model_calls"] == 0


def test_scoring_detects_incomplete_correct_table_and_all_failure_attempts(tmp_path):
    card = cases("locked")[0]
    truth = gold([card])[card["case_id"]]
    row = execute(card, {"system": "B0", "seed": 17011}, MissionStore(tmp_path / "missions"), tmp_path)
    missing = copy.deepcopy(row)
    del missing["released"]["values"][card["required_keys"][0]]
    assert not score(card, truth, missing)["success"]
    failed = {**row, "released": None, "state": "FAILED"}
    result = score(card, truth, failed)
    assert not result["success"] and result["execution_failed"]
    assert result["numeric"]["claims"] == 0


def test_unattempted_units_and_zero_claim_denominators_cannot_look_successful():
    assert rate(0, 0) is None
    summary = summarize(schedule(), [], cases("locked"))
    assert summary["status"] == "INCONCLUSIVE_INCOMPLETE_MATRIX"
    assert summary["primary"]["exploratory_paired_case_interval_95_pp"] is None
    assert [s["planned"] for s in summary["systems"]] == [96, 96, 96, 96, 24]
    assert all(s["attempted"] == s["successes"] == 0 and s["released_numeric_error_rate"] is None for s in summary["systems"])
