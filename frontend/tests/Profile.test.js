import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { ref } from "vue";

vi.mock("@auth0/auth0-vue", async (importOriginal) => ({
  ...(await importOriginal()),
  useAuth0: () => ({ user: ref({ name: "Ryan Hillman", picture: "/me.png" }) }),
}));

import { setProfile } from "../src/stores/profileStore";
import Profile from "../src/views/Profile.vue";
import { RequireProfile } from "./helpers";

describe("Profile", () => {
  it("has an h1 for screen readers, without changing the layout", () => {
    setProfile({ username: "ryan_h", lessons_completed: [] });
    const wrapper = mount(Profile, {
      global: { stubs: { RequireProfile, AccountActions: true } },
    });

    const h1 = wrapper.findAll("h1");
    expect(h1.map((h) => h.text())).toEqual(["Profile"]);
    expect(h1[0].classes()).toContain("visually-hidden");
  });

  it("loads the profile picture without a referrer, which Google requires", () => {
    setProfile({ username: "ryan_h", lessons_completed: [] });
    const wrapper = mount(Profile, {
      global: { stubs: { RequireProfile, AccountActions: true } },
    });

    expect(wrapper.get(".profile-picture").attributes("referrerpolicy")).toBe("no-referrer");
  });
});
