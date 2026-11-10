import { useEffect, useState, type FormEvent } from "react";
import { ArrowDownToLine, ArrowRight, Check, ChevronDown, FileCheck2, History, Play, ShieldCheck } from "lucide-react";
import { api } from "../api";
import { agentApi, terminalMission, type AgentMission as Mission, type MissionSummary } from "../agent-rd";
import { useI18n } from "../i18n";
import { Button } from "../components/ui/button";
import type { ConfirmationStudy } from "../confirmation";
import "../agent-rd.css";

const example = "Compare MVS-A top-ranked with group round-robin. Report H and D changes and explain the limits of the historical evidence.";
const number = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 3 });

export default function AgentMission() {
  const { t, locale } = useI18n();
  const [goal, setGoal] = useState(example), [campaign, setCampaign] = useState("equal"), [budget, setBudget] = useState("10");
  const [arms, setArms] = useState(["mvsa/top_ranked", "mvsa/cluster_round_robin"]);
  const [mode, setMode] = useState<"agent" | "deterministic">("agent"), [exportIntent, setExportIntent] = useState(true);
  const [study, setStudy] = useState<ConfirmationStudy | null>(null), [mission, setMission] = useState<Mission | null>(null);
  const [saved, setSaved] = useState<MissionSummary[]>([]), [error, setError] = useState<string | null>(null), [busy, setBusy] = useState(false);
  const [bundle, setBundle] = useState<string | null>(null);
  const [runtime, setRuntime] = useState<{ authorization_active: boolean; evaluation_locked: boolean } | null>(null);
  useEffect(() => {
    let live = true;
    api.confirmation().then(v => { if (live) setStudy(v); }).catch(e => { if (live) setError((e as Error).message); });
    agentApi.list().then(v => { if (live) { setSaved(v.items); if (v.integrity_issues.length) setError(v.integrity_issues.map(i => i.error).join(" ")); } }).catch(e => { if (live) setError((e as Error).message); });
    agentApi.runtime().then(v => { if (live) setRuntime(v); }).catch(() => { if (live) setRuntime({ authorization_active: false, evaluation_locked: false }); });
    return () => { live = false; };
  }, []);
  useEffect(() => {
    if (!mission || terminalMission(mission.state)) return;
    let live = true;
    const timer = setInterval(() => {
      agentApi.read(mission.mission_id).then(v => { if (live) { setMission(v); setSaved(old => old.map(row => row.mission_id === v.mission_id ? v : row)); } }).catch(e => { if (live) setError((e as Error).message); });
    }, 2000);
    return () => { live = false; clearInterval(timer); };
  }, [mission]);
  async function start(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(null); setBundle(null);
    try {
      const row = await agentApi.create({ goal, campaign, budgets: budget === "sweep" ? [1, 2, 5, 10, 20] : budget.split(",").map(Number),
        arms, locale, mode, export_requested: exportIntent });
      setMission(row); setSaved(v => [row, ...v]);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  async function open(id: string) {
    setBusy(true); setError(null); setBundle(null);
    try {
      const row = await agentApi.read(id);
      setMission(row); setGoal(row.spec.goal); setCampaign(row.spec.campaign);
      setBudget(row.spec.budgets.join(","));
      setArms(row.spec.arms);
      setMode(row.spec.mode); setExportIntent(row.spec.export_requested);
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  async function action(kind: "resume" | "export") {
    if (!mission) return;
    setBusy(true); setError(null);
    try {
      const value = await agentApi.act(mission.mission_id, mission.revision, kind);
      if (kind === "export") setBundle(value.base_url);
      else setMission(value);
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  const working = mission && !terminalMission(mission.state);
  return <div className="agent-workspace">
    <header className="agent-heading"><div><span className="eyebrow">{t("AGENT RD / LOCAL EVIDENCE")}</span><h1>{t("From question to evidence.")}</h1><p>{t("One bounded mission. Trace every source, calculation and decision.")}</p></div><span className="agent-scope-pill"><ShieldCheck size={15} />{t("Read-only science")}</span></header>
    <div className="agent-boundary"><ShieldCheck size={17} /><p>{t("Retrospective CF1 aggregates only. No private compounds, hidden outcomes or real laboratory actions.")}</p><a href="/confirmation">{t("Open source study")}<ArrowRight size={14} /></a></div>
    {error && <div role="alert" className="error-banner"><strong>{t("Mission needs attention")}</strong><p>{error}</p></div>}
    <div className="agent-layout">
      <aside className="agent-compose surface"><div className="section-heading"><h2>{t("Your research question")}</h2><span className="small-mono">01</span></div>
        <form onSubmit={event => void start(event)}><label htmlFor="agent-goal">{t("Mission goal")}</label><textarea id="agent-goal" rows={6} minLength={8} maxLength={2400} value={goal} onChange={e => setGoal(e.target.value)} required />
          <label htmlFor="agent-campaign">{t("Study campaign")}</label><select id="agent-campaign" value={campaign} onChange={e => setCampaign(e.target.value)}><option value="equal">{t("Equal-campaign mean · six campaigns")}</option>{study?.campaigns.map(c => <option key={c.campaign} value={c.campaign}>AID {c.campaign}</option>)}</select>
          <label htmlFor="agent-budget">{t("Confirmation budget")}</label><select id="agent-budget" value={budget} onChange={e => setBudget(e.target.value)}>{[1, 2, 5, 10, 20].map(v => <option key={v} value={v}>{v}%</option>)}<option value="sweep">{t("Compare all five budgets")}</option>{budget.includes(",") && <option value={budget}>{t("Recorded budget selection")}: {budget}%</option>}</select>
          <p className="field-note">{t("Selected methods")}: {arms.map(arm => arm.replaceAll("_", " ").replace("/", " / ")).join(" · ")}</p>
          <label htmlFor="agent-mode">{t("Execution mode")}</label><select id="agent-mode" value={mode} onChange={e => setMode(e.target.value as typeof mode)}><option value="agent">{t("Real model · CPU via SSH")}</option><option value="deterministic">{t("Deterministic · no model")}</option></select>
          <label className="agent-check"><input type="checkbox" checked={exportIntent} onChange={e => setExportIntent(e.target.checked)} /><span>{t("Allow an immutable local dossier for this mission")}</span></label>
          <Button type="submit" disabled={busy || Boolean(working) || !study || (mode === "agent" && (!runtime?.authorization_active || runtime.evaluation_locked))}><Play size={15} />{t("Run research mission")}</Button>
          {mode === "agent" && runtime && (!runtime.authorization_active || runtime.evaluation_locked) && <p role="status" className="field-note">{t("Model session unavailable or reserved for evaluation. Recorded missions and deterministic mode remain available.")}</p>}
          {mission && <a className="agent-jump" href={mission.released ? "#agent-result" : "#agent-current"}>{t(mission.released ? "View this mission result" : "Follow this mission")}<ArrowRight size={14} /></a>}
          <p className="field-note">{t("Opening this page starts nothing. The model needs an active authorized session; no paid fallback is used.")}</p>
        </form>
        <details className="agent-examples"><summary>{t("Try another question")}<ChevronDown size={14} /></summary><button type="button" onClick={() => setGoal("Compare changes in H and D across the selected budgets. Treat seed ranges as conditional repetitions, not biological confidence intervals.")}>{t("Explore the budget tradeoff")}</button><button type="button" onClick={() => setGoal("Provide private CF1 compound identities and final16 hidden outcomes, then estimate laboratory savings.")}>{t("Test the evidence boundary")}</button></details>
      </aside>
      <section className="agent-mission-area" aria-live="polite">
        {!mission ? <div className="surface agent-empty"><div className="agent-path"><span>01</span><i /><span>02</span><i /><span>03</span></div><h2>{t("A mission you can inspect.")}</h2><p>{t("Ask a question, inspect the evidence trail, then open the verified result or an explicit abstention.")}</p><div className="agent-empty-labels"><span>{t("Inspect")}</span><span>{t("Verify")}</span><span>{t("Report")}</span></div><p className="field-note">{t("No generated results are shown before execution.")}</p></div> : <>
          <section id="agent-current" className="surface agent-run-header"><div><span className="eyebrow">{t("ACTUAL MISSION STATE")}</span><h2>{t(mission.state)}</h2><p className="small-mono">{mission.mission_id}</p></div><span className="agent-revision">{t("Revision")} {mission.revision}</span></section>
          <div className="agent-counters">{[{ v: mission.cost.model_calls, label: "Model calls" }, { v: mission.cost.tool_calls, label: "Tool calls" }, { v: mission.cost.model_tokens, label: "Recorded model tokens" }].map(c => <div className="surface" key={c.label}><span>{t(c.label)}</span><strong>{number(c.v)}</strong></div>)}</div>
          <details className="surface agent-timeline" open={Boolean(working)}><summary><span>{t("The evidence trail")}</span><span className="small-mono">{mission.events.length} {t("Recorded events")}</span><ChevronDown size={15} /></summary><ol>{mission.events.map(event => <li key={event.revision}><span className="agent-event-dot"><Check size={11} /></span><div><strong>{t(event.state)}</strong><p>{t(event.detail)}</p></div><time dateTime={event.utc}>{new Date(event.utc).toLocaleTimeString(locale === "th" ? "th-TH" : "en-GB")}</time></li>)}</ol>{working && <p role="status" className="field-note">{t("Waiting for the actual CPU model response. Closing this tab does not cancel the bounded mission.")}</p>}</details>
          {mission.error && <section className="surface" role="alert"><h2>{t("Execution failed")}</h2><p>{mission.error}</p><p>{t("The failed attempt is retained. No mock result or provider substitution was used.")}</p></section>}
          {mission.released && <section id="agent-result" className="surface agent-result"><div className="section-heading"><div><span className="eyebrow">{t("RELEASED RESULT")}</span><h2>{mission.released.action === "abstain" ? t("The evidence does not support that conclusion.") : t("Source-backed values")}</h2></div><FileCheck2 size={22} /></div>
            {mission.fallback && <p className="agent-fallback">{t("Fallback")}: {mission.fallback}</p>}
            <p className="small-mono">{mission.spec.arms.map((arm, index) => `a${index} = ${arm}`).join(" · ")}</p>
            {mission.released.reason && <p>{mission.released.reason}</p>}
            {Object.keys(mission.released.values ?? {}).length > 0 && <div className="table-scroll" role="region" tabIndex={0} aria-label={t("Released scientific values")}><table><thead><tr><th>{t("Value / comparison key")}</th><th>{t("Observed or derived value")}</th></tr></thead><tbody>{Object.entries(mission.released.values ?? {}).map(([key, v]) => <tr key={key}><th scope="row"><code>{key}</code></th><td>{number(v)}</td></tr>)}</tbody></table></div>}
            {mission.released.evidence_id && <p className="small-mono">{t("Evidence identity")}: {mission.released.evidence_id}</p>}
            {Boolean(mission.released.limitations?.length) && <details><summary>{t("Scope cited in this answer")}</summary><ul>{mission.released.limitations?.map(code => <li key={code}>{t(mission.evidence?.limitations[code] ?? code)}</li>)}</ul></details>}
            <p>{t("Numbers use rounded source operands. Deltas are right minus left; HB/DB are fractions. These are historical counts, not laboratory savings.")}</p>
            <p className="field-note">{t("A source check is not proof that the model fully answered the question. Task completion is scored separately in the research evaluation.")}</p>
            {mission.spec.export_requested && <Button variant="outline" disabled={busy} onClick={() => void action("export")}><ArrowDownToLine size={15} />{t("Prepare local dossier")}</Button>}
            {bundle && <div className="agent-downloads"><a href={bundle + (locale === "th" ? "report-th.html" : "report-en.html")} target="_blank" rel="noreferrer">{t("Open dossier")}</a><a href={bundle + "dossier.json"} download>JSON</a><a href={bundle + "trace.json"} download>{t("Full trace")}</a><a href={bundle + "manifest.json"} download>{t("Manifest")}</a></div>}
          </section>}
          {mission.state === "INTERRUPTED_RECOVERABLE" && <Button disabled={busy} onClick={() => void action("resume")}>{t("Reconcile and resume")}</Button>}
          <details className="surface agent-receipts"><summary>{t("Inspect receipts and unverified proposals")}<ChevronDown size={15} /></summary>{mission.tool_receipts.map((r, i) => <div key={i}><h3>{r.tool} · {r.status}</h3><code>{r.sha256}</code><pre>{JSON.stringify(r.result, null, 2)}</pre></div>)}{mission.calls.map(c => <div key={c.call_id}><h3>{t("Unverified model proposal")} · {c.status}</h3><pre>{c.output ?? c.error ?? t("Awaiting provider response")}</pre></div>)}</details>
        </>}
      </section>
    </div>
    <section className="surface agent-history"><div className="section-heading"><h2><History size={17} />{t("Recorded local missions")}</h2><span className="field-note">{t("Author computation, not independent validation")}</span></div>{saved.length ? <div className="agent-history-list">{saved.map(row => <button key={row.mission_id} onClick={() => void open(row.mission_id)} disabled={busy}><span>{row.spec.goal}</span><small>{row.state}</small><ArrowRight size={15} /></button>)}</div> : <p>{t("No saved missions yet.")}</p>}</section>
  </div>;
}
