import { describe, expect, it, vi } from "vitest";

// Every route is treated as signed in; auth.js needs Auth0 settings that CI
// doesn't have.
vi.mock("@auth0/auth0-vue", () => ({ authGuard: () => true }));
vi.mock("../src/auth", () => ({ auth0: {} }));

import router from "../src/router";
import { showToast, toastState } from "../src/stores/toastStore";

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

  it("clears error toasts on a new page, but not on an in-page link", async () => {
    await router.push("/quiz");
    showToast("Could not pause the quiz.", "error");

    await router.push("/quiz#main");
    expect(toastState.toasts).toHaveLength(1);

    await router.push("/translate");
    expect(toastState.toasts).toEqual([]);
  });

  it("moves focus to the page content on a page change, not on an in-page link", async () => {
    const main = document.createElement("main");
    main.id = "main";
    main.tabIndex = -1;
    const button = document.createElement("button");
    document.body.append(main, button);

    await router.push("/quiz");
    button.focus();
    await router.push("/quiz#main");
    expect(document.activeElement).toBe(button);

    await router.push("/translate");
    expect(document.activeElement).toBe(main);
    main.remove();
    button.remove();
  });
});
