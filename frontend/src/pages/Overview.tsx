import { useEffect, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Database,
  GitBranch,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../state";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { GoLink, KpiStrip, SourceBadge, Workflow } from "../components/shared";
import { RecordedBenchmarkChart } from "../components/charts";
import { short } from "../lib";
import type { Candidate } from "../types";

export default function Overview() {
  const { run, evidence, meta } = useApp();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [candidateError, setCandidateError] = useState(false);
  useEffect(() => {
    if (!run) return;
    let alive = true;
    setCandidate(null);
    setCandidateError(false);
    api
      .candidates(run.session_id, { page_size: 1 })
      .then((r) => {
        if (alive) setCandidate(r.items[0] ?? null);
      })
      .catch(() => { if (alive) setCandidateError(true); });
    return () => {
      alive = false;
    };
  }, [run?.session_id]);
  if (!run) return null;
  const scenario = run.report.manifest.scenario_config;
  const historical =
    run.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA";
  return (
    <>
      <div className="mission-hero">
        <div className="mission-copy">
          <div className="hero-badges">
            <SourceBadge />
            <Badge>Personal research portfolio</Badge>
          </div>
          <h1>
            {"Every assay is a decision."}
            <br />
            <span>{"Make yours reproducible."}</span>
          </h1>
          <p>
            {(`A library of ${scenario.candidate_count.toLocaleString()} candidates. A budget of ${scenario.budget_units} simulated cost units. Which compounds should we test first—and what changes when results arrive?`)}
          </p>
          <div className="hero-actions">
            <Button asChild>
              <Link to="/lab">
                {"Enter simulation lab"}
                <ArrowRight size={17} />
              </Link>
            </Button>
            <Button asChild variant="ghost">
              <Link to="/scenario">
                {"Design a scenario"}
                <ArrowUpRight size={16} />
              </Link>
            </Button>
          </div>
          <div className="hero-footnote">
            <ShieldCheck size={15} />
            {historical
              ? "Historical labels. Simulated operations. No claims of drug efficacy."
              : "Synthetic labels and operations. No biological efficacy meaning."}
          </div>
        </div>
        <div className="hero-specimen">
          <div className="specimen-header">
            <span>
              {"From the public candidate pool"}
            </span>
            <span className="small-mono">
              {candidate?.compound_id ?? (candidateError ? "Preview unavailable" : "Loading…")}
            </span>
          </div>
          {candidate?.canonical_smiles && meta?.molecule_rendering ? (
            <img
              className="specimen-image"
              src={`/api/v1/runs/${run.session_id}/molecules/${candidate.compound_id}.svg`}
              alt={`RDKit 2D structure of ${candidate.compound_id}`}
            />
          ) : (
            <div className="descriptor-art">
              <Database size={42} />
              <strong>{candidate?.feature_count ?? "—"}</strong>
              <span>public numerical features</span>
            </div>
          )}
          <div className="specimen-footer">
            <div>
              <span>{"Representation"}</span>
              <strong>
                {historical ? "Morgan fingerprint" : "Synthetic descriptors"}
              </strong>
            </div>
            <Badge className="badge-neutral">
              {candidate?.feature_count ?? "—"} features
            </Badge>
          </div>
          <p className="specimen-note">
            {candidateError ? "Candidate preview could not load. Open Compound explorer to retry the public data request." : (historical
                ? "Structure is public. Its assay outcome stays hidden until requested and delivered."
                : "Synthetic numerical descriptors only; no real molecular structure or biological assay.")}
          </p>
        </div>
      </div>
      <KpiStrip run={run} />
      <section className="workflow-section">
        <div className="section-heading">
          <div>
            <h2>
              {"A closed loop, with an open audit trail"}
            </h2>
            <p>
              {"Live campaign state, not an illustration of laboratory integration."}
            </p>
          </div>
          <GoLink to="/lab">
            {"Follow the campaign"}
          </GoLink>
        </div>
        <Workflow run={run} />
      </section>
      <div className="overview-bottom">
        <section className="surface">
          <div className="section-heading">
            <div>
              <h2>
                {"Evidence before ambition"}
              </h2>
              <p>
                {"Recorded HIV benchmark · 10 paired seeds · B = 30"}
              </p>
            </div>
            <Badge className="badge-neutral">v0.1 evidence</Badge>
          </div>
          {evidence && (
            <RecordedBenchmarkChart rows={evidence.statistics.summary} />
          )}
          <div className="honesty-note">
            <GitBranch size={17} />
            <p>
              {"The learned controllers matched Greedy because all 300/300 historical requests used their Greedy fallback. This is not successful learned transfer."}
            </p>
          </div>
          <GoLink to="/evidence">
            {"Read methods and limitations"}
          </GoLink>
        </section>
        <section className="research-note">
          <BookOpen size={23} />
          <h2>
            {"A research instrument.\nAn honest portfolio."}
          </h2>
          <p>
            {(historical
                ? "Explore policy trade-offs with real historical assay data. Inspect every decision, budget reservation and delivered result."
                : "Explore policy trade-offs with synthetic fixtures. Inspect every decision, budget reservation and delivered result.")}
          </p>
          <dl>
            <div>
              <dt>Assay</dt>
              <dd>
                {run.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA"
                  ? "NCI DTP · HIV"
                  : "Synthetic binary"}
              </dd>
            </div>
            <div>
              <dt>Data rights</dt>
              <dd>{run.report.manifest.dataset.terms_status}</dd>
            </div>
            <div>
              <dt>Code revision</dt>
              <dd className="small-mono">
                {short(meta?.repo_git_sha ?? "—", 12)}
              </dd>
            </div>
          </dl>
          <GoLink to="/presentation">
            {"Open the guided presentation"}
          </GoLink>
        </section>
      </div>
    </>
  );
}
