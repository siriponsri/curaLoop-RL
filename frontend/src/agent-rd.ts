import { request } from "./api";

export interface MissionSpec {
  goal: string; campaign: string; budgets: number[]; arms: string[];
  locale: "en" | "th"; mode: "agent" | "deterministic"; export_requested: boolean;
}
export interface AgentReport {
  action: string; values?: Record<string, number>; limitations?: string[];
  reason?: string; evidence_id?: string;
}
export interface AgentMission {
  mission_id: string; revision: number; state: string; created_utc: string; spec: MissionSpec;
  events: { revision: number; state: string; detail: string; utc: string }[];
  calls: { call_id: string; status: string; output?: string; error?: string }[];
  tool_receipts: { tool: string; sha256: string; status: string; result: unknown }[];
  candidate: AgentReport | null; released: AgentReport | null;
  verification: { valid: boolean; errors: string[]; verified_values: number } | null;
  fallback: string | null; error: string | null;
  cost: { model_calls: number; tool_calls: number; model_tokens: number; model_cpu_seconds: number; model_wall_seconds: number; failed_calls: number; paid_cost_usd: number };
  evidence: { source_hashes: { path: string; sha256: string }[]; limitations: Record<string, string> } | null;
}
export type MissionSummary = Pick<AgentMission, "mission_id" | "revision" | "state" | "created_utc" | "spec" | "cost">;
export const terminalMission = (state: string) => ["COMPLETED", "ABSTAINED", "FAILED", "CANCELLED", "INTERRUPTED_RECOVERABLE"].includes(state);
const post = <T>(path: string, body: unknown) => request<T>(path, { method: "POST", body: JSON.stringify(body) });
export const agentApi = {
  runtime: () => request<{ authorization_active: boolean; evaluation_locked: boolean; model: string | null; provider_health: string; paid_fallback: boolean }>("/agent/runtime"),
  list: () => request<{ items: MissionSummary[]; integrity_issues: { mission_id: string; error: string }[] }>("/agent/missions"),
  read: (id: string) => request<AgentMission>("/agent/missions/" + id),
  create: (spec: MissionSpec) => post<AgentMission>("/agent/missions", spec),
  act: (id: string, expected_revision: number, action: "resume" | "export") => post<AgentMission & { files: string[]; base_url: string }>("/agent/missions/" + id + "/action", { expected_revision, action }),
};
