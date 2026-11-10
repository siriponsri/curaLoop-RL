import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import App from "./App";
import { AppProvider } from "./state";
import { api, ApiError } from "./api";
import fixtures from "./__fixtures__/api-states.json";
import recorded from "./__fixtures__/cf1-equal-10.json";
import type { ConfirmationStudy } from "./confirmation";
import type { DatasetInfo, Evidence, Meta, PolicyInfo } from "./types";

beforeEach(() => {
  localStorage.clear();
  vi.spyOn(api, "meta").mockResolvedValue(fixtures.meta as Meta);
  vi.spyOn(api, "datasets").mockResolvedValue(fixtures.datasets as DatasetInfo[]);
  vi.spyOn(api, "policies").mockResolvedValue(fixtures.policies as PolicyInfo[]);
  vi.spyOn(api, "evidence").mockResolvedValue(fixtures.evidence as Evidence);
  vi.spyOn(api, "confirmation").mockResolvedValue(recorded as ConfirmationStudy);
  vi.spyOn(api, "create");
  vi.spyOn(api, "action");
  vi.spyOn(api, "runs");
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

function show() {
  render(<MemoryRouter initialEntries={["/confirmation"]}><AppProvider><App /></AppProvider></MemoryRouter>);
}

it("opens a real-source recorded study without creating or listing simulator campaigns", async () => {
  show();
  const table = await screen.findByRole("region", { name: "Confirmation comparison table" });
  expect(within(table).getAllByRole("row")).toHaveLength(19);
  expect(screen.getByText("6,896")).toBeInTheDocument();
  expect(api.create).not.toHaveBeenCalled();
  expect(api.action).not.toHaveBeenCalled();
  expect(api.runs).not.toHaveBeenCalled();
  expect(screen.getByText(/RL was not evaluated/)).toBeInTheDocument();
  await userEvent.click(screen.getByRole("link", { name: "Scenario builder" }));
  expect(await screen.findByRole("button", { name: "Create campaign" })).toBeInTheDocument();
  expect(api.create).not.toHaveBeenCalled();
  await userEvent.click(screen.getByRole("link", { name: "Confirmation evidence" }));
  await screen.findByRole("region", { name: "Confirmation comparison table" });
  expect(api.create).not.toHaveBeenCalled();
});

it("preserves campaign, budget and selected arm through an EN/TH switch and exports those exact filters", async () => {
  show();
  const table = await screen.findByRole("region", { name: "Confirmation comparison table" });
  await userEvent.click(within(table).getByRole("button", { name: /Random forest.*Group round-robin/ }));
  await userEvent.selectOptions(screen.getByLabelText("Study campaign"), "628/677");
  await waitFor(() => expect(api.confirmation).toHaveBeenLastCalledWith("628/677", 10));
  await userEvent.selectOptions(await screen.findByLabelText("Confirmation budget"), "5");
  await screen.findByRole("region", { name: "Confirmation comparison table" });
  await userEvent.click(screen.getByRole("button", { name: "ไทย" }));
  expect(screen.getByLabelText("แคมเปญในการศึกษา")).toHaveValue("628/677");
  expect(screen.getByLabelText("งบจำนวนการยืนยันผล")).toHaveValue("5");
  const link = screen.getByRole("link", { name: "ดาวน์โหลดบันทึกเปรียบเทียบ" });
  const query = new URL(link.getAttribute("href")!, "http://localhost").searchParams;
  expect(Object.fromEntries(query)).toEqual({ campaign: "628/677", budget_percent: "5", ranker: "rf", operator: "cluster_round_robin", locale: "th" });
  expect(api.create).not.toHaveBeenCalled();
  expect(api.action).not.toHaveBeenCalled();
});

it("fails closed with a useful unavailable state and retries without sample metrics", async () => {
  vi.mocked(api.confirmation).mockRejectedValueOnce(new ApiError("Source verification failed", 503));
  show();
  expect(await screen.findByRole("alert")).toHaveTextContent("Confirmation evidence unavailable");
  expect(screen.queryByRole("table")).not.toBeInTheDocument();
  expect(screen.queryByText("6,896")).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Retry study" }));
  await screen.findByRole("region", { name: "Confirmation comparison table" });
  expect(api.create).not.toHaveBeenCalled();
});
