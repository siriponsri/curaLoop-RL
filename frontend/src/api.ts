import type {
  CandidatePage,
  DatasetInfo,
  Evidence,
  Job,
  Meta,
  Policy,
  PolicyInfo,
  RunView,
  Scenario,
} from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
export async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch("/api/v1" + path, {
      ...options,
      headers: { "Content-Type": "application/json", ...options?.headers },
    });
  } catch {
    throw new ApiError(
      "Cannot reach the local API. Start Start-CuraLoop-Web.cmd, then retry.",
      0,
    );
  }
  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new ApiError(
      typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail),
      response.status,
    );
  }
  return response.json() as Promise<T>;
}
const post = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "POST", body: JSON.stringify(body) });
export const api = {
  meta: () => request<Meta>("/meta"),
  datasets: () => request<DatasetInfo[]>("/datasets"),
  policies: () => request<PolicyInfo[]>("/policies"),
  evidence: () => request<Evidence>("/evidence"),
  create: (scenario: Scenario, policy: Policy) =>
    post<RunView>("/runs", { scenario, policy }),
  run: (id: string) => request<RunView>("/runs/" + id),
  action: (run: RunView, action: string, steps = 1) =>
    post<RunView>(`/runs/${run.session_id}/${action}`, {
      expected_revision: run.revision,
      steps,
    }),
  candidates: (id: string, params: Record<string, string | number | boolean>) =>
    request<CandidatePage>(
      `/runs/${id}/candidates?` +
        new URLSearchParams(
          Object.entries(params).map(([k, v]) => [k, String(v)]),
        ),
    ),
  compare: (scenario: Scenario, policies: Policy[]) =>
    post<{ job_id: string; status: string }>("/comparisons", {
      scenario,
      policies,
    }),
  job: (id: string) => request<Job>("/comparisons/" + id),
  resume: (payload: unknown) => post<RunView>("/resume", payload),
};
export function runExport(id: string, format: "json" | "csv") {
  return `/api/v1/runs/${id}/export?format=${format}`;
}
export function comparisonExport(id: string, format: "json" | "csv") {
  return `/api/v1/comparisons/${id}/export?format=${format}`;
}
