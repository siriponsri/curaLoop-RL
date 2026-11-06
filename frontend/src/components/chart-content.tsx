import { useI18n } from "../i18n";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
  ErrorBar,
  Legend,
} from "recharts";
import {
  colors,
  policyNames,
  type Policy,
  type RunReport,
  type SummaryRow,
} from "../types";

export function DiscoveryChart({ reports }: { reports: RunReport[] }) {
  const { t } = useI18n();

  const costs = [
    ...new Set(reports.flatMap((r) => r.curve.map((p) => p.spent_units))),
  ].sort((a, b) => a - b);
  const points = costs.map((spent) => {
    const row: Record<string, number | null> = { spent };
    for (const r of reports) {
      const last = r.curve.filter((p) => p.spent_units <= spent).at(-1);
      row[r.manifest.policy_id] =
        (r.curve.at(-1)?.spent_units ?? 0) >= spent
          ? (last?.confirmed_hits ?? 0)
          : null;
    }
    return row;
  });
  return (
    <div
      className="scientific-chart"
      role="group"
      aria-label={t("Confirmed hits versus simulated settled cost")}
    >
      <ResponsiveContainer width="100%" height={290}>
        <LineChart
          data={points}
          margin={{ top: 16, right: 15, bottom: 22, left: 0 }}
        >
          <CartesianGrid
            strokeDasharray="3 5"
            vertical={false}
            stroke="#D9D5CF"
          />
          <XAxis
            dataKey="spent"
            tickLine={false}
            axisLine={false}
            label={{
              value: t("Settled simulated cost units"),
              position: "insideBottom",
              offset: -14,
            }}
          />
          <YAxis
            allowDecimals={false}
            tickLine={false}
            axisLine={false}
            width={32}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 10,
              border: "1px solid #D9D5CF",
              fontSize: 12,
            }}
            labelFormatter={(v) => `${t("Cost units")}: ${v}`}
          />
          <Legend verticalAlign="top" height={34} />
          {reports.map((r, i) => (
            <Line
              key={r.manifest.policy_id}
              name={policyNames[r.manifest.policy_id]}
              type="stepAfter"
              dataKey={r.manifest.policy_id}
              stroke={colors[r.manifest.policy_id]}
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
              strokeDasharray={i > 1 ? `${i * 2} 4` : undefined}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
export function RecordedBenchmarkChart({ rows }: { rows: SummaryRow[] }) {
  const { t } = useI18n();

  return (
    <div
      className="scientific-chart"
      role="group"
      aria-label={t("Recorded mean hits and seed standard deviation")}
    >
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          layout="vertical"
          data={rows.map((r) => ({
            ...r,
            name: policyNames[r.policy],
            error: [Math.min(r.mean_hits, r.sd_hits), r.sd_hits],
          }))}
          margin={{ top: 15, right: 25, left: 0, bottom: 20 }}
        >
          <CartesianGrid horizontal={false} strokeDasharray="3 5" />
          <XAxis
            type="number"
            domain={[0, "auto"]}
            allowDecimals={false}
            tickLine={false}
            axisLine={false}
            label={{
              value: t("New active hits · mean"),
              position: "insideBottom",
              offset: -13,
            }}
          />
          <YAxis
            type="category"
            dataKey="name"
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 11 }}
            width={113}
          />
          <Tooltip />
          <Bar
            dataKey="mean_hits"
            name={t("Mean hits · recorded")}
            fill="#A6492D"
            radius={[0, 4, 4, 0]}
            isAnimationActive={false}
          >
            <ErrorBar
              dataKey="error"
              direction="x"
              isAnimationActive={false}
              width={5}
              strokeWidth={1.5}
              stroke="#b66914"
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="chart-method-note">
        {t("Mean ± seed SD; lower display bound clipped at zero. Exact SD is retained in the benchmark table.")}
      </p>
    </div>
  );
}
export function ReturnChart({ returns }: { returns: number[] }) {
  const { t } = useI18n();
  return (
    <div className="training-chart">
      <ResponsiveContainer width="100%" height={150}>
        <LineChart
          data={returns.map((reward, episode) => ({
            episode: episode + 1,
            reward,
          }))}
        >
          <CartesianGrid vertical={false} strokeDasharray="3 5" />
          <XAxis
            dataKey="episode"
            tick={{ fontSize: 10 }}
            minTickGap={40}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            width={24}
            tick={{ fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip labelFormatter={value => t("Episode {count}", { count: String(value) })} />
          <Line
            type="monotone"
            name={t("Training reward")}
            dataKey="reward"
            stroke="#A6492D"
            strokeWidth={1.4}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
export function QueueChart({ reports }: { reports: RunReport[] }) {
  const { t } = useI18n();
  const rows = reports.flatMap((r) =>
    r.curve.map((p) => ({
      step: p.step,
      pending: p.pending_assays,
      policy: r.manifest.policy_id,
    })),
  );
  const policies = reports.map((r) => r.manifest.policy_id);
  const points = Array.from(
    { length: Math.max(0, ...rows.map((r) => r.step)) + 1 },
    (_, step) =>
      Object.fromEntries([
        ["step", step],
        ...policies.map((p) => [
          p,
          rows.filter((r) => r.policy === p && r.step <= step).at(-1)
            ?.pending ?? 0,
        ]),
      ]),
  );
  return (
    <div className="scientific-chart">
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={points}>
          <CartesianGrid vertical={false} strokeDasharray="3 5" />
          <XAxis dataKey="step" axisLine={false} tickLine={false} />
          <YAxis
            width={25}
            allowDecimals={false}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip labelFormatter={value => t("Simulated step {count}", { count: String(value) })} />
          {policies.map((p) => (
            <Line
              dataKey={p}
              key={p}
              name={policyNames[p as Policy]}
              stroke={colors[p as Policy]}
              type="stepAfter"
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
