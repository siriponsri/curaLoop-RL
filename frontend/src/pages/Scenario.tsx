import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  RotateCcw,
  SlidersHorizontal,
} from "lucide-react";
import { useApp, defaultScenario } from "../state";
import { PageHeading } from "../components/shared";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  policyNames,
  type Policy,
  type Scenario as ScenarioType,
} from "../types";

export function validateScenario(s: ScenarioType): string | null {
  if (!Number.isInteger(s.seed) || s.seed < 0 || s.seed > 4294967295)
    return "Seed must be an integer from 0 to 4294967295.";
  if (
    !Number.isInteger(s.budget_units) ||
    s.budget_units < 0 ||
    s.budget_units > 10000
  )
    return "Budget must be an integer from 0 to 10000.";
  if (s.initial_count > s.candidate_count || s.initial_count < 0)
    return "Initial labels cannot exceed the candidate pool.";
  for (const [key, min, max] of [
    ["initial_count", 0, 2000],
    ["batch_size", 1, 100],
    ["delay_steps", 0, 100],
    ["assay_cost_units", 1, 100],
    ["delay_jitter", 0, 20],
    ["missing_percent", 0, 100],
  ] as const) {
    if (!Number.isInteger(s[key]) || s[key] < min || s[key] > max)
      return `${key} must be an integer in [${min}, ${max}].`;
  }
  return null;
}
export default function ScenarioPage() {
  const { run, datasets, policies, create, busy } = useApp();
  const nav = useNavigate();
  const [draft, setDraft] = useState<ScenarioType>(
      run?.report.manifest.scenario_config ?? defaultScenario,
    ),
    [policy, setPolicy] = useState<Policy>(
      run?.report.manifest.policy_id ?? "greedy",
    ),
    [error, setError] = useState<string | null>(null);
  const change = (name: keyof ScenarioType, value: number) =>
    setDraft((old) => ({ ...old, [name]: value }));
  async function submit(e: FormEvent) {
    e.preventDefault();
    const err = validateScenario(draft);
    setError(err);
    if (!err && (await create(draft, policy))) nav("/lab");
  }
  const fields: [keyof ScenarioType, string, number, number][] = [
    ["seed", "Random seed", 0, 4294967295],
    ["budget_units", "Screening budget", 0, 10000],
    [
      "initial_count",
      "Initial labelled samples",
      0,
      draft.candidate_count,
    ],
    [
      "batch_size",
      "Concurrent assay capacity",
      1,
      100,
    ],
    ["delay_steps", "Feedback delay · steps", 0, 100],
    [
      "assay_cost_units",
      "Cost per assay · units",
      1,
      100,
    ],
  ];
  return (
    <>
      <PageHeading
        title={"Scenario builder"}
        description={"Change the constraints. Keep the comparison fair."}
      />
      <div className="scenario-layout">
        <form onSubmit={submit} noValidate className="surface scenario-form">
          <div className="form-section">
            <div className="form-section-heading">
              <DatabaseMark />
              <div>
                <h2>{"Research material"}</h2>
                <p>
                  {"No download or API key required."}
                </p>
              </div>
            </div>
            <label className="field-label" htmlFor="dataset">
              {"Dataset"}
            </label>
            <select
              id="dataset"
              value={draft.dataset}
              onChange={(e) => {
                const d = datasets.find((d) => d.id === e.target.value)!;
                setDraft({
                  ...draft,
                  dataset: d.id,
                  candidate_count: d.candidate_count,
                  initial_count: d.default_initial_count,
                });
              }}
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} · {d.candidate_count.toLocaleString()} candidates
                </option>
              ))}
            </select>
            <div className="dataset-description">
              <Badge
                className={
                  draft.dataset.startsWith("hiv") ? "badge-teal" : "badge-amber"
                }
              >
                {draft.dataset.startsWith("hiv")
                  ? "HISTORICAL_PUBLIC_DATA"
                  : "SYNTHETIC_ONLY"}
              </Badge>
              <span>
                {
                  datasets.find((d) => d.id === draft.dataset)
                    ?.feature_description
                }
              </span>
            </div>
          </div>
          <div className="form-section">
            <div className="form-section-heading">
              <SlidersHorizontal size={21} />
              <div>
                <h2>{"Campaign conditions"}</h2>
                <p>
                  {"Costs, capacity and time are scenario assumptions."}
                </p>
              </div>
            </div>
            <div className="form-grid">
              {fields.map(([key, en, min, max]) => (
                <div className="field" key={key}>
                  <label htmlFor={key}>{(en)}</label>
                  <input
                    id={key}
                    type="number"
                    min={min}
                    max={max}
                    step={1}
                    value={Number.isNaN(draft[key]) ? "" : draft[key]}
                    onChange={(e) =>
                      change(
                        key,
                        e.target.value === "" ? NaN : Number(e.target.value),
                      )
                    }
                  />
                </div>
              ))}
            </div>
          </div>
          <div className="form-section">
            <label className="field-label" htmlFor="policy">
              {"Selection policy"}
            </label>
            <select
              id="policy"
              value={policy}
              onChange={(e) => setPolicy(e.target.value as Policy)}
            >
              {policies.map((p) => (
                <option key={p.id} value={p.id}>
                  {policyNames[p.id]} · {p.status}
                </option>
              ))}
            </select>
            {policy === "q_learning" || policy === "contextual_bandit" ? (
              <p className="field-note amber-text">
                {"Trained on synthetic tasks. Unseen states use a labelled Greedy fallback; no validated pharmaceutical transfer."}
              </p>
            ) : (
              <p className="field-note">
                {"Predictive policies use only previously revealed labels. One-class data triggers a labelled random fallback."}
              </p>
            )}
          </div>
          <details className="advanced-settings">
            <summary>
              {"Advanced synthetic assumptions"}
            </summary>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="jitter">
                  {"Additional delay jitter · steps"}
                </label>
                <input
                  id="jitter"
                  type="number"
                  min={0}
                  max={20}
                  value={draft.delay_jitter}
                  onChange={(e) =>
                    change("delay_jitter", Number(e.target.value))
                  }
                />
              </div>
              <div className="field">
                <label htmlFor="missing">
                  {"Missing outcomes · %"}
                </label>
                <input
                  id="missing"
                  type="number"
                  min={0}
                  max={100}
                  value={draft.missing_percent}
                  onChange={(e) =>
                    change("missing_percent", Number(e.target.value))
                  }
                />
              </div>
            </div>
            <p className="field-note">
              {"Missing results consume cost. They are neither active hits nor inactive training labels."}
            </p>
          </details>
          {error && (
            <div role="alert" className="error-message">
              {error}
            </div>
          )}
          <div className="form-footer">
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setDraft(defaultScenario);
                setPolicy("greedy");
                setError(null);
              }}
            >
              <RotateCcw size={15} />
              {"Restore defaults"}
            </Button>
            <Button type="submit" disabled={Boolean(busy)}>
              {busy
                ? "Creating…"
                : "Create campaign"}
              <ArrowRight size={16} />
            </Button>
          </div>
        </form>
        <aside className="scenario-review">
          <Badge className="badge-teal">
            {"Before you begin"}
          </Badge>
          <h2>
            {"One scenario.\nA common starting point."}
          </h2>
          <dl className="scenario-numbers">
            <div>
              <dt>{"Available library"}</dt>
              <dd>{draft.candidate_count.toLocaleString()}</dd>
            </div>
            <div>
              <dt>{"Maximum new assays"}</dt>
              <dd>
                {Number.isFinite(draft.budget_units)
                  ? Math.min(
                      draft.candidate_count - draft.initial_count,
                      Math.floor(draft.budget_units / draft.assay_cost_units),
                    )
                  : "—"}
              </dd>
            </div>
            <div>
              <dt>{"Results become visible after"}</dt>
              <dd>
                {draft.delay_steps}
                <small>
                  {" "}
                  steps{draft.delay_jitter ? ` + 0–${draft.delay_jitter}` : ""}
                </small>
              </dd>
            </div>
          </dl>
          <ul className="check-list">
            {[
              "The same seed labels for every policy.",
              "Existing seed labels are sunk cost and excluded from new hits.",
              "Pending outcomes never train the predictor.",
              "A new scenario creates an independent run.",
            ].map((x) => (
              <li key={x}>
                <CheckCircle2 size={17} />
                {x}
              </li>
            ))}
          </ul>
          <p className="muted small">
            The current run is saved locally after each accepted action. Keep a single-run JSON as a portable recovery copy.
          </p>
        </aside>
      </div>
    </>
  );
}
function DatabaseMark() {
  return (
    <svg
      width="23"
      height="23"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      aria-hidden="true"
    >
      <ellipse cx="12" cy="5" rx="8" ry="3" />
      <path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0" />
    </svg>
  );
}
