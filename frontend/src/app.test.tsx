import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, render, screen, waitFor, within } from "@testing-library/react";
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
  it("inspects simulator stages without advancing the engine or asserting a fit", async () => {
    vi.mocked(api.create).mockResolvedValue(fixtures.pending as RunView);
    const action = vi.spyOn(api, "action");
    show("/lab");
    const stage = await screen.findByRole("button", { name: /Model update/ });
    await userEvent.click(stage);
    expect(stage).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText(/Observed labels become available/)).toBeInTheDocument();
    expect(screen.getByText("Last selection model status")).toBeInTheDocument();
    expect(action).not.toHaveBeenCalled();
  });
  it("keeps pending assay outcomes hidden in the table and compound record", async () => {
    vi.mocked(api.candidates).mockResolvedValue({ items: [{ compound_id: "PENDING-01", status: "pending", canonical_smiles: null, scaffold_id: null, feature_count: 8, feature_nonzero: 3, public_features_preview: [], revealed_active: true, predicted_probability: .9, explanation: null }], total: 1, page: 1, page_size: 12 });
    show("/compounds");
    const table = await screen.findByRole("region", { name: "Compound library table" });
    expect(within(table).getByText("Unrevealed")).toBeInTheDocument();
    expect(within(table).queryByText("Observed active")).not.toBeInTheDocument();
    await userEvent.click(within(table).getByRole("button", { name: "PENDING-01" }));
    const dialog = screen.getByRole("dialog");
    expect(within(dialog).getByText("Unrevealed")).toBeInTheDocument();
    expect(within(dialog).queryByText("Observed active")).not.toBeInTheDocument();
    expect(within(dialog).getByRole("heading", { name: "Selection history" })).toBeInTheDocument();
  });
  it("loads the real-response fixture and navigates through the actual route shell", async () => {
    show();
    expect(
      await screen.findByRole("heading", { name: "Discovery overview" }),
    ).toBeInTheDocument();
    await userEvent.click(
      screen.getByRole("link", { name: "Scenario builder" }),
    );
    expect(
      await screen.findByRole("heading", { name: "Scenario builder" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Screening budget")).toHaveValue(6);
  });
  it("restores Thai without changing a pending campaign or its API values", async () => {
    localStorage.setItem("curaloop-language", "th");
    localStorage.setItem("curaloop-session", fixtures.pending.session_id);
    vi.mocked(api.run).mockResolvedValue(fixtures.pending as RunView);
    const action = vi.spyOn(api, "action");
    show("/lab");
    await screen.findByRole("heading", { name: "ห้องจำลอง Digital Twin" });
    expect(document.documentElement.lang).toBe("th");
    expect(localStorage.getItem("curaloop-language")).toBe("th");
    expect(screen.getAllByText("กำลังรอผล").length).toBeGreaterThan(0);
    await userEvent.click(screen.getByRole("button", { name: "EN" }));
    await screen.findByRole("heading", { name: "Digital Twin Simulation Lab" });
    expect(document.documentElement.lang).toBe("en");
    expect(screen.getByText("Awaiting feedback")).toBeInTheDocument();
    expect(api.create).not.toHaveBeenCalled();
    expect(api.run).toHaveBeenCalledTimes(1);
    expect(action).not.toHaveBeenCalled();
    expect(localStorage.getItem("curaloop-session")).toBe(fixtures.pending.session_id);
    expect(screen.getByText("Not a Validated Digital Twin")).toBeInTheDocument();
  });
  it("keeps unsaved scenario input when switching language", async () => {
    show("/scenario");
    const budget = await screen.findByLabelText("Screening budget");
    await userEvent.clear(budget);
    await userEvent.type(budget, "17");
    await userEvent.click(screen.getByRole("button", { name: "ไทย" }));
    expect(screen.getByLabelText("งบคัดกรองจำลอง")).toHaveValue(17);
    expect(api.create).toHaveBeenCalledTimes(1);
  });
  it("sends canonical compound filters from a Thai interface", async () => {
    localStorage.setItem("curaloop-language", "th");
    show("/compounds");
    await userEvent.selectOptions(await screen.findByLabelText("สถานะสาร"), "pending");
    await waitFor(() => expect(api.candidates).toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ status: "pending" })));
  });
  it("browses actual eligible candidates without selecting assays or resetting on language change", async () => {
    const candidate = { compound_id: "SYN-01", status: "eligible", canonical_smiles: null,
      scaffold_id: null, feature_count: 8, feature_nonzero: 6, public_features_preview: [0.2],
      revealed_active: null, predicted_probability: null, explanation: null };
    vi.mocked(api.candidates).mockResolvedValueOnce({ items: [candidate], total: 2, page: 1, page_size: 1 })
      .mockResolvedValueOnce({ items: [{ ...candidate, compound_id: "SYN-02" }], total: 2, page: 2, page_size: 1 });
    const action = vi.spyOn(api, "action");
    show();
    await screen.findByText("SYN-01");
    await userEvent.click(screen.getByRole("button", { name: "Next compound" }));
    await screen.findByText("SYN-02");
    expect(api.candidates).toHaveBeenLastCalledWith(expect.any(String), { page_size: 1, page: 2, status: "eligible" });
    await userEvent.click(screen.getByRole("button", { name: "ไทย" }));
    expect(screen.getByText("SYN-02")).toBeInTheDocument();
    expect(api.candidates).toHaveBeenCalledTimes(2);
    expect(api.create).toHaveBeenCalledTimes(1);
    expect(action).not.toHaveBeenCalled();
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
      await screen.findByRole("heading", { name: "Digital Twin Simulation Lab" }),
    ).toBeInTheDocument();
  });
  it("turns a real action response into a pending state, with no fake hits", async () => {
    vi.spyOn(api, "action").mockResolvedValue(fixtures.pending as RunView);
    show("/lab");
    await screen.findByRole("heading", { name: "Digital Twin Simulation Lab" });
    expect(screen.getByRole("button", { name: "Advance +1 step" })).toBeDisabled();
    await userEvent.click(screen.getByRole("button", { name: "Select next batch" }));
    await waitFor(() =>
      expect(api.action).toHaveBeenCalledWith(expect.anything(), "select"),
    );
    expect(await screen.findByText("Awaiting feedback")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Advance +1 step" })).toBeEnabled();
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
      await screen.findByRole("heading", { name: "Discovery overview" }),
    ).toBeInTheDocument();
  });
  it("preserves provenance, weak evaluation and controller fallback disclosures", async () => {
    show("/evidence");
    // The first lazy-route transform can exceed Testing Library's one-second
    // default on the explicitly capped single-core acceptance machine.
    await screen.findByRole("heading", { name: "Research evidence" }, { timeout: 10000 });
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
    expect(screen.getByRole("button", { name: "Advance +1 step" })).toBeEnabled();
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
    expect(await screen.findByRole("heading", { name: "Discovery overview" })).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("en");
  });
  it("blocks old-campaign actions while a saved revision is recovering across navigation", async () => {
    localStorage.setItem("curaloop-session", fixtures.run.session_id);
    vi.mocked(api.runs).mockResolvedValue({ items: [], recovery_issues: [{ kind: "run", id: "damaged", message: "A saved campaign needs recovery." }], storage: { schema_version: 1, status: "ok" } });
    vi.spyOn(api, "revisions").mockResolvedValue({ session_id: "damaged", items: [{ revision: 2, saved_at: "2026-11-04T10:00:00Z" }] });
    let completeRecovery!: (run: RunView) => void;
    vi.spyOn(api, "recoverRevision").mockImplementation(() => new Promise(resolve => { completeRecovery = resolve; }));
    vi.spyOn(api, "action").mockResolvedValue(fixtures.run as RunView);
    show("/evidence");
    await screen.findByRole("heading", { name: "Research evidence" });
    await userEvent.click(await screen.findByRole("button", { name: "Inspect saved revisions" }));
    await userEvent.click(await screen.findByRole("button", { name: "Recover selected revision" }));
    expect(api.recoverRevision).toHaveBeenCalledWith("damaged", 2);
    await userEvent.click(screen.getByRole("link", { name: "Simulation lab" }));
    await screen.findByRole("heading", { name: "Digital Twin Simulation Lab" });
    const select = screen.getByRole("button", { name: "Select next batch" });
    expect(select).toBeDisabled();
    await userEvent.click(select);
    expect(api.action).not.toHaveBeenCalled();
    await act(async () => { completeRecovery({ ...fixtures.pending, session_id: "recovered-session" } as RunView); });
    expect(await screen.findByText("Awaiting feedback")).toBeInTheDocument();
    expect(localStorage.getItem("curaloop-session")).toBe("recovered-session");
    expect(screen.getByRole("button", { name: "Advance +1 step" })).toBeEnabled();
    expect(api.action).not.toHaveBeenCalled();
  });
  it("reports a stale-action refresh failure without an unhandled rejection", async () => {
    vi.spyOn(api, "action").mockRejectedValue(new ApiError("Stale action rejected.", 409));
    vi.mocked(api.run).mockRejectedValue(new ApiError("Local server unavailable.", 0));
    show("/lab");
    await screen.findByRole("heading", { name: "Digital Twin Simulation Lab" });
    await userEvent.click(screen.getByRole("button", { name: "Select next batch" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Refresh also failed: Local server unavailable.");
    expect(screen.getByRole("button", { name: "Select next batch" })).toBeEnabled();
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
    expect(screen.getByRole("button", { name: "Compare selected policies" })).toBeEnabled();
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
