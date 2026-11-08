import { useState } from "react";
import { ArrowRight, Boxes, Clock3, FlaskConical, RefreshCw } from "lucide-react";
import { useI18n } from "../i18n";
import type { RunView } from "../types";

/** Inspection only: stage navigation never advances the engine or exposes a label. */
export function SimulationFlow({ run }: { run: RunView }) {
  const { t } = useI18n();
  const [stage, setStage] = useState(0);
  const report = run.report;
  const latest = report.requests.at(-1);
  const stages = [
    { title: "Compound selection", icon: Boxes, value: report.requests.length, unit: "accepted requests",
      description: "Selections reserve budget. Predicted probabilities are not assay results." },
    { title: "Assay queue", icon: Clock3, value: run.pending.length, unit: "pending assays",
      description: "Pending outcomes remain hidden until their scheduled delivery step." },
    { title: "Result delivery", icon: FlaskConical, value: report.metrics.delivered_assays, unit: "delivered assays",
      description: "Only delivered, observed actives count as new hits. Missing outcomes are excluded." },
    { title: "Model update", icon: RefreshCw, value: [...report.initial_results, ...report.delivered_results].filter(x => x.active !== null).length,
      unit: "available observations", description: "Observed labels become available for the next decision. A fitted model is reported only when the engine records one." },
  ];
  const active = stages[stage];
  return <section className="surface simulation-flow" aria-label={t("Interactive screening process")}>
    <div className="section-heading"><div><span className="eyebrow">{t("Retrospective Simulator")}</span><h2>{t("From selection to the next decision")}</h2></div><span className="small-mono">{t("Step")} {report.metrics.step}</span></div>
    <p className="small muted">{t("Select a stage to inspect its data. Engine actions use the controls above.")}</p>
    <div className="simulation-stages" role="group" aria-label={t("Inspect workflow stage")}>
      {stages.map((item, i) => <div className="simulation-stage-wrap" key={item.title}>
        <button type="button" className="simulation-stage" aria-pressed={stage === i} onClick={() => setStage(i)}>
          <span className="stage-top"><item.icon size={19} /><span>0{i + 1}</span></span>
          <strong>{t(item.title)}</strong><span className="stage-count">{item.value}<small>{t(item.unit)}</small></span>
        </button>{i < 3 && <ArrowRight className="stage-arrow" size={15} aria-hidden="true" />}
      </div>)}
    </div>
    <div className="stage-detail" aria-live="polite"><div><strong>{t("Inspecting {stage}", { stage: t(active.title) })}</strong><p>{t(active.description)}</p></div>
      {stage === 0 && <span className="small-mono">{latest?.compound_id ?? t("No accepted request yet")}</span>}
      {stage === 1 && <span>{run.pending.length ? t("Next delivery at step {step}", { step: Math.min(...run.pending.map(x => x.due_at_step)) }) : t("No assays in flight")}</span>}
      {stage === 2 && <span>{t("Confirmed new hits")}: {report.metrics.confirmed_hits}</span>}
      {stage === 3 && <span className="model-status"><small>{t("Last selection model status")}</small><code>{latest?.model_status ?? t("No model decision yet")}</code></span>}
    </div>
  </section>;
}
