import { useEffect, useRef, useState } from "react";
import { ArrowDownToLine, ArrowUpRight, CheckCheck, FileCheck2, ShieldCheck } from "lucide-react";
import { api } from "../api";
import { Button } from "../components/ui/button";
import { useI18n } from "../i18n";
import { confirmationExport, operatorNames, rankerNames, type ConfirmationArm, type ConfirmationStudy } from "../confirmation";
import "../confirmation.css";

const fmt = (n: number) => n.toLocaleString("en-US", { maximumFractionDigits: 2 });

function TradeoffChart({ arms, selected, onSelect }: { arms: ConfirmationArm[]; selected: string; onSelect: (arm: ConfirmationArm) => void }) {
  const { t } = useI18n();
  const max = Math.max(1, ...arms.flatMap(a => [a.metrics.confirmed_positives.max, a.metrics.positive_structure_groups.max]));
  const upper = Math.ceil(max / 5) * 5;
  const x = (v: number) => 80 + 370 * v / upper;
  const y = (v: number) => 450 - 370 * v / upper;
  return <svg className="cf-tradeoff" viewBox="0 0 560 540" role="group" aria-label={t("Hits and chemotype coverage; every point is a historical arm")}>
    {[0, 1, 2, 3, 4].map(i => <g key={i}><line x1="80" x2="450" y1={y(upper * i / 4)} y2={y(upper * i / 4)} stroke="#e6e1db" />
      <text x="65" y={y(upper * i / 4) + 4} textAnchor="end">{fmt(upper * i / 4)}</text><text x={x(upper * i / 4)} y="478" textAnchor="middle">{fmt(upper * i / 4)}</text></g>)}
    <line x1="80" y1="450" x2="450" y2="450" stroke="#867f78" /><line x1="80" y1="80" x2="80" y2="450" stroke="#867f78" />
    <text x="265" y="520" textAnchor="middle">{t("Confirmed positives (H)")}</text><text x="80" y="45">{t("Positive structure groups (D)")}</text>
    {arms.map(a => {
      const key = a.ranker + "/" + a.operator;
      const px = x(a.metrics.confirmed_positives.mean), py = y(a.metrics.positive_structure_groups.mean);
      const colour = selected.startsWith(a.ranker + "/") ? "#a6492d" : "#898681";
      const label = `${t(rankerNames[a.ranker])} · ${t(operatorNames[a.operator])} · H ${fmt(a.metrics.confirmed_positives.mean)} · D ${fmt(a.metrics.positive_structure_groups.mean)}`;
      return <g key={key} role="button" tabIndex={0} aria-label={label} aria-pressed={selected === key} onClick={() => onSelect(a)} onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(a); } }} className="cf-chart-point">
        <title>{label}</title><line x1={x(a.metrics.confirmed_positives.min)} x2={x(a.metrics.confirmed_positives.max)} y1={py} y2={py} stroke={colour} opacity=".65" />
        <line x1={px} x2={px} y1={y(a.metrics.positive_structure_groups.min)} y2={y(a.metrics.positive_structure_groups.max)} stroke={colour} opacity=".65" />
        {selected === key && <circle cx={px} cy={py} r="10" fill="none" stroke={colour} strokeWidth="2" />}
        {a.operator === "cluster_round_robin" ? <path d={`M${px} ${py - 5}l5 9h-10z`} fill={colour} stroke="white" /> : a.operator === "classical_max_min" ? <rect x={px - 4} y={py - 4} width="8" height="8" fill={colour} stroke="white" /> : <circle cx={px} cy={py} r="4.5" fill={colour} stroke="white" />}
      </g>;
    })}
  </svg>;
}

export default function Confirmation() {
  const { t, locale } = useI18n();
  const [campaign, setCampaign] = useState("equal"), [budget, setBudget] = useState(10);
  const [ranker, setRanker] = useState("mvsa"), [operator, setOperator] = useState("top_ranked");
  const [data, setData] = useState<ConfirmationStudy | null>(null), [error, setError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);
  const filterFocus = useRef<string | null>(null);
  useEffect(() => {
    let live = true;
    setData(null); setError(null);
    api.confirmation(campaign, budget).then(value => { if (live) setData(value); }).catch(err => { if (live) setError((err as Error).message); });
    return () => { live = false; };
  }, [campaign, budget, reload]);
  useEffect(() => {
    if (data && filterFocus.current) {
      document.getElementById(filterFocus.current)?.focus();
      filterFocus.current = null;
    }
  }, [data]);
  const selected = data?.arms.find(a => a.ranker === ranker && a.operator === operator);
  function selectArm(arm: ConfirmationArm) { setRanker(arm.ranker); setOperator(arm.operator); }
  return <div className="cf-workspace">
    <header className="cf-heading"><div><span className="eyebrow">{t("Recorded study / CF1")}</span><h1>{t("Confirmation evidence")}</h1><p>{t("Choose what to confirm. See what each tradeoff costs in hits.")}</p></div><span className="cf-status"><FileCheck2 size={15} />{t("Development study complete")}</span></header>
    <div className="cf-scope"><ShieldCheck size={18} /><p>{t("Historical primary-to-confirmation evidence. Opening this study does not start an experiment or change your campaign.")}</p></div>
    {error ? <section className="surface cf-unavailable" role="alert"><h2>{t("Confirmation evidence unavailable")}</h2><p>{t("Source verification failed or the study could not be loaded. No replacement values are shown.")}</p><p>{t("Original diagnostic")}: {error}</p><Button onClick={() => setReload(v => v + 1)}>{t("Retry study")}</Button></section> : !data ? <section className="surface loading-panel" role="status">{t("Verifying recorded evidence…")}</section> : <>
      <p className="field-note">{t("Full recorded study; these totals do not change with the comparison filters.")}</p>
      <section className="cf-study-stats" aria-label={t("Study scope")}>
        {[{ n: data.campaigns.length, label: "Campaigns", note: "Exposed development campaigns" }, { n: data.universe_observations, label: "Supported confirmations", note: "Historical assay-specific observations" }, { n: 18, label: "Historical arms", note: "Six rankers × three operators" }].map(s => <div className="surface" key={s.label}><span>{t(s.label)}</span><strong>{fmt(s.n)}</strong><small>{t(s.note)}</small></div>)}
      </section>
      <section className="surface cf-controls" aria-label={t("Study filters")}>
        <label htmlFor="cf-campaign">{t("Study campaign")}<select id="cf-campaign" value={campaign} onChange={e => { filterFocus.current = "cf-campaign"; setCampaign(e.target.value); }}><option value="equal">{t("Equal-campaign mean · six campaigns")}</option>{data.campaigns.map(c => <option key={c.campaign} value={c.campaign}>AID {c.campaign}</option>)}</select></label>
        <label htmlFor="cf-budget">{t("Confirmation budget")}<select id="cf-budget" value={budget} onChange={e => { filterFocus.current = "cf-budget"; setBudget(Number(e.target.value)); }}>{data.budgets.map(b => <option key={b} value={b}>{b}% {t("of supported universe")}</option>)}</select></label>
        <div className="cf-filter-note"><CheckCheck size={16} /><span>{t("Recorded results only")}<small>{t("Five fixed seeds; no model rerun")}</small></span></div>
      </section>
      <div className="cf-analysis-grid"><section className="surface cf-chart-panel"><div className="section-heading"><div><h2>{t("The hit–coverage tradeoff")}</h2><p>{t("Select a point or a table row to inspect an arm.")}</p></div><span className="small-mono">H / D</span></div>
        <TradeoffChart arms={data.arms} selected={ranker + "/" + operator} onSelect={selectArm} />
        <div className="cf-legend"><span><i style={{ background: "#a6492d" }} />{t("Selected ranker")}: {t(rankerNames[ranker])}</span><span><i style={{ background: "#898681" }} />{t("Other rankers")}</span></div>
        <p className="field-note">{t("Circle: top ranked · triangle: round-robin · square: max-min. Whiskers show observed seed ranges.")}</p>
      </section><section className="surface cf-arm-detail" aria-live="polite"><span className="eyebrow">{t("Selected historical arm")}</span><h2>{t(rankerNames[ranker])}</h2><p>{t(operatorNames[operator])}</p>
        {selected && <><div className="cf-primary-pair"><div><span>{t("Confirmed positives (H)")}</span><strong>{fmt(selected.metrics.confirmed_positives.mean)}</strong></div><div><span>{t("Positive structure groups (D)")}</span><strong>{fmt(selected.metrics.positive_structure_groups.mean)}</strong></div></div>
          <dl className="cf-detail-list"><div><dt>{t("Fingerprint groups D(FP)")}</dt><dd>{fmt(selected.metrics.positive_fingerprint_groups.mean)}</dd></div><div><dt>{t(campaign === "equal" ? "Mean confirmations (B)" : "Confirmations (B)")}</dt><dd>{fmt(selected.metrics.confirmation_count.mean)}</dd></div><div><dt>H / B</dt><dd>{fmt(100 * selected.metrics.hits_per_confirmation.mean)}%</dd></div><div><dt>D / B</dt><dd>{fmt(100 * selected.metrics.groups_per_confirmation.mean)}%</dd></div></dl>
          <p className="field-note">{t("Ratios describe historical counts per confirmation, not financial or clinical value.")}</p></>}
        <Button asChild variant="outline"><a href={confirmationExport(campaign, budget, ranker, operator, locale)} download><ArrowDownToLine size={16} />{t("Export comparison brief")}</a></Button><small className="cf-export-note">{t("JSON with filters, all arms, limitations and source hashes. Local download only.")}</small>
      </section></div>
      <section className="surface cf-table-section" data-cf-campaign={data.campaign} data-cf-budget={data.budget_percent}><div className="section-heading"><div><h2>{t("All 18 comparisons")}</h2><p>{t("Mean [observed seed range]. Unfavorable outcomes remain visible.")}</p></div></div>
        <p className="field-note">{t("On narrow screens, scroll the table horizontally to see every metric.")}</p>
        <div className="table-scroll" role="region" tabIndex={0} aria-label={t("Confirmation comparison table")}><table><thead><tr><th>{t("Ranker / operator")}</th><th>H</th><th>D</th><th>D(FP)</th><th>H / B</th><th>D / B</th></tr></thead><tbody>{data.arms.map(a => <tr key={a.ranker + a.operator} className={ranker === a.ranker && operator === a.operator ? "cf-selected-row" : ""}><th scope="row"><button type="button" onClick={() => selectArm(a)} aria-label={t(rankerNames[a.ranker]) + " · " + t(operatorNames[a.operator])} data-ranker={a.ranker} data-operator={a.operator} aria-pressed={ranker === a.ranker && operator === a.operator}>{t(rankerNames[a.ranker])}<small>{t(operatorNames[a.operator])}</small></button></th>{(["confirmed_positives", "positive_structure_groups", "positive_fingerprint_groups"] as const).map(m => <td key={m}>{fmt(a.metrics[m].mean)}<small>[{fmt(a.metrics[m].min)}, {fmt(a.metrics[m].max)}]</small></td>)}<td>{fmt(100 * a.metrics.hits_per_confirmation.mean)}%</td><td>{fmt(100 * a.metrics.groups_per_confirmation.mean)}%</td></tr>)}</tbody></table></div>
      </section>
      <section className="surface cf-interpretation"><h2>{t("What this study supports")}</h2><p>{t("A classical coverage–hit tradeoff is established here. A novel selector and independent confirmation benefit are not established.")}</p><ul>{data.limitations.map(note => <li key={note}>{t(note)}</li>)}</ul></section>
      <details className="surface cf-provenance"><summary>{t("Source provenance and exact budgets")}</summary><p>{t(data.aggregation)}</p><div className="table-scroll"><table><thead><tr><th>{t("Campaign")}</th><th>{t("Supported universe")}</th><th>{t("Confirmations (B)")}</th></tr></thead><tbody>{data.campaigns.map(c => <tr key={c.campaign}><th>AID {c.campaign}</th><td>{fmt(c.universe_size)}</td><td>{c.budgets[data.budgets.indexOf(budget)]}</td></tr>)}</tbody></table></div><p>{t("Paper and pinned source")}: <a href={data.paper_url} target="_blank" rel="noreferrer">MVS-A <ArrowUpRight size={13} /></a> · <a href={data.source_url} target="_blank" rel="noreferrer">AIC_Finder</a></p>{data.source_hashes.map(s => <div className="cf-hash" key={s.path}><span>{s.path}</span><code>{s.sha256}</code></div>)}</details>
    </>}
  </div>;
}
