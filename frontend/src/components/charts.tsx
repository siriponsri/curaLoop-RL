import { lazy, Suspense } from "react";
import { useI18n } from "../i18n";
import type { RunReport, SummaryRow } from "../types";

const Discovery = lazy(() => import("./chart-content").then(module => ({ default: module.DiscoveryChart })));
const Recorded = lazy(() => import("./chart-content").then(module => ({ default: module.RecordedBenchmarkChart })));
const Returns = lazy(() => import("./chart-content").then(module => ({ default: module.ReturnChart })));
const Queue = lazy(() => import("./chart-content").then(module => ({ default: module.QueueChart })));
function LoadingChart() {
  const { t } = useI18n();
  return <div className="loading-panel chart-loading" role="status">{t("Loading chart…")}</div>;
}
export function DiscoveryChart(props: { reports: RunReport[] }) {
  return <Suspense fallback={<LoadingChart />}><Discovery {...props} /></Suspense>;
}
export function RecordedBenchmarkChart(props: { rows: SummaryRow[] }) {
  return <Suspense fallback={<LoadingChart />}><Recorded {...props} /></Suspense>;
}
export function ReturnChart(props: { returns: number[] }) {
  return <Suspense fallback={<LoadingChart />}><Returns {...props} /></Suspense>;
}
export function QueueChart(props: { reports: RunReport[] }) {
  return <Suspense fallback={<LoadingChart />}><Queue {...props} /></Suspense>;
}
