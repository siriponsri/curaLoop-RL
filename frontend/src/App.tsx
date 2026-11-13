import { Component, lazy, Suspense, useRef, useState, type ReactNode } from "react";
import { NavLink, Route, Routes, useLocation, Link } from "react-router-dom";
import {
  BarChart3,
  Bot,
  BookOpen,
  ChevronRight,
  FileCheck,
  FlaskConical,
  LayoutDashboard,
  Menu,
  Microscope,
  Presentation,
  Settings2,
  ShieldCheck,
  Wifi,
  X,
} from "lucide-react";
import { useApp } from "./state";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import { Dialog } from "./components/ui/dialog";
import { SavedRuns } from "./components/recovery";
import { I18nProvider, LanguageSwitch, useI18n } from "./i18n";
import { useWorkspaceMotion } from "./motion";
const Overview = lazy(() => import("./pages/Overview"));
const Scenario = lazy(() => import("./pages/Scenario"));
const Lab = lazy(() => import("./pages/Lab"));
const Compounds = lazy(() => import("./pages/Compounds"));
const Benchmarks = lazy(() => import("./pages/Benchmarks"));
const Evidence = lazy(() => import("./pages/Evidence"));
const Confirmation = lazy(() => import("./pages/Confirmation"));
const AgentMission = lazy(() => import("./pages/AgentMission"));
const LocalWorkflow = lazy(() => import("./pages/LocalWorkflow"));
const GuidedPresentation = lazy(() => import("./pages/Presentation"));

const pages = [
  { path: "/workflow", en: "Molecular workflow", icon: FlaskConical },
  { path: "/", en: "Discovery overview", icon: LayoutDashboard },
  { path: "/lab", en: "Simulation lab", icon: FlaskConical },
  { path: "/benchmarks", en: "Benchmark arena", icon: BarChart3 },
  {
    path: "/compounds",
    en: "Compound explorer",
    icon: Microscope,
  },
  {
    path: "/scenario",
    en: "Scenario builder",
    icon: Settings2,
  },
  {
    path: "/evidence",
    en: "Research evidence",
    icon: BookOpen,
  },
  {
    path: "/confirmation",
    en: "Confirmation evidence",
    icon: FileCheck,
  },
  { path: "/agent", en: "Agent mission control", icon: Bot },
  {
    path: "/presentation",
    en: "Guided presentation",
    icon: Presentation,
  },
];

export default function App() {
  return <I18nProvider><Workspace /></I18nProvider>;
}
function Workspace() {
  const { t } = useI18n();
  const store = useApp();
  const { run, meta, loading, error, notice, busy } = store;
  const { pathname } = useLocation();
  const content = useRef<HTMLElement>(null);
  useWorkspaceMotion(content, pathname);
  const [mobile, setMobile] = useState(false);
  const active = pages.find((p) => p.path === pathname);
  function navigation() {
    return (
      <>
        <Link to="/" className="brand-link" onClick={() => setMobile(false)}>
          <img src="/brand/logo-v2.png" alt={t("CuraLoop-RL")} />
        </Link>
        <nav className="main-nav" aria-label={t("Main navigation")}>
          {pages.map((p, i) => (
            <div key={p.path}>
              {i === 4 && <div className="nav-divider" />}
              <NavLink
                to={p.path}
                aria-label={t(p.en)}
                end={p.path === "/"}
                onClick={() => setMobile(false)}
                className={({ isActive }) =>
                  isActive ? "nav-item nav-active" : "nav-item"
                }
              >
                <p.icon size={19} />
                <span>{t(p.en)}</span>
                {p.path === "/lab" && run?.pending.length ? (
                  <Badge>{run.pending.length}</Badge>
                ) : null}
              </NavLink>
            </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <span className="status-dot" />
          {t("Local research workspace")}<small>{t("v")}{meta?.web_version ?? "0.3.0"}</small>
        </div>
      </>
    );
  }
  return (
    <div className="app-shell dashboard-shell">
      <a href="#main-content" className="skip-link">
        {t("Skip to content")}</a>
      <aside className="sidebar">{navigation()}</aside>
      <Dialog
        open={mobile}
        onOpenChange={setMobile}
        title={t("Research workspace")}
        description={t("CuraLoop-RL navigation")}
      >
        <div className="mobile-navigation">{navigation()}</div>
      </Dialog>
      <div className="main-shell">
        <header className="topbar">
          <div className="topbar-path">
            <button
              className="mobile-menu icon-button"
              onClick={() => setMobile(true)}
              aria-label={t("Open navigation")}
            >
              <Menu size={21} />
            </button>
            <span>{t("Workspace")}</span>
            <ChevronRight size={13} />
            <strong>{active ? t(active.en) : t("Not found")}</strong>
          </div>
          <div className="topbar-controls">
            <LanguageSwitch />
            <span className="connection-pill">
              <Wifi size={13} />
              {loading ? t("Connecting") : !meta ? t("Connection unavailable") : t("Local API")}
            </span>
          </div>
        </header>
        <main id="main-content" className="main-content" ref={content}>
          {error && (
            <div className="error-banner" role="alert">
              <div>
                <strong>
                  {t("The action could not be completed")}
                </strong>
                <p>{error}</p>
              </div>
              <div className="button-row">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => void store.retry()}
                >
                  {t("Reconnect")}
                </Button>
                <button
                  aria-label={t("Dismiss error")}
                  onClick={store.clearError}
                  className="icon-button"
                >
                  <X size={17} />
                </button>
              </div>
            </div>
          )}
          {notice && !error && (
            <div role="status" className="notice-banner">
              <CheckMark />
              {t(notice)}
            </div>
          )}
          {pathname === "/confirmation" || pathname === "/agent" || pathname === "/workflow" ? (
            <RouteBoundary key={pathname} fallback={<RouteError />}>
              <Suspense fallback={<div className="loading-panel" role="status">{t("Loading workspace…")}</div>}>
                {pathname === "/workflow" ? <LocalWorkflow /> : pathname === "/agent" ? <AgentMission /> : <Confirmation />}
              </Suspense>
            </RouteBoundary>
          ) : loading ? (
            <div className="initial-loading">
              <div className="spinner" />
              <h1>
                {t("Connecting your research workspace")}
              </h1>
              <p>
                {t("Loading public metadata and the current local campaign.")}
              </p>
            </div>
          ) : !run && pathname === "/scenario" ? (
            <RouteBoundary key="empty-scenario" fallback={<RouteError />}>
              <Suspense fallback={<div className="loading-panel" role="status">{t("Loading workspace…")}</div>}>
                <Scenario />
              </Suspense>
            </RouteBoundary>
          ) : !run ? (
            <SavedRuns includeImport />
          ) : (
            <RouteBoundary key={pathname + run.session_id} fallback={<RouteError />}>
            <Suspense fallback={<div className="loading-panel" role="status">{t("Loading workspace…")}</div>}>
            <Routes key={run.session_id}>
              <Route path="/" element={<Overview />} />
              <Route path="/scenario" element={<Scenario />} />
              <Route path="/lab" element={<Lab />} />
              <Route path="/compounds" element={<Compounds />} />
              <Route path="/benchmarks" element={<Benchmarks />} />
              <Route path="/evidence" element={<Evidence />} />
              <Route path="/presentation" element={<GuidedPresentation />} />
              <Route
                path="*"
                element={
                  <div className="empty-state">
                    <h1>{t("Page not found")}</h1>
                    <Button asChild>
                      <Link to="/">{t("Back to overview")}</Link>
                    </Button>
                  </div>
                }
              />
            </Routes>
            </Suspense>
            </RouteBoundary>
          )}
        </main>
        <footer className="app-footer">
          <span>
            <ShieldCheck size={14} />
            {t("Independent research prototype")}
          </span>
        </footer>
      </div>
      {busy && (
        <div className="operation-indicator" role="status">
          <span className="spinner small-spinner" />
          {t("Running the local engine…")}
        </div>
      )}
    </div>
  );
}
function CheckMark() {
  return <ShieldCheck size={16} />;
}
class RouteBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}
function RouteError() {
  const { t } = useI18n();
  return (
      <div className="error-message" role="alert">
        <h1>{t("This workspace could not load")}</h1>
        <p>{t("Your saved campaigns remain on the local server. Reload to retry loading this page.")}</p>
        <Button onClick={() => window.location.reload()}>{t("Reload workspace")}</Button>
      </div>
    );
}
