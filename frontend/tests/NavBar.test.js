// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
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
// The logo is served from public/, which tests can't import.
vi.mock("/logo.png", () => ({ default: "/logo.png" }));

import NavBar from "../src/components/NavBar.vue";

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
});
