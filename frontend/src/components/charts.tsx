import { lazy, Suspense } from "react";
import type { RunReport, SummaryRow } from "../types";

const Discovery = lazy(() => import("./chart-content").then(module => ({ default: module.DiscoveryChart })));
const Recorded = lazy(() => import("./chart-content").then(module => ({ default: module.RecordedBenchmarkChart })));
const Returns = lazy(() => import("./chart-content").then(module => ({ default: module.ReturnChart })));
const Queue = lazy(() => import("./chart-content").then(module => ({ default: module.QueueChart })));
const loading = <div className="loading-panel chart-loading" role="status">Loading chart…</div>;
export function DiscoveryChart(props: { reports: RunReport[] }) {
  return <Suspense fallback={loading}><Discovery {...props} /></Suspense>;
}
export function RecordedBenchmarkChart(props: { rows: SummaryRow[] }) {
  return <Suspense fallback={loading}><Recorded {...props} /></Suspense>;
}
export function ReturnChart(props: { returns: number[] }) {
  return <Suspense fallback={loading}><Returns {...props} /></Suspense>;
}
export function QueueChart(props: { reports: RunReport[] }) {
  return <Suspense fallback={loading}><Queue {...props} /></Suspense>;
}
