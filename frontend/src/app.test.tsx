import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import App from "./App";
import { AppProvider } from "./state";
import { api } from "./api";
import fixtures from "./__fixtures__/api-states.json";
import type { DatasetInfo, Evidence, Meta, PolicyInfo, RunView } from "./types";

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
  it("switches Thai language and keeps an explicit scientific limitation", async () => {
    show("/lab");
    await screen.findByRole("heading", { name: "Simulation lab" });
    await userEvent.click(screen.getByRole("button", { name: "TH" }));
    expect(
      screen.getByRole("heading", { name: "ห้องจำลองการคัดเลือกสาร" }),
    ).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("th");
    expect(
      screen.getByText("ยังไม่ใช่ Digital Twin ที่ผ่านการยืนยัน"),
    ).toBeInTheDocument();
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
});
