import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import App from "./App";
import { AppProvider } from "./state";
import { api } from "./api";
import { agentApi, type AgentMission } from "./agent-rd";
import fixtures from "./__fixtures__/api-states.json";
import recorded from "./__fixtures__/cf1-equal-10.json";
import real from "./__fixtures__/agent-real-development-v3.json";
import type { ConfirmationStudy } from "./confirmation";
import type { DatasetInfo, Evidence, Meta, PolicyInfo } from "./types";

beforeEach(() => {
  localStorage.clear();
  vi.spyOn(api, "meta").mockResolvedValue(fixtures.meta as Meta);
  vi.spyOn(api, "datasets").mockResolvedValue(fixtures.datasets as DatasetInfo[]);
  vi.spyOn(api, "policies").mockResolvedValue(fixtures.policies as PolicyInfo[]);
  vi.spyOn(api, "evidence").mockResolvedValue(fixtures.evidence as Evidence);
  vi.spyOn(api, "confirmation").mockResolvedValue(recorded as ConfirmationStudy);
  vi.spyOn(api, "create"); vi.spyOn(api, "action"); vi.spyOn(api, "runs");
  vi.spyOn(agentApi, "list").mockResolvedValue({ items: [], integrity_issues: [] });
  vi.spyOn(agentApi, "runtime").mockResolvedValue({ authorization_active: true, evaluation_locked: false, model: "recorded test identity", provider_health: "NOT_PROBED", paid_fallback: false });
  vi.spyOn(agentApi, "create"); vi.spyOn(agentApi, "read"); vi.spyOn(agentApi, "act");
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); });
function show() { render(<MemoryRouter initialEntries={["/agent"]}><AppProvider><App /></AppProvider></MemoryRouter>); }

it("opens an empty mission workspace without starting model or simulator execution", async () => {
  show();
  expect(await screen.findByText("No generated results are shown before execution.")).toBeInTheDocument();
  expect(agentApi.create).not.toHaveBeenCalled();
  expect(api.create).not.toHaveBeenCalled(); expect(api.action).not.toHaveBeenCalled(); expect(api.runs).not.toHaveBeenCalled();
});

it("shows a preserved actual development response and requires explicit dossier action", async () => {
  vi.mocked(agentApi.list).mockResolvedValue({ items: [real as AgentMission], integrity_issues: [] });
  vi.mocked(agentApi.read).mockResolvedValue(real as AgentMission);
  vi.mocked(agentApi.act).mockResolvedValue({ ...real, files: ["dossier.json"], base_url: "/recorded-dossier/" } as AgentMission & { files: string[]; base_url: string });
  show();
  await userEvent.click(await screen.findByRole("button", { name: /Report only the mean H and D/ }));
  expect(await screen.findByText("Source-backed values")).toBeInTheDocument();
  expect(screen.getByText("136.2")).toBeInTheDocument();
  expect(screen.getByText(/a0 = mvsa\/top_ranked/)).toBeInTheDocument();
  expect(screen.getByLabelText("Study campaign")).toHaveValue(real.spec.campaign);
  expect(screen.getByLabelText("Mission goal")).toHaveValue(real.spec.goal);
  expect(agentApi.act).not.toHaveBeenCalled();
  await userEvent.click(screen.getByRole("button", { name: /Prepare local dossier/ }));
  expect(await screen.findByRole("link", { name: "Open dossier" })).toHaveAttribute("href", "/recorded-dossier/report-en.html");
  expect(agentApi.act).toHaveBeenCalledWith(real.mission_id, real.revision, "export");
});

it("retains provider failure as an error instead of showing a fabricated result", async () => {
  vi.mocked(agentApi.create).mockResolvedValue({ ...real, state: "FAILED", released: null, error: "Owned model unavailable", calls: [], cost: { ...real.cost, failed_calls: 1 } } as AgentMission);
  show();
  await waitFor(() => expect(screen.getByRole("button", { name: "Run research mission" })).toBeEnabled());
  await userEvent.click(screen.getByRole("button", { name: "Run research mission" }));
  expect(await screen.findByText("Owned model unavailable")).toBeInTheDocument();
  expect(screen.queryByText("Source-backed values")).not.toBeInTheDocument();
  expect(screen.getByText("The failed attempt is retained. No mock result or provider substitution was used.")).toBeInTheDocument();
});

it("switches the mission controls to Thai without creating a mission", async () => {
  show();
  await screen.findByText("No generated results are shown before execution.");
  await userEvent.click(screen.getByRole("button", { name: "ไทย" }));
  expect(screen.getByLabelText("โจทย์ที่ต้องการศึกษา")).toBeInTheDocument();
  expect(agentApi.create).not.toHaveBeenCalled();
});
