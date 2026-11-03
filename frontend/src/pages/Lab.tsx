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
  const { run, act, busy, t } = useApp();
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
        title={t("Simulation lab", "ห้องจำลองการคัดเลือกสาร")}
        description={t(
          "Run the actual engine. Follow every decision and its consequences.",
          "รัน engine จริง ติดตามการเลือกสาร งบประมาณ และผลที่เกิดขึ้น",
        )}
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
            {t(
              "Not a Validated Digital Twin",
              "ยังไม่ใช่ Digital Twin ที่ผ่านการยืนยัน",
            )}
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
              ? t("Selecting…", "กำลังเลือก…")
              : t("Select next batch", "เลือก batch ถัดไป")}
          </Button>
          <Button
            aria-label="Advance time"
            variant="outline"
            onClick={() => void act("advance")}
            disabled={Boolean(busy) || run.pending.length === 0}
          >
            <Clock3 size={16} />
            {t("Advance +1 step", "เลื่อนเวลา +1")}
          </Button>
          <Button
            aria-label="Finish campaign"
            variant="outline"
            onClick={() => void act("finish")}
            disabled={Boolean(busy) || run.done}
          >
            <FastForward size={16} />
            {busy === "finish"
              ? t("Running…", "กำลังรัน…")
              : t("Complete run", "รันจนจบ")}
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
            {t("Verify replay", "ตรวจ replay")}
          </Button>
          <Button
            aria-label="Reset campaign"
            variant="ghost"
            size="sm"
            onClick={() => void act("reset")}
            disabled={Boolean(busy)}
          >
            <RotateCcw size={15} />
            {t("Reset", "เริ่มใหม่")}
          </Button>
        </div>
      </div>
      <KpiStrip run={run} />
      <div className="lab-board">
        <section className="surface loop-surface">
          <div className="section-heading">
            <div>
              <h2>{t("The screening loop", "วงจรการคัดเลือกสาร")}</h2>
              <p>
                {t(
                  "Live counts from accepted requests and delivered events.",
                  "จำนวนจริงจากคำขอที่รับและเหตุการณ์ส่งคืนผล",
                )}
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
              <strong>{t("Budget ledger", "บัญชีงบทดสอบจำลอง")}</strong>
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
                {t("Spent", "จ่ายแล้ว")} <b>{m.spent_units}</b>
              </span>
              <span>
                <i className="legend-dot reserved" />
                {t("Reserved", "จองรอผล")} <b>{m.reserved_units}</b>
              </span>
              <span>
                <i className="legend-dot available" />
                {t("Available", "คงเหลือ")} <b>{m.remaining_units}</b>
              </span>
            </div>
          </div>
          <div className="chart-heading">
            <h3>{t("Confirmed discoveries", "ผล active ใหม่ที่ส่งคืนแล้ว")}</h3>
            <span className="muted small">
              {t(
                "No pending or predicted positives",
                "ไม่นับ pending หรือผลคาดการณ์",
              )}
            </span>
          </div>
          <DiscoveryChart reports={[r]} />
        </section>
        <aside className="surface pending-surface">
          <div className="section-heading">
            <h2>{t("Feedback queue", "คิวรอผล")}</h2>
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
                  {t("Due at step", "กำหนดส่งคืนขั้นที่")} {p.due_at_step}{" "}
                  <span>
                    · {p.due_at_step - m.step} {t("remaining", "ขั้นที่เหลือ")}
                  </span>
                </p>
              </div>
            ))
          ) : (
            <EmptyState
              title={
                run.done
                  ? t("Queue cleared", "ไม่มีผลค้าง")
                  : t("No assays in flight", "ยังไม่มี assay รอผล")
              }
              description={
                run.done
                  ? t(
                      "Every accepted request has a delivered or missing outcome.",
                      "ทุกคำขอมีผลส่งคืนหรือระบุว่าสูญหายแล้ว",
                    )
                  : t(
                      "Select a batch to reserve budget and schedule feedback.",
                      "เลือก batch เพื่อจองงบและกำหนดเวลารับผล",
                    )
              }
            />
          )}
          <div className="queue-footer">
            <CheckCircle2 size={15} />
            <span>
              {t("Missing outcomes", "ผลสูญหาย")}: {m.missing_assays}
              <br />
              {t("Initial seed hits", "Seed hits เดิม")}: {m.seed_hits} (
              {t("excluded", "ไม่นับใน hits ใหม่")})
            </span>
          </div>
        </aside>
      </div>
      <section className="surface decisions-section">
        <div className="section-heading">
          <div>
            <h2>{t("Policy decisions", "เหตุผลในการเลือกสาร")}</h2>
            <p>
              {t(
                "Actual model status, predicted probabilities and outcome visibility.",
                "สถานะโมเดล คะแนนคาดการณ์ และผลที่เปิดเผยจากการรันจริง",
              )}
            </p>
          </div>
          <span className="small-mono">{r.requests.length} requests</span>
        </div>
        {r.requests.length ? (
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label={t("Experiment decision table", "ตารางการตัดสินใจทดลอง")}
          >
            <table>
              <thead>
                <tr>
                  <th>{t("Compound", "สาร")}</th>
                  <th>{t("Observed status", "สถานะที่ทราบ")}</th>
                  <th>{t("Due step", "กำหนดส่งผล")}</th>
                  <th>P(active)</th>
                  <th>{t("Selection explanation", "คำอธิบายการเลือก")}</th>
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
                            ? t("Pending", "รอผล")
                            : outcomes.get(q.request_id)?.active === true
                              ? t("Observed active", "ทราบผล active")
                              : outcomes.get(q.request_id)?.active === false
                                ? t("Observed inactive", "ทราบผล inactive")
                                : t("Missing outcome", "ผลสูญหาย")}
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
            title={t(
              "Your next decision starts here",
              "เริ่มการเลือกสารที่นี่",
            )}
            description={t(
              "Select the first batch. Scores only appear when a valid model can be fitted.",
              "เลือก batch แรก คะแนนจะปรากฏเมื่อมีข้อมูลฝึกโมเดลได้จริง",
            )}
          />
        )}
      </section>
      <section className="surface timeline-section">
        <div className="section-heading">
          <div>
            <h2>{t("Event timeline", "บันทึกเหตุการณ์")}</h2>
            <p>
              {t(
                "Append-only scientific history. No future labels.",
                "ประวัติเหตุการณ์ตามลำดับ ไม่มี labels จากอนาคต",
              )}
            </p>
          </div>
          <Badge>{r.events.length} events</Badge>
        </div>
        <div className="filter-row">
          <div className="search-field">
            <Search size={16} />
            <input
              aria-label="Search event compound"
              placeholder={t("Search compound ID…", "ค้นหารหัสสาร…")}
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
              {t("All event types", "ทุกประเภทเหตุการณ์")}
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
          aria-label={t("Event timeline", "ลำดับเหตุการณ์")}
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
              {t("No events match this filter.", "ไม่มีเหตุการณ์ตรงกับตัวกรอง")}
            </p>
          )}
        </div>
        <p className="small muted">
          {t(
            "Showing up to 100 recent matching events. Export retains the complete public ledger.",
            "แสดงล่าสุดไม่เกิน 100 เหตุการณ์ ไฟล์ export เก็บ public ledger ครบทั้งหมด",
          )}
        </p>
      </section>
    </>
  );
}
