import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { computeAccessibleName } from "dom-accessibility-api";

vi.mock("../src/api/users", () => ({ getMe: vi.fn(), completeLesson: vi.fn() }));
vi.mock("../src/api/tts", () => ({ synthesizeSpeech: vi.fn() }));

import { synthesizeSpeech } from "../src/api/tts";
import { completeLesson } from "../src/api/users";
import { LESSONS } from "../src/data/lessons";
import { toastState } from "../src/stores/toastStore";
import Lesson from "../src/views/Lesson.vue";
import { RequireProfile } from "./helpers";

describe("Lesson", () => {
  it("titles the page with a heading", () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    expect(wrapper.get("h1").text()).toBe("Select any lesson to begin!");
  });

  it("gives each lesson a heading, and never skips a heading level in any lesson", async () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    expect(wrapper.findAll("h2").map((h) => h.text())).toEqual(
      LESSONS.map((lesson) => wrapper.get(`#${lesson.slug}-title`).text() + ":"),
    );

    for (const lesson of LESSONS) {
      await wrapper.get(`#${lesson.slug}`).trigger("click");
      const levels = wrapper
        .findAll("h1, h2, h3, h4, h5, h6")
        .map((h) => Number(h.element.tagName[1]));
      expect(levels.filter((level) => level === 1)).toHaveLength(1);
      levels.forEach((level, i) => {
        if (i > 0)
          expect(level, `${lesson.slug} heading ${i}`).toBeLessThanOrEqual(levels[i - 1] + 1);
      });
      await wrapper.get(`#${lesson.slug}`).trigger("click");
    }
  });

  it("makes each conjugation a button named Play plus the word, Play in English", async () => {
    const wrapper = mount(Lesson, {
      attachTo: document.body,
      global: { stubs: { RequireProfile } },
    });
    const lesson = LESSONS.find((l) => l.sections.some((s) => s.t === "conj"));
    await wrapper.get(`#${lesson.slug}`).trigger("click");

    const words = lesson.sections
      .filter((s) => s.t === "conj")
      .flatMap((s) => s.rows.map((r) => r[1]));
    const buttons = wrapper.findAll(".speakable");
    expect(buttons).toHaveLength(words.length);
    buttons.forEach((button, i) => {
      expect(button.element.tagName).toBe("BUTTON");
      expect(button.attributes("type")).toBe("button");
      expect(button.get(".visually-hidden").attributes("lang")).toBe("en");
      expect(computeAccessibleName(button.element)).toBe(`Play ${words[i]}`);
    });
    wrapper.unmount();
  });

  it("shows practice instructions right after the practice heading", async () => {
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    await wrapper.get("#regular-are-verbs").trigger("click");

    const heading = wrapper
      .findAll("h4")
      .find((h) => h.text() === "Now let's practice some on your own!").element;
    expect(heading.nextElementSibling.textContent).toBe("Fill in the correct form of the verb.");
  });

  it("says to wait a minute when playing a word hits the rate limit", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    synthesizeSpeech.mockRejectedValueOnce(
      Object.assign(new Error("30 per 1 minute"), { status: 429 }),
    );
    toastState.toasts = [];
    const wrapper = mount(Lesson, { global: { stubs: { RequireProfile } } });
    await wrapper.get("#avere-essere").trigger("click");

    await wrapper.get(".speakable").trigger("click");
    await flushPromises();

    expect(toastState.toasts.at(-1).message).toBe("Too many requests. Try again in a minute.");
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
    // The text marked Italian, minus any text inside it marked otherwise.
    const italian = (el) =>
      el.findAll('[lang="it"]').map((it) => {
        const copy = it.element.cloneNode(true);
        copy.querySelectorAll('[lang]:not([lang="it"])').forEach((other) => other.remove());
        return copy.textContent.trim();
      });

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
