import { useEffect, useState } from "react";
import { ArrowUpRight, ChevronLeft, ChevronRight, RotateCcw, ZoomIn, ZoomOut } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../state";
import { useI18n } from "../i18n";
import { Button } from "../components/ui/button";
import { GoLink, SourceBadge, Workflow } from "../components/shared";
import { RecordedBenchmarkChart } from "../components/charts";
import { policyNames, type Candidate } from "../types";

export default function Overview() {
  const { run, evidence, meta } = useApp();
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
  return <>
    <div className="page-heading studio-heading">
      <div><h1>{t(historical ? "HIV screening" : "Synthetic screening")}</h1>
        <p>{t("Current campaign")} <span className="studio-heading-detail">· {policyNames[run.report.manifest.policy_id]} · {t("Random seed")} {run.report.manifest.seed}</span></p></div>
      <Button asChild><Link to="/lab">{t("Open simulation lab")}<ArrowUpRight size={16} /></Link></Button>
    </div>
    <div className="molecular-studio">
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
      <aside className="studio-inspector">
        <h2>{t("Candidate record")}</h2>
        <dl className="studio-facts">
          <div><dt>{t("Assay / target")}</dt><dd>{historical ? "NCI DTP · HIV" : t("Synthetic binary")}</dd></div>
          <div><dt>{t("Representation")}</dt><dd>{t(historical ? "Morgan fingerprint" : "Synthetic descriptors")}</dd></div>
          <div><dt>{t("Selection policy")}</dt><dd>{policyNames[run.report.manifest.policy_id]}</dd></div>
        </dl>
        <p className="studio-outcome-note">{t("Assay outcome stays hidden until requested and delivered.")}</p>
        <div className="studio-budget"><span>{t("Budget available")}</span>
          <div><strong>{run.report.metrics.remaining_units}</strong><small> / {scenario.budget_units} {t("simulated units")}</small></div>
          <div className="studio-budget-track" role="img" aria-label={t("Budget available") + ": " + run.report.metrics.remaining_units}><span style={{ width: `${100 * run.report.metrics.remaining_units / Math.max(1, scenario.budget_units)}%` }} /></div>
          <p>{t("Spent")} {run.report.metrics.spent_units} · {t("Reserved")} {run.report.metrics.reserved_units}</p>
          <p>{t("Confirmed new hits")}: {run.report.metrics.confirmed_hits}</p>
        </div>
        <details className="studio-source-detail"><summary>{t("Campaign details")}</summary><dl>
          <dt>{t("Dataset")}</dt><dd>{run.report.manifest.dataset.name}</dd>
          <dt>{t("Session")}</dt><dd>{run.session_id}</dd>
          {candidate?.canonical_smiles && <><dt>Canonical SMILES</dt><dd>{candidate.canonical_smiles}</dd></>}
        </dl><GoLink to="/scenario">{t("Edit scenario")}</GoLink></details>
      </aside>
    </div>
    <section className="studio-workflow" aria-label={t("Screening workflow")}><Workflow run={run} /></section>
    <p className="studio-provenance">{t(historical ? "Historical labels. Simulated operations. No claims of drug efficacy." : "Synthetic labels and operations. No biological efficacy meaning.")}</p>
    <details className="recorded-evidence">
      <summary>{t("Recorded benchmark and limitations")}</summary><p className="muted">{t("Recorded HIV benchmark · 10 paired seeds · B = 30")}</p>
      {evidence && <RecordedBenchmarkChart rows={evidence.statistics.summary} />}
      <p className="honesty-note">{t("The learned controllers matched Greedy because all 300/300 historical requests used their Greedy fallback. This is not successful learned transfer.")}</p>
      <GoLink to="/evidence">{t("Read methods and limitations")}</GoLink>
    </details>
  </>;
}
