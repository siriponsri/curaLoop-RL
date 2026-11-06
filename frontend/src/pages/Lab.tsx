import { useI18n } from "../i18n";
import { useState } from "react";
import {
  CheckCircle2,
  Clock3,
  FastForward,
  Play,
  RefreshCcw,
  RotateCcw,
  Search,
} from "lucide-react";
import { useApp } from "../state";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  EmptyState,
  ExportButtons,
  KpiStrip,
  PageHeading,
  SourceBadge,
  Workflow,
} from "../components/shared";
import { DiscoveryChart } from "../components/charts";
import { number } from "../lib";
import { policyNames } from "../types";

export default function Lab() {
  const { t } = useI18n();
  const { run, act, busy } = useApp();
  const [filter, setFilter] = useState("all"),
    [search, setSearch] = useState("");
  if (!run) return null;
  const r = run.report,
    m = r.metrics;
  const events = r.events
    .filter(
      (e) =>
        (filter === "all" || e.event_type === filter) &&
        (!search ||
          (e.compound_id ?? "").toLowerCase().includes(search.toLowerCase())),
    )
    .slice()
    .reverse();
  const outcomes = new Map(r.delivered_results.map((x) => [x.request_id, x]));
  return (
    <>
      <PageHeading
        title={t("Simulation lab")}
        description={t("Review requests, advance time, and inspect delivered results.")}
      >
        <ExportButtons id={run.session_id} />
      </PageHeading>
      <div className="lab-context">
        <div>
          <SourceBadge />
          <Badge className="badge-amber">
            {t("Retrospective Screening Simulator")}</Badge>
          <span>
            {t("Not a Validated Digital Twin")}
          </span>
        </div>
        <span className="small-mono">
          {policyNames[r.manifest.policy_id]} {t(" · seed ")}{r.manifest.seed} {t(" · step")}{" "}
          {m.step}
        </span>
      </div>
      <div className="lab-toolbar">
        <div className="button-row">
          <Button
            variant={run.can_select ? "default" : "outline"}
            onClick={() => void act("select")}
            disabled={Boolean(busy) || !run.can_select}
          >
            <Play size={16} />
            {busy === "select"
              ? t("Selecting…")
              : t("Select next batch")}
          </Button>
          <Button
            variant={!run.can_select && run.pending.length > 0 ? "default" : "outline"}
            onClick={() => void act("advance")}
            disabled={Boolean(busy) || run.pending.length === 0}
          >
            <Clock3 size={16} />
            {t("Advance +1 step")}
          </Button>
          <Button
            variant="outline"
            onClick={() => void act("finish")}
            disabled={Boolean(busy) || run.done}
          >
            <FastForward size={16} />
            {busy === "finish"
              ? t("Running…")
              : t("Complete run")}
          </Button>
        </div>
        <div className="button-row">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => void act("replay")}
            disabled={Boolean(busy)}
          >
            <RefreshCcw size={15} />
            {t("Verify replay")}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => void act("reset")}
            disabled={Boolean(busy)}
          >
            <RotateCcw size={15} />
            {t("Reset")}
          </Button>
        </div>
      </div>
      <KpiStrip run={run} />
      <div className="lab-board">
        <aside className="surface pending-surface">
          <div className="section-heading">
            <h2>{t("Feedback queue")}</h2>
            <Badge>{run.pending.length}</Badge>
          </div>
          {run.pending.length ? (
            run.pending.map((p) => (
              <div className="queue-item" key={p.request_id}>
                <div>
                  <span className="small-mono">{p.compound_id}</span>
                  <Badge className="badge-amber">{t("pending")}</Badge>
                </div>
                <p>
                  <Clock3 size={13} />
                  {t("Due at step")} {p.due_at_step}{" "}
                  <span>
                    {t("·")}{p.due_at_step - m.step} {t("remaining")}
                  </span>
                </p>
              </div>
            ))
          ) : (
            <EmptyState
              title={
                run.done
                  ? t("Queue cleared")
                  : t("No assays in flight")
              }
              description={
                run.done
                  ? t("Every accepted request has a delivered or missing outcome.")
                  : t("Select a batch to reserve budget and schedule feedback.")
              }
            />
          )}
          <div className="queue-footer">
            <CheckCircle2 size={15} />
            <span>
              {t("Missing outcomes")}{t(": ")}{m.missing_assays}
              <br />
              {t("Initial seed hits")}{t(": ")}{m.seed_hits} {t("(")}{t("excluded")}{t(")")}</span>
          </div>
        </aside>
        <section className="surface loop-surface">
          <div className="section-heading">
            <div>
              <h2>{t("The screening loop")}</h2>
              <p>
                {t("Live counts from accepted requests and delivered events.")}
              </p>
            </div>
            <Badge
              className={
                run.done
                  ? "badge-teal"
                  : run.pending.length
                    ? "badge-amber"
                    : "badge-neutral"
              }
            >
              {run.done
                ? t("Completed")
                : run.pending.length
                  ? t("Awaiting feedback")
                  : t("Ready to select")}
            </Badge>
          </div>
          <details className="lab-workflow-details"><summary>{t("Screening workflow")}</summary><Workflow run={run} /></details>
          <div className="budget-ledger">
            <div className="ledger-heading">
              <strong>{t("Budget ledger")}</strong>
              <span>
                {r.manifest.scenario_config.budget_units} {t("simulated units")}</span>
            </div>
            <div
              className="ledger-track"
              role="img"
              aria-label={t("Spent {spent}, reserved {reserved}, remaining {remaining}", { spent: m.spent_units, reserved: m.reserved_units, remaining: m.remaining_units })}
            >
              <span
                className="ledger-spent"
                style={{
                  width: `${(100 * m.spent_units) / Math.max(1, r.manifest.scenario_config.budget_units)}%`,
                }}
              />
              <span
                className="ledger-reserved"
                style={{
                  width: `${(100 * m.reserved_units) / Math.max(1, r.manifest.scenario_config.budget_units)}%`,
                }}
              />
            </div>
            <div className="ledger-labels">
              <span>
                <i className="legend-dot spent" />
                {t("Spent")} <b>{m.spent_units}</b>
              </span>
              <span>
                <i className="legend-dot reserved" />
                {t("Reserved")} <b>{m.reserved_units}</b>
              </span>
              <span>
                <i className="legend-dot available" />
                {t("Available")} <b>{m.remaining_units}</b>
              </span>
            </div>
          </div>
          <div className="chart-heading">
            <h3>{t("Confirmed discoveries")}</h3>
            <span className="muted small">
              {t("No pending or predicted positives")}
            </span>
          </div>
          {m.delivered_assays > 0 ? <DiscoveryChart reports={[r]} /> : <p className="chart-pending-note">{t("Confirmed discoveries appear after results are delivered.")}</p>}
        </section>
      </div>
      <section className="surface decisions-section">
        <div className="section-heading">
          <div>
            <h2>{t("Policy decisions")}</h2>
            <p>
              {t("Actual model status, predicted probabilities and outcome visibility.")}
            </p>
          </div>
          <span className="small-mono">{r.requests.length} {t(" requests")}</span>
        </div>
        {r.requests.length ? (
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label={t("Experiment decision table")}
          >
            <table>
              <thead>
                <tr>
                  <th>{t("Compound")}</th>
                  <th>{t("Observed status")}</th>
                  <th>{t("Due step")}</th>
                  <th>{t("P(active)")}</th>
                  <th>{t("Selection explanation")}</th>
                </tr>
              </thead>
              <tbody>
                {r.requests
                  .slice()
                  .reverse()
                  .map((q) => (
                    <tr key={q.request_id}>
                      <td className="small-mono">{q.compound_id}</td>
                      <td>
                        <Badge
                          className={
                            outcomes.has(q.request_id)
                              ? "badge-teal"
                              : "badge-amber"
                          }
                        >
                          {!outcomes.has(q.request_id)
                            ? t("Pending")
                            : outcomes.get(q.request_id)?.active === true
                              ? t("Observed active")
                              : outcomes.get(q.request_id)?.active === false
                                ? t("Observed inactive")
                                : t("Missing outcome")}
                        </Badge>
                      </td>
                      <td>{q.due_at_step}</td>
                      <td>
                        {q.predicted_probability == null
                          ? "—"
                          : number(q.predicted_probability, 3)}
                      </td>
                      <td className="explanation-cell">
                        {t("Original engine explanation (English)")}: {q.explanation}
                        <small>{q.model_status}</small>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title={t("Your next decision starts here")}
            description={t("Select the first batch. Scores only appear when a valid model can be fitted.")}
          />
        )}
      </section>
      <section className="surface timeline-section">
        <div className="section-heading">
          <div>
            <h2>{t("Event timeline")}</h2>
            <p>
              {t("Append-only scientific history. No future labels.")}
            </p>
          </div>
          <Badge>{r.events.length} {t(" events")}</Badge>
        </div>
        <div className="filter-row">
          <div className="search-field">
            <Search size={16} />
            <input
              aria-label={t("Search event compound")}
              placeholder={t("Search compound ID…")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            aria-label={t("Event type filter")}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">
              {t("All event types")}
            </option>
            {Array.from(new Set(r.events.map((e) => e.event_type))).map((x) => (
              <option key={x} value={x}>{t(x)}</option>
            ))}
          </select>
        </div>
        <div
          className="event-list"
          tabIndex={0}
          role="region"
          aria-label={t("Event timeline")}
        >
          {events.slice(0, 100).map((e) => (
            <div className="event-row" key={e.event_id}>
              <span
                className={
                  "event-dot " +
                  (e.event_type === "RESULT_DELIVERED" ? "event-delivered" : "")
                }
              />
              <span className="event-step">{t("step ")}{e.step}</span>
              <div>
                <strong>{t(e.event_type)}</strong>
                <span>
                  {e.compound_id || t("Campaign")}
                  {e.delivered_active !== null
                    ? " · " + t("{outcome} revealed", { outcome: e.delivered_active ? t("active") : t("inactive") })
                    : ""}
                </span>
              </div>
              <span className="event-cost">
                {e.cost_units ? t("{count} units", { count: e.cost_units }) : ""}
              </span>
            </div>
          ))}
          {!events.length && (
            <p className="muted">
              {t("No events match this filter.")}
            </p>
          )}
        </div>
        <p className="small muted">
          {t("Showing up to 100 recent matching events. Export retains the complete public ledger.")}
        </p>
      </section>
    </>
  );
}
