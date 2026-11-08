import { useEffect, useState } from "react";
import { ArrowUpRight, Beaker, Coins, Layers3, Target, ChevronLeft, ChevronRight, RotateCcw, ZoomIn, ZoomOut } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../state";
import { useI18n } from "../i18n";
import { Button } from "../components/ui/button";
import { GoLink, SourceBadge } from "../components/shared";
import { DiscoveryChart } from "../components/charts";
import { policyNames, type Candidate } from "../types";

export default function Overview() {
  const { run, meta } = useApp();
  const { t } = useI18n();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [candidateError, setCandidateError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [index, setIndex] = useState(0);
  const [total, setTotal] = useState<number | null>(null);
  const [zoom, setZoom] = useState(1);
  const [imageError, setImageError] = useState(false);
  useEffect(() => {
    if (!run) return;
    let alive = true;
    setCandidate(null); setCandidateError(false); setLoading(true); setImageError(false);
    api.candidates(run.session_id, { page_size: 1, page: index + 1, status: "eligible" })
      .then((r) => { if (alive) { setCandidate(r.items[0] ?? null); setTotal(r.total); } })
      .catch(() => { if (alive) setCandidateError(true); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [run?.session_id, run?.revision, index]);
  if (!run) return null;
  const scenario = run.report.manifest.scenario_config;
  const historical = run.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA";
  const count = total ?? run.eligible_count;
  const structure = Boolean(candidate?.canonical_smiles && meta?.molecule_rendering && !imageError);
  function move(delta: number) {
    setCandidate(null); setLoading(true); setCandidateError(false); setZoom(1);
    setIndex(value => value + delta);
  }
  const m = run.report.metrics;
  const poolCount = run.eligible_count + run.pending.length + run.report.delivered_results.length + run.report.initial_results.length;
  const stats = [
    { title: "Campaign compounds", value: poolCount, icon: Layers3, note: "Current pool including initial observations" },
    { title: "Experiment budget", value: scenario.budget_units, icon: Coins, note: "Simulated cost units, not currency" },
    { title: "Confirmed new hits", value: m.confirmed_hits, icon: Target, note: "Delivered actives; initial seed hits excluded" },
    { title: "Assays delivered", value: m.delivered_assays, icon: Beaker, note: "Missing outcomes reported separately" },
  ];
  return <>
    <div className="page-heading dashboard-heading">
      <div><span className="eyebrow">{t("Pharmaceutical Research Platform")}</span><h1>{t("Discovery overview")}</h1>
        <p>{t(historical ? "HIV screening" : "Synthetic screening")} · {t("Current campaign")} · {t("Random seed")} {run.report.manifest.seed}</p></div>
      <Button asChild><Link to="/lab">{t("Open simulation lab")}<ArrowUpRight size={16} /></Link></Button>
    </div>
    <div className="discovery-metrics">{stats.map(item => <section className="surface discovery-metric" key={item.title}>
      <div><span>{t(item.title)}</span><item.icon size={17} /></div><strong>{item.value.toLocaleString("en-US")}</strong><p>{t(item.note)}</p>
    </section>)}</div>
    <div className="overview-grid">
      <section className="surface campaign-performance">
        <div className="section-heading"><div><h2>{t("Discovery performance")}</h2><p>{t("Confirmed hits against simulated cost")}</p></div><SourceBadge /></div>
        {m.delivered_assays > 0 ? <DiscoveryChart reports={[run.report]} /> : <div className="performance-empty"><Target size={28} /><h3>{t("Ready for the first discovery")}</h3><p>{t("Confirmed discoveries appear after results are delivered.")}</p><GoLink to="/lab">{t("Open simulation lab")}</GoLink></div>}
        <div className="campaign-summary"><div><span>{t("Selection policy")}</span><strong>{policyNames[run.report.manifest.policy_id]}</strong></div><div><span>{t("In flight")}</span><strong>{m.pending_assays}</strong></div><div><span>{t("Missing outcomes")}</span><strong>{m.missing_assays}</strong></div></div>
      </section>
      <section className="studio-object" aria-label={t("Candidate preview")}>
        <div className="studio-object-heading">
          <strong className="small-mono">{candidate?.compound_id ?? t(loading ? "Loading…" : candidateError ? "Preview unavailable" : "No eligible candidates")}</strong><SourceBadge />
        </div>
        <div className="molecule-viewport" aria-busy={loading}>
          {structure && candidate ? <>
            <div className="molecule-tools" role="group" aria-label={t("Structure view controls")}>
              <span>{t("2D structure")}</span>
              <button type="button" className="icon-button" aria-label={t("Zoom in structure")} disabled={zoom >= 1.8} onClick={() => setZoom(value => Math.min(1.8, Number((value + .2).toFixed(1))))}><ZoomIn size={16} /></button>
              <button type="button" className="icon-button" aria-label={t("Zoom out structure")} disabled={zoom <= 1} onClick={() => setZoom(value => Math.max(1, Number((value - .2).toFixed(1))))}><ZoomOut size={16} /></button>
              <button type="button" className="icon-button" aria-label={t("Reset structure view")} disabled={zoom === 1} onClick={() => setZoom(1)}><RotateCcw size={15} /></button>
            </div>
            <img className="studio-molecule" style={{ transform: `scale(${zoom})` }} src={`/api/v1/runs/${run.session_id}/molecules/${candidate.compound_id}.svg`} alt={t("RDKit 2D molecular structure {id}", { id: candidate.compound_id })} onError={() => setImageError(true)} />
          </> : <div className="studio-descriptors">
            <strong>{loading ? "—" : candidate?.feature_count ?? "—"}</strong>
            <span>{t(loading ? "Loading public candidates…" : candidateError ? "Preview unavailable" : historical ? "Public descriptors" : "Synthetic descriptors")}</span>
            {!loading && <p>{t(historical ? "Structure renderer unavailable; public SMILES remains in details" : "No molecular structure in this synthetic fixture")}</p>}
          </div>}
          <p className="molecule-caption">{t(historical ? "Public structure · Outcome unrevealed" : "Synthetic descriptors · Outcome unrevealed")}</p>
        </div>
        <div className="studio-object-pagination">
          <button type="button" disabled={loading || index === 0} onClick={() => move(-1)}><ChevronLeft size={15} />{t("Previous compound")}</button>
          <span>{candidate ? index + 1 : 0} / {count.toLocaleString("en-US")} {t("eligible")}</span>
          <button type="button" disabled={loading || index + 1 >= count} onClick={() => move(1)}>{t("Next compound")}<ChevronRight size={15} /></button>
        </div>
      </section>
    </div>
    <section className="surface campaign-brief">
      <div><span className="eyebrow">{t("Campaign brief")}</span><h2>{run.report.manifest.dataset.name}</h2><p>{t("Assay / target")}: {historical ? "NCI DTP · HIV" : t("Synthetic binary")}</p></div>
      <div className="brief-budget"><div><strong>{m.remaining_units}</strong><span>{t("available of {budget} simulated units", { budget: scenario.budget_units })}</span></div><div className="studio-budget-track"><span style={{ width: `${100 * m.remaining_units / Math.max(1, scenario.budget_units)}%` }} /></div><p>{t("Spent")} {m.spent_units} · {t("Reserved")} {m.reserved_units}</p></div>
      <div className="brief-actions"><GoLink to="/compounds">{t("Explore compounds")}</GoLink><GoLink to="/benchmarks">{t("Compare policies")}</GoLink><GoLink to="/scenario">{t("Edit scenario")}</GoLink></div>
    </section>
    <p className="studio-provenance">{t(historical ? "Historical labels. Simulated operations. No claims of drug efficacy." : "Synthetic labels and operations. No biological efficacy meaning.")}</p>
    <p className="small muted">{t("Assay outcome stays hidden until requested and delivered.")} <Link to="/evidence">{t("Read methods and limitations")}</Link></p>
  </>;
}
