// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

// The real API modules load auth.js, which needs Auth0 settings that CI
// doesn't have.
vi.mock("../src/api/leaderboard", () => ({
  getLeaderboard: vi.fn().mockResolvedValue([
    { username: "carla", score: 45, time_seconds: 200 },
    { username: "ryan_h", score: 40, time_seconds: 60 },
  ]),
}));
vi.mock("../src/api/users", () => ({ getMe: vi.fn() }));

import { getLeaderboard } from "../src/api/leaderboard";
import { setProfile } from "../src/stores/profileStore";
import { toastState } from "../src/stores/toastStore";
import Leaderboard from "../src/views/Leaderboard.vue";

// Renders the page without loading a profile.
const RequireProfile = {
  setup(_, { slots }) {
    return () => slots.default();
  },
};

describe("Leaderboard", () => {
  it("tells screen readers which row is yours", async () => {
    setProfile({ username: "ryan_h" });
    const wrapper = mount(Leaderboard, { global: { stubs: { RequireProfile } } });
    await flushPromises();

    const rows = wrapper.findAll("tbody tr");
    expect(rows[0].find(".visually-hidden").exists()).toBe(false);
    expect(rows[1].get(".visually-hidden").text()).toBe("(you)");
  });

  it("says when loading failed, instead of showing an empty leaderboard", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    getLeaderboard.mockRejectedValueOnce(new Error("down"));
    toastState.toasts = [];
    const wrapper = mount(Leaderboard, {
      attachTo: document.body,
      global: { stubs: { RequireProfile } },
    });
    await flushPromises();

    expect(wrapper.text()).toContain("Could not load the leaderboard.");
    expect(wrapper.text()).not.toContain("be the first");
    expect(toastState.toasts).toEqual([]);

    await wrapper.get("button").trigger("click");
    await flushPromises();

    expect(wrapper.findAll("tbody tr")).toHaveLength(2);
    expect(document.activeElement).toBe(wrapper.get(".leaderboard-wrap").element.parentElement);
    wrapper.unmount();
  });
});
