import {
  ArrowRight,
  ArrowUpRight,
  Check,
  Download,
  FlaskConical,
  Hourglass,
  Layers3,
  MoveRight,
  ScanSearch,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { number } from "../lib";
import { useApp } from "../state";
import { runExport } from "../api";
import type { RunView } from "../types";

export function PageHeading({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children && <div className="heading-actions">{children}</div>}
    </div>
  );
}
export function SourceBadge() {
  const { run } = useApp();
  return (
    <Badge
      className={
        run?.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA"
          ? "badge-teal"
          : "badge-amber"
      }
    >
      <span className="status-dot" />
      {run?.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA"
        ? "Historical assay data"
        : "Synthetic fixture"}
    </Badge>
  );
}
export function KpiStrip({ run }: { run: RunView }) {

  const m = run.report.metrics;
  return (
    <div className="kpi-strip">
      <div>
        <span>{"Confirmed new hits"}</span>
        <strong>{number(m.confirmed_hits)}</strong>
        <small>
          {"Delivered only · excludes seed labels"}
        </small>
      </div>
      <div>
        <span>{"Assays delivered"}</span>
        <strong>
          {number(m.delivered_assays)}
          <small>/ {run.report.requests.length}</small>
        </strong>
        <small>
          {"Missing outcomes counted separately"}
        </small>
      </div>
      <div>
        <span>{"Pending feedback"}</span>
        <strong>{number(m.pending_assays)}</strong>
        <small>
          {"No label visible until due"}
        </small>
      </div>
      <div>
        <span>{"Budget available"}</span>
        <strong>
          {number(m.remaining_units)}
          <small> units</small>
        </strong>
        <small>
          {"Simulated cost · never THB or USD"}
        </small>
      </div>
    </div>
  );
}
export function Workflow({
  run,
  compact = false,
}: {
  run: RunView;
  compact?: boolean;
}) {

  const stages = [
    {
      icon: Layers3,
      label: "Candidate pool",
      count: run.eligible_count,
      to: "/compounds",
    },
    {
      icon: ScanSearch,
      label: "Policy selection",
      count: run.report.requests.length,
      to: "/lab",
    },
    {
      icon: Hourglass,
      label: "Result queue",
      count: run.pending.length,
      to: "/lab",
    },
    {
      icon: FlaskConical,
      label: "Delivered results",
      count: run.report.metrics.delivered_assays,
      to: "/lab",
    },
  ];
  return (
    <div
      className={"workflow " + (compact ? "workflow-compact" : "")}
      aria-label="Live screening workflow"
    >
      {stages.map((stage, i) => (
        <div className="workflow-segment" key={stage.label}>
          <Link
            to={stage.to}
            className={
              "flow-step " +
              (i === 2 && run.pending.length ? "flow-step-active" : "")
            }
          >
            <stage.icon size={compact ? 19 : 23} />
            <strong>{number(stage.count)}</strong>
            <span>{stage.label}</span>
            {i === 3 && run.done && <Check size={15} className="flow-check" />}
          </Link>
          {i < stages.length - 1 && (
            <MoveRight className="flow-arrow" size={20} />
          )}
        </div>
      ))}
    </div>
  );
}
export function ExportButtons({ id }: { id: string }) {
  return (
    <div className="button-row">
      <Button asChild variant="outline" size="sm">
        <a href={runExport(id, "json")} download>
          <Download size={15} />
          JSON
        </a>
      </Button>
      <Button asChild variant="outline" size="sm">
        <a href={runExport(id, "csv")} download>
          <Download size={15} />
          CSV
        </a>
      </Button>
    </div>
  );
}
export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="empty-state">
      <FlaskConical size={26} />
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}
export function GoLink({
  to,
  children,
}: {
  to: string;
  children: React.ReactNode;
}) {
  return (
    <Link className="text-link" to={to}>
      {children}
      <ArrowUpRight size={16} />
    </Link>
  );
}
export function NextLink({
  to,
  children,
}: {
  to: string;
  children: React.ReactNode;
}) {
  return (
    <Button asChild>
      <Link to={to}>
        {children}
        <ArrowRight size={16} />
      </Link>
    </Button>
  );
}
