import { describe, expect, it, vi } from "vitest";

// Every route is treated as signed in.
vi.mock("@auth0/auth0-vue", async (importOriginal) => ({
  ...(await importOriginal()),
  authGuard: () => true,
}));

import router, { reloadOnMissingFile } from "../src/router";
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

  it.each([
    ["script", "/quiz", "Failed to fetch dynamically imported module: /assets/Quiz-old.js"],
    ["stylesheet", "/lesson", "Unable to preload CSS for /assets/Lesson-old.css"],
  ])(
    "reloads once when a page's %s is gone after a deploy, not in a loop",
    async (_, path, message) => {
      sessionStorage.clear();
      const reload = vi.fn();
      const gone = new TypeError(message);
      const to = { fullPath: path };

      expect(reloadOnMissingFile(gone, to, reload)).toBe(true);
      expect(reload).toHaveBeenCalledWith(path);
      // Still missing after that reload: let the error stand.
      expect(reloadOnMissingFile(gone, to, reload)).toBe(false);
      expect(reload).toHaveBeenCalledTimes(1);

      // The page loading resets the guard, so a later deploy reloads again.
      await router.push(path);
      expect(reloadOnMissingFile(gone, to, reload)).toBe(true);
      expect(reload).toHaveBeenCalledTimes(2);
    },
  );

  it("doesn't reload for other errors", () => {
    sessionStorage.clear();
    const reload = vi.fn();
    expect(reloadOnMissingFile(new Error("Something else"), { fullPath: "/quiz" }, reload)).toBe(
      false,
    );
    expect(reload).not.toHaveBeenCalled();
  });
});
