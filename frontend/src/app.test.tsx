import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import App from "./App";
import { AppProvider } from "./state";
import { api, ApiError } from "./api";
import fixtures from "./__fixtures__/api-states.json";
import type { DatasetInfo, Evidence, Job, Meta, PolicyInfo, RunView } from "./types";

beforeEach(() => {
  localStorage.clear();
  vi.spyOn(api, "meta").mockResolvedValue(fixtures.meta as Meta);
  vi.spyOn(api, "datasets").mockResolvedValue(
    fixtures.datasets as DatasetInfo[],
  );
  vi.spyOn(api, "policies").mockResolvedValue(
    fixtures.policies as PolicyInfo[],
  );
  vi.spyOn(api, "evidence").mockResolvedValue(fixtures.evidence as Evidence);
  vi.spyOn(api, "create").mockResolvedValue(fixtures.run as RunView);
  vi.spyOn(api, "run").mockResolvedValue(fixtures.run as RunView);
  vi.spyOn(api, "runs").mockResolvedValue({ items: [], recovery_issues: [], storage: { schema_version: 1, status: "ok" } });
  vi.spyOn(api, "jobs").mockResolvedValue({ items: [], recovery_issues: [] });
  vi.spyOn(api, "candidates").mockResolvedValue({
    items: [],
    total: 0,
    page: 1,
    page_size: 12,
  });
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
function show(path = "/") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AppProvider>
        <App />
      </AppProvider>
    </MemoryRouter>,
  );
}

describe("runnable research UI", () => {
  it("loads the real-response fixture and navigates through the actual route shell", async () => {
    show();
    expect(
      await screen.findByText("Every assay is a decision."),
    ).toBeInTheDocument();
    await userEvent.click(
      screen.getByRole("link", { name: "Scenario builder" }),
    );
    expect(
      await screen.findByRole("heading", { name: "Scenario builder" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Screening budget")).toHaveValue(6);
  });
  it("renders English despite a legacy Thai preference and retains the scientific limitation", async () => {
    localStorage.setItem("curaloop-language", "th");
    document.documentElement.lang = "th";
    show("/lab");
    await screen.findByRole("heading", { name: "Simulation lab" });
    expect(document.documentElement.lang).toBe("en");
    expect(localStorage.getItem("curaloop-language")).toBeNull();
    expect(screen.queryByRole("button", { name: "TH" })).not.toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/[\u0e00-\u0e7f]/);
    expect(screen.getByText("Not a Validated Digital Twin")).toBeInTheDocument();
  });
  it("validates the form before making an engine request", async () => {
    show("/scenario");
    await screen.findByRole("heading", { name: "Scenario builder" });
    const budget = screen.getByLabelText("Screening budget");
    await userEvent.clear(budget);
    await userEvent.type(budget, "10001");
    await userEvent.click(
      screen.getByRole("button", { name: "Create campaign" }),
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Budget must be an integer",
    );
    expect(api.create).toHaveBeenCalledTimes(1);
  });
  it("applies a valid changed dataset with the correct candidate count", async () => {
    show("/scenario");
    await screen.findByRole("heading", { name: "Scenario builder" });
    await userEvent.selectOptions(
      screen.getByLabelText("Dataset"),
      "synthetic_shift_v1",
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Create campaign" }),
    );
    await waitFor(() => expect(api.create).toHaveBeenCalledTimes(2));
    expect(vi.mocked(api.create).mock.calls[1][0].dataset).toBe(
      "synthetic_shift_v1",
    );
    expect(vi.mocked(api.create).mock.calls[1][0].candidate_count).toBe(240);
    expect(
      await screen.findByRole("heading", { name: "Simulation lab" }),
    ).toBeInTheDocument();
  });
  it("turns a real action response into a pending state, with no fake hits", async () => {
    vi.spyOn(api, "action").mockResolvedValue(fixtures.pending as RunView);
    show("/lab");
    await screen.findByRole("heading", { name: "Simulation lab" });
    expect(screen.getByRole("button", { name: "Advance time" })).toBeDisabled();
    await userEvent.click(screen.getByRole("button", { name: "Select batch" }));
    await waitFor(() =>
      expect(api.action).toHaveBeenCalledWith(expect.anything(), "select"),
    );
    expect(await screen.findByText("Awaiting feedback")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Advance time" })).toBeEnabled();
    expect(
      screen.getAllByText("0", { selector: ".kpi-strip strong" }).length,
    ).toBeGreaterThan(0);
  });
  it("shows API errors and a working reconnect action", async () => {
    vi.mocked(api.meta).mockRejectedValueOnce(
      new Error("Local server unavailable"),
    );
    show();
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Local server unavailable",
    );
    await userEvent.click(screen.getByRole("button", { name: "Reconnect" }));
    expect(
      await screen.findByText("Every assay is a decision."),
    ).toBeInTheDocument();
  });
  it("preserves provenance, weak evaluation and controller fallback disclosures", async () => {
    show("/evidence");
    await screen.findByRole("heading", { name: "Research evidence" });
    expect(
      screen.getByText(
        "Original in-process synthetic generator; no external data.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText(/300 \/ 300 requests/)).toBeInTheDocument();
    expect(
      screen.getByText(/not the official|custom split/i),
    ).toBeInTheDocument();
    expect(
      screen.getAllByRole("link", { name: "JSON" }).length,
    ).toBeGreaterThan(0);
  });
  it("has a functional guided-presentation chapter control", async () => {
    show("/presentation");
    await screen.findByRole("heading", { name: "Guided presentation" });
    await userEvent.click(screen.getByRole("button", { name: "Next chapter" }));
    expect(
      screen.getByRole("heading", { name: "What is real?" }),
    ).toBeInTheDocument();
  });
  it("opens saved pending feedback after restart without creating or charging a new campaign", async () => {
    localStorage.setItem("curaloop-session", fixtures.pending.session_id);
    vi.mocked(api.run).mockResolvedValue(fixtures.pending as RunView);
    show("/lab");
    expect(await screen.findByText("Awaiting feedback")).toBeInTheDocument();
    expect(api.run).toHaveBeenCalledWith(fixtures.pending.session_id);
    expect(api.create).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Advance time" })).toBeEnabled();
  });
  it("keeps corrupt saved-state errors visible and recovers an explicit validated revision", async () => {
    localStorage.setItem("curaloop-session", "damaged");
    vi.mocked(api.run).mockRejectedValue(new ApiError("Saved snapshot failed reconciliation.", 422));
    vi.mocked(api.runs).mockResolvedValue({ items: [], recovery_issues: [{ kind: "run", id: "damaged", message: "Saved snapshot failed reconciliation." }], storage: { schema_version: 1, status: "ok" } });
    vi.spyOn(api, "revisions").mockResolvedValue({ session_id: "damaged", items: [{ revision: 2, saved_at: "2026-11-04T10:00:00Z" }] });
    vi.spyOn(api, "recoverRevision").mockResolvedValue(fixtures.pending as RunView);
    show("/lab");
    await screen.findByRole("heading", { name: "Saved campaigns & recovery" });
    expect(api.create).not.toHaveBeenCalled();
    await userEvent.click(await screen.findByRole("button", { name: "Inspect saved revisions" }));
    await userEvent.click(await screen.findByRole("button", { name: "Recover selected revision" }));
    expect(api.recoverRevision).toHaveBeenCalledWith("damaged", 2);
    expect(await screen.findByText("Awaiting feedback")).toBeInTheDocument();
  });
  it("can operate when browser preference storage is blocked", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => { throw new Error("Storage blocked"); });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("Storage blocked"); });
    vi.spyOn(Storage.prototype, "removeItem").mockImplementation(() => { throw new Error("Storage blocked"); });
    show();
    expect(await screen.findByText("Every assay is a decision.")).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("en");
  });
  it("reports a stale-action refresh failure without an unhandled rejection", async () => {
    vi.spyOn(api, "action").mockRejectedValue(new ApiError("Stale action rejected.", 409));
    vi.mocked(api.run).mockRejectedValue(new ApiError("Local server unavailable.", 0));
    show("/lab");
    await screen.findByRole("heading", { name: "Simulation lab" });
    await userEvent.click(screen.getByRole("button", { name: "Select batch" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Refresh also failed: Local server unavailable.");
    expect(screen.getByRole("button", { name: "Select batch" })).toBeEnabled();
  });
  it("recovers an interrupted comparison without automatically running it again", async () => {
    localStorage.setItem("curaloop-comparison", "saved-job");
    const interrupted: Job = { job_id: "saved-job", status: "interrupted", scenario: fixtures.run.report.manifest.scenario_config as Job["scenario"], policies: ["greedy"], reports: [], error: "Server stopped before this comparison completed." };
    vi.spyOn(api, "job").mockResolvedValue(interrupted);
    vi.mocked(api.jobs).mockResolvedValue({ items: [interrupted], recovery_issues: [] });
    vi.spyOn(api, "compare");
    show("/benchmarks");
    expect(await screen.findByText("Server stopped before this comparison completed.")).toBeInTheDocument();
    expect(api.compare).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Run comparison" })).toBeEnabled();
    expect(screen.getByText(/This comparison was interrupted/)).toBeInTheDocument();
  });
  it("retries a failed comparison status check without submitting duplicate work", async () => {
    localStorage.setItem("curaloop-comparison", "finished-job");
    const completed: Job = { job_id: "finished-job", status: "completed", scenario: { ...fixtures.run.report.manifest.scenario_config, dataset: "hiv_moleculenet_replay_v1", seed: 17 } as Job["scenario"], policies: ["greedy"], reports: [fixtures.run.report as RunView["report"]], error: null };
    vi.spyOn(api, "job").mockRejectedValueOnce(new ApiError("Connection interrupted.", 0)).mockResolvedValue(completed);
    vi.spyOn(api, "compare");
    show("/benchmarks");
    expect(await screen.findByRole("alert")).toHaveTextContent("Connection interrupted.");
    await userEvent.click(screen.getByRole("button", { name: "Retry comparison status" }));
    expect(await screen.findByRole("heading", { name: "Comparison complete" })).toBeInTheDocument();
    expect(screen.getByText("Historical assay data")).toBeInTheDocument();
    expect(screen.getByText(/seed 17/)).toBeInTheDocument();
    expect(api.compare).not.toHaveBeenCalled();
  });
});
