from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app/streamlit_app.py"
PAGES = ["Overview · ภาพรวม", "Scenario Setup · ตั้งเงื่อนไข", "Screening Run · จำลองการคัดเลือก",
         "Compare & Export · เปรียบเทียบและส่งออก"]


def app():
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not at.exception
    return at


def test_overview_provenance_logo_and_real_demo_navigation():
    at = app()
    assert at.session_state.run.dataset.data_origin == "HISTORICAL_PUBLIC_DATA"
    assert any("Not an official GPO" in c.value for c in at.caption)
    at.button(key="try_demo").click().run()
    assert not at.exception and at.radio(key="screen").value == PAGES[2]
    assert at.button(key="select").disabled is False


def test_scenario_apply_reset_zero_budget_and_dataset_choice():
    at = app()
    at.radio(key="screen").set_value(PAGES[1]).run()
    at.selectbox(key="cfg_dataset").set_value("synthetic_shift_v1")
    at.number_input(key="cfg_budget").set_value(0)
    at.number_input(key="cfg_seed").set_value(7)
    at.button(key="apply").click().run()
    assert not at.exception
    assert at.session_state.run.scenario.budget_units == 0
    assert at.session_state.run.scenario.dataset == "synthetic_shift_v1"
    at.radio(key="screen").set_value(PAGES[2]).run()
    assert at.button(key="select").disabled and at.session_state.run.done
    at.radio(key="screen").set_value(PAGES[1]).run()
    at.button(key="restore").click().run()
    assert not at.exception and at.session_state.run.scenario.budget_units == 30


def test_run_buttons_pending_delivery_complete_and_reset():
    at = app()
    at.radio(key="screen").set_value(PAGES[2]).run()
    at.button(key="select").click().run()
    assert not at.exception and at.session_state.run.metrics["pending_assays"] == 5
    assert at.session_state.run.metrics["confirmed_hits"] == 0
    at.button(key="advance").click().run()
    assert at.session_state.run.metrics["delivered_assays"] == 0
    at.button(key="advance").click().run()
    assert at.session_state.run.metrics["delivered_assays"] == 5
    at.button(key="finish").click().run(timeout=60)
    assert not at.exception and at.session_state.run.metrics["spent_units"] == 30
    at.button(key="reset_run").click().run()
    assert at.session_state.run.metrics["spent_units"] == 0 and not at.session_state.run.requests


def test_compare_screen_executes_and_exposes_downloads():
    from curaloop.domain import Scenario
    from curaloop.service import RunService
    at = app()
    at.session_state.run = RunService(Scenario(candidate_count=24, initial_count=6, budget_units=3))
    at.radio(key="screen").set_value(PAGES[3]).run()
    at.button(key="compare").click().run(timeout=60)
    assert not at.exception
    assert len(at.session_state.comparison) == 5
    assert len(at.get("download_button")) == 4
    assert at.session_state.comparison[0]["metrics"]["spent_units"] == 3


def test_apply_new_scenario_clears_stale_comparison():
    at = app()
    at.session_state.comparison = [{"stale": True}]
    at.radio(key="screen").set_value(PAGES[1]).run()
    at.button(key="apply").click().run()
    assert at.session_state.comparison is None and not at.exception


def test_paired_benchmark_control_runs_real_zero_budget_replays():
    from curaloop.domain import Scenario
    from curaloop.service import RunService
    at = app()
    at.session_state.run = RunService(Scenario(budget_units=0))
    at.radio(key="screen").set_value(PAGES[3]).run()
    at.number_input(key="benchmark_seed_count").set_value(2)
    at.button(key="run_benchmark").click().run(timeout=60)
    assert not at.exception
    assert len(at.session_state.paired_benchmark["runs"]) == 10
    assert all(r["metrics"]["spent_units"] == 0 for r in at.session_state.paired_benchmark["runs"])
