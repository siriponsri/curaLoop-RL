import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { api, ApiError } from "./api";
import type {
  DatasetInfo,
  Evidence,
  Meta,
  Policy,
  PolicyInfo,
  RunView,
  Scenario,
} from "./types";

export const defaultScenario: Scenario = {
  dataset: "hiv_moleculenet_replay_v1",
  seed: 42,
  candidate_count: 1200,
  initial_count: 48,
  budget_units: 30,
  batch_size: 5,
  delay_steps: 2,
  assay_cost_units: 1,
  delay_jitter: 0,
  missing_percent: 0,
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
  lang: "en" | "th";
  setLang: (lang: "en" | "th") => void;
  t: (en: string, th: string) => string;
  retry: () => void;
  clearError: () => void;
  create: (scenario: Scenario, policy: Policy) => Promise<boolean>;
  act: (action: string) => Promise<void>;
  setRun: (run: RunView) => void;
}
const Context = createContext<Store | null>(null);
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
  const [lang, setLanguage] = useState<"en" | "th">(
    localStorage.getItem("curaloop-language") === "th" ? "th" : "en",
  );
  const setLang = useCallback((value: "en" | "th") => {
    setLanguage(value);
    localStorage.setItem("curaloop-language", value);
    document.documentElement.lang = value;
  }, []);
  const t = useCallback(
    (en: string, th: string) => (lang === "th" ? th : en),
    [lang],
  );
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);
  const acceptRun = useCallback((value: RunView) => {
    setRun(value);
    localStorage.setItem("curaloop-session", value.session_id);
  }, []);
  const retry = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [m, d, p, e] = await Promise.all([
        api.meta(),
        api.datasets(),
        api.policies(),
        api.evidence(),
      ]);
      setMeta(m);
      setDatasets(d);
      setPolicies(p);
      setEvidence(e);
      const id = localStorage.getItem("curaloop-session");
      let current: RunView;
      try {
        current = id
          ? await api.run(id)
          : await api.create(defaultScenario, "greedy");
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          current = await api.create(defaultScenario, "greedy");
          setNotice(
            "Local server restarted. A fresh run was created; JSON exports can be resumed.",
          );
        } else throw err;
      }
      acceptRun(current);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, [acceptRun]);
  useEffect(() => {
    void retry();
  }, [retry]);
  const create = useCallback(
    async (scenario: Scenario, policy: Policy) => {
      setBusy("create");
      setError(null);
      try {
        acceptRun(await api.create(scenario, policy));
        setNotice("Scenario applied · fresh independent campaign");
        return true;
      } catch (err) {
        setError((err as Error).message);
        return false;
      } finally {
        setBusy(null);
      }
    },
    [acceptRun],
  );
  const act = useCallback(
    async (action: string) => {
      if (!run || busy) return;
      setBusy(action);
      setError(null);
      try {
        acceptRun(await api.action(run, action));
        setNotice(
          action === "replay"
            ? "Public event replay reconciled successfully."
            : null,
        );
      } catch (err) {
        setError((err as Error).message);
        if (err instanceof ApiError && err.status === 409) {
          acceptRun(await api.run(run.session_id));
        }
      } finally {
        setBusy(null);
      }
    },
    [run, busy, acceptRun],
  );
  return (
    <Context.Provider
      value={{
        run,
        meta,
        datasets,
        policies,
        evidence,
        loading,
        busy,
        error,
        notice,
        lang,
        setLang,
        t,
        retry,
        clearError: () => setError(null),
        create,
        act,
        setRun: acceptRun,
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useApp() {
  const context = useContext(Context);
  if (!context) throw new Error("AppProvider required");
  return context;
}
