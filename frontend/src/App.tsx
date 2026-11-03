import { useState } from "react";
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
import Overview from "./pages/Overview";
import Scenario from "./pages/Scenario";
import Lab from "./pages/Lab";
import Compounds from "./pages/Compounds";
import Benchmarks from "./pages/Benchmarks";
import Evidence from "./pages/Evidence";
import GuidedPresentation from "./pages/Presentation";

const pages = [
  { path: "/", en: "Overview", th: "ภาพรวม", icon: LayoutDashboard },
  {
    path: "/compounds",
    en: "Compound explorer",
    th: "สำรวจสาร",
    icon: Microscope,
  },
  {
    path: "/scenario",
    en: "Scenario builder",
    th: "ตั้งเงื่อนไข",
    icon: Settings2,
  },
  { path: "/lab", en: "Simulation lab", th: "ห้องจำลอง", icon: FlaskConical },
  {
    path: "/benchmarks",
    en: "Benchmark arena",
    th: "เปรียบเทียบนโยบาย",
    icon: BarChart3,
  },
  {
    path: "/evidence",
    en: "Research evidence",
    th: "หลักฐานการวิจัย",
    icon: BookOpen,
  },
  {
    path: "/presentation",
    en: "Guided presentation",
    th: "โหมดนำเสนอ",
    icon: Presentation,
  },
];

export default function App() {
  const store = useApp();
  const { run, meta, t, lang, setLang, loading, error, notice, busy } = store;
  const { pathname } = useLocation();
  const [mobile, setMobile] = useState(false);
  const active = pages.find((p) => p.path === pathname);
  function navigation() {
    return (
      <>
        <Link to="/" className="brand-link" onClick={() => setMobile(false)}>
          <img src="/brand/logo.png" alt="CuraLoop-RL" />
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
                <span>{t(p.en, p.th)}</span>
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
            {t("Your local research space", "พื้นที่วิจัยในเครื่องของคุณ")}
          </strong>
          <p>
            {t(
              "Real data. Traceable decisions. No cloud dependency.",
              "ข้อมูลจริง ตรวจสอบการตัดสินใจได้ ไม่พึ่งบริการ cloud",
            )}
          </p>
          <Link to="/evidence" onClick={() => setMobile(false)}>
            {t("Inspect the evidence", "ดูหลักฐาน")}
            <ArrowRight size={14} />
          </Link>
        </div>
        <div className="sidebar-bottom">
          <span className="status-dot" />
          Localhost · CPU only <small>v{meta?.web_version ?? "0.2.0"}</small>
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
        title={t("Research workspace", "หน้าทำงานวิจัย")}
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
            <span>{t("Workspace", "หน้าทำงาน")}</span>
            <ChevronRight size={13} />
            <strong>{active ? t(active.en, active.th) : "Not found"}</strong>
          </div>
          <div className="topbar-controls">
            <span className="connection-pill">
              <Wifi size={13} />
              {loading ? "Connecting" : "Local API"}
            </span>
            <div className="language-switch" aria-label="Interface language">
              <button
                aria-pressed={lang === "en"}
                onClick={() => setLang("en")}
              >
                EN
              </button>
              <button
                aria-pressed={lang === "th"}
                onClick={() => setLang("th")}
              >
                TH
              </button>
            </div>
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
                  {t(
                    "The action could not be completed",
                    "ยังดำเนินการไม่สำเร็จ",
                  )}
                </strong>
                <p>{error}</p>
              </div>
              <div className="button-row">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => void store.retry()}
                >
                  {t("Reconnect", "เชื่อมต่อใหม่")}
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
          {loading || !run ? (
            <div className="initial-loading">
              <div className="spinner" />
              <h1>
                {t(
                  "Connecting your research workspace",
                  "กำลังเชื่อมต่อหน้าทำงานวิจัย",
                )}
              </h1>
              <p>
                {t(
                  "Loading public metadata and the current local campaign.",
                  "กำลังโหลดข้อมูลสาธารณะและ campaign ในเครื่อง",
                )}
              </p>
              {!loading && (
                <Button onClick={() => void store.retry()}>
                  Retry local connection
                </Button>
              )}
            </div>
          ) : (
            <Routes>
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
          )}
        </main>
        <footer className="app-footer">
          <span>
            <ShieldCheck size={14} />
            {t(
              "Independent personal portfolio · Not an official GPO system",
              "โครงการส่วนบุคคล · ไม่ใช่ระบบทางการของ GPO",
            )}
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
          {t("Running the local engine…", "กำลังรัน engine ในเครื่อง…")}
        </div>
      )}
    </div>
  );
}
function CheckMark() {
  return <ShieldCheck size={16} />;
}
