// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";

// Every route is treated as signed in; auth.js needs Auth0 settings that CI
// doesn't have.
vi.mock("@auth0/auth0-vue", () => ({ authGuard: () => true }));
vi.mock("../src/auth", () => ({ auth0: {} }));

import router from "../src/router";

describe("router", () => {
  it.each([
    ["/", "Conversate"],
    ["/quiz", "Quiz | Conversate"],
    ["/lesson", "Lessons | Conversate"],
    ["/no-such-page", "Page not found | Conversate"],
  ])("titles %s as %s", async (path, title) => {
    await router.push(path);
    expect(document.title).toBe(title);
  });
});
