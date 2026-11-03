import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, request } from "./api";
afterEach(() => vi.unstubAllGlobals());
describe("typed API errors", () => {
  it("reports a readable local-server connection error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("failed fetch")),
    );
    await expect(request("/health")).rejects.toThrow(
      "Cannot reach the local API",
    );
  });
  it("retains the actual validation error and HTTP status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({ detail: "Budget must be nonnegative." }),
      }),
    );
    try {
      await request("/runs");
      throw new Error("Expected rejection");
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).status).toBe(422);
      expect((e as Error).message).toBe("Budget must be nonnegative.");
    }
  });
  it("accepts a successful empty DELETE response", async () => {
    const json = vi.fn();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 204, json }));
    await expect(request("/runs/old", { method: "DELETE" })).resolves.toBeUndefined();
    expect(json).not.toHaveBeenCalled();
  });
});
