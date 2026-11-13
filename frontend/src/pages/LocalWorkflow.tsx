import { useEffect, useState, type FormEvent } from "react";
import { ArrowDownToLine, ArrowRight, FileCode2, FlaskConical, History, Play, ShieldCheck, Upload } from "lucide-react";
import { Button } from "../components/ui/button";
import { useI18n } from "../i18n";
import "../local-workflow.css";

const base = "/api/v1/local-workflow";
const example = "compound_id,smiles\naspirin,CC(=O)Oc1ccccc1C(=O)O\ncaffeine,Cn1c(=O)c2c(ncn2C)n(C)c1=O\nethanol,CCO\nbenzene,c1ccccc1\nbenzoic_acid,O=C(O)c1ccccc1\ninvalid,bad!\nethanol,CCO\n";
type Parameters = { molecular_weight_max: number; logp_max: number; tpsa_max: number };
type Compound = { compound_id: string; canonical_smiles: string; molecular_weight: number; logp: number; tpsa: number; selected: boolean };
type Job = { job_id: string; state: string; revision: number; attempt: number; error: string | null; spec: { mode: string; goal: string; csv_text: string; parameters: Parameters }; parameters: Parameters | null; result: { counts: Record<string, number>; new_model_calls: number } | null; provider_calls: { call_id: string; status: string; tokens?: number }[]; events?: { revision: number; state: string; detail: string; utc: string }[]; data?: { compounds: Compound[]; rdkit_version: string } };
type Runtime = { model_session_authorized: boolean };
const terminal = (state: string) => ["COMPLETED", "FAILED", "CANCELLED", "INTERRUPTED", "ABSTAINED"].includes(state);
async function request<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(base + path, body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!response.ok) { const detail = await response.json().catch(() => ({})); throw new Error(typeof detail.detail === "string" ? detail.detail : `Request failed (${response.status})`); }
  return response.json() as Promise<T>;
}

export default function LocalWorkflow() {
  const { locale } = useI18n();
  const l = (en: string, th: string) => locale === "th" ? th : en;
  const [csv, setCsv] = useState(example), [goal, setGoal] = useState("Select compounds with molecular weight at most 100 g/mol. Keep other limits at the supplied defaults.");
  const [limits, setLimits] = useState<Parameters>({ molecular_weight_max: 500, logp_max: 5, tpsa_max: 140 });
  const [mode, setMode] = useState("deterministic"), [runtime, setRuntime] = useState<Runtime | null>(null);
  const [job, setJob] = useState<Job | null>(null), [saved, setSaved] = useState<Job[]>([]), [error, setError] = useState("");
  const [busy, setBusy] = useState(false), [query, setQuery] = useState(""), [selected, setSelected] = useState(0);
  const working = Boolean(job && !terminal(job.state));
  useEffect(() => {
    let live = true;
    request<Runtime>("/runtime").then(v => { if (live) setRuntime(v); }).catch(e => { if (live) setError(String(e.message)); });
    request<{ items: Job[] }>("/jobs").then(v => { if (live) setSaved(v.items); }).catch(e => { if (live) setError(String(e.message)); });
    return () => { live = false; };
  }, []);
  useEffect(() => {
    if (!job || terminal(job.state)) return;
    let live = true;
    const timer = setInterval(() => {
      request<Job>("/jobs/" + job.job_id).then(v => { if (live) { setJob(v); setSaved(old => [v, ...old.filter(s => s.job_id !== v.job_id)]); } }).catch(e => { if (live) { setError(String(e.message)); clearInterval(timer); } });
    }, 1200);
    return () => { live = false; clearInterval(timer); };
  }, [job]);
  async function start(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setSelected(0);
    try { const row = await request<Job>("/jobs", { csv_text: csv, goal, mode, locale, parameters: limits }); setJob(row); setSaved(old => [row, ...old]); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  async function open(id: string) {
    setBusy(true); setError(""); setSelected(0);
    try { const row = await request<Job>("/jobs/" + id); setJob(row); setCsv(row.spec.csv_text); setGoal(row.spec.goal); setLimits(row.spec.parameters); setMode(row.spec.mode); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  async function act(action: "cancel" | "resume") {
    if (!job) return;
    setBusy(true); setError("");
    try { setJob(await request<Job>(`/jobs/${job.job_id}/${action}`, { expected_revision: job.revision })); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  async function upload(file?: File) {
    if (!file) return;
    if (file.size > 1024 ** 2) { setError(l("CSV exceeds 1 MiB.", "ไฟล์ CSV ใหญ่เกิน 1 MiB")); return; }
    setCsv(await file.text()); setError("");
  }
  const compounds = job?.data?.compounds ?? [], compound = compounds[selected], counts = job?.result?.counts;
  const states: Record<string, string> = { QUEUED: l("Queued", "รอประมวลผล"), VALIDATING: l("Checking input", "ตรวจข้อมูล"), PLANNING: l("Model planning", "โมเดลกำหนดเงื่อนไข"), COMPUTING: l("RDKit computing", "RDKit กำลังคำนวณ"), VERIFYING: l("Verifying artifacts", "ตรวจหลักฐานและไฟล์"), REPORTING: l("Preparing report", "เตรียมรายงาน"), COMPLETED: l("Completed", "เสร็จสมบูรณ์"), FAILED: l("Failed", "ไม่สำเร็จ"), CANCELLED: l("Cancelled", "ยกเลิกแล้ว"), CANCEL_REQUESTED: l("Cancelling", "กำลังยกเลิก"), INTERRUPTED: l("Interrupted", "งานถูกขัดจังหวะ"), ABSTAINED: l("Outside scope", "อยู่นอกขอบเขต") };
  return <div className="local-workflow">
    <header className="workflow-heading"><div><span className="eyebrow">{l("MOLECULAR WORKFLOW / LOCAL", "เวิร์กโฟลว์โมเลกุล / บนเครื่อง")}</span><h1>{l("From compounds to a traceable report.", "จากสารเคมี สู่รายงานที่ตรวจสอบได้")}</h1><p>{l("Bring a CSV. Compute real molecular descriptors. Collect the evidence.", "นำเข้า CSV คำนวณคุณสมบัติโมเลกุลจริง และเก็บหลักฐานพร้อมรายงาน")}</p></div><span className="workflow-scope"><ShieldCheck size={16} />{l("Physicochemical analysis", "วิเคราะห์คุณสมบัติทางเคมี")}</span></header>
    <div className="workflow-layout"><section className="surface workflow-compose"><div className="section-heading"><h2>{l("Prepare your analysis", "เตรียมการวิเคราะห์")}</h2><FileCode2 size={18} /></div><form onSubmit={e => void start(e)}>
      <label htmlFor="workflow-csv">{l("Compound CSV", "ไฟล์สารเคมี CSV")}</label><p className="field-note">compound_id, smiles · {l("Up to 2,000 rows / 1 MiB", "สูงสุด 2,000 แถว / 1 MiB")}</p><textarea id="workflow-csv" className="workflow-csv" rows={9} value={csv} onChange={e => setCsv(e.target.value)} required disabled={working} spellCheck={false} />
      <label className="workflow-upload"><Upload size={14} />{l("Choose a CSV file", "เลือกไฟล์ CSV")}<input aria-label={l("Upload compound CSV", "นำเข้าไฟล์สารเคมี CSV")} type="file" accept=".csv,text/csv" disabled={working} onChange={e => void upload(e.target.files?.[0])} /></label>
      <label htmlFor="workflow-mode">{l("Execution", "วิธีประมวลผล")}</label><select id="workflow-mode" value={mode} onChange={e => setMode(e.target.value)} disabled={working}><option value="deterministic">{l("Explicit limits · no model", "ใช้ค่าที่กำหนด · ไม่เรียกโมเดล")}</option><option value="agent" disabled={!runtime?.model_session_authorized}>{l("Local model + RDKit tools", "โมเดลบนเครื่อง + เครื่องมือ RDKit")}</option></select>
      {mode === "agent" && <><label htmlFor="workflow-goal">{l("Filtering request", "คำขอคัดกรอง")}</label><textarea id="workflow-goal" rows={3} maxLength={2000} value={goal} onChange={e => setGoal(e.target.value)} disabled={working} /><p className="field-note">{l("The model translates numeric criteria; unspecified limits use the defaults below.", "โมเดลแปลคำขอเป็นเงื่อนไขตัวเลข ค่าที่ไม่ระบุจะใช้ค่าเริ่มต้นด้านล่าง")}</p></>}
      <fieldset disabled={working}><legend>{mode === "agent" ? l("Default limits", "ค่าเริ่มต้น") : l("Filter limits", "เกณฑ์คัดกรอง")}</legend><div className="workflow-limits">{([{ key: "molecular_weight_max", label: "MW ≤ (g/mol)", min: 1, max: 2000 }, { key: "logp_max", label: "LogP ≤", min: -20, max: 20 }, { key: "tpsa_max", label: "TPSA ≤ (Å²)", min: 0, max: 1000 }] as const).map(field => <label key={field.key} htmlFor={field.key}>{field.label}<input id={field.key} type="number" step="any" min={field.min} max={field.max} required value={Number.isNaN(limits[field.key]) ? "" : limits[field.key]} onChange={e => setLimits(old => ({ ...old, [field.key]: e.target.value === "" ? NaN : Number(e.target.value) }))} /></label>)}</div></fieldset>
      <Button type="submit" disabled={busy || working || !runtime || (mode === "agent" && !runtime.model_session_authorized)}><Play size={15} />{l("Run analysis", "เริ่มวิเคราะห์")}</Button><p className="field-note">{runtime?.model_session_authorized ? l("Authorized model session available. Health is confirmed only by a real response.", "มีสิทธิ์ใช้โมเดลในรอบนี้ ต้องรอคำตอบจริงเพื่อยืนยันการทำงาน") : l("Model session offline. Explicit-limit analysis remains available; no automatic provider fallback.", "โมเดลออฟไลน์ ยังวิเคราะห์ด้วยค่าที่กำหนดได้ ไม่มีการสลับผู้ให้บริการอัตโนมัติ")}</p>
    </form></section><section className="workflow-results">
      {error && <div role="alert" className="error-banner"><strong>{l("Analysis needs attention", "โปรดตรวจสอบงานวิเคราะห์")}</strong><p>{error}</p><Button variant="outline" size="sm" onClick={() => { setError(""); if (job) void open(job.job_id); }}>{l("Refresh saved state", "อ่านสถานะที่บันทึกใหม่")}</Button></div>}
      <div className="workflow-stats">{[["input_rows", l("Input rows", "แถวข้อมูล")], ["valid", l("Valid structures", "โครงสร้างถูกต้อง")], ["selected", l("Within limits", "ผ่านเกณฑ์")], ["rejected", l("Rejected rows", "แถวที่ปฏิเสธ")]].map(([key, label]) => <div className="surface" key={key}><span>{label}</span><strong>{counts?.[key] ?? "—"}</strong></div>)}</div>
      {!job ? <div className="surface workflow-empty"><FlaskConical size={38} strokeWidth={1.2} /><span className="eyebrow">CSV <ArrowRight size={12} /> RDKit <ArrowRight size={12} /> {l("REPORT", "รายงาน")}</span><h2>{l("Your analysis starts here.", "เริ่มงานวิเคราะห์ของคุณที่นี่")}</h2><p>{l("The supplied molecules are an editable author example. Counts and results appear only after actual computation.", "สารตัวอย่างแก้ไขได้ จำนวนและผลลัพธ์จะแสดงหลังจากคำนวณจริงเท่านั้น")}</p></div> : <>
        <section className="surface workflow-status" aria-live="polite"><div><span className="eyebrow">{l("SAVED EXECUTION", "สถานะที่บันทึก")}</span><h2>{states[job.state] ?? job.state}</h2><code>{job.job_id.slice(0, 8)} · {l("Attempt", "ครั้งที่")} {job.attempt} · {l("Revision", "รุ่น")} {job.revision}</code></div><div className="button-row">{working && <Button variant="outline" disabled={busy || job.state === "CANCEL_REQUESTED"} onClick={() => void act("cancel")}>{l("Cancel", "ยกเลิก")}</Button>}{["INTERRUPTED", "CANCELLED"].includes(job.state) && <Button variant="outline" disabled={busy} onClick={() => void act("resume")}>{l("Resume as new attempt", "ทำต่อเป็นครั้งใหม่")}</Button>}{job.state === "COMPLETED" && <a className="workflow-download" href={`${base}/jobs/${job.job_id}/artifacts/bundle.zip`}><ArrowDownToLine size={15} />{l("Download bundle", "ดาวน์โหลดชุดผลลัพธ์")}</a>}</div></section>
        {working && <p role="status" className="field-note">{l("Actual work is running. Cancellation may wait for an in-flight model response. Closing this tab does not cancel the job.", "กำลังประมวลผลจริง การยกเลิกอาจต้องรอโมเดลตอบ การปิดหน้านี้จะไม่ยกเลิกงาน")}</p>}
        {job.error && <div className="error-banner" role="alert"><strong>{l("Retained execution issue", "บันทึกปัญหาการทำงาน")}</strong><p>{job.error}</p><p>{l("No mock result or automatic rerun was used.", "ไม่มีการใช้ผลจำลองหรือรันซ้ำอัตโนมัติ")}</p></div>}
        {job.data && <section className="surface workflow-compounds"><div className="section-heading"><div><h2>{l("Computed compounds", "สารที่คำนวณแล้ว")}</h2><p>RDKit {job.data.rdkit_version} · {l("Current artifact checks passed", "ไฟล์ผลลัพธ์ผ่านการตรวจรุ่นปัจจุบัน")}</p></div><ShieldCheck size={19} /></div><label className="workflow-search" htmlFor="workflow-search">{l("Find a compound", "ค้นหาสาร")}<input id="workflow-search" type="search" placeholder={l("Search by ID or SMILES", "ค้นด้วยรหัสหรือ SMILES")} value={query} onChange={e => setQuery(e.target.value)} /></label><div className="workflow-compound-grid"><div className="table-scroll" tabIndex={0} role="region" aria-label={l("Computed descriptor table", "ตารางคุณสมบัติที่คำนวณ")}><table><thead><tr><th>{l("Compound", "สาร")}</th><th>MW</th><th>LogP</th><th>TPSA</th><th>{l("Filter", "เกณฑ์")}</th></tr></thead><tbody>{compounds.map((c, index) => ({ c, index })).filter(({ c }) => `${c.compound_id} ${c.canonical_smiles}`.toLowerCase().includes(query.toLowerCase())).map(({ c, index }) => <tr key={index} className={index === selected ? "workflow-row-active" : ""}><th scope="row"><button type="button" aria-pressed={index === selected} onClick={() => setSelected(index)}>{c.compound_id}</button></th><td>{c.molecular_weight.toFixed(2)}</td><td>{c.logp.toFixed(2)}</td><td>{c.tpsa.toFixed(2)}</td><td>{c.selected ? l("Within", "ผ่าน") : l("Outside", "ไม่ผ่าน")}</td></tr>)}</tbody></table></div>{compound && <figure className="workflow-molecule"><img src={`${base}/jobs/${job.job_id}/structures/${selected}`} alt={l(`2D structure of ${compound.compound_id}`, `โครงสร้าง 2 มิติของ ${compound.compound_id}`)} /><figcaption><strong>{compound.compound_id}</strong><code>{compound.canonical_smiles}</code></figcaption></figure>}</div><p className="field-note">{l("MW: g/mol · LogP: dimensionless · TPSA: Å². Rejected rows and reasons are in rejected.csv.", "MW: g/mol · LogP: ไม่มีหน่วย · TPSA: Å² แถวที่ไม่รับและเหตุผลอยู่ใน rejected.csv")}</p><div className="workflow-links">{["report.html", "selected.csv", "rejected.csv", "evidence.json", "manifest.json"].map(name => <a key={name} href={`${base}/jobs/${job.job_id}/artifacts/${name}`} target="_blank" rel="noreferrer">{name}<ArrowRight size={12} /></a>)}</div></section>}
        {job.parameters && <details className="surface workflow-detail"><summary>{l("Applied numeric limits", "เงื่อนไขตัวเลขที่ใช้จริง")}</summary><pre>{JSON.stringify(job.parameters, null, 2)}</pre></details>}
        <details className="surface workflow-detail"><summary>{l("Execution and evidence trail", "ลำดับการทำงานและหลักฐาน")} · {job.events?.length ?? 0}</summary><ol>{job.events?.map(event => <li key={event.revision}><strong>{states[event.state] ?? event.state}</strong><time>{new Date(event.utc).toLocaleTimeString(locale === "th" ? "th-TH" : "en-GB")}</time><p>{event.detail}</p></li>)}</ol><p>{l("Real provider attempts", "จำนวนการเรียกโมเดลจริง")}: {job.provider_calls.length} · {l("Recorded generated tokens", "โทเคนคำตอบที่บันทึก")}: {job.provider_calls.reduce((sum, c) => sum + (c.tokens ?? 0), 0)}</p><p className="field-note">{l("Technical trace messages retain their original English text.", "ข้อความเทคนิคในบันทึกคงภาษาอังกฤษต้นฉบับ")}</p></details>
      </>}
      <section className="surface workflow-history"><h2><History size={16} />{l("Saved analyses", "งานที่บันทึกไว้")}</h2>{saved.length ? <div>{saved.map(s => <button type="button" key={s.job_id} disabled={busy || working} onClick={() => void open(s.job_id)}><code>{s.job_id.slice(0, 8)}</code><span>{states[s.state] ?? s.state}</span><ArrowRight size={14} /></button>)}</div> : <p className="field-note">{l("No saved analyses yet.", "ยังไม่มีงานที่บันทึก")}</p>}</section>
    </section></div>
    <aside className="workflow-boundary"><ShieldCheck size={18} /><div><strong>{l("What this result means", "ขอบเขตของผลลัพธ์")}</strong><p>{l("Descriptor filters are not biological activity, safety or clinical efficacy predictions. The model has two bounded roles: numeric criteria and export acknowledgement. External agent comparison was not run because native benchmark admission did not pass; superiority and user benefit are unestablished.", "เกณฑ์คุณสมบัติโมเลกุลไม่ใช่การทำนายฤทธิ์ ความปลอดภัย หรือประสิทธิผลทางคลินิก โมเดลทำหน้าที่แปลเงื่อนไขตัวเลขและยืนยันการส่งออกเท่านั้น ยังไม่ได้รันการเปรียบเทียบ agent ภายนอก เพราะข้อมูลไม่ผ่านด่านความพร้อม จึงยังสรุปความเหนือกว่าหรือประโยชน์ต่อผู้ใช้ไม่ได้")}</p></div></aside>
  </div>;
}
