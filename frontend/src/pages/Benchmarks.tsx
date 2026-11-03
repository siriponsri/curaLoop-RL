import { useEffect, useState } from "react";
import { BarChart3, Download, Play, ShieldCheck } from "lucide-react";
import { api, comparisonExport } from "../api";
import { useApp } from "../state";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { PageHeading, SourceBadge } from "../components/shared";
import {
  DiscoveryChart,
  QueueChart,
  RecordedBenchmarkChart,
} from "../components/charts";
import { colors, policyNames, type Job, type Policy } from "../types";
import { number } from "../lib";

export default function Benchmarks() {
  const { run, evidence, t } = useApp();
  const [selected, setSelected] = useState<Policy[]>([
      "random",
      "greedy",
      "uncertainty",
    ]),
    [job, setJob] = useState<Job | null>(null),
    [jobId, setJobId] = useState<string | null>(null),
    [starting, setStarting] = useState(false),
    [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (!jobId) return;
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const j = await api.job(jobId!);
        if (!active) return;
        setJob(j);
        if (j.status === "failed") setError(j.error);
        if (j.status === "queued" || j.status === "running")
          timer = setTimeout(() => void poll(), 900);
      } catch (err) {
        if (active) setError((err as Error).message);
      }
    }
    void poll();
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [jobId]);
  if (!run) return null;
  const running =
    starting || job?.status === "running" || job?.status === "queued";
  async function start() {
    if (!run) return;
    setStarting(true);
    setError(null);
    setJob(null);
    try {
      const j = await api.compare(
        run.report.manifest.scenario_config,
        selected,
      );
      setJobId(j.job_id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStarting(false);
    }
  }
  return (
    <>
      <PageHeading
        title={t("Benchmark arena", "เปรียบเทียบนโยบาย")}
        description={t(
          "Matched conditions. Independent campaigns. Evidence you can export.",
          "เงื่อนไขเดียวกัน campaign แยกกัน และส่งออกหลักฐานได้",
        )}
      />
      <div className="presentation-origin">
        <SourceBadge />
      </div>
      <div className="surface benchmark-config">
        <div className="section-heading">
          <div>
            <h2>
              {t(
                "Run a matched comparison",
                "รันการเปรียบเทียบภายใต้เงื่อนไขเดียวกัน",
              )}
            </h2>
            <p>
              {t(
                "Uses the active scenario, including its unchanged seed.",
                "ใช้เงื่อนไข campaign ปัจจุบันและ seed เดิมโดยไม่เลือกเฉพาะผลที่สวย",
              )}
            </p>
          </div>
          <Badge className="badge-teal">
            <ShieldCheck size={13} />
            Shared initial conditions
          </Badge>
        </div>
        <div className="scenario-chips">
          <span>
            seed <b>{run.report.manifest.seed}</b>
          </span>
          <span>
            budget <b>{run.report.manifest.scenario_config.budget_units}</b>{" "}
            units
          </span>
          <span>
            capacity <b>{run.report.manifest.scenario_config.batch_size}</b>
          </span>
          <span>
            delay <b>{run.report.manifest.scenario_config.delay_steps}</b> steps
          </span>
          <span>
            seed labels <b>{run.report.manifest.initial_label_ids.length}</b>
          </span>
        </div>
        <div className="policy-picks">
          {(Object.keys(policyNames) as Policy[]).map((p) => (
            <label
              className={
                selected.includes(p) ? "policy-pick selected" : "policy-pick"
              }
              key={p}
            >
              <input
                type="checkbox"
                checked={selected.includes(p)}
                disabled={Boolean(running)}
                onChange={(e) =>
                  setSelected((old) =>
                    e.target.checked ? [...old, p] : old.filter((x) => x !== p),
                  )
                }
              />
              <span
                className="policy-color"
                style={{ background: colors[p] }}
              />
              <span>
                {policyNames[p]}
                {p === "q_learning" || p === "contextual_bandit" ? (
                  <small>Synthetic-trained · fallback disclosed</small>
                ) : (
                  <small>Baseline acquisition policy</small>
                )}
              </span>
            </label>
          ))}
        </div>
        <div className="comparison-start">
          <Button
            aria-label="Run comparison"
            disabled={Boolean(running) || !selected.length}
            onClick={() => void start()}
          >
            <Play size={16} />
            {running
              ? t("Running actual campaigns…", "กำลังรัน campaign จริง…")
              : t("Compare selected policies", "เปรียบเทียบนโยบายที่เลือก")}
          </Button>
          <span>
            {t(
              "CPU only · may take a minute · no paid calls",
              "ใช้ CPU ในเครื่อง · อาจใช้เวลาราวหนึ่งนาที · ไม่มีบริการเสียเงิน",
            )}
          </span>
        </div>
        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}
      </div>
      {running && (
        <div className="comparison-running" role="status">
          <div className="spinner" />
          <div>
            <strong>
              {t(
                "Independent engines are running",
                "กำลังรัน engine แยกกันสำหรับแต่ละนโยบาย",
              )}
            </strong>
            <p>
              {t(
                "Waiting for real results. No placeholder scores are displayed.",
                "กำลังรอผลจริง ระบบจะไม่แสดงคะแนนตัวอย่างระหว่างรอ",
              )}
            </p>
          </div>
        </div>
      )}
      {job?.status === "completed" && (
        <section className="surface benchmark-result">
          <div className="section-heading">
            <div>
              <h2>{t("Comparison complete", "เปรียบเทียบครบแล้ว")}</h2>
              <p>
                {job.reports.length}{" "}
                {t(
                  "independent campaigns · actual public event logs",
                  "campaign อิสระ · ผลจาก public event log จริง",
                )}
              </p>
            </div>
            <div className="button-row">
              {(["json", "csv"] as const).map((format) => (
                <Button variant="outline" size="sm" asChild key={format}>
                  <a href={comparisonExport(job.job_id, format)} download>
                    <Download size={14} />
                    {format.toUpperCase()}
                  </a>
                </Button>
              ))}
            </div>
          </div>
          <DiscoveryChart reports={job.reports} />
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label={t("Benchmark data table", "ตารางผลเปรียบเทียบ")}
          >
            <table>
              <thead>
                <tr>
                  <th>Policy</th>
                  <th>New hits</th>
                  <th>Delivered</th>
                  <th>Spent units</th>
                  <th>Sim. steps</th>
                  <th>Hit rate</th>
                  <th>Controller fallback</th>
                </tr>
              </thead>
              <tbody>
                {job.reports.map((r) => (
                  <tr key={r.manifest.policy_id}>
                    <td>
                      <span
                        className="policy-color"
                        style={{ background: colors[r.manifest.policy_id] }}
                      />
                      {policyNames[r.manifest.policy_id]}
                    </td>
                    <td>
                      <strong>{r.metrics.confirmed_hits}</strong>
                    </td>
                    <td>{r.metrics.delivered_assays}</td>
                    <td>{r.metrics.spent_units}</td>
                    <td>{r.metrics.step}</td>
                    <td>
                      {r.metrics.hit_rate === null
                        ? "—"
                        : `${number(100 * r.metrics.hit_rate, 1)}%`}
                    </td>
                    <td>
                      {r.metrics.controller_requests
                        ? `${r.metrics.controller_fallback_requests} / ${r.metrics.controller_requests}`
                        : "Not applicable"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="honesty-note">
            <ShieldCheck size={18} />
            <p>
              {t(
                "One seed is illustrative, not a general superiority claim. Unseen controller states use Greedy fallback; equal results do not prove learned transfer.",
                "ผลจาก seed เดียวเป็นเพียงตัวอย่าง ไม่ยืนยันความเหนือกว่า state ที่ไม่เคยฝึกใช้ Greedy fallback ผลเท่ากันจึงไม่พิสูจน์ learned transfer",
              )}
            </p>
          </div>
          <details>
            <summary>
              {t(
                "Inspect pending queue over simulated time",
                "ดูจำนวนผลค้างตามเวลาจำลอง",
              )}
            </summary>
            <QueueChart reports={job.reports} />
          </details>
        </section>
      )}
      {evidence && (
        <section className="surface recorded-benchmark">
          <div className="section-heading">
            <div>
              <h2>
                {t(
                  "The recorded research benchmark",
                  "ผล benchmark ที่บันทึกไว้ก่อนหน้า",
                )}
              </h2>
              <p>
                {t(
                  "v0.1 · 50 executed campaigns · 10 paired seeds · not a new execution by opening this page",
                  "v0.1 · รันจริง 50 campaigns · 10 paired seeds · การเปิดหน้านี้ไม่ได้รันประเมินใหม่",
                )}
              </p>
            </div>
            <BarChart3 size={23} />
          </div>
          <RecordedBenchmarkChart rows={evidence.statistics.summary} />
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label={t("Benchmark data table", "ตารางผลเปรียบเทียบ")}
          >
            <table>
              <thead>
                <tr>
                  <th>Policy</th>
                  <th>Seeds</th>
                  <th>Mean new hits</th>
                  <th>SD across seeds</th>
                  <th>Range</th>
                </tr>
              </thead>
              <tbody>
                {evidence.statistics.summary.map((r) => (
                  <tr key={r.policy}>
                    <td>{policyNames[r.policy]}</td>
                    <td>{r.n_seeds}</td>
                    <td>{r.mean_hits}</td>
                    <td>{number(r.sd_hits, 2)}</td>
                    <td>
                      {r.min_hits}–{r.max_hits}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="field-note">
            {t(
              "Error bars show seed standard deviation, not a confidence interval across biological targets.",
              "Error bars แสดงส่วนเบี่ยงเบนมาตรฐานระหว่าง seeds ไม่ใช่ช่วงความเชื่อมั่นระหว่าง biological targets",
            )}
          </p>
          <div className="honesty-note amber-note">
            <ShieldCheck size={18} />
            <p>
              {evidence.controller_historical_fallback}.{" "}
              {t(
                "No RL superiority or useful pharmaceutical transfer has been established.",
                "ยังไม่ยืนยันว่า RL เหนือกว่า baseline หรือถ่ายโอนสู่งานเภสัชกรรมได้",
              )}
            </p>
          </div>
        </section>
      )}
    </>
  );
}
