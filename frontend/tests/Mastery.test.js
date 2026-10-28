import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";

import { setProfile } from "../src/stores/profileStore";
import Mastery from "../src/views/Mastery.vue";
import { RequireProfile } from "./helpers";

describe("Mastery", () => {
  it("has one h1, then steps down to h2", () => {
    setProfile({ username: "ryan_h", lessons_completed: [1] });
    const wrapper = mount(Mastery, { global: { stubs: { RequireProfile } } });

    expect(wrapper.findAll("h1").map((h) => h.text())).toEqual(["Mastery"]);
    expect(wrapper.findAll("h2").map((h) => h.text())).toEqual(["Completed Lessons"]);
    expect(wrapper.find("h3").exists()).toBe(false);
  });

  it("marks the Italian in completed lesson titles", () => {
    setProfile({ username: "ryan_h", lessons_completed: [1] });
    const wrapper = mount(Mastery, { global: { stubs: { RequireProfile } } });

    const item = wrapper.get(".completed-list li");
    expect(item.text()).toContain("Lesson 1: Avere and Essere");
    expect(item.findAll('[lang="it"]').map((span) => span.text())).toEqual(["Avere", "Essere"]);
  });

  it("hides each check mark from screen readers, as the heading says they're completed", () => {
    setProfile({ username: "ryan_h", lessons_completed: [1] });
    const wrapper = mount(Mastery, { global: { stubs: { RequireProfile } } });

    expect(wrapper.get(".completed-check").attributes("aria-hidden")).toBe("true");
  });
});
