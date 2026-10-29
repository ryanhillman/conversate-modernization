import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@auth0/auth0-vue", () => ({ createAuth0: vi.fn(() => ({})) }));

const VALID = {
  VITE_AUTH0_DOMAIN: "example.us.auth0.com",
  VITE_AUTH0_CLIENT_ID: "client-id",
  VITE_AUTH0_AUDIENCE: "https://api.example",
};

// auth.js checks its config when first imported, so each test loads it fresh.
async function loadWith(env) {
  vi.resetModules();
  for (const [name, value] of Object.entries(env)) vi.stubEnv(name, value);
  return import("../src/auth");
}

afterEach(() => vi.unstubAllEnvs());

describe("auth config", () => {
  it("creates the Auth0 client when every setting is present", async () => {
    await expect(loadWith(VALID)).resolves.toHaveProperty("auth0");
  });

  it("names every missing setting and how to fix it", async () => {
    await expect(
      loadWith({ ...VALID, VITE_AUTH0_DOMAIN: "", VITE_AUTH0_AUDIENCE: "" }),
    ).rejects.toThrow(
      "Missing VITE_AUTH0_DOMAIN, VITE_AUTH0_AUDIENCE. Copy frontend/.env.example to frontend/.env",
    );
  });
});
