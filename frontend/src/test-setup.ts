import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";
import { configure } from "@testing-library/react";
// The first lazy route is transformed on demand in the test environment.
configure({ asyncUtilTimeout: 5000 });
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
vi.stubGlobal("ResizeObserver", ResizeObserverMock);
