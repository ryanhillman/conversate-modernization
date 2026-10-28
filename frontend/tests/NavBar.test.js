import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { computeAccessibleName } from "dom-accessibility-api";
import { ref } from "vue";

vi.mock("@auth0/auth0-vue", () => ({
  useAuth0: () => ({
    isAuthenticated: ref(true),
    isLoading: ref(false),
    user: ref({ name: "Ryan Hillman", picture: "/me.png" }),
  }),
}));
vi.mock("vue-router", () => ({ useRoute: () => ({ fullPath: "/" }) }));
// auth.js needs Auth0 settings that CI doesn't have.
vi.mock("../src/auth", () => ({ logout: vi.fn() }));
// On Windows, Vitest can't resolve the template's /logo.png, a public/ file.
vi.mock("/logo.png", () => ({ default: "/logo.png" }));

import { logout } from "../src/auth";
import NavBar from "../src/components/NavBar.vue";
import { pages } from "../src/router/pages";

describe("NavBar", () => {
  it("shows the user's name without making it a heading", () => {
    const wrapper = mount(NavBar, { global: { stubs: { RouterLink: true } } });

    expect(wrapper.find("h1, h2, h3, h4, h5, h6").exists()).toBe(false);
    expect(wrapper.get(".nav-user-name").text()).toBe("Ryan Hillman");
  });

  it("loads profile pictures without a referrer, which Google requires", () => {
    const wrapper = mount(NavBar, { global: { stubs: { RouterLink: true } } });
    const pictures = wrapper.findAll(".nav-user-profile");

    expect(pictures).toHaveLength(2);
    for (const picture of pictures) {
      expect(picture.attributes("referrerpolicy")).toBe("no-referrer");
    }
  });

  it("makes the menu toggle a button that controls the menu, not an ARIA menu", async () => {
    const wrapper = mount(NavBar, { global: { stubs: { RouterLink: true } } });
    const toggle = wrapper.get("#profileDropDown");

    expect(toggle.element.tagName).toBe("BUTTON");
    expect(toggle.attributes("type")).toBe("button");
    expect(toggle.attributes("aria-haspopup")).toBeUndefined();
    expect(wrapper.find(`#${toggle.attributes("aria-controls")}`).classes()).toContain(
      "dropdown-menu",
    );

    await toggle.trigger("click");
    expect(toggle.attributes("aria-expanded")).toBe("true");
  });

  it("logs out with buttons, not links", async () => {
    logout.mockClear();
    const wrapper = mount(NavBar, { global: { stubs: { RouterLink: true } } });
    const buttons = wrapper.findAll("button").filter((b) => b.text() === "Log out");

    expect(buttons).toHaveLength(2);
    expect(wrapper.findAll("a").filter((a) => a.text() === "Log out")).toHaveLength(0);
    for (const button of buttons) {
      expect(button.attributes("type")).toBe("button");
      await button.trigger("click");
    }
    expect(logout).toHaveBeenCalledTimes(2);
  });

  it("closes the menu when focus moves past it, but not when focus goes nowhere", async () => {
    const wrapper = mount(NavBar, { global: { stubs: { RouterLink: true } } });
    const toggle = wrapper.get("#profileDropDown");
    const menuItem = wrapper.get(".dropdown-item");
    await toggle.trigger("click");

    // A click that leaves focus nowhere (as Safari does on buttons).
    await menuItem.trigger("focusout", { relatedTarget: null });
    expect(toggle.attributes("aria-expanded")).toBe("true");

    // Tab from the menu to something after it.
    await menuItem.trigger("focusout", { relatedTarget: document.body });
    expect(toggle.attributes("aria-expanded")).toBe("false");
  });

  it("links every page, in order", () => {
    const wrapper = mount(NavBar, { global: { stubs: { RouterLink: true } } });

    expect(wrapper.findAll("router-link-stub").map((link) => link.attributes("to"))).toEqual(
      pages.map((page) => page.path),
    );
  });

  it("names the profile picture toggle for the menu it opens", () => {
    const wrapper = mount(NavBar, { global: { stubs: { RouterLink: true } } });

    expect(computeAccessibleName(wrapper.get("#profileDropDown").element)).toBe("Account menu");
  });
});
