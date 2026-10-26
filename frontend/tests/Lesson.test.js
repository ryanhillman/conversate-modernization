// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";

// The real API modules load auth.js, which needs Auth0 settings that CI
// doesn't have.
vi.mock("../src/api/users", () => ({ getMe: vi.fn(), completeLesson: vi.fn() }));
vi.mock("../src/api/tts", () => ({ synthesizeSpeech: vi.fn() }));

import { LESSONS } from "../src/data/lessons";
import Lesson from "../src/views/Lesson.vue";

// Renders the page without loading a profile.
const RequireProfile = {
  setup(_, { slots }) {
    return () => slots.default();
  },
};

describe("Lesson", () => {
  it("names each Toggle button with its visible text and the lesson title", () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    const button = wrapper.get(`#${LESSONS[0].slug}`);

    expect(button.text()).toBe("Toggle lesson");
    expect(button.attributes("aria-label")).toBe(`Toggle lesson: ${LESSONS[0].menuTitle}`);
  });
});
