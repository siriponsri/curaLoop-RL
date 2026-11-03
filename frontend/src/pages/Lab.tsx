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
        title={"Simulation lab"}
        description={"Run the actual engine. Follow every decision and its consequences."}
      >
        <ExportButtons id={run.session_id} />
      </PageHeading>
      <div className="lab-context">
        <div>
          <SourceBadge />
          <Badge className="badge-amber">
            Retrospective Screening Simulator
          </Badge>
          <span>
            {"Not a Validated Digital Twin"}
          </span>
        </div>
        <span className="small-mono">
          {policyNames[r.manifest.policy_id]} · seed {r.manifest.seed} · step{" "}
          {m.step}
        </span>
      </div>
      <div className="lab-toolbar">
        <div className="button-row">
          <Button
            aria-label="Select batch"
            onClick={() => void act("select")}
            disabled={Boolean(busy) || !run.can_select}
          >
            <Play size={16} />
            {busy === "select"
              ? "Selecting…"
              : "Select next batch"}
          </Button>
          <Button
            aria-label="Advance time"
            variant="outline"
            onClick={() => void act("advance")}
            disabled={Boolean(busy) || run.pending.length === 0}
          >
            <Clock3 size={16} />
            {"Advance +1 step"}
          </Button>
          <Button
            aria-label="Finish campaign"
            variant="outline"
            onClick={() => void act("finish")}
            disabled={Boolean(busy) || run.done}
          >
            <FastForward size={16} />
            {busy === "finish"
              ? "Running…"
              : "Complete run"}
          </Button>
        </div>
        <div className="button-row">
          <Button
            aria-label="Reconcile replay"
            variant="ghost"
            size="sm"
            onClick={() => void act("replay")}
            disabled={Boolean(busy)}
          >
            <RefreshCcw size={15} />
            {"Verify replay"}
          </Button>
          <Button
            aria-label="Reset campaign"
            variant="ghost"
            size="sm"
            onClick={() => void act("reset")}
            disabled={Boolean(busy)}
          >
            <RotateCcw size={15} />
            {"Reset"}
          </Button>
        </div>
      </div>
      <KpiStrip run={run} />
      <div className="lab-board">
        <section className="surface loop-surface">
          <div className="section-heading">
            <div>
              <h2>{"The screening loop"}</h2>
              <p>
                {"Live counts from accepted requests and delivered events."}
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
                ? "Completed"
                : run.pending.length
                  ? "Awaiting feedback"
                  : "Ready to select"}
            </Badge>
          </div>
          <Workflow run={run} />
          <div className="budget-ledger">
            <div className="ledger-heading">
              <strong>{"Budget ledger"}</strong>
              <span>
                {r.manifest.scenario_config.budget_units} simulated units
              </span>
            </div>
            <div
              className="ledger-track"
              role="img"
              aria-label={`Spent ${m.spent_units}, reserved ${m.reserved_units}, remaining ${m.remaining_units}`}
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
                {"Spent"} <b>{m.spent_units}</b>
              </span>
              <span>
                <i className="legend-dot reserved" />
                {"Reserved"} <b>{m.reserved_units}</b>
              </span>
              <span>
                <i className="legend-dot available" />
                {"Available"} <b>{m.remaining_units}</b>
              </span>
            </div>
          </div>
          <div className="chart-heading">
            <h3>{"Confirmed discoveries"}</h3>
            <span className="muted small">
              {"No pending or predicted positives"}
            </span>
          </div>
          <DiscoveryChart reports={[r]} />
        </section>
        <aside className="surface pending-surface">
          <div className="section-heading">
            <h2>{"Feedback queue"}</h2>
            <Badge>{run.pending.length}</Badge>
          </div>
          {run.pending.length ? (
            run.pending.map((p) => (
              <div className="queue-item" key={p.request_id}>
                <div>
                  <span className="small-mono">{p.compound_id}</span>
                  <Badge className="badge-amber">pending</Badge>
                </div>
                <p>
                  <Clock3 size={13} />
                  {"Due at step"} {p.due_at_step}{" "}
                  <span>
                    · {p.due_at_step - m.step} {"remaining"}
                  </span>
                </p>
              </div>
            ))
          ) : (
            <EmptyState
              title={
                run.done
                  ? "Queue cleared"
                  : "No assays in flight"
              }
              description={
                run.done
                  ? "Every accepted request has a delivered or missing outcome."
                  : "Select a batch to reserve budget and schedule feedback."
              }
            />
          )}
          <div className="queue-footer">
            <CheckCircle2 size={15} />
            <span>
              {"Missing outcomes"}: {m.missing_assays}
              <br />
              {"Initial seed hits"}: {m.seed_hits} (
              {"excluded"})
            </span>
          </div>
        </aside>
      </div>
      <section className="surface decisions-section">
        <div className="section-heading">
          <div>
            <h2>{"Policy decisions"}</h2>
            <p>
              {"Actual model status, predicted probabilities and outcome visibility."}
            </p>
          </div>
          <span className="small-mono">{r.requests.length} requests</span>
        </div>
        {r.requests.length ? (
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label={"Experiment decision table"}
          >
            <table>
              <thead>
                <tr>
                  <th>{"Compound"}</th>
                  <th>{"Observed status"}</th>
                  <th>{"Due step"}</th>
                  <th>P(active)</th>
                  <th>{"Selection explanation"}</th>
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
                            ? "Pending"
                            : outcomes.get(q.request_id)?.active === true
                              ? "Observed active"
                              : outcomes.get(q.request_id)?.active === false
                                ? "Observed inactive"
                                : "Missing outcome"}
                        </Badge>
                      </td>
                      <td>{q.due_at_step}</td>
                      <td>
                        {q.predicted_probability == null
                          ? "—"
                          : number(q.predicted_probability, 3)}
                      </td>
                      <td className="explanation-cell">
                        {q.explanation}
                        <small>{q.model_status}</small>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title={"Your next decision starts here"}
            description={"Select the first batch. Scores only appear when a valid model can be fitted."}
          />
        )}
      </section>
      <section className="surface timeline-section">
        <div className="section-heading">
          <div>
            <h2>{"Event timeline"}</h2>
            <p>
              {"Append-only scientific history. No future labels."}
            </p>
          </div>
          <Badge>{r.events.length} events</Badge>
        </div>
        <div className="filter-row">
          <div className="search-field">
            <Search size={16} />
            <input
              aria-label="Search event compound"
              placeholder={"Search compound ID…"}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            aria-label="Event type filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">
              {"All event types"}
            </option>
            {Array.from(new Set(r.events.map((e) => e.event_type))).map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </div>
        <div
          className="event-list"
          tabIndex={0}
          role="region"
          aria-label={"Event timeline"}
        >
          {events.slice(0, 100).map((e) => (
            <div className="event-row" key={e.event_id}>
              <span
                className={
                  "event-dot " +
                  (e.event_type === "RESULT_DELIVERED" ? "event-delivered" : "")
                }
              />
              <span className="event-step">step {e.step}</span>
              <div>
                <strong>{e.event_type.replaceAll("_", " ")}</strong>
                <span>
                  {e.compound_id || "Campaign"}
                  {e.delivered_active !== null
                    ? ` · ${e.delivered_active ? "active" : "inactive"} revealed`
                    : ""}
                </span>
              </div>
              <span className="event-cost">
                {e.cost_units ? `${e.cost_units} units` : ""}
              </span>
            </div>
          ))}
          {!events.length && (
            <p className="muted">
              {"No events match this filter."}
            </p>
          )}
        </div>
        <p className="small muted">
          {"Showing up to 100 recent matching events. Export retains the complete public ledger."}
        </p>
      </section>
    </>
  );
}
