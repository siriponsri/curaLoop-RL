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

export function validateScenario(s: ScenarioType, thai = false): string | null {
  if (!Number.isInteger(s.seed) || s.seed < 0 || s.seed > 4294967295)
    return thai
      ? "เมล็ดสุ่มต้องเป็นจำนวนเต็มตั้งแต่ 0 ถึง 4294967295"
      : "Seed must be an integer from 0 to 4294967295.";
  if (
    !Number.isInteger(s.budget_units) ||
    s.budget_units < 0 ||
    s.budget_units > 10000
  )
    return thai
      ? "งบจำลองต้องเป็นจำนวนเต็มตั้งแต่ 0 ถึง 10000"
      : "Budget must be an integer from 0 to 10000.";
  if (s.initial_count > s.candidate_count || s.initial_count < 0)
    return thai
      ? "จำนวนข้อมูลตั้งต้นต้องไม่เกินจำนวนสารในชุดข้อมูล และต้องไม่ติดลบ"
      : "Initial labels cannot exceed the candidate pool.";
  for (const [key, min, max] of [
    ["initial_count", 0, 2000],
    ["batch_size", 1, 100],
    ["delay_steps", 0, 100],
    ["assay_cost_units", 1, 100],
    ["delay_jitter", 0, 20],
    ["missing_percent", 0, 100],
  ] as const) {
    if (!Number.isInteger(s[key]) || s[key] < min || s[key] > max)
      return thai
        ? `${key} ต้องเป็นจำนวนเต็มตั้งแต่ ${min} ถึง ${max}`
        : `${key} must be an integer in [${min}, ${max}].`;
  }
  return null;
}
export default function ScenarioPage() {
  const { run, datasets, policies, create, busy, t } = useApp();
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
    const err = validateScenario(draft, t("en", "th") === "th");
    setError(err);
    if (!err && (await create(draft, policy))) nav("/lab");
  }
  const fields: [keyof ScenarioType, string, string, number, number][] = [
    ["seed", "Random seed", "เมล็ดสุ่ม", 0, 4294967295],
    ["budget_units", "Screening budget", "งบทดสอบจำลอง", 0, 10000],
    [
      "initial_count",
      "Initial labelled samples",
      "ข้อมูลตั้งต้นที่รู้ผล",
      0,
      draft.candidate_count,
    ],
    [
      "batch_size",
      "Concurrent assay capacity",
      "จำนวน assay ที่รอผลได้พร้อมกัน",
      1,
      100,
    ],
    ["delay_steps", "Feedback delay · steps", "เวลารอผล · ขั้นจำลอง", 0, 100],
    [
      "assay_cost_units",
      "Cost per assay · units",
      "ต้นทุนต่อ assay · หน่วยจำลอง",
      1,
      100,
    ],
  ];
  return (
    <>
      <PageHeading
        title={t("Scenario builder", "ออกแบบเงื่อนไขการจำลอง")}
        description={t(
          "Change the constraints. Keep the comparison fair.",
          "ปรับเงื่อนไขการทำงาน และรักษาความยุติธรรมในการเปรียบเทียบ",
        )}
      />
      <div className="scenario-layout">
        <form onSubmit={submit} noValidate className="surface scenario-form">
          <div className="form-section">
            <div className="form-section-heading">
              <DatabaseMark />
              <div>
                <h2>{t("Research material", "ข้อมูลสำหรับการศึกษา")}</h2>
                <p>
                  {t(
                    "No download or API key required.",
                    "ใช้ข้อมูลที่รวมไว้ในเครื่อง ไม่ต้องดาวน์โหลดหรือใช้ API key",
                  )}
                </p>
              </div>
            </div>
            <label className="field-label" htmlFor="dataset">
              {t("Dataset", "ชุดข้อมูล")}
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
                <h2>{t("Campaign conditions", "เงื่อนไข campaign")}</h2>
                <p>
                  {t(
                    "Costs, capacity and time are scenario assumptions.",
                    "ต้นทุน ความจุ และเวลา เป็นสมมติฐานจำลอง",
                  )}
                </p>
              </div>
            </div>
            <div className="form-grid">
              {fields.map(([key, en, th, min, max]) => (
                <div className="field" key={key}>
                  <label htmlFor={key}>{t(en, th)}</label>
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
              {t("Selection policy", "วิธีเลือกสาร")}
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
                {t(
                  "Trained on synthetic tasks. Unseen states use a labelled Greedy fallback; no validated pharmaceutical transfer.",
                  "ฝึกบนโจทย์สังเคราะห์ state ที่ไม่เคยฝึกจะใช้ Greedy fallback ยังไม่ยืนยันการถ่ายโอนไปงานเภสัชกรรม",
                )}
              </p>
            ) : (
              <p className="field-note">
                {t(
                  "Predictive policies use only previously revealed labels. One-class data triggers a labelled random fallback.",
                  "ใช้เฉพาะผลที่เปิดเผยแล้ว หากมีคลาสเดียวจะระบุการใช้ random fallback",
                )}
              </p>
            )}
          </div>
          <details className="advanced-settings">
            <summary>
              {t("Advanced synthetic assumptions", "สมมติฐานจำลองเพิ่มเติม")}
            </summary>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="jitter">
                  {t(
                    "Additional delay jitter · steps",
                    "เวลารอเพิ่มต่อสาร · ขั้นจำลอง",
                  )}
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
                  {t("Missing outcomes · %", "ผลสูญหายจำลอง · %")}
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
              {t(
                "Missing results consume cost. They are neither active hits nor inactive training labels.",
                "ผลสูญหายใช้ต้นทุน แต่ไม่นับเป็น active hit หรือ inactive label",
              )}
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
              {t("Restore defaults", "คืนค่าเริ่มต้น")}
            </Button>
            <Button type="submit" disabled={Boolean(busy)}>
              {busy
                ? t("Creating…", "กำลังสร้าง…")
                : t("Create campaign", "สร้าง campaign")}
              <ArrowRight size={16} />
            </Button>
          </div>
        </form>
        <aside className="scenario-review">
          <Badge className="badge-teal">
            {t("Before you begin", "ก่อนเริ่มจำลอง")}
          </Badge>
          <h2>
            {t(
              "One scenario.\nA common starting point.",
              "เงื่อนไขเดียวกัน\nจุดเริ่มต้นที่เท่ากัน",
            )}
          </h2>
          <dl className="scenario-numbers">
            <div>
              <dt>{t("Available library", "ขนาดกลุ่มสาร")}</dt>
              <dd>{draft.candidate_count.toLocaleString()}</dd>
            </div>
            <div>
              <dt>{t("Maximum new assays", "ทดสอบใหม่ได้สูงสุด")}</dt>
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
              <dt>{t("Results become visible after", "เปิดผลหลังผ่านเวลา")}</dt>
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
              t(
                "The same seed labels for every policy.",
                "ทุก policy ได้ seed labels ชุดเดียวกัน",
              ),
              t(
                "Existing seed labels are sunk cost and excluded from new hits.",
                "seed labels เป็นต้นทุนเดิม ไม่นับใน hits ใหม่",
              ),
              t(
                "Pending outcomes never train the predictor.",
                "ผลที่ยังรอไม่ถูกนำไปฝึกโมเดล",
              ),
              t(
                "A new scenario creates an independent run.",
                "เงื่อนไขใหม่สร้าง run ที่แยกจากเดิม",
              ),
            ].map((x) => (
              <li key={x}>
                <CheckCircle2 size={17} />
                {x}
              </li>
            ))}
          </ul>
          <p className="muted small">
            {t(
              "The current run is kept in server memory. Export a snapshot before restarting the local service.",
              "run เก็บในหน่วยความจำ ควร export snapshot ก่อนเริ่ม local service ใหม่",
            )}
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
