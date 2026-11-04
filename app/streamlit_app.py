"""Four functional views backed by the same public RunService as the CLI."""

import base64
import json
from dataclasses import asdict
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from curaloop import __version__
from curaloop.domain import BASELINES, DATASETS, POLICIES, Scenario
from curaloop.export import csv_report, json_report
from curaloop.service import LIMITATIONS, RunService, code_identity, compare

st.set_page_config(page_title="CuraLoop-RL | Screening Decision Lab", page_icon="◉", layout="wide")
font_path = Path(__file__).resolve().parents[1] / "assets/fonts/NotoSansThai.ttf"
if font_path.exists():
    font_data = base64.b64encode(font_path.read_bytes()).decode("ascii")
    st.markdown(f"<style>@font-face {{font-family: 'CuraThai'; src: url(data:font/ttf;base64,{font_data}) format('truetype'); font-weight:100 900; font-style:normal;}} "
                "html,body,.stApp {font-family:'CuraThai',sans-serif;} "
                "h1,h2,h3,h4,p,label,input,button,textarea,small,[data-testid='stMarkdownContainer'],[data-testid='stWidgetLabel'],[data-testid='stCaptionContainer'] {font-family:'CuraThai',sans-serif !important;} </style>",
                unsafe_allow_html=True)
@alt.theme.register("curaloop", enable=True)
def curaloop_theme() -> alt.theme.ThemeConfig:
    return {"config": {"font": "CuraThai", "axis": {"labelFont": "CuraThai", "titleFont": "CuraThai"},
                       "legend": {"labelFont": "CuraThai", "titleFont": "CuraThai"}}}


st.markdown("""
<style>
.stApp {background:#f6f8fa; color:#16333b;}
.block-container {max-width:1320px; padding-top:3.8rem; padding-bottom:3rem;}
h1,h2,h3 {letter-spacing:-.025em;}
[data-testid="stSidebar"] {background:#eaf1f2; border-right:1px solid #d6e2e4;}
[data-testid="stMetric"] {background:white; border:1px solid #dbe5e8; border-radius:10px; padding:16px;}
.eyebrow {font-size:13px; font-weight:700; color:#13766d; letter-spacing:.12em;}
.provenance {padding:10px 14px; background:#e6f3ed; border-left:4px solid #16766b; border-radius:4px; font-size:14px;}
.hint {color:#50666e; font-size:16px; line-height:1.7;}
</style>
""", unsafe_allow_html=True)

SCREENS = ["Overview", "Scenario Setup", "Screening Run", "Compare & Export"]
DATASET_LABELS = {"hiv_moleculenet_replay_v1": "Historical · MoleculeNet HIV (1200 real molecules)",
                  "synthetic_linear_v1": "Synthetic · Linear signal (240 candidates)",
                  "synthetic_shift_v1": "Synthetic · Nonlinear shift (240 candidates)"}


def example_scenario() -> Scenario:
    return Scenario(dataset="hiv_moleculenet_replay_v1", candidate_count=1200, initial_count=48)


def start_example() -> None:
    replace_run(example_scenario(), "greedy")
    st.session_state.screen = SCREENS[2]


def replace_run(scenario: Scenario, policy: str) -> None:
    st.session_state.run = RunService(scenario, policy)
    st.session_state.comparison = None
    st.session_state.pop("paired_benchmark", None)


if "run" not in st.session_state:
    replace_run(example_scenario(), "greedy")
run: RunService = st.session_state.run

with st.sidebar:
    st.image(str(Path(__file__).resolve().parents[1] / "assets/branding/curaloop-logo-v2.png"), width=230)
    st.caption("PHARMACEUTICAL SCREENING\nDECISION LAB")
    screen = st.radio("Workspace", SCREENS, key="screen")
    st.divider()
    st.markdown("**" + run.dataset.data_origin + "**")
    st.caption(f"v{__version__} · CPU / Offline\n3 baselines + trained Q-learning / bandit\nTraining source: synthetic tasks")
    st.caption("Personal independent project.\nNot an official GPO system.")

st.markdown('<div class="eyebrow">CURALOOP-RL / RESEARCH WORKBENCH</div>', unsafe_allow_html=True)
st.title(screen.split(" · ")[0])
st.markdown('<div class="provenance">' + ("Historical public assay" if run.dataset.data_origin == "HISTORICAL_PUBLIC_DATA"
            else "Synthetic descriptors and fictional assay outcomes") + ' | Simulated costs and delays | '
            'Retrospective simulator — not a validated Digital Twin</div>', unsafe_allow_html=True)
if notice := st.session_state.pop("run_notice", None):
    st.success(notice)
st.write("")


def metric_strip(service: RunService) -> None:
    m = service.metrics
    cols = st.columns(4)
    cols[0].metric("Confirmed hits", m["confirmed_hits"], help="New delivered active outcomes only; excludes seed labels.")
    cols[1].metric("Delivered assays", m["delivered_assays"], help="Observed Boolean outcomes; excludes missing outcomes and seed labels.")
    cols[2].metric("Pending", m["pending_assays"])
    cols[3].metric("Available units", m["remaining_units"], help="Total budget minus spent and reserved units.")


def export_controls(reports: list[dict], prefix: str) -> None:
    c1, c2 = st.columns(2)
    c1.download_button("Download JSON / Full report", json_report(reports).encode("utf-8"),
                       file_name=f"curaloop-{prefix}.json", mime="application/json", key=prefix + "_json")
    c2.download_button("Download CSV / Event ledger", csv_report(reports).encode("utf-8-sig"),
                       file_name=f"curaloop-{prefix}.csv", mime="text/csv", key=prefix + "_csv")
    st.caption("Includes scenario, provenance, algorithm version, public events and metrics; excludes unrevealed outcomes. "
               "Only a single-run JSON can resume a campaign. Comparison JSON contains independent runs; CSV is an audit ledger.")


def discovery_chart(reports: list[dict]) -> None:
    points = [{**p, "policy": r["manifest"]["policy_id"]} for r in reports for p in r["curve"]]
    if not points:
        st.info("No public events are available to plot yet.")
        return
    chart = alt.Chart(pd.DataFrame(points)).mark_line(interpolate="step-after", point=True).encode(
        x=alt.X("spent_units:Q", title="Settled simulated cost units", scale=alt.Scale(zero=True)),
        y=alt.Y("confirmed_hits:Q", title="New delivered active hits", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("policy:N", title="Policy", scale=alt.Scale(domain=list(POLICIES), range=["#64748b", "#087f72", "#b66914", "#6d4da3", "#1976a3"])),
        strokeDash=alt.StrokeDash("policy:N", legend=None), order="event_index:Q",
        tooltip=["policy:N", "spent_units:Q", "confirmed_hits:Q", "step:Q", "pending_assays:Q"],
    ).properties(height=310)
    st.altair_chart(chart, width="stretch")


if screen == SCREENS[0]:
    st.header(f"With capacity to test {run.scenario.budget_units // run.scenario.assay_cost_units} of {run.scenario.candidate_count} candidates, where should we start?")
    st.markdown("Public descriptors are available before selection, while unrevealed assay outcomes remain private. "
                "Choose how to allocate the screening budget and update decisions as delayed results arrive.")
    columns = st.columns(4)
    for col, (title, text) in zip(columns, [
        ("01 · Select candidates", "Random samples uniformly; Greedy favors predicted activity; Uncertainty favors predictions near 0.5."),
        ("02 · Submit simulated assays", "Reserve budget and queue capacity immediately. Duplicate requests are rejected."),
        ("03 · Wait for feedback", "Pending outcomes are neither confirmed hits nor model-training labels."),
        ("04 · Update decisions", "Only seed labels and delivered outcomes inform the next batch."),
    ]):
        with col, st.container(border=True):
            st.subheader(title)
            st.write(text)
    metric_strip(run)
    st.button("Start historical example", type="primary", key="try_demo", on_click=start_example)
    with st.expander("Provenance & limits", expanded=True):
        if run.dataset.data_origin == "HISTORICAL_PUBLIC_DATA":
            st.write("The current campaign replays historical MoleculeNet HIV assays from NCI DTP / DeepChem. "
                     "The label-blind 1,200-molecule derivative includes 1,024-bit Morgan fingerprints and source hashes. "
                     "TDC declares CC BY 4.0. Costs and delays are simulated assumptions.")
            st.write("Historical seed labels are sampled uniformly without consulting their outcomes. Every policy receives "
                     "the same seed labels as preexisting sunk cost; seed hits are excluded from new hits.")
        else:
            st.write("The current campaign uses generated numerical descriptors and fictional outcomes. "
                     "It is a synthetic engineering fixture, not historical biological evidence. Costs and delays are simulated.")
            st.write("Synthetic seed labels use disclosed oracle-assisted stratification. Every policy receives "
                     "the same seed labels as preexisting sunk cost; seed hits are excluded from new hits.")
        st.write("The separate historical HIV resource and two synthetic fixtures support reproducible simulator checks. "
                 "The learned controllers were trained only on synthetic tasks.")
        st.markdown("[MoleculeNet paper](https://doi.org/10.1039/C7SC02664A) · [Dataset & license](https://tdcommons.ai/single_pred_tasks/hts/#hiv)")
        st.write("Independent personal project; not an official GPO project and not institutionally endorsed.")
    st.subheader("Evidence status")
    st.dataframe(pd.DataFrame([
        {"Capability": "Offline screening + 3 baseline policies", "Status": "IMPLEMENTED"},
        {"Capability": "Historical HIV replay + scaffold predictor benchmark", "Status": "IMPLEMENTED · custom subset / split"},
        {"Capability": "Bandit / tabular Q-learning", "Status": "TRAINED on synthetic tasks · real-assay evaluation separate"},
        {"Capability": "Live lab / operational Digital Twin", "Status": "NOT AVAILABLE"},
    ]), hide_index=True, width="stretch")

elif screen == SCREENS[1]:
    st.header("Configure a screening campaign")
    st.caption("Apply creates an independent run and clears previous comparisons. Editing this form does not change the active run.")
    if st.button("Restore defaults", key="restore"):
        replace_run(example_scenario(), "greedy")
        for key in list(st.session_state):
            if key.startswith("cfg_"):
                del st.session_state[key]
        st.rerun()
    s = run.scenario
    with st.form("scenario_form"):
        dataset = st.selectbox("Dataset", DATASETS, index=DATASETS.index(s.dataset),
                               format_func=lambda x: DATASET_LABELS[x], key="cfg_dataset")
        st.caption("LIT-PCBA is unavailable in this release: redistribution rights, assay semantics and preprocessing require separate review.")
        left, right = st.columns(2)
        seed = left.number_input("Random seed", 0, 2**32 - 1, s.seed, key="cfg_seed")
        budget = right.number_input("Budget units", 0, 10000, s.budget_units, key="cfg_budget")
        initial = left.number_input("Initial labels", 0, 2000, s.initial_count, key="cfg_initial")
        batch = right.slider("Batch capacity", 1, 100, s.batch_size, key="cfg_batch")
        delay = left.slider("Delay steps", 0, 100, s.delay_steps, key="cfg_delay")
        policy = right.selectbox("Selection policy", POLICIES, index=POLICIES.index(run.policy), key="cfg_policy")
        with st.expander("Synthetic stress assumptions"):
            cost = st.slider("Cost units per assay", 1, 100, s.assay_cost_units, key="cfg_cost")
            jitter = st.slider("Delay jitter steps", 0, 20, s.delay_jitter, key="cfg_jitter")
            missing = st.slider("Missing outcomes (%)", 0, 100, s.missing_percent, key="cfg_missing")
            st.caption("Missingness is a simulated assumption. Missing outcomes consume budget and are neither active nor inactive.")
        applied = st.form_submit_button("Apply scenario", type="primary", key="apply")
    if applied:
        try:
            scenario = Scenario(dataset=dataset, seed=int(seed), candidate_count=1200 if dataset == "hiv_moleculenet_replay_v1" else 240,
                                initial_count=initial, budget_units=int(budget),
                                batch_size=batch, delay_steps=delay, assay_cost_units=cost,
                                delay_jitter=jitter, missing_percent=missing)
            replace_run(scenario, policy)
            st.session_state.run_notice = "New run created. Open Screening Run to select the first batch."
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    st.json({"active_scenario": asdict(run.scenario), "policy": run.policy}, expanded=False)

elif screen == SCREENS[2]:
    st.header("Inspect each decision and delivered outcome")
    st.caption(f"{run.policy.upper()} · seed {run.scenario.seed} · simulated step {run.observation.step} · {run.dataset.name}")
    c1, c2, c3, c4 = st.columns(4)
    obs = run.observation
    can_select = bool(obs.slots_available and obs.eligible_candidate_ids and
                      obs.budget_remaining_units >= obs.assay_cost_units and not run.done)
    if c1.button("Select batch", type="primary", disabled=not can_select, key="select"):
        try:
            with st.spinner("Selecting from revealed public observations…"):
                run.next_batch()
            st.rerun()
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
    if c2.button("Advance +1", disabled=not run.pending, key="advance"):
        try:
            run.advance()
            st.rerun()
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
    if c3.button("Complete run", disabled=run.done, key="finish"):
        try:
            with st.spinner("Executing the campaign locally on CPU…"):
                run.finish()
            st.rerun()
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
    if c4.button("Reset run", key="reset_run"):
        replace_run(run.scenario, run.policy)
        st.rerun()
    metric_strip(run)
    m = run.metrics
    st.caption(f"Budget {run.scenario.budget_units} = spent {m['spent_units']} + reserved {m['reserved_units']} "
               f"+ available {m['remaining_units']} units · missing outcomes {m['missing_assays']} · seed hits {m['seed_hits']} (excluded from new hits)")
    if run.done:
        st.success("Campaign complete: no pending feedback; budget or eligible candidates are exhausted.")
    elif run.pending and not can_select:
        st.info("Awaiting feedback: advance simulated time to reveal outcomes when due.")
    elif not run.requests:
        st.info("No new assays requested. Select a batch to begin.")
    st.subheader("Actual selection decisions")
    if run.requests:
        rows = [asdict(r) for r in run.requests]
        statuses = {r.request_id: "MISSING" if r.active is None else "DELIVERED" for r in run.results}
        for row in rows:
            row["status"] = statuses.get(row["request_id"], "PENDING")
        st.dataframe(pd.DataFrame(rows)[["compound_id", "status", "scheduled_at_step", "due_at_step",
                                          "cost_units", "predicted_probability", "model_status", "explanation"]],
                     hide_index=True, width="stretch")
    else:
        st.caption("No selections yet. Predicted probabilities appear only when a model can be fitted.")
    lcol, rcol = st.columns(2)
    with lcol:
        st.subheader("Pending queue")
        if run.pending:
            st.dataframe(pd.DataFrame([{"compound_id": r.compound_id, "due_at_step": r.due_at_step,
                                         "steps_remaining": r.due_at_step - run.observation.step} for r in run.pending]),
                         hide_index=True, width="stretch")
        else:
            st.caption("No pending feedback.")
    with rcol:
        st.subheader("Delivered outcomes")
        if run.results:
            st.dataframe(pd.DataFrame([asdict(r) for r in run.results])[["compound_id", "active", "delivered_at_step", "quality_flag"]],
                         hide_index=True, width="stretch")
        else:
            st.caption("No new delivered outcomes. Pending requests never count as hits.")
    discovery_chart([run.report()])
    with st.expander("Event timeline", expanded=False):
        st.dataframe(pd.DataFrame([asdict(e) for e in run.events])[["event_type", "step", "compound_id", "cost_units", "delivered_active", "explanation"]],
                     hide_index=True, width="stretch")
    with st.expander("Seed labels & evidence"):
        st.dataframe(pd.DataFrame([asdict(r) for r in run.initial_results]), hide_index=True, width="stretch")
        st.json(run.report()["manifest"], expanded=False)

else:
    st.header("Compare selection policies under matched conditions")
    st.write("Each policy starts an independent campaign with the same candidate pool, seed labels, features, budget and assumptions. "
             "One policy's outcomes are never shared with another policy.")
    st.caption(f"Active scenario: {run.scenario.scenario_id} · seed {run.scenario.seed} · budget {run.scenario.budget_units} · batch {run.scenario.batch_size} · delay {run.scenario.delay_steps}")
    include_learned = st.checkbox("Include trained Q-learning and contextual bandit", value=True, key="include_learned")
    if st.button("Compare policies", type="primary", key="compare"):
        try:
            with st.spinner("Executing independent matched-policy campaigns…"):
                st.session_state.comparison = compare(run.scenario, POLICIES if include_learned else BASELINES)
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
    reports = st.session_state.comparison
    if reports:
        st.success("Comparison complete · matched initial conditions")
        discovery_chart(reports)
        summary = [{"Policy": r["manifest"]["policy_id"], "New confirmed hits": r["metrics"]["confirmed_hits"],
                    "Delivered": r["metrics"]["delivered_assays"], "Missing": r["metrics"]["missing_assays"],
                    "Spent units": r["metrics"]["spent_units"], "Simulated steps": r["metrics"]["step"],
                    "Hit rate": r["metrics"]["hit_rate"], "AUC-DB normalized": r["metrics"]["auc_discovery_budget_normalized"]}
                   for r in reports]
        st.dataframe(pd.DataFrame(summary), hide_index=True, width="stretch")
        usage = [{"Policy": r["manifest"]["policy_id"],
                  "Controller requests": r["metrics"]["controller_requests"],
                  "Unseen-state fallback requests": r["metrics"]["controller_fallback_requests"]}
                 for r in reports if r["manifest"]["controller"]]
        if usage:
            st.dataframe(pd.DataFrame(usage), hide_index=True, width="stretch")
            st.caption("Unseen-state fallback uses Greedy when a state is absent from the learned controller. "
                       "Fallback outcomes do not demonstrate successful learned transfer.")
        queue = [{"policy": r["manifest"]["policy_id"], **p} for r in reports for p in r["curve"]]
        st.altair_chart(alt.Chart(pd.DataFrame(queue)).mark_line(interpolate="step-after").encode(
            x=alt.X("step:Q", title="Simulated steps"),
            y=alt.Y("pending_assays:Q", title="Pending assays", axis=alt.Axis(tickMinStep=1)),
            color="policy:N", order="event_index:Q", tooltip=["policy:N", "step:Q", "pending_assays:Q"],
        ).properties(height=180), width="stretch")
        st.warning("This single-seed simulation does not establish general policy superiority, drug efficacy or actual cost savings.")
        st.caption("AUC-DB is the left-step area under the discovery curve up to the configured budget, divided by "
                   "budget × floor(budget/cost). It excludes seed hits and is not model AUROC.")
        export_controls(reports, "comparison")
    else:
        st.info("Compare policies to execute real simulator runs and plot their public event ledgers.")
    with st.expander("Current run (including partial)", expanded=not bool(reports)):
        export_controls([run.report()], "current-run")
    with st.expander("Resume a public snapshot"):
        st.caption("This Streamlit fallback keeps its active run in browser-session memory. "
                   "Export single-run JSON before closing it; the primary web application provides durable local storage.")
        upload = st.file_uploader("CuraLoop single-run JSON only / Max 10 MB", type=["json"], key="resume_upload")
        if st.button("Validate & resume", disabled=upload is None, key="resume"):
            try:
                if upload.size > 10_000_000:
                    raise ValueError("File exceeds 10 MB.")
                payload = json.loads(upload.getvalue().decode("utf-8-sig"))
                if len(payload["runs"]) != 1:
                    raise ValueError("Resume accepts one current-run report, not a comparison export.")
                restored = RunService.restore(payload["runs"][0])
                st.session_state.run = restored
                st.session_state.comparison = None
                st.session_state.pop("paired_benchmark", None)
                for key in list(st.session_state):
                    if key.startswith("cfg_"):
                        del st.session_state[key]
                st.session_state.run_notice = "Public event ledger validated. Open Screening Run to continue."
                st.rerun()
            except (ValueError, KeyError, TypeError) as exc:
                st.error(f"Snapshot could not be resumed: {exc}")
    with st.expander("Scientific limitations"):
        for limitation in LIMITATIONS:
            st.write("• " + limitation)
    with st.expander("Learning Lab / Trained controllers"):
        from curaloop.learning import load_checkpoint
        for name in ("q_learning", "contextual_bandit"):
            cp = load_checkpoint(name)
            st.write(f"**{name}** · {cp['status']} · {cp['training_episodes']} episodes · synthetic training only")
            st.caption(f"Checkpoint SHA256 {cp['checkpoint_sha256']}")
            st.line_chart(pd.DataFrame({"training_return": cp["episode_returns"]}), height=160)
        st.caption("Training curves show recorded training rewards, not validation performance or drug efficacy evidence.")
    with st.expander("Benchmark Lab / Paired seeds and scaffold audit"):
        evidence_path = Path(__file__).resolve().parents[1] / "docs/evidence/hiv-benchmark/summary.json"
        if evidence_path.exists():
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            st.write("**Recorded historical HIV benchmark / Separate from the current campaign**")
            st.caption("HIV subset: 1,200 molecules · 10 seeds · budget 30 · 48 initial labels · custom replay, not a leaderboard")
            st.dataframe(pd.DataFrame(evidence["statistics"]["summary"]), hide_index=True, width="stretch")
            predictor = evidence["predictor_benchmark"]
            st.write(f"Scaffold audit: train {predictor['train_count']} / test {predictor['test_count']} · overlap {predictor['scaffold_overlap']}")
            st.write({k: predictor[k] for k in ("auroc", "average_precision", "brier_score", "test_prevalence")})
            st.caption("The separate predictor audit uses a custom project split and never trains the selection policies. "
                       "It is not drug efficacy validation. Each learned controller used Greedy fallback on all 300 recorded historical requests.")
        seed_count = st.number_input("Paired seeds for a new benchmark", 2, 20, 5, key="benchmark_seed_count")
        st.caption("Uses the current scenario with seeds 0..N−1 and all five policies. CPU execution can take several minutes. "
                   "New outputs do not overwrite the recorded historical benchmark.")
        if st.button("Run paired benchmark", key="run_benchmark"):
            from dataclasses import replace

            from curaloop.benchmark import summarize
            paired_reports = []
            progress = st.progress(0)
            for index in range(int(seed_count)):
                paired_reports.extend(compare(replace(run.scenario, seed=index), POLICIES))
                progress.progress((index + 1) / int(seed_count))
            st.session_state.paired_benchmark = {"runs": paired_reports, "statistics": summarize(paired_reports)}
        if "paired_benchmark" in st.session_state:
            b = st.session_state.paired_benchmark
            st.dataframe(pd.DataFrame(b["statistics"]["summary"]), hide_index=True, width="stretch")
            st.caption(b["statistics"]["interpretation"])
            st.download_button("Download paired benchmark JSON", json.dumps(b, ensure_ascii=False, indent=2).encode(),
                               file_name="curaloop-paired-benchmark.json", mime="application/json", key="paired_benchmark_json")

st.divider()
st.caption("Personal research demo · Not an official GPO project · Not validated for wet-lab, GMP or clinical use. "
           f"Code {code_identity()['repo_git_sha'][:12]} · No API keys or paid services required")
