import { useI18n } from "../i18n";
import { useEffect, useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Grid2X2,
  List,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import { api } from "../api";
import { useApp } from "../state";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Dialog } from "../components/ui/dialog";
import { EmptyState, PageHeading, SourceBadge } from "../components/shared";
import type { Candidate, CandidatePage } from "../types";

export default function Compounds() {
  const { t } = useI18n();
  const { run, meta } = useApp();
  const [search, setSearch] = useState(""),
    [status, setStatus] = useState("all"),
    [sort, setSort] = useState("id"),
    [page, setPage] = useState(1),
    [list, setList] = useState(true),
    [result, setResult] = useState<CandidatePage | null>(null),
    [selected, setSelected] = useState<Candidate | null>(null),
    [loading, setLoading] = useState(true),
    [error, setError] = useState<string | null>(null),
    [retry, setRetry] = useState(0);
  useEffect(() => {
    if (!run) return;
    let alive = true;
    setLoading(true);
    const timer = setTimeout(() => {
      api
        .candidates(run.session_id, {
          search,
          status,
          sort,
          descending: sort === "feature_count",
          page,
          page_size: 12,
        })
        .then((data) => {
          if (alive) {
            setResult(data);
            setError(null);
          }
        })
        .catch((e) => {
          if (alive) setError(e.message);
        })
        .finally(() => {
          if (alive) setLoading(false);
        });
    }, 180);
    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, [run?.session_id, run?.revision, search, status, sort, page, retry]);
  if (!run) return null;
  const molecule = (c: Candidate) =>
    `/api/v1/runs/${run.session_id}/molecules/${encodeURIComponent(c.compound_id)}.svg`;
  const outcome = (c: Candidate) =>
    c.status === "eligible" || c.status === "pending"
      ? "Unrevealed"
      : c.revealed_active === null
        ? "Missing outcome"
        : c.revealed_active
          ? "Observed active"
          : "Observed inactive";
  return (
    <>
      <PageHeading
        title={t("Compound explorer")}
        description={t("Public structures and descriptors. Assay labels stay private until revealed.")}
      >
        <SourceBadge />
      </PageHeading>
      <div className="surface explorer-controls">
        <div className="search-field">
          <Search size={18} />
          <input
            aria-label={t("Search compounds")}
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder={t("Search a compound ID…")}
          />
        </div>
        <div className="filter-controls">
          <SlidersHorizontal size={16} />
          <select
            aria-label={t("Compound status")}
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
          >
            {["all", "eligible", "seed", "pending", "delivered", "missing"].map(
              (s) => (
                <option key={s} value={s}>
                  {s === "all" ? t("All statuses") : t(s)}
                </option>
              ),
            )}
          </select>
          <select
            aria-label={t("Sort compounds")}
            value={sort}
            onChange={(e) => { setSort(e.target.value); setPage(1); }}
          >
            <option value="id">{t("Compound ID")}</option>
            <option value="feature_count">{t("Nonzero features ↓")}</option>
          </select>
          <div className="view-toggle">
            <button
              aria-label={t("Grid view")}
              aria-pressed={!list}
              onClick={() => setList(false)}
            >
              <Grid2X2 size={16} />
            </button>
            <button
              aria-label={t("List view")}
              aria-pressed={list}
              onClick={() => setList(true)}
            >
              <List size={16} />
            </button>
          </div>
        </div>
      </div>
      <div className="results-heading">
        <p>
          <strong>{result?.total ?? "—"}</strong>{" "}
          {t("matching compounds")}{" "}
          <span>{t("· ")}{run.report.manifest.dataset.assay_id}</span>
        </p>
        <span>
          {t("No hidden label is sent to this browser")}
        </span>
      </div>
      {list && <p id="compound-table-hint" className="table-scroll-hint">{t("Swipe horizontally to view status, outcomes and selection history. Open a compound ID for details.")}</p>}
      {error ? (
        <div className="error-message" role="alert">
          {error}
          <Button size="sm" onClick={() => setRetry((n) => n + 1)}>
            {t("Retry")}</Button>
        </div>
      ) : loading ? (
        <div className="loading-panel" role="status">
          <div className="spinner" />
          {t("Loading public candidates…")}
        </div>
      ) : !result?.items.length ? (
        <EmptyState
          title={t("No compounds found")}
          description={t("Try another compound ID or remove the status filter.")}
          action={
            <Button
              variant="outline"
              onClick={() => {
                setSearch("");
                setStatus("all");
                setPage(1);
              }}
            >
              {t("Clear filters")}</Button>
          }
        />
      ) : list ? (
        <div className="surface table-scroll compound-table" role="region" aria-label={t("Compound library table")} aria-describedby="compound-table-hint" tabIndex={0}>
          <table><thead><tr><th>{t("Compound")}</th><th>{t("2D structure")}</th><th>{t("Observed status")}</th><th>{t("Assay outcome")}</th><th>{t("Public descriptors")}</th><th>{t("Selection history")}</th></tr></thead>
          <tbody>{result.items.map(c => <tr key={c.compound_id}>
            <td><button className="compound-record-link" onClick={() => setSelected(c)}>{c.compound_id}<ChevronRight size={14} /></button></td>
            <td>{c.canonical_smiles && meta?.molecule_rendering ? <img src={molecule(c)} alt={t("RDKit 2D molecular structure {id}", { id: c.compound_id })} loading="lazy" /> : <span className="small muted">{t("Numerical fixture")}</span>}</td>
            <td><Badge className={c.status === "pending" ? "badge-amber" : "badge-neutral"}>{t(c.status)}</Badge></td>
            <td><span className="outcome-cell">{t(outcome(c))}</span></td>
            <td>{c.feature_nonzero} / {c.feature_count}</td>
            <td>{run.report.requests.filter(q => q.compound_id === c.compound_id).length} {t("accepted requests")}</td>
          </tr>)}</tbody></table>
        </div>
      ) : (
        <div className="compound-grid">
          {result.items.map((c) => (
            <button
              className="compound-item"
              key={c.compound_id}
              onClick={() => setSelected(c)}
            >
              <div className="compound-item-top">
                <strong className="small-mono">{c.compound_id}</strong>
                <Badge
                  className={
                    c.status === "pending"
                      ? "badge-amber"
                      : c.status === "eligible"
                        ? "badge-neutral"
                        : "badge-teal"
                  }
                >
                  {t(c.status)}
                </Badge>
              </div>
              {c.canonical_smiles && meta?.molecule_rendering ? (
                <img
                  src={molecule(c)}
                  alt={t("RDKit 2D molecular structure {id}", { id: c.compound_id })}
                  loading="lazy"
                />
              ) : (
                <div className="numerical-candidate">
                  <strong>{c.feature_count}</strong>
                  <span>
                    {t("numerical descriptors")}
                    <br />
                    {c.canonical_smiles ? t("Structure renderer unavailable; public SMILES remains in details") : t("No molecular structure in this synthetic fixture")}
                  </span>
                </div>
              )}
              <div className="compound-item-bottom">
                <div>
                  <span>{t(outcome(c))}</span>
                  <small>
                    {c.feature_nonzero} {t(" / ")}{c.feature_count}{" "}
                    {t("nonzero features")}
                  </small>
                </div>
                <ChevronRight size={17} />
              </div>
            </button>
          ))}
        </div>
      )}
      <div className="pagination">
        <span>
          {t("Page")} {page} {t(" /")}{" "}
          {Math.max(1, Math.ceil((result?.total ?? 0) / 12))}
        </span>
        <div className="button-row">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1 || loading}
            onClick={() => setPage((p) => p - 1)}
          >
            <ChevronLeft size={16} />
            {t("Previous")}
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={page * 12 >= (result?.total ?? 0) || loading}
            onClick={() => setPage((p) => p + 1)}
          >
            {t("Next")}
            <ChevronRight size={16} />
          </Button>
        </div>
      </div>
      <Dialog
        open={Boolean(selected)}
        onOpenChange={(open) => {
          if (!open) setSelected(null);
        }}
        title={selected?.compound_id ?? t("Compound details")}
        description={t("Public structure and observed assay information only.")}
      >
        {selected && (
          <>
            {selected.canonical_smiles && meta?.molecule_rendering ? (
              <img
                className="dialog-molecule"
                src={molecule(selected)}
                alt={t("RDKit 2D molecular structure {id}", { id: selected.compound_id })}
              />
            ) : (
              <p>{t("No molecular rendering is available for this candidate.")}</p>
            )}
            <div className="detail-outcome">
              <Badge>{t(selected.status)}</Badge>
              <strong>{t(outcome(selected))}</strong>
            </div>
            <dl className="details-list">
              <div>
                <dt>{t("Canonical SMILES")}</dt>
                <dd className="small-mono break-text">
                  {selected.canonical_smiles ??
                    t("Not applicable · synthetic numerical fixture")}
                </dd>
              </div>
              <div>
                <dt>{t("Murcko scaffold")}</dt>
                <dd className="small-mono break-text">
                  {selected.scaffold_id || "Acyclic / not applicable"}
                </dd>
              </div>
              <div>
                <dt>{t("Public descriptors")}</dt>
                <dd>
                  {selected.feature_count} {t(" dimensions ·")}{" "}
                  {selected.feature_nonzero} {t("nonzero")}</dd>
              </div>
              {selected.explanation && (
                <div>
                  <dt>{t("Actual selection rationale")}</dt>
                  <dd>{selected.explanation}</dd>
                </div>
              )}
            </dl>
            <section className="compound-history"><h3>{t("Selection history")}</h3>
              {run.report.requests.filter(q => q.compound_id === selected.compound_id).map(q => {
                const delivered = run.report.delivered_results.find(x => x.request_id === q.request_id);
                return <div key={q.request_id}><strong>{t("Selected at step {step}", { step: q.scheduled_at_step })}</strong><p>{t("Due at step")} {q.due_at_step} · {q.cost_units} {t("simulated units")}</p><p>{delivered ? t(delivered.active === null ? "Missing outcome" : delivered.active ? "Observed active" : "Observed inactive") : t("Unrevealed")}</p><p className="small muted">{t("Original engine explanation (English)")}: {q.explanation}</p></div>;
              })}
              {!run.report.requests.some(q => q.compound_id === selected.compound_id) && <p className="muted">{t("No accepted request for this compound. Initial observations are not new selections.")}</p>}
            </section>
          </>
        )}
      </Dialog>
    </>
  );
}
