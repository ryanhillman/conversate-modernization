// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

// The real API modules load auth.js, which needs Auth0 settings that CI
// doesn't have.
vi.mock("../src/api/users", () => ({ getMe: vi.fn(), completeLesson: vi.fn() }));
vi.mock("../src/api/tts", () => ({ synthesizeSpeech: vi.fn() }));

import { completeLesson } from "../src/api/users";
import { LESSONS } from "../src/data/lessons";
import Lesson from "../src/views/Lesson.vue";

// Renders the page without loading a profile.
const RequireProfile = {
  setup(_, { slots }) {
    return () => slots.default();
  },
};

describe("Lesson", () => {
  it("titles the page with a heading", () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    expect(wrapper.get("h1").text()).toBe("Select any lesson to begin!");
  });

  it("names each Toggle button with its visible text and the lesson title", () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    const button = wrapper.get(`#${LESSONS[0].slug}`);

    expect(button.text()).toBe("Toggle lesson");
    expect(button.attributes("aria-label")).toBe(`Toggle lesson: ${LESSONS[0].menuTitle}`);
  });

  it("moves focus to the Toggle button once Mark lesson complete disappears", async () => {
    const lesson = LESSONS.find((l) => !l.questions.length);
    completeLesson.mockResolvedValue({ username: "ryan_h", lessons_completed: [lesson.id] });
    const wrapper = mount(Lesson, {
      attachTo: document.body,
      global: { stubs: { RequireProfile } },
    });

    await wrapper.get(`#${lesson.slug}`).trigger("click");
    const markComplete = wrapper.get(".complete-lesson button");
    markComplete.element.focus();
    await markComplete.trigger("click");
    await flushPromises();

    expect(wrapper.find(".complete-lesson").exists()).toBe(false);
    expect(document.activeElement.id).toBe(lesson.slug);
    wrapper.unmount();
  });
});
