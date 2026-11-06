import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { api, ApiError } from "./api";
import { readPreference, removePreference, writePreference } from "./lib";
import type { DatasetInfo, Evidence, Meta, Policy, PolicyInfo, RunView, Scenario } from "./types";

export const defaultScenario: Scenario = {
  dataset: "hiv_moleculenet_replay_v1", seed: 42, candidate_count: 1200,
  initial_count: 48, budget_units: 30, batch_size: 5, delay_steps: 2,
  assay_cost_units: 1, delay_jitter: 0, missing_percent: 0,
};
interface Store {
  run: RunView | null;
  meta: Meta | null;
  datasets: DatasetInfo[];
  policies: PolicyInfo[];
  evidence: Evidence | null;
  loading: boolean;
  busy: string | null;
  error: string | null;
  notice: string | null;
  retry: () => void;
  clearError: () => void;
  create: (scenario: Scenario, policy: Policy) => Promise<boolean>;
  openSaved: (id: string) => Promise<boolean>;
  importSnapshot: (payload: unknown) => Promise<boolean>;
  recoverSavedRevision: (id: string, revision: number) => Promise<boolean>;
  act: (action: string) => Promise<void>;
}
const Context = createContext<Store | null>(null);
const message = (err: unknown) => err instanceof Error ? err.message : String(err);

export function AppProvider({ children }: { children: ReactNode }) {
  const [run, setRun] = useState<RunView | null>(null),
    [meta, setMeta] = useState<Meta | null>(null),
    [datasets, setDatasets] = useState<DatasetInfo[]>([]),
    [policies, setPolicies] = useState<PolicyInfo[]>([]),
    [evidence, setEvidence] = useState<Evidence | null>(null);
  const [loading, setLoading] = useState(true),
    [busy, setBusy] = useState<string | null>(null),
    [error, setError] = useState<string | null>(null),
    [notice, setNotice] = useState<string | null>(null);
  const inFlight = useRef(false);
  const acceptRun = useCallback((value: RunView) => {
    setRun(value);
    writePreference("curaloop-session", value.session_id);
  }, []);
  const retry = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    setLoading(true);
    setError(null);
    try {
      const [m, d, p, e] = await Promise.all([
        api.meta(), api.datasets(), api.policies(), api.evidence(),
      ]);
      setMeta(m); setDatasets(d); setPolicies(p); setEvidence(e);
      const id = readPreference("curaloop-session");
      let current: RunView | null = null;
      if (id) {
        try { current = await api.run(id); }
        catch (err) {
          // Only a genuinely absent ID permits selecting another saved run.
          // Corrupt/incompatible storage remains visible for explicit recovery.
          if (!(err instanceof ApiError && err.status === 404)) throw err;
          removePreference("curaloop-session");
          setNotice("The previous campaign is unavailable. Saved campaigns and portable JSON recovery are available in Research evidence.");
        }
      }
      if (!current) {
        const saved = await api.runs();
        if (saved.recovery_issues.length) {
          throw new Error("Saved-state recovery needs attention. " + saved.recovery_issues.map(issue => issue.message).join(" "));
        }
        current = saved.items.length ? await api.run(saved.items[0].session_id) : await api.create(defaultScenario, "greedy");
      }
      acceptRun(current);
    } catch (err) { setError(message(err)); }
    finally { inFlight.current = false; setLoading(false); }
  }, [acceptRun]);
  useEffect(() => { void retry(); }, [retry]);
  const create = useCallback(async (scenario: Scenario, policy: Policy) => {
    if (inFlight.current) return false;
    inFlight.current = true; setBusy("create"); setError(null);
    try {
      acceptRun(await api.create(scenario, policy));
      setNotice("Scenario applied · fresh independent campaign");
      return true;
    } catch (err) { setError(message(err)); return false; }
    finally { inFlight.current = false; setBusy(null); }
  }, [acceptRun]);
  const openSaved = useCallback(async (id: string) => {
    if (inFlight.current) return false;
    inFlight.current = true; setBusy("open"); setError(null);
    try {
      acceptRun(await api.run(id));
      setNotice("Saved campaign opened. Its public event history and pending queue were validated by the Python engine.");
      return true;
    } catch (err) { setError(message(err)); return false; }
    finally { inFlight.current = false; setBusy(null); }
  }, [acceptRun]);
  const importSnapshot = useCallback(async (payload: unknown) => {
    if (inFlight.current) return false;
    inFlight.current = true; setBusy("resume"); setError(null);
    try {
      acceptRun(await api.resume(payload));
      setNotice("Snapshot reconciled. Your campaign is ready in Simulation lab.");
      return true;
    } catch (err) { setError(message(err)); return false; }
    finally { inFlight.current = false; setBusy(null); }
  }, [acceptRun]);
  const recoverSavedRevision = useCallback(async (id: string, revision: number) => {
    if (inFlight.current) return false;
    inFlight.current = true; setBusy("recover"); setError(null);
    try {
      acceptRun(await api.recoverRevision(id, revision));
      setNotice("Recovered campaign opened. Your validated campaign is ready in Simulation lab.");
      return true;
    } catch (err) { setError(message(err)); return false; }
    finally { inFlight.current = false; setBusy(null); }
  }, [acceptRun]);
  const act = useCallback(async (action: string) => {
    if (!run || inFlight.current) return;
    inFlight.current = true; setBusy(action); setError(null);
    try {
      acceptRun(await api.action(run, action));
      setNotice(action === "replay" ? "Public event replay reconciled successfully." : null);
    } catch (err) {
      setError(message(err));
      if (err instanceof ApiError && err.status === 409) {
        try { acceptRun(await api.run(run.session_id)); }
        catch (refreshError) { setError(message(err) + " Refresh also failed: " + message(refreshError)); }
      }
    } finally { inFlight.current = false; setBusy(null); }
  }, [run, acceptRun]);
  return (
    <Context.Provider value={{ run, meta, datasets, policies, evidence, loading, busy, error, notice,
      retry, clearError: () => setError(null), create, openSaved, importSnapshot, recoverSavedRevision, act }}>
      {children}
    </Context.Provider>
  );
}
export function useApp() {
  const context = useContext(Context);
  if (!context) throw new Error("AppProvider required");
  return context;
}
