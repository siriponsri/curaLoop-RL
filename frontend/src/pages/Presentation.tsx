import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Clock3,
  Play,
  Presentation,
} from "lucide-react";
import { useApp } from "../state";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  KpiStrip,
  PageHeading,
  SourceBadge,
  Workflow,
} from "../components/shared";

export default function GuidedPresentation() {
  const { run, act, busy } = useApp();
  const [step, setStep] = useState(0);
  if (!run) return null;
  const slides = [
    {
      title: "The decision",
      time: "0:00–1:00",
      text: "A screening library has more candidates than the available budget. We choose what to assay first—not what to prescribe.",
    },
    {
      title: "What is real?",
      time: "1:00–2:00",
      text: (run.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA"
          ? "HIV assay outcomes and molecular structures are historical public data. Costs, timing and capacity are simulated assumptions."
          : "This campaign uses synthetic descriptors and fictional labels. It contains no real molecular structures or biological assay outcomes. Costs, timing and capacity are simulated assumptions."),
    },
    {
      title: "Select, then wait",
      time: "2:00–3:30",
      text: "Select a batch below. Watch budget become reserved. Advance simulated time until results are due. Pending compounds are not confirmed hits.",
    },
    {
      title: "Adapt with evidence",
      time: "3:30–5:00",
      text: "Only delivered labels update the policy. Every request and outcome is recorded in an immutable public ledger.",
    },
    {
      title: "Compare honestly",
      time: "5:00–7:00",
      text: "Use matched conditions and export the result. Trained controllers used Greedy fallback on the historical benchmark. This remains a retrospective simulator.",
    },
  ];
  return (
    <>
      <PageHeading
        title={"Guided presentation"}
        description={"A 5–7 minute walkthrough using the live campaign—no scripted success data."}
      />
      <div className="presentation-origin">
        <SourceBadge /> <span>{run.report.manifest.dataset.name}</span>
      </div>
      <div className="presentation-layout">
        <aside className="presentation-steps">
          {slides.map((s, i) => (
            <button
              key={i}
              className={step === i ? "active" : ""}
              onClick={() => setStep(i)}
            >
              <span>{i + 1}</span>
              <div>
                <strong>{s.title}</strong>
                <small>{s.time}</small>
              </div>
            </button>
          ))}
        </aside>
        <div className="surface presentation-stage">
          <Badge className="badge-teal">
            <Presentation size={14} />
            {slides[step].time}
          </Badge>
          <h2>{slides[step].title}</h2>
          <p className="presentation-copy">{slides[step].text}</p>
          <Workflow run={run} compact />
          <div className="presentation-actions">
            <Button
              aria-label="Presentation select batch"
              onClick={() => void act("select")}
              disabled={Boolean(busy) || !run.can_select}
            >
              <Play size={15} />
              {"Select batch"}
            </Button>
            <Button
              aria-label="Presentation advance time"
              variant="outline"
              onClick={() => void act("advance")}
              disabled={Boolean(busy) || !run.pending.length}
            >
              <Clock3 size={15} />
              {"Advance +1"}
            </Button>
            <Button asChild variant="ghost">
              <Link to={step === 4 ? "/benchmarks" : "/lab"}>
                {step === 4
                  ? "Open benchmark arena"
                  : "Inspect full lab"}
                <ArrowRight size={15} />
              </Link>
            </Button>
          </div>
          <div className="presentation-footer">
            <Button
              variant="ghost"
              onClick={() => setStep((s) => s - 1)}
              disabled={!step}
            >
              <ArrowLeft size={15} />
              {"Back"}
            </Button>
            <span>
              {step + 1} / {slides.length}
            </span>
            <Button
              variant="outline"
              onClick={() => setStep((s) => s + 1)}
              disabled={step === slides.length - 1}
            >
              {"Next chapter"}
              <ArrowRight size={15} />
            </Button>
          </div>
        </div>
      </div>
      <KpiStrip run={run} />
    </>
  );
}
