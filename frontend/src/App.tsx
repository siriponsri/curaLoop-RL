import { Component, lazy, Suspense, useState, type ReactNode } from "react";
import { NavLink, Route, Routes, useLocation, Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  ChevronRight,
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
import { short } from "./lib";
import { SavedRuns } from "./components/recovery";
const Overview = lazy(() => import("./pages/Overview"));
const Scenario = lazy(() => import("./pages/Scenario"));
const Lab = lazy(() => import("./pages/Lab"));
const Compounds = lazy(() => import("./pages/Compounds"));
const Benchmarks = lazy(() => import("./pages/Benchmarks"));
const Evidence = lazy(() => import("./pages/Evidence"));
const GuidedPresentation = lazy(() => import("./pages/Presentation"));

const pages = [
  { path: "/", en: "Overview", icon: LayoutDashboard },
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
  { path: "/lab", en: "Simulation lab", icon: FlaskConical },
  {
    path: "/benchmarks",
    en: "Benchmark arena",
    icon: BarChart3,
  },
  {
    path: "/evidence",
    en: "Research evidence",
    icon: BookOpen,
  },
  {
    path: "/presentation",
    en: "Guided presentation",
    icon: Presentation,
  },
];

export default function App() {
  const store = useApp();
  const { run, meta, loading, error, notice, busy } = store;
  const { pathname } = useLocation();
  const [mobile, setMobile] = useState(false);
  const active = pages.find((p) => p.path === pathname);
  function navigation() {
    return (
      <>
        <Link to="/" className="brand-link" onClick={() => setMobile(false)}>
          <img src="/brand/logo-v2.png" alt="CuraLoop-RL" />
          <span>Pharmaceutical decision lab</span>
        </Link>
        <nav className="main-nav" aria-label="Main navigation">
          {pages.map((p, i) => (
            <div key={p.path}>
              {i === 5 && <div className="nav-divider" />}
              <NavLink
                aria-label={p.en}
                to={p.path}
                end={p.path === "/"}
                onClick={() => setMobile(false)}
                className={({ isActive }) =>
                  isActive ? "nav-item nav-active" : "nav-item"
                }
              >
                <p.icon size={19} />
                <span>{(p.en)}</span>
                {p.path === "/lab" && run?.pending.length ? (
                  <Badge>{run.pending.length}</Badge>
                ) : null}
              </NavLink>
            </div>
          ))}
        </nav>
        <div className="sidebar-research">
          <span className="research-symbol">
            <FlaskConical size={19} />
          </span>
          <strong>
            {"Your local research space"}
          </strong>
          <p>
            {"Real data. Traceable decisions. No cloud dependency."}
          </p>
          <Link to="/evidence" onClick={() => setMobile(false)}>
            {"Inspect the evidence"}
            <ArrowRight size={14} />
          </Link>
        </div>
        <div className="sidebar-bottom">
          <span className="status-dot" />
          Localhost · CPU only <small>v{meta?.web_version ?? "0.3.0"}</small>
        </div>
      </>
    );
  }
  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        Skip to content
      </a>
      <aside className="sidebar">{navigation()}</aside>
      <Dialog
        open={mobile}
        onOpenChange={setMobile}
        title={"Research workspace"}
        description="CuraLoop-RL navigation"
      >
        <div className="mobile-navigation">{navigation()}</div>
      </Dialog>
      <div className="main-shell">
        <header className="topbar">
          <div className="topbar-path">
            <button
              className="mobile-menu icon-button"
              onClick={() => setMobile(true)}
              aria-label="Open navigation"
            >
              <Menu size={21} />
            </button>
            <span>{"Workspace"}</span>
            <ChevronRight size={13} />
            <strong>{active ? (active.en) : "Not found"}</strong>
          </div>
          <div className="topbar-controls">
            <span className="connection-pill">
              <Wifi size={13} />
              {loading ? "Connecting" : !run ? "Connection unavailable" : "Local API"}
            </span>
            <div
              className="owner-avatar"
              aria-label="Personal research workspace"
            >
              CL
            </div>
          </div>
        </header>
        <main id="main-content" className="main-content">
          {error && (
            <div className="error-banner" role="alert">
              <div>
                <strong>
                  {"The action could not be completed"}
                </strong>
                <p>{error}</p>
              </div>
              <div className="button-row">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => void store.retry()}
                >
                  {"Reconnect"}
                </Button>
                <button
                  aria-label="Dismiss error"
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
              {notice}
            </div>
          )}
          {loading ? (
            <div className="initial-loading">
              <div className="spinner" />
              <h1>
                {"Connecting your research workspace"}
              </h1>
              <p>
                {"Loading public metadata and the current local campaign."}
              </p>
            </div>
          ) : !run ? (
            <SavedRuns includeImport />
          ) : (
            <RouteBoundary key={pathname + run.session_id}>
            <Suspense fallback={<div className="loading-panel" role="status">Loading workspace…</div>}>
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
                    <h1>Page not found</h1>
                    <Button asChild>
                      <Link to="/">Back to overview</Link>
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
            {"Independent personal portfolio · Not an official GPO system"}
          </span>
          <div>
            <span className="small-mono">
              {short(meta?.repo_git_sha ?? "local", 10)}
            </span>
            <a
              href="https://shadcndashboard.dev/"
              target="_blank"
              rel="noreferrer"
            >
              Shadcn Dashboard inspiration
            </a>
          </div>
        </footer>
      </div>
      {busy && (
        <div className="operation-indicator" role="status">
          <span className="spinner small-spinner" />
          {"Running the local engine…"}
        </div>
      )}
    </div>
  );
}
function CheckMark() {
  return <ShieldCheck size={16} />;
}
class RouteBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    return this.state.failed ? (
      <div className="error-message" role="alert">
        <h1>This workspace could not load</h1>
        <p>Your saved campaigns remain on the local server. Reload to retry loading this page.</p>
        <Button onClick={() => window.location.reload()}>Reload workspace</Button>
      </div>
    ) : this.props.children;
  }
}
