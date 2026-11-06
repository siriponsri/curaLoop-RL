"""Synthetic fixture catalogue only; no molecular outcomes or external providers."""

from .contracts import Brief, Source, draft_plan
from .workflow import Workflow


def catalogue():
    base = {"citation": "Synthetic engineering example, not a research paper",
            "version": "fixture-v1", "locator": "fixture:paragraph-1",
            "role": "development_fixture", "available": True,
            "target": "DEMO_TARGET", "endpoint": "DEMO_CONFIRMATION", "unit": "uM",
            "statement": "Synthetic source statement for workflow testing; no compound result."}
    return {key: Source(source_id=key, measurement_status=status, **base)
            for key, status in [("fixture_measured", "measured_exact"),
                                ("fixture_paper", "metadata_only"),
                                ("fixture_default", "default_filled"),
                                ("fixture_censored", "tested_censored"),
                                ("fixture_missing", "missing"),
                                ("fixture_untested", "untested"),
                                ("fixture_prediction", "predicted")]}


def brief(source_ids=("fixture_measured",), **changes):
    values = {"question": "Prepare a confirmation study proposal for the demo target.",
              "target": "DEMO_TARGET", "endpoint": "DEMO_CONFIRMATION", "unit": "uM",
              "source_ids": source_ids, "request_count": 2, "unit_cost": 3., "budget": 6.}
    return Brief(**(values | changes))


def run_demo(output):
    plan = draft_plan(brief(tuple(catalogue())), catalogue())
    workflow = Workflow(output)
    try:
        state = workflow.start("demo-v1", plan)
        report = workflow.build_report("demo-v1", state["revision"])
        preview = workflow.preview_delivery("demo-v1", report["revision"])
        return {"status": "PASS_OFFLINE_DEMO", "plan_sha256": plan["plan_sha256"],
                "report": report, "preview": preview,
                "live_sources_contacted": False, "llm_invoked": False,
                "scientific_campaign_run": False, "synthetic": True}
    finally:
        workflow.close()
