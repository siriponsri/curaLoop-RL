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
alt.themes.register("curaloop", lambda: {"config": {"font": "CuraThai", "axis": {"labelFont": "CuraThai", "titleFont": "CuraThai"}, "legend": {"labelFont": "CuraThai", "titleFont": "CuraThai"}}})
alt.themes.enable("curaloop")
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

SCREENS = ["Overview · ภาพรวม", "Scenario Setup · ตั้งเงื่อนไข", "Screening Run · จำลองการคัดเลือก",
           "Compare & Export · เปรียบเทียบและส่งออก"]
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
    st.image(str(Path(__file__).resolve().parents[1] / "assets/curaloop-logo.png"), width=230)
    st.caption("PHARMACEUTICAL SCREENING\nDECISION LAB")
    screen = st.radio("Workspace / หน้าทำงาน", SCREENS, key="screen")
    st.divider()
    st.markdown("**" + run.dataset.data_origin + "**")
    st.caption(f"v{__version__} · CPU / Offline\n3 baselines + trained Q-learning / bandit\nTraining source: synthetic tasks")
    st.caption("Personal independent project.\nNot an official GPO system.")

st.markdown('<div class="eyebrow">CURALOOP-RL / RESEARCH WORKBENCH</div>', unsafe_allow_html=True)
st.title(screen.split(" · ")[0])
st.markdown('<div class="provenance">' + ("ข้อมูล assay จริงย้อนหลัง · Historical public assay" if run.dataset.data_origin == "HISTORICAL_PUBLIC_DATA"
            else "ข้อมูลจำลอง · Synthetic demo") + ' | ต้นทุนและเวลาจำลอง | '
            'Retrospective simulator — ยังไม่ใช่ Digital Twin</div>', unsafe_allow_html=True)
st.write("")


def metric_strip(service: RunService) -> None:
    m = service.metrics
    cols = st.columns(4)
    cols[0].metric("พบผล active แล้ว / Confirmed hits", m["confirmed_hits"], help="นับเฉพาะผลใหม่ที่ส่งคืนแล้ว ไม่รวม seed labels")
    cols[1].metric("ผลส่งคืน / Delivered assays", m["delivered_assays"], help="ไม่รวมผลสูญหายและข้อมูลตั้งต้น")
    cols[2].metric("รอผล / Pending", m["pending_assays"])
    cols[3].metric("งบคงเหลือ / Available units", m["remaining_units"], help="งบทั้งหมด − งบจ่ายแล้ว − งบจอง")


def export_controls(reports: list[dict], prefix: str) -> None:
    c1, c2 = st.columns(2)
    c1.download_button("ดาวน์โหลด JSON / Full report", json_report(reports).encode("utf-8"),
                       file_name=f"curaloop-{prefix}.json", mime="application/json", key=prefix + "_json")
    c2.download_button("ดาวน์โหลด CSV / Event report", csv_report(reports).encode("utf-8-sig"),
                       file_name=f"curaloop-{prefix}.csv", mime="text/csv", key=prefix + "_csv")
    st.caption("มี scenario, provenance, algorithm version, event log และ metrics; ไม่มีตารางคำตอบที่ยังไม่เปิดเผย")


def discovery_chart(reports: list[dict]) -> None:
    points = [{**p, "policy": r["manifest"]["policy_id"]} for r in reports for p in r["curve"]]
    if not points:
        st.info("ยังไม่มี event สำหรับแสดงกราฟ")
        return
    chart = alt.Chart(pd.DataFrame(points)).mark_line(interpolate="step-after", point=True).encode(
        x=alt.X("spent_units:Q", title="ต้นทุนที่ชำระแล้ว (simulated cost units)", scale=alt.Scale(zero=True)),
        y=alt.Y("confirmed_hits:Q", title="Confirmed active hits · ผลใหม่ที่ส่งคืนแล้ว", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("policy:N", title="Policy", scale=alt.Scale(domain=list(POLICIES), range=["#64748b", "#087f72", "#b66914", "#6d4da3", "#1976a3"])),
        strokeDash=alt.StrokeDash("policy:N", legend=None), order="event_index:Q",
        tooltip=["policy:N", "spent_units:Q", "confirmed_hits:Q", "step:Q", "pending_assays:Q"],
    ).properties(height=310)
    st.altair_chart(chart, width="stretch")


if screen == SCREENS[0]:
    st.header(f"ถ้าทดสอบได้เพียง {run.scenario.budget_units // run.scenario.assay_cost_units} จาก {run.scenario.candidate_count} ตัว เราจะเริ่มจากตัวไหน?")
    st.markdown("สารแต่ละตัวมีคุณลักษณะที่รู้ล่วงหน้า แต่ผลการทดสอบ (assay) ยังถูกซ่อนไว้ "
                "เราจึงต้องเลือกว่าจะใช้ทรัพยากรทดสอบตัวใดก่อน และปรับการเลือกเมื่อได้รับผลใหม่")
    columns = st.columns(4)
    for col, (title, text) in zip(columns, [
        ("01 · เลือกสาร", "Random สุ่ม / Greedy เลือกคะแนนสูง / Uncertainty เลือกตัวที่โมเดลยังไม่แน่ใจ"),
        ("02 · ส่งทดสอบจำลอง", "จองงบและความจุคิวทันที ระบบไม่ยอมรับการทดสอบซ้ำ"),
        ("03 · รอผลครบกำหนด", "ผล pending ยังไม่เป็น active hit และยังไม่ใช้ฝึกโมเดล"),
        ("04 · เรียนรู้รอบใหม่", "ใช้เฉพาะ seed labels และผลที่ส่งคืนแล้ว เพื่อเลือก batch ถัดไป"),
    ]):
        with col, st.container(border=True):
            st.subheader(title)
            st.write(text)
    metric_strip(run)
    st.button("ลองข้อมูลจริง / Start example demo", type="primary", key="try_demo", on_click=start_example)
    with st.expander("ที่มาของข้อมูลและขอบเขต / Provenance & limits", expanded=True):
        st.write("ข้อมูลหลัก: MoleculeNet HIV จาก NCI DTP / DeepChem เป็นผล assay จริงย้อนหลัง "
                 "ชุดย่อย 1,200 โมเลกุลสุ่มโดยไม่ใช้ label พร้อม Morgan fingerprints 1,024 bits "
                 "และ source hash; TDC ระบุ CC BY 4.0 ส่วนต้นทุนและเวลารอเป็นสมมติฐาน")
        st.write("Seed labels ของข้อมูลจริงสุ่มโดยไม่ดูคำตอบ ทุกนโยบายได้ชุดเดียวกัน "
                 "ถือเป็นข้อมูลเดิมที่จ่ายต้นทุนไปแล้วและไม่นับเป็น hits ใหม่ "
                 "ยังมีข้อมูลสังเคราะห์สองชุดสำหรับตรวจระบบและฝึก controller")
        st.markdown("[MoleculeNet paper](https://doi.org/10.1039/C7SC02664A) · [Dataset & license](https://tdcommons.ai/single_pred_tasks/hts/#hiv)")
        st.write("โครงการส่วนบุคคล ไม่ใช่โครงการทางการขององค์การเภสัชกรรม และไม่ได้รับการรับรองจากหน่วยงาน")
    st.subheader("สถานะการพัฒนา / Evidence status")
    st.dataframe(pd.DataFrame([
        {"Capability": "Offline screening + 3 baseline policies", "Status": "IMPLEMENTED"},
        {"Capability": "Historical HIV replay + scaffold predictor benchmark", "Status": "IMPLEMENTED · custom subset / split"},
        {"Capability": "Bandit / tabular Q-learning", "Status": "TRAINED on synthetic tasks · real-assay evaluation separate"},
        {"Capability": "Live lab / operational Digital Twin", "Status": "NOT AVAILABLE"},
    ]), hide_index=True, width="stretch")

elif screen == SCREENS[1]:
    st.header("กำหนดเงื่อนไขการคัดเลือกสาร")
    st.caption("การกด Apply จะสร้าง run ใหม่และล้างผลเปรียบเทียบเดิม การแก้ในฟอร์มยังไม่เปลี่ยน run ที่กำลังดู")
    if st.button("คืนค่าเริ่มต้น / Restore defaults", key="restore"):
        replace_run(example_scenario(), "greedy")
        for key in list(st.session_state):
            if key.startswith("cfg_"):
                del st.session_state[key]
        st.rerun()
    s = run.scenario
    with st.form("scenario_form"):
        dataset = st.selectbox("Dataset / ชุดข้อมูล", DATASETS, index=DATASETS.index(s.dataset),
                               format_func=lambda x: DATASET_LABELS[x], key="cfg_dataset")
        st.caption("LIT-PCBA ยังไม่เปิดให้ใช้ในเวอร์ชันนี้: ต้องตรวจสิทธิ์ ข้อมูล assay และ preprocessing ก่อน")
        left, right = st.columns(2)
        seed = left.number_input("Random seed", 0, 2**32 - 1, s.seed, key="cfg_seed")
        budget = right.number_input("งบทดสอบจำลอง / Budget units", 0, 240, s.budget_units, key="cfg_budget")
        initial = left.slider("ข้อมูลตั้งต้น / Initial labels", 0, 120, s.initial_count, key="cfg_initial")
        batch = right.slider("ความจุคิว / Batch capacity", 1, 20, s.batch_size, key="cfg_batch")
        delay = left.slider("เวลารอผล / Delay steps", 0, 10, s.delay_steps, key="cfg_delay")
        policy = right.selectbox("Selection policy / วิธีเลือก", POLICIES, index=POLICIES.index(run.policy), key="cfg_policy")
        with st.expander("เงื่อนไขจำลองเพิ่มเติม / Synthetic stress assumptions"):
            cost = st.slider("ต้นทุนต่อ assay / Cost units", 1, 5, s.assay_cost_units, key="cfg_cost")
            jitter = st.slider("เวลารอเพิ่มต่อสาร / Delay jitter steps", 0, 5, s.delay_jitter, key="cfg_jitter")
            missing = st.slider("โอกาสผลสูญหายจำลอง / Missing outcomes (%)", 0, 50, s.missing_percent, key="cfg_missing")
            st.caption("การสูญหายเป็นสมมติฐานเท่านั้น ผลที่สูญหายใช้ต้นทุนและไม่ถูกนับเป็น active หรือ inactive")
        applied = st.form_submit_button("เริ่มการจำลอง / Apply scenario", type="primary", key="apply")
    if applied:
        try:
            scenario = Scenario(dataset=dataset, seed=int(seed), candidate_count=1200 if dataset == "hiv_moleculenet_replay_v1" else 240,
                                initial_count=initial, budget_units=int(budget),
                                batch_size=batch, delay_steps=delay, assay_cost_units=cost,
                                delay_jitter=jitter, missing_percent=missing)
            replace_run(scenario, policy)
            run = st.session_state.run
            st.success("สร้าง run ใหม่แล้ว ไปที่ Screening Run เพื่อส่ง batch แรก")
        except ValueError as exc:
            st.error(str(exc))
    st.json({"active_scenario": asdict(run.scenario), "policy": run.policy}, expanded=False)

elif screen == SCREENS[2]:
    st.header("ดูการตัดสินใจและผลที่เปิดเผยทีละรอบ")
    st.caption(f"{run.policy.upper()} · seed {run.scenario.seed} · simulated step {run.observation.step} · {run.dataset.name}")
    c1, c2, c3, c4 = st.columns(4)
    obs = run.observation
    can_select = bool(obs.slots_available and obs.eligible_candidate_ids and
                      obs.budget_remaining_units >= obs.assay_cost_units and not run.done)
    if c1.button("เลือก batch ถัดไป / Select", type="primary", disabled=not can_select, key="select"):
        try:
            with st.spinner("กำลังคำนวณจากข้อมูลที่เปิดเผยแล้ว…"):
                run.next_batch()
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
    if c2.button("เลื่อนเวลา +1 / Advance", disabled=not run.pending, key="advance"):
        run.advance()
    if c3.button("รันจนจบ / Complete run", disabled=run.done, key="finish"):
        with st.spinner("กำลังรัน campaign จริงบน CPU…"):
            run.finish()
    if c4.button("เริ่มใหม่ / Reset run", key="reset_run"):
        replace_run(run.scenario, run.policy)
        st.rerun()
    metric_strip(run)
    m = run.metrics
    st.caption(f"งบทั้งหมด {run.scenario.budget_units} = ชำระแล้ว {m['spent_units']} + จองรอผล {m['reserved_units']} "
               f"+ คงเหลือ {m['remaining_units']} units · ผลสูญหาย {m['missing_assays']} · seed hits {m['seed_hits']} (ไม่นับใน hits ใหม่)")
    if run.done:
        st.success("การจำลองครบแล้ว: ไม่มีผลค้าง และงบหรือ candidate ที่เลือกได้หมดแล้ว")
    elif run.pending and not can_select:
        st.info("กำลังรอผล: เลื่อนเวลาจำลองเพื่อเปิดเผยผลที่ครบกำหนด")
    elif not run.requests:
        st.info("ยังไม่ได้ทดสอบสารใหม่ กด Select เพื่อเริ่ม batch แรก")
    st.subheader("เหตุผลการเลือก / Actual selection decisions")
    if run.requests:
        rows = [asdict(r) for r in run.requests]
        statuses = {r.request_id: "MISSING" if r.active is None else "DELIVERED" for r in run.results}
        for row in rows:
            row["status"] = statuses.get(row["request_id"], "PENDING")
        st.dataframe(pd.DataFrame(rows)[["compound_id", "status", "scheduled_at_step", "due_at_step",
                                          "cost_units", "predicted_probability", "model_status", "explanation"]],
                     hide_index=True, width="stretch")
    else:
        st.caption("ยังไม่มีการเลือก คะแนนคาดการณ์จะแสดงเฉพาะเมื่อฝึกโมเดลได้")
    lcol, rcol = st.columns(2)
    with lcol:
        st.subheader("คิวรอผล / Pending queue")
        if run.pending:
            st.dataframe(pd.DataFrame([{"compound_id": r.compound_id, "due_at_step": r.due_at_step,
                                         "steps_remaining": r.due_at_step - run.observation.step} for r in run.pending]),
                         hide_index=True, width="stretch")
        else:
            st.caption("ไม่มีผลค้าง")
    with rcol:
        st.subheader("ผลที่เปิดเผยแล้ว / Delivered outcomes")
        if run.results:
            st.dataframe(pd.DataFrame([asdict(r) for r in run.results])[["compound_id", "active", "delivered_at_step", "quality_flag"]],
                         hide_index=True, width="stretch")
        else:
            st.caption("ยังไม่มีผลใหม่ส่งคืน ไม่มี pending ใดนับเป็น hit")
    discovery_chart([run.report()])
    with st.expander("Event timeline / บันทึกเหตุการณ์", expanded=False):
        st.dataframe(pd.DataFrame([asdict(e) for e in run.events])[["event_type", "step", "compound_id", "cost_units", "delivered_active", "explanation"]],
                     hide_index=True, width="stretch")
    with st.expander("ข้อมูลตั้งต้นและ metadata / Seed & evidence"):
        st.dataframe(pd.DataFrame([asdict(r) for r in run.initial_results]), hide_index=True, width="stretch")
        st.json(run.report()["manifest"], expanded=False)

else:
    st.header("เปรียบเทียบวิธีเลือกสารภายใต้เงื่อนไขเดียวกัน")
    st.write("แต่ละนโยบายเริ่มใหม่ด้วย candidate pool, seed labels, features, งบและเงื่อนไขเดียวกัน "
             "ผลจาก run หนึ่งไม่ถูกนำไปใช้โดยอีกนโยบาย")
    st.caption(f"Active scenario: {run.scenario.scenario_id} · seed {run.scenario.seed} · budget {run.scenario.budget_units} · batch {run.scenario.batch_size} · delay {run.scenario.delay_steps}")
    include_learned = st.checkbox("รวม Q-learning และ contextual bandit ที่ฝึกแล้ว", value=True, key="include_learned")
    if st.button("เปรียบเทียบนโยบาย / Compare policies", type="primary", key="compare"):
        with st.spinner("กำลังจำลองทั้งสามนโยบายอย่างอิสระ…"):
            st.session_state.comparison = compare(run.scenario, POLICIES if include_learned else BASELINES)
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
            st.caption("Unseen-state fallback ใช้ Greedy เมื่อ controller ไม่เคยเรียน state นั้น; อย่านับผล fallback เป็นความสำเร็จของ learned strategy")
        queue = [{"policy": r["manifest"]["policy_id"], **p} for r in reports for p in r["curve"]]
        st.altair_chart(alt.Chart(pd.DataFrame(queue)).mark_line(interpolate="step-after").encode(
            x=alt.X("step:Q", title="เวลาจำลอง / Simulated steps"),
            y=alt.Y("pending_assays:Q", title="จำนวน assay ที่รอผล", axis=alt.Axis(tickMinStep=1)),
            color="policy:N", order="event_index:Q", tooltip=["policy:N", "step:Q", "pending_assays:Q"],
        ).properties(height=180), width="stretch")
        st.warning("นี่เป็นการจำลองจาก seed เดียว จึงยังสรุปไม่ได้ว่าวิธีใดเหนือกว่าโดยทั่วไป "
                   "และไม่ใช่หลักฐานฤทธิ์ของยาหรือการประหยัดต้นทุนจริง")
        st.caption("AUC-DB = พื้นที่ใต้กราฟแบบ left-step ถึงงบที่กำหนด หารด้วย budget × floor(budget/cost); "
                   "ไม่นับ seed hits และไม่ใช่ AUROC ของโมเดล")
        export_controls(reports, "comparison")
    else:
        st.info("กดเปรียบเทียบเพื่อสร้างผลจริงและกราฟจาก event log")
    with st.expander("ส่งออก run ที่กำลังดู / Current run (including partial)", expanded=not bool(reports)):
        export_controls([run.report()], "current-run")
    with st.expander("กลับมาทำต่อจาก JSON / Resume a public snapshot"):
        upload = st.file_uploader("ไฟล์ CuraLoop JSON เท่านั้น / Max 10 MB", type=["json"], key="resume_upload")
        if st.button("ตรวจและกลับมาทำต่อ / Validate & resume", disabled=upload is None, key="resume"):
            try:
                if upload.size > 10_000_000:
                    raise ValueError("File exceeds 10 MB.")
                payload = json.loads(upload.getvalue().decode("utf-8-sig"))
                if len(payload["runs"]) != 1:
                    raise ValueError("Resume accepts one current-run report, not a comparison export.")
                restored = RunService.restore(payload["runs"][0])
                st.session_state.run = restored
                st.session_state.comparison = None
                st.success("ตรวจ event log สำเร็จ กลับไป Screening Run เพื่อทำต่อได้")
            except (ValueError, KeyError, TypeError) as exc:
                st.error(f"ไม่สามารถกลับมาทำต่อได้: {exc}")
    with st.expander("ข้อจำกัด / Scientific limitations"):
        for limitation in LIMITATIONS:
            st.write("• " + limitation)
    with st.expander("Learning Lab / ตรวจ controller ที่ฝึกแล้ว"):
        from curaloop.learning import load_checkpoint
        for name in ("q_learning", "contextual_bandit"):
            cp = load_checkpoint(name)
            st.write(f"**{name}** · {cp['status']} · {cp['training_episodes']} episodes · synthetic training only")
            st.caption(f"Checkpoint SHA256 {cp['checkpoint_sha256']}")
            st.line_chart(pd.DataFrame({"training_return": cp["episode_returns"]}), height=160)
        st.caption("Training curves มาจาก reward ที่บันทึกจริง ไม่ใช่ผล validation หรือหลักฐานว่ายาได้ผล")
    with st.expander("Benchmark Lab / Paired seeds และ scaffold audit"):
        evidence_path = Path(__file__).resolve().parents[1] / "docs/evidence/hiv-benchmark/summary.json"
        if evidence_path.exists():
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            st.write("**ผล benchmark ที่บันทึกไว้ / Recorded evidence**")
            st.caption("HIV subset 1200 molecules · 10 seeds · budget 30 · initial labels 48 · custom replay ไม่ใช่ leaderboard")
            st.dataframe(pd.DataFrame(evidence["statistics"]["summary"]), hide_index=True, width="stretch")
            predictor = evidence["predictor_benchmark"]
            st.write(f"Scaffold audit: train {predictor['train_count']} / test {predictor['test_count']} · overlap {predictor['scaffold_overlap']}")
            st.write({k: predictor[k] for k in ("auroc", "average_precision", "brier_score", "test_prevalence")})
            st.caption("ผล predictor audit ไม่ได้ถูกใช้ฝึก policy และใช้ split ของโครงการนี้ ผลนี้ไม่ใช่การยืนยันประสิทธิผลของยา")
        seed_count = st.number_input("จำนวน paired seeds สำหรับรันใหม่ / Seed count", 2, 20, 5, key="benchmark_seed_count")
        st.caption("ใช้ active scenario ปัจจุบันและ seeds 0..N−1 ทั้ง 5 policies; อาจใช้เวลาหลายนาทีบน CPU")
        if st.button("รัน benchmark ใหม่จริง / Run paired benchmark", key="run_benchmark"):
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
            st.download_button("ดาวน์โหลด paired benchmark JSON", json.dumps(b, ensure_ascii=False, indent=2).encode(),
                               file_name="curaloop-paired-benchmark.json", mime="application/json", key="paired_benchmark_json")

st.divider()
st.caption("Personal research demo · Not an official GPO project · Not validated for wet-lab, GMP or clinical use. "
           f"Code {code_identity()['repo_git_sha'][:12]} · ไม่มี API key หรือบริการเสียเงิน")
