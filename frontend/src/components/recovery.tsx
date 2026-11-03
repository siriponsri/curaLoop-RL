import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../state";
import { policyNames, type SavedRuns as SavedRunsResponse } from "../types";
import { Button } from "./ui/button";

export function SnapshotImport() {
  const { importSnapshot, busy } = useApp();
  const [file, setFile] = useState<File | null>(null);
  const [working, setWorking] = useState(false);
  const [status, setStatus] = useState("");
  async function resume() {
    if (!file || working) return;
    setWorking(true); setStatus("");
    try {
      if (file.size > 10_000_000) throw new Error("JSON file exceeds 10 MB.");
      if (!(await importSnapshot(JSON.parse(await file.text())))) setStatus("Could not resume. Review the error above and retry when the local engine is ready.");
    } catch (err) { setStatus("Could not resume: " + (err as Error).message); }
    finally { setWorking(false); }
  }
  return <div className="snapshot-import">
    <label className="file-field">
      <span>{file?.name ?? "Choose a run JSON · max 10 MB"}</span>
      <input aria-label="Resume JSON file" type="file" accept=".json,application/json" onChange={event => { setFile(event.target.files?.[0] ?? null); setStatus(""); }} />
    </label>
    <Button variant="outline" disabled={!file || working || Boolean(busy)} onClick={() => void resume()}>{working ? "Validating…" : "Validate & resume"}</Button>
    {status && <p role="status" className="field-note">{status}</p>}
  </div>;
}

export function SavedRuns({ includeImport = false }: { includeImport?: boolean }) {
  const { run, openSaved, recoverSavedRevision, busy } = useApp();
  const [saved, setSaved] = useState<SavedRunsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [revisions, setRevisions] = useState<{ id: string; items: { revision: number; saved_at: string }[] } | null>(null);
  const [revision, setRevision] = useState(0);
  const refresh = useCallback(async () => {
    setError(null);
    try { setSaved(await api.runs()); }
    catch (err) { setError((err as Error).message); }
  }, []);
  useEffect(() => { void refresh(); }, [refresh, run?.session_id, run?.revision]);
  async function remove(id: string) {
    if (!window.confirm("Permanently delete this saved campaign and its local revisions? Export a single-run JSON first if you need a portable copy.")) return;
    setWorking(true);
    try { await api.deleteRun(id); await refresh(); }
    catch (err) { setError((err as Error).message); }
    finally { setWorking(false); }
  }
  async function inspectRevisions(id: string) {
    setWorking(true); setError(null);
    try {
      const result = await api.revisions(id);
      setRevisions({ id, items: result.items });
      setRevision(result.items[0]?.revision ?? 0);
    } catch (err) { setError((err as Error).message); }
    finally { setWorking(false); }
  }
  async function recover() {
    if (!revisions) return;
    setWorking(true); setError(null);
    try {
      if (await recoverSavedRevision(revisions.id, revision)) { setRevisions(null); await refresh(); }
    }
    catch (err) { setError((err as Error).message); }
    finally { setWorking(false); }
  }
  return <section className="surface saved-runs">
    <div className="section-heading"><div><h2>Saved campaigns & recovery</h2><p>Public snapshots are saved on this computer after accepted actions. Pending feedback resumes at its saved simulated step.</p></div><Button variant="outline" size="sm" disabled={working} onClick={() => void refresh()}>Refresh saved campaigns</Button></div>
    {error && <p className="error-message" role="alert">{error}</p>}
    {saved?.recovery_issues.map(issue => <div className="error-message" role="alert" key={issue.id + issue.kind}><p>{issue.message}</p><p className="small-mono break-text">{issue.id}</p><div className="button-row"><Button size="sm" variant="outline" disabled={working} onClick={() => void inspectRevisions(issue.id)}>Inspect saved revisions</Button><Button size="sm" variant="destructive" disabled={working || issue.id === run?.session_id} onClick={() => void remove(issue.id)}>Delete damaged campaign</Button></div></div>)}
    {saved && !saved.items.length && !saved.recovery_issues.length && <p>No saved campaigns yet. Create a scenario or restore a single-run JSON.</p>}
    {Boolean(saved?.items.length) && <div className="table-scroll" tabIndex={0} role="region" aria-label="Saved campaign table"><table><thead><tr><th>Campaign</th><th>State</th><th>Spent</th><th>Saved</th><th>Actions</th></tr></thead><tbody>{saved?.items.map(item => <tr key={item.session_id}><td><strong>{item.dataset.startsWith("hiv") ? "Historical HIV" : "Synthetic fixture"}</strong><br />{policyNames[item.policy]} · revision {item.revision}<br /><small className="small-mono">{item.session_id.slice(0, 12)}</small></td><td>{item.done ? "Completed" : `${item.pending_assays} pending`}{item.session_id === run?.session_id && " · current"}</td><td>{item.spent_units} units</td><td>{item.updated_at}</td><td><div className="button-row"><Button size="sm" variant="outline" disabled={working || Boolean(busy) || item.session_id === run?.session_id} onClick={() => void openSaved(item.session_id)}>Open campaign</Button><Button size="sm" variant="destructive" disabled={working || Boolean(busy) || item.session_id === run?.session_id} onClick={() => void remove(item.session_id)}>Delete saved campaign</Button></div></td></tr>)}</tbody></table></div>}
    {revisions && <div className="recovery-revisions"><h3>Recover a validated revision</h3><p>This creates an independent recovered campaign and retains the original record.</p>{revisions.items.length ? <><label htmlFor="recovery-revision">Saved revision</label><select id="recovery-revision" value={revision} onChange={event => setRevision(Number(event.target.value))}>{revisions.items.map(item => <option key={item.revision} value={item.revision}>Revision {item.revision} · {item.saved_at}</option>)}</select><Button disabled={working || Boolean(busy)} onClick={() => void recover()}>Recover selected revision</Button></> : <p>No local revision is available. Restore a portable single-run JSON instead.</p>}</div>}
    {includeImport && <><h3>Portable single-run JSON recovery</h3><p>Comparison JSON and CSV ledgers cannot resume one campaign.</p><SnapshotImport /></>}
  </section>;
}
