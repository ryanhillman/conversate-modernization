import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

vi.mock("../src/api/users", () => ({ getMe: vi.fn() }));
vi.mock("../src/stores/announceStore", () => ({ announce: vi.fn() }));
vi.mock("vue-router", () => ({ useRoute: () => ({ meta: { title: "Mastery" } }) }));

import { getMe } from "../src/api/users";
import { announce } from "../src/stores/announceStore";
import RequireProfile from "../src/components/RequireProfile.vue";
import { setProfile } from "../src/stores/profileStore";
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
    expect(announce).toHaveBeenCalledWith("Could not load your profile.");
  });

  it("gives the loading and error screens an h1 with the page's title", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    const error = new Error("Request failed: 500");
    error.status = 500;
    let fail;
    getMe.mockReset().mockReturnValue(new Promise((_, reject) => (fail = reject)));

    const wrapper = mount(RequireProfile);
    expect(wrapper.text()).toContain("Loading…");
    expect(wrapper.get("h1").text()).toBe("Mastery");

    fail(error);
    await flushPromises();
    expect(wrapper.text()).toContain("Could not load your profile.");
    expect(wrapper.get("h1").text()).toBe("Mastery");
  });

  it("titles the page for the username form, then shows the page in place once it's set", async () => {
    const error = new Error("Request failed: 404");
    error.status = 404;
    getMe.mockReset().mockRejectedValue(error);
    document.title = "Mastery | Conversate";

    const wrapper = mount(RequireProfile, {
      attachTo: document.body,
      global: { stubs: { SetUsername: true } },
      slots: { default: "<p>Page content</p>" },
    });
    await flushPromises();
    expect(document.title).toBe("Set your username | Conversate");

    setProfile({ username: "ryan_h" });
    await flushPromises();

    expect(wrapper.text()).toBe("Page content");
    expect(document.title).toBe("Mastery | Conversate");
    expect(document.activeElement.textContent).toBe("Page content");
    wrapper.unmount();
    setProfile(null);
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
