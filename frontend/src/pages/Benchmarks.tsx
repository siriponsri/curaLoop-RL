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
import { number, readPreference, removePreference, writePreference } from "../lib";

export default function Benchmarks() {
  const { run, evidence } = useApp();
  const [selected, setSelected] = useState<Policy[]>([
      "random",
      "greedy",
      "uncertainty",
    ]),
    [job, setJob] = useState<Job | null>(null),
    [jobId, setJobId] = useState<string | null>(() => readPreference("curaloop-comparison")),
    [starting, setStarting] = useState(false),
    [error, setError] = useState<string | null>(null),
    [pollVersion, setPollVersion] = useState(0),
    [history, setHistory] = useState<Job[]>([]),
    [historyError, setHistoryError] = useState<string | null>(null),
    [historyVersion, setHistoryVersion] = useState(0);
  useEffect(() => {
    let active = true;
    api.jobs().then(result => {
      if (!active) return;
      setHistory(result.items);
      setHistoryError(result.recovery_issues.length ? result.recovery_issues.map(issue => issue.message).join(" ") : null);
    }).catch(err => { if (active) setHistoryError((err as Error).message); });
    return () => { active = false; };
  }, [historyVersion, job?.status]);
  useEffect(() => {
    if (!jobId) return;
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const j = await api.job(jobId!);
        if (!active) return;
        setJob(j);
        setError(j.status === "failed" || j.status === "interrupted" ? j.error : null);
        if (j.status === "queued" || j.status === "running")
          timer = setTimeout(() => void poll(), 900);
      } catch (err) {
        if (active) {
          setError((err as Error).message);
          if (err instanceof Error && "status" in err && err.status === 404) removePreference("curaloop-comparison");
        }
      }
    }
    void poll();
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [jobId, pollVersion]);
  if (!run) return null;
  const running =
    starting || job?.status === "running" || job?.status === "queued" || Boolean(jobId && !job && !error);
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
      writePreference("curaloop-comparison", j.job_id);
      setJob({ job_id: j.job_id, status: "queued", scenario: run.report.manifest.scenario_config, policies: selected, reports: [], error: null });
      setJobId(j.job_id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setStarting(false);
    }
  }
  function openJob(id: string) {
    setError(null); setJob(null); setJobId(id); setPollVersion(value => value + 1);
    writePreference("curaloop-comparison", id);
  }
  async function deleteJob() {
    if (!job || !window.confirm("Delete this saved comparison? Download its JSON or CSV first if you need a portable copy.")) return;
    try {
      await api.deleteJob(job.job_id);
      removePreference("curaloop-comparison"); setJob(null); setJobId(null); setError(null);
      setHistoryVersion(value => value + 1);
    } catch (err) { setError((err as Error).message); }
  }
  return (
    <>
      <PageHeading
        title={"Benchmark arena"}
        description={"Matched conditions. Independent campaigns. Evidence you can export."}
      />
      <div className="presentation-origin">
        <SourceBadge />
      </div>
      <section className="surface comparison-history">
        <div className="section-heading"><div><h2>Saved comparisons</h2><p>Completed results survive restart. Interrupted jobs are recorded honestly and are never rerun automatically.</p></div><Button variant="outline" size="sm" onClick={() => setHistoryVersion(value => value + 1)}>Refresh comparison history</Button></div>
        {historyError && <p className="error-message" role="alert">{historyError}</p>}
        <label htmlFor="saved-comparison">Open a saved comparison</label>
        <select id="saved-comparison" value={history.some(item => item.job_id === jobId) ? jobId! : ""} onChange={event => { if (event.target.value) openJob(event.target.value); }}>
          <option value="">Choose a comparison</option>
          {history.map(item => <option key={item.job_id} value={item.job_id}>{item.scenario.dataset.startsWith("hiv") ? "Historical HIV" : "Synthetic fixture"} · seed {item.scenario.seed} · budget {item.scenario.budget_units} · {item.status} · {item.job_id.slice(0, 8)}</option>)}
        </select>
      </section>
      <div className="surface benchmark-config">
        <div className="section-heading">
          <div>
            <h2>
              {"Run a matched comparison"}
            </h2>
            <p>
              {"Uses the active scenario, including its unchanged seed."}
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
              ? "Running actual campaigns…"
              : "Compare selected policies"}
          </Button>
          <span>
            {"CPU only · may take a minute · no paid calls"}
          </span>
        </div>
        {error && (
          <div className="error-message" role="alert">
            {error}
            {jobId && <div className="button-row"><Button variant="outline" size="sm" onClick={() => { setError(null); setPollVersion(value => value + 1); }}>Retry comparison status</Button></div>}
          </div>
        )}
        {job?.status === "interrupted" && <p className="honesty-note-text">This comparison was interrupted. No completed results are claimed. Use the active scenario controls to explicitly start a new independent comparison.</p>}
        {job && ["completed", "failed", "interrupted"].includes(job.status) && <Button size="sm" variant="destructive" onClick={() => void deleteJob()}>Delete saved comparison</Button>}
      </div>
      {running && (
        <div className="comparison-running" role="status">
          <div className="spinner" />
          <div>
            <strong>
              {error ? "Comparison status needs attention" : "Independent engines are running"}
            </strong>
            <p>
              {"Waiting for real results. No placeholder scores are displayed."}
            </p>
          </div>
        </div>
      )}
      {job?.status === "completed" && (
        <section className="surface benchmark-result">
          <div className="section-heading">
            <div>
              <h2>{"Comparison complete"}</h2>
              <p><strong>{job.scenario.dataset.startsWith("hiv") ? "Historical assay data" : "Synthetic fixture"}</strong> · seed {job.scenario.seed} · budget {job.scenario.budget_units} units · capacity {job.scenario.batch_size} · delay {job.scenario.delay_steps} steps</p>
              <p>
                {job.reports.length}{" "}
                {"independent campaigns · actual public event logs"}
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
            aria-label={"Benchmark data table"}
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
                  <th>Learned action share</th>
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
                    <td>{r.metrics.controller_requests ? `${number(100 * (r.metrics.controller_requests - r.metrics.controller_fallback_requests) / r.metrics.controller_requests, 1)}% (${r.metrics.controller_requests - r.metrics.controller_fallback_requests} / ${r.metrics.controller_requests})` : "Not applicable"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="honesty-note">
            <ShieldCheck size={18} />
            <p>
              {"One seed is illustrative, not a general superiority claim. Unseen controller states use Greedy fallback; equal results do not prove learned transfer."}
            </p>
          </div>
          <details>
            <summary>
              {"Inspect pending queue over simulated time"}
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
                  {"Recorded HIV research benchmark"}
              </h2>
              <p>
                  {"Historical MoleculeNet HIV · v0.1 · 50 executed campaigns · 10 paired seeds · not a new execution by opening this page"}
              </p>
            </div>
            <BarChart3 size={23} />
          </div>
          <RecordedBenchmarkChart rows={evidence.statistics.summary} />
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label={"Benchmark data table"}
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
            {"Error bars show seed standard deviation, not a confidence interval across biological targets."}
          </p>
          <div className="honesty-note amber-note">
            <ShieldCheck size={18} />
            <p>
              {evidence.controller_historical_fallback}.{" "}
              {"No RL superiority or useful pharmaceutical transfer has been established."}
            </p>
          </div>
        </section>
      )}
    </>
  );
}
