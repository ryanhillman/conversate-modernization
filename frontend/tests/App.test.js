// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";

// auth.js needs Auth0 settings that CI doesn't have.
vi.mock("@auth0/auth0-vue", () => ({ useAuth0: () => ({ error: { value: null } }) }));
vi.mock("../src/auth", () => ({ auth0: {}, logout: vi.fn() }));
// The footer logo is served from public/, which tests can't import.
vi.mock("/logo.png", () => ({ default: "/logo.png" }));
// jsdom has no ResizeObserver, which the toasts use.
vi.stubGlobal(
  "ResizeObserver",
  class {
    observe() {}
    disconnect() {}
  },
);

import App from "../src/App.vue";

describe("App", () => {
  it("puts the page in a main landmark, with a skip link to it first", () => {
    const wrapper = mount(App, {
      global: { stubs: { NavBar: true, RouterView: true } },
    });

    expect(wrapper.find("main#main").exists()).toBe(true);
    expect(wrapper.find("a").attributes("href")).toBe("#main");
    expect(wrapper.find("a").text()).toBe("Skip to main content");
  });
});
