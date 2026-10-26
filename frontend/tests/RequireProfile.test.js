// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

// The real module loads auth.js, which needs Auth0 settings that CI doesn't
// have.
vi.mock("../src/api/users", () => ({ getMe: vi.fn() }));

import { getMe } from "../src/api/users";
import RequireProfile from "../src/components/RequireProfile.vue";
import { toastState } from "../src/stores/toastStore";

describe("RequireProfile", () => {
  it("says on the page when the profile can't load, without a toast too", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    const error = new Error("Request failed: 500");
    error.status = 500;
    getMe.mockRejectedValue(error);
    toastState.toasts = [];

    const wrapper = mount(RequireProfile);
    await flushPromises();

    expect(wrapper.text()).toContain("Could not load your profile.");
    expect(toastState.toasts).toEqual([]);
  });

  it("keeps focus in place when Try again is used", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    const error = new Error("Request failed: 500");
    error.status = 500;
    getMe.mockReset().mockRejectedValueOnce(error).mockRejectedValueOnce(error);
    getMe.mockResolvedValueOnce({ username: "ryan_h" });
    const wrapper = mount(RequireProfile, {
      attachTo: document.body,
      slots: { default: "<p>Page content</p>" },
    });
    await flushPromises();

    // Fails again: focus lands on the new Try again.
    await wrapper.get("button").trigger("click");
    await flushPromises();
    expect(document.activeElement.textContent).toBe("Try again");

    // Loads: focus lands on the page that replaced it.
    await wrapper.get("button").trigger("click");
    await flushPromises();
    expect(document.activeElement.textContent).toBe("Page content");
    wrapper.unmount();
  });
});
