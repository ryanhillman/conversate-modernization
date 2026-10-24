import { beforeEach, describe, expect, it, vi } from "vitest";

const auth0 = vi.hoisted(() => ({
  isAuthenticated: { value: true },
  getAccessTokenSilently: vi.fn(),
  loginWithRedirect: vi.fn(),
}));
vi.mock("../src/auth", () => ({ auth0 }));

import { api } from "../src/api/http";

const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

function respond(status, data) {
  fetchMock.mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => (data === undefined ? Promise.reject(new SyntaxError()) : Promise.resolve(data)),
  });
}

beforeEach(() => {
  vi.clearAllMocks();
  auth0.isAuthenticated.value = true;
  auth0.getAccessTokenSilently.mockResolvedValue("token-123");
});

describe("api re-login handling", () => {
  it.each(["login_required", "consent_required", "missing_refresh_token", "invalid_grant"])(
    "sends the user to log in on %s and never calls the API",
    async (code) => {
      auth0.getAccessTokenSilently.mockRejectedValue({ error: code });

      await expect(api("/api/me")).rejects.toEqual({ error: code });
      expect(auth0.loginWithRedirect).toHaveBeenCalledTimes(1);
      expect(fetchMock).not.toHaveBeenCalled();
    },
  );

  it("rethrows other token errors without redirecting", async () => {
    auth0.getAccessTokenSilently.mockRejectedValue({ error: "timeout" });

    await expect(api("/api/me")).rejects.toEqual({ error: "timeout" });
    expect(auth0.loginWithRedirect).not.toHaveBeenCalled();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe("api requests", () => {
  it("sends the access token and a JSON body", async () => {
    respond(200, { ok: true });

    await expect(api("/api/me", { method: "PUT", body: { user_name: "ryan_h" } })).resolves.toEqual(
      { ok: true },
    );
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toMatch(/\/api\/me$/);
    expect(init.method).toBe("PUT");
    expect(init.headers).toEqual({
      Authorization: "Bearer token-123",
      "Content-Type": "application/json",
    });
    expect(init.body).toBe('{"user_name":"ryan_h"}');
  });

  it("skips the token when signed out", async () => {
    auth0.isAuthenticated.value = false;
    respond(200, []);

    await api("/api/leaderboard");
    expect(auth0.getAccessTokenSilently).not.toHaveBeenCalled();
    expect(fetchMock.mock.calls[0][1].headers).toEqual({});
  });

  it("throws the server's error message with the status", async () => {
    respond(409, { error: "user_name already exists" });

    await expect(api("/api/me", { method: "PUT", body: {} })).rejects.toMatchObject({
      message: "user_name already exists",
      status: 409,
    });
  });

  it("throws on a successful response that isn't JSON", async () => {
    respond(200, undefined);

    await expect(api("/api/me")).rejects.toMatchObject({
      message: "Request failed: 200",
      status: 200,
    });
  });
});
