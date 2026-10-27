// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { computeAccessibleName } from "dom-accessibility-api";

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

  it("names each Toggle button from its own text and the marked-up title", () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    const button = wrapper.get("#avere-essere");

    expect(button.text()).toBe("Toggle lesson");
    expect(button.attributes("aria-label")).toBeUndefined();
    expect(button.attributes("aria-labelledby")).toBe("avere-essere-toggle avere-essere-title");
    const title = wrapper.get("#avere-essere-title");
    expect(title.text()).toBe("Avere and Essere");
    expect(title.findAll('[lang="it"]').map((span) => span.text())).toEqual(["Avere", "Essere"]);
  });

  it("gives each Toggle button the accessible name Toggle lesson plus its title", () => {
    const wrapper = mount(Lesson, {
      attachTo: document.body,
      global: { stubs: { RequireProfile } },
    });

    for (const lesson of LESSONS) {
      const button = wrapper.get(`#${lesson.slug}`).element;
      const title = wrapper.get(`#${lesson.slug}-title`).text();
      expect(computeAccessibleName(button)).toBe(`Toggle lesson ${title}`);
    }
    wrapper.unmount();
  });

  it("marks Italian in titles, conjugations, prompts, and answer boxes", async () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    const italian = (el) => el.findAll('[lang="it"]').map((span) => span.text());

    expect(italian(wrapper.get('label[for="avere-essere"]'))).toEqual(["Avere", "Essere"]);

    await wrapper.get("#avere-essere").trigger("click");
    expect(italian(wrapper.get(".lesson-content ul"))).toEqual([
      "io",
      "ho",
      "tu",
      "hai",
      "lui/lei",
      "ha",
      "noi",
      "abbiamo",
      "voi",
      "avete",
      "loro",
      "hanno",
    ]);
    expect(wrapper.get("#lesson-1-question-1").attributes("lang")).toBe("it");

    await wrapper.get("#basic-greetings").trigger("click");
    expect(italian(wrapper.get('label[for="lesson-2-question-1"]'))).toEqual(["Ciao"]);
    expect(wrapper.get("#lesson-2-question-1").attributes("lang")).toBe("en");
  });

  it("never shows the markup itself, in any lesson", async () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    for (const lesson of LESSONS) {
      await wrapper.get(`#${lesson.slug}`).trigger("click");
      expect(wrapper.text(), lesson.slug).not.toMatch(/<\/?(i|strong|it)>/);
    }
  });

  it("keeps Mark lesson complete focusable while it saves", async () => {
    const lesson = LESSONS.find((l) => !l.questions.length);
    completeLesson.mockReturnValueOnce(new Promise(() => {}));
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    await wrapper.get(`#${lesson.slug}`).trigger("click");

    const button = wrapper.get(".complete-lesson button");
    await button.trigger("click");
    await button.trigger("click");

    expect(button.attributes("disabled")).toBeUndefined();
    expect(button.attributes("aria-disabled")).toBe("true");
    expect(completeLesson).toHaveBeenCalledTimes(1);
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
