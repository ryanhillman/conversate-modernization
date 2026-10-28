import { afterEach, describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";

import Home from "../src/views/Home.vue";

const mountHome = () => mount(Home, { global: { stubs: { RouterLink: true } } });
const shines = (wrapper) => wrapper.get(".welcome-card").classes().includes("welcome-shine");

afterEach(() => {
  sessionStorage.clear();
  vi.restoreAllMocks();
});

describe("Home", () => {
  it("sweeps the welcome only the first time Home appears in a session", () => {
    expect(shines(mountHome())).toBe(true);
    expect(shines(mountHome())).toBe(false);
  });

  it("still sweeps when session storage isn't available", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(shines(mountHome())).toBe(true);
  });
});
