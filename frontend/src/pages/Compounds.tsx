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
  const { run, meta } = useApp();
  const [search, setSearch] = useState(""),
    [status, setStatus] = useState("all"),
    [sort, setSort] = useState("id"),
    [page, setPage] = useState(1),
    [list, setList] = useState(false),
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
        title={"Compound explorer"}
        description={"Public structures and descriptors. Assay labels stay private until revealed."}
      >
        <SourceBadge />
      </PageHeading>
      <div className="surface explorer-controls">
        <div className="search-field">
          <Search size={18} />
          <input
            aria-label="Search compounds"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder={"Search a compound ID…"}
          />
        </div>
        <div className="filter-controls">
          <SlidersHorizontal size={16} />
          <select
            aria-label="Compound status"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
          >
            {["all", "eligible", "seed", "pending", "delivered", "missing"].map(
              (s) => (
                <option key={s} value={s}>
                  {s === "all" ? "All statuses" : s}
                </option>
              ),
            )}
          </select>
          <select
            aria-label="Sort compounds"
            value={sort}
            onChange={(e) => { setSort(e.target.value); setPage(1); }}
          >
            <option value="id">Compound ID</option>
            <option value="feature_count">Nonzero features ↓</option>
          </select>
          <div className="view-toggle">
            <button
              aria-label="Grid view"
              aria-pressed={!list}
              onClick={() => setList(false)}
            >
              <Grid2X2 size={16} />
            </button>
            <button
              aria-label="List view"
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
          {"matching compounds"}{" "}
          <span>· {run.report.manifest.dataset.assay_id}</span>
        </p>
        <span>
          {"No hidden label is sent to this browser"}
        </span>
      </div>
      {error ? (
        <div className="error-message" role="alert">
          {error}
          <Button size="sm" onClick={() => setRetry((n) => n + 1)}>
            Retry
          </Button>
        </div>
      ) : loading ? (
        <div className="loading-panel" role="status">
          <div className="spinner" />
          {"Loading public candidates…"}
        </div>
      ) : !result?.items.length ? (
        <EmptyState
          title={"No compounds found"}
          description={"Try another compound ID or remove the status filter."}
          action={
            <Button
              variant="outline"
              onClick={() => {
                setSearch("");
                setStatus("all");
                setPage(1);
              }}
            >
              Clear filters
            </Button>
          }
        />
      ) : (
        <div className={list ? "compound-list" : "compound-grid"}>
          {result.items.map((c) => (
            <button
              className="compound-item"
              key={c.compound_id}
              onClick={() => setSelected(c)}
              aria-label={`Inspect ${c.compound_id}`}
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
                  {c.status}
                </Badge>
              </div>
              {c.canonical_smiles && meta?.molecule_rendering ? (
                <img
                  src={molecule(c)}
                  alt={`RDKit 2D molecular structure ${c.compound_id}`}
                  loading="lazy"
                />
              ) : (
                <div className="numerical-candidate">
                  <strong>{c.feature_count}</strong>
                  <span>
                    {"numerical descriptors"}
                    <br />
                    {c.canonical_smiles ? "Structure renderer unavailable; public SMILES remains in details" : "No molecular structure in this synthetic fixture"}
                  </span>
                </div>
              )}
              <div className="compound-item-bottom">
                <div>
                  <span>{outcome(c)}</span>
                  <small>
                    {c.feature_nonzero} / {c.feature_count}{" "}
                    {"nonzero features"}
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
          {"Page"} {page} /{" "}
          {Math.max(1, Math.ceil((result?.total ?? 0) / 12))}
        </span>
        <div className="button-row">
          <Button
            aria-label="Previous compound page"
            variant="outline"
            size="sm"
            disabled={page === 1 || loading}
            onClick={() => setPage((p) => p - 1)}
          >
            <ChevronLeft size={16} />
            {"Previous"}
          </Button>
          <Button
            aria-label="Next compound page"
            variant="outline"
            size="sm"
            disabled={page * 12 >= (result?.total ?? 0) || loading}
            onClick={() => setPage((p) => p + 1)}
          >
            {"Next"}
            <ChevronRight size={16} />
          </Button>
        </div>
      </div>
      <Dialog
        open={Boolean(selected)}
        onOpenChange={(open) => {
          if (!open) setSelected(null);
        }}
        title={selected?.compound_id ?? "Compound details"}
        description={"Public structure and observed assay information only."}
      >
        {selected && (
          <>
            {selected.canonical_smiles && meta?.molecule_rendering ? (
              <img
                className="dialog-molecule"
                src={molecule(selected)}
                alt={`Structure of ${selected.compound_id}`}
              />
            ) : (
              <p>No molecular rendering is available for this candidate.</p>
            )}
            <div className="detail-outcome">
              <Badge>{selected.status}</Badge>
              <strong>{outcome(selected)}</strong>
            </div>
            <dl className="details-list">
              <div>
                <dt>Canonical SMILES</dt>
                <dd className="small-mono break-text">
                  {selected.canonical_smiles ??
                    "Not applicable · synthetic numerical fixture"}
                </dd>
              </div>
              <div>
                <dt>Murcko scaffold</dt>
                <dd className="small-mono break-text">
                  {selected.scaffold_id || "Acyclic / not applicable"}
                </dd>
              </div>
              <div>
                <dt>Public descriptors</dt>
                <dd>
                  {selected.feature_count} dimensions ·{" "}
                  {selected.feature_nonzero} nonzero
                </dd>
              </div>
              {selected.explanation && (
                <div>
                  <dt>Actual selection rationale</dt>
                  <dd>{selected.explanation}</dd>
                </div>
              )}
            </dl>
          </>
        )}
      </Dialog>
    </>
  );
}
