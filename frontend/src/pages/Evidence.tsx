import { useI18n } from "../i18n";
import {
  ArrowUpRight,
  CheckCircle2,
  Download,
  FileJson,
  GitBranch,
  ShieldCheck,
} from "lucide-react";
import { useApp } from "../state";
import { Badge } from "../components/ui/badge";
import { SavedRuns, SnapshotImport } from "../components/recovery";
import { ExportButtons, PageHeading, SourceBadge } from "../components/shared";
import { ReturnChart } from "../components/charts";
import { number, short } from "../lib";

export default function Evidence() {
  const { t } = useI18n();
  const { run, meta, evidence } = useApp();
  if (!run || !meta || !evidence) return null;
  const m = run.report.manifest;
  return (
    <>
      <PageHeading
        title={t("Research evidence")}
        description={t("Trace the data, methods and limits behind every number.")}
      >
        <ExportButtons id={run.session_id} />
      </PageHeading>
      <div className="evidence-intro">
        <ShieldCheck size={26} />
        <div>
          <h2>
            {t("A personal research workbench, with explicit boundaries.")}
          </h2>
          <p>
            {t("Not an official GPO system. No lab integration, validated Digital Twin, clinical efficacy or GMP claim.")}
          </p>
        </div>
      </div>
      <div className="evidence-grid">
        <section className="surface">
          <div className="section-heading">
            <h2>{t("Dataset provenance")}</h2>
            <SourceBadge />
          </div>
          <dl className="details-list">
            <div>
              <dt>{t("Assay / target")}</dt>
              <dd>{m.dataset.assay_id}</dd>
            </div>
            <div>
              <dt>{t("Label semantics")}</dt>
              <dd>{m.dataset.label_semantics}</dd>
            </div>
            <div>
              <dt>{t("Dataset release")}</dt>
              <dd>{m.dataset.release}</dd>
            </div>
            <div>
              <dt>{t("Dataset SHA256")}</dt>
              <dd className="small-mono break-text">{m.dataset.sha256}</dd>
            </div>
            <div>
              <dt>{t("Source")}</dt>
              <dd className="break-text">{m.dataset.source}</dd>
            </div>
            <div>
              <dt>{t("Rights status")}</dt>
              <dd>{m.dataset.terms_status}</dd>
            </div>
            <div>
              <dt>{t("Seed-label selection")}</dt>
              <dd>
                {m.initial_label_selection}
                <br />
                {m.initial_labels_budget_rule}
              </dd>
            </div>
          </dl>
          <p className="small muted">
            {t("References for the separately recorded historical HIV benchmark")}
          </p>
          <div className="evidence-links">
            {evidence.source_links.map((link) => (
              <a
                href={link.url}
                key={link.url}
                target="_blank"
                rel="noreferrer"
              >
                {link.title}
                <ArrowUpRight size={15} />
              </a>
            ))}
          </div>
        </section>
        <section className="surface">
          <div className="section-heading">
            <h2>{t("Reproduction identity")}</h2>
            <GitBranch size={20} />
          </div>
          <dl className="details-list">
            <div>
              <dt>{t("Web / engine version")}</dt>
              <dd>
                {t("v")}{meta.web_version} {t(" / v")}{meta.engine_version}
              </dd>
            </div>
            <div>
              <dt>{t("Current code revision")}</dt>
              <dd className="small-mono break-text">
                {meta.repo_git_sha}
                <br />
                <Badge className="badge-amber">
                  {meta.working_tree_dirty === false
                    ? t("Clean working tree")
                    : meta.working_tree_dirty === true
                      ? t("Uncommitted changes present")
                      : t("Git state unavailable")}
                </Badge>
              </dd>
            </div>
            <div>
              <dt>{t("Engine source SHA256")}</dt>
              <dd className="small-mono break-text">{meta.source_sha256}</dd>
            </div>
            <div>
              <dt>{t("Frontend build SHA256")}</dt>
              <dd className="small-mono break-text">
                {meta.frontend_build_sha256 ??
                  t("Not available")}
              </dd>
            </div>
            <div>
              <dt>{t("Algorithm")}</dt>
              <dd>{m.algorithm_version}</dd>
            </div>
            <div>
              <dt>{t("Scenario source")}</dt>
              <dd>
                <Badge className="badge-amber">{m.scenario_origin}</Badge>
              </dd>
            </div>
            <div>
              <dt>{t("Digital Twin maturity")}</dt>
              <dd>{t("RETROSPECTIVE_SIMULATOR")}</dd>
            </div>
          </dl>
          <div className="verification-note">
            <CheckCircle2 size={18} />
            <p>
              {t("Test counts are versioned evidence. The original v0.1 and web-v0.2 results remain in docs/evidence; current Windows release verification is recorded separately in docs/evidence/poc-v0.3.")}</p>
          </div>
        </section>
      </div>
      <section className="surface">
        <div className="section-heading">
          <div>
            <h2>
              {t("Held-out predictor audit")}
            </h2>
            <p>{evidence.predictor.scope}</p>
          </div>
          <Badge>{t("Recorded · v0.1")}</Badge>
        </div>
        <div className="predictor-metrics">
          <div>
            <span>{t("AUROC")}</span>
            <strong>{number(evidence.predictor.auroc, 3)}</strong>
          </div>
          <div>
            <span>{t("Average precision")}</span>
            <strong>{number(evidence.predictor.average_precision, 4)}</strong>
          </div>
          <div>
            <span>{t("Test prevalence")}</span>
            <strong>
              {number(evidence.predictor.test_prevalence * 100, 1)}{t("%")}</strong>
          </div>
          <div>
            <span>{t("Scaffold overlap")}</span>
            <strong>{evidence.predictor.scaffold_overlap}</strong>
          </div>
        </div>
        <p className="honesty-note-text">
          {t("960 train / 240 test molecules, with only 6 test actives. These weak predictions and the custom split do not establish drug-discovery utility or a published leaderboard result.")}
        </p>
      </section>
      <section className="surface">
        <div className="section-heading">
          <div>
            <h2>
              {t("Trained controllers, visible limitations")}
            </h2>
            <p>
              {t("Training returns are actual checkpoint records—not evaluation performance.")}
            </p>
          </div>
          <Badge className="badge-amber">{t("Synthetic training only")}</Badge>
        </div>
        <div className="controller-grid">
          {evidence.controllers.map((cp) => (
            <div key={cp.policy_id}>
              <h3>
                {cp.policy_id === "q_learning"
                  ? t("Tabular Q-learning")
                  : t("Contextual bandit")}
              </h3>
              <span className="muted small">
                {cp.training_episodes} {t(" episodes ·")}{" "}
                {short(cp.checkpoint_sha256, 16)}
              </span>
              <ReturnChart returns={cp.episode_returns} />
            </div>
          ))}
        </div>
        <div className="honesty-note amber-note">
          <ShieldCheck size={18} />
          <p>
            {evidence.controller_historical_fallback}{t(".")}{" "}
            {t("All recorded historical selections therefore came from Greedy fallback, not learned controller transfer.")}
          </p>
        </div>
      </section>
      <div className="evidence-grid">
        <section className="surface">
          <h2>{t("Scientific limitations")}</h2>
          <ul className="limitations-list">
            {m.limitations.map((item) => (
              <li key={item}>
                {(item)}
              </li>
            ))}
          </ul>
        </section>
        <section className="surface resume-section">
          <FileJson size={28} />
          <h2>
            {t("Your evidence travels with you")}
          </h2>
          <p>
            {t("The local database saves your campaign after accepted actions. A single-run JSON is a portable recovery copy; it can restore a validated pending queue and event history on another installation. Comparison JSON contains independent reports; CSV is an event ledger. Neither can resume a single campaign.")}</p>
          <ExportButtons id={run.session_id} />
          <hr />
          <SnapshotImport />
          <p className="muted small">
            <Download size={13} />
            {(meta.session_note)}
          </p>
        </section>
      </div>
      <SavedRuns />
    </>
  );
}
