import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

vi.mock("../src/api/quiz", () => ({
  startQuiz: vi.fn(),
  answerQuiz: vi.fn(),
  pauseQuiz: vi.fn(),
  resumeQuiz: vi.fn(),
  submitQuiz: vi.fn(),
}));
vi.mock("../src/stores/announceStore", () => ({ announce: vi.fn() }));

import { answerQuiz, pauseQuiz, resumeQuiz, startQuiz, submitQuiz } from "../src/api/quiz";
import { announce } from "../src/stores/announceStore";
import { toastState } from "../src/stores/toastStore";
import Quiz from "../src/views/Quiz.vue";
import { RequireProfile } from "./helpers";

const QUESTION = { it: "pane", choices: ["bread", "cheese", "wine", "milk"] };

function httpError(status) {
  const error = new Error(`Request failed: ${status}`);
  error.status = status;
  return error;
}

function quizStarting(questionCount) {
  startQuiz.mockResolvedValue({
    questions: Array.from({ length: questionCount }, (_, i) => ({ ...QUESTION, it: `word ${i}` })),
    seconds_remaining: 250,
    pauses_remaining: 1,
  });
}

// Attached, so focus can be checked; the real transition runs, so its
// after-enter hook fires.
async function startQuizPage() {
  const wrapper = mount(Quiz, {
    attachTo: document.body,
    global: { stubs: { RequireProfile, transition: false } },
  });
  await wrapper.get("button").trigger("click");
  await flushPromises();
  return wrapper;
}

async function answer(wrapper) {
  await wrapper.get(".quiz-choice").trigger("click");
  await flushPromises();
}

// Starts a one-question quiz and answers it, which submits the result.
async function finishQuiz() {
  const wrapper = await startQuizPage();
  await answer(wrapper);
  await vi.advanceTimersByTimeAsync(500);
  return wrapper;
}

let wrapper;

beforeEach(() => {
  vi.useFakeTimers();
  vi.resetAllMocks();
  vi.spyOn(console, "error").mockImplementation(() => {});
  toastState.toasts = [];
  quizStarting(1);
  answerQuiz.mockResolvedValue({ correct: true });
});
afterEach(() => {
  wrapper?.unmount();
  vi.useRealTimers();
});

describe("Quiz start", () => {
  it("announces a quiz that fails to load, since focus goes to Try again", async () => {
    startQuiz.mockRejectedValueOnce(httpError(500));
    wrapper = await startQuizPage();

    expect(wrapper.text()).toContain("Could not load the quiz.");
    expect(document.activeElement.textContent).toBe("Try again");
    expect(announce).toHaveBeenCalledWith("Could not load the quiz.");
  });
});

describe("Quiz start screen", () => {
  it("titles the start screen Timed Quiz, and offers Start and Practice", () => {
    wrapper = mount(Quiz, { global: { stubs: { RequireProfile } } });

    const h1 = wrapper.get("h1");
    expect(h1.text()).toBe("Timed Quiz");
    expect(h1.classes()).not.toContain("visually-hidden");
    expect(wrapper.findAll("button").map((b) => b.text())).toEqual(["Start", "Practice"]);
  });

  it("hides the title once a quiz starts, keeping it for screen readers", async () => {
    quizStarting(2);
    wrapper = await startQuizPage();
    const h1 = wrapper.get("h1");
    expect(h1.text()).toBe("Timed Quiz");
    expect(h1.classes()).toContain("visually-hidden");
  });
});

describe("Quiz practice", () => {
  it("runs without a timer or Pause, and says the result isn't saved", async () => {
    startQuiz.mockResolvedValue({
      questions: [QUESTION],
      practice: true,
      seconds_remaining: null,
      pauses_remaining: 0,
    });
    submitQuiz.mockResolvedValue({
      score: 1,
      time_seconds: 400,
      is_new_best: false,
      practice: true,
    });
    wrapper = mount(Quiz, {
      attachTo: document.body,
      global: { stubs: { RequireProfile, transition: false } },
    });

    await wrapper.findAll("button")[1].trigger("click");
    await flushPromises();
    expect(startQuiz).toHaveBeenCalledWith(true);
    expect(wrapper.get(".quiz-meta").text()).toContain("Practice: no timer");
    expect(wrapper.get("h1").text()).toBe("Practice");
    expect(wrapper.find(".quiz-timer").exists()).toBe(false);
    expect(wrapper.find(".quiz-meta button").exists()).toBe(false);

    // Well past the timed quiz's limit, the question is still there.
    await vi.advanceTimersByTimeAsync(400000);
    expect(submitQuiz).not.toHaveBeenCalled();

    await answer(wrapper);
    await vi.advanceTimersByTimeAsync(500);
    expect(wrapper.text()).toContain("Practice result, not saved to the leaderboard.");
  });
});

describe("Quiz submit", () => {
  it("offers to retry saving a failed result, without starting a new quiz", async () => {
    submitQuiz
      .mockRejectedValueOnce(httpError(500))
      .mockResolvedValueOnce({ score: 1, time_seconds: 10, is_new_best: false });

    wrapper = await finishQuiz();
    expect(wrapper.text()).toContain("Could not save your result.");
    expect(announce).toHaveBeenCalledWith("Could not save your result.");
    expect(document.activeElement.textContent).toBe("Try again");

    await wrapper.get("button").trigger("click");
    await flushPromises();

    expect(submitQuiz).toHaveBeenCalledTimes(2);
    expect(startQuiz).toHaveBeenCalledTimes(1);
    expect(wrapper.text()).toContain("Score: 1 / 1");
  });

  it("returns to the start screen when no quiz is in progress", async () => {
    submitQuiz.mockRejectedValueOnce(httpError(409));

    wrapper = await finishQuiz();

    expect(wrapper.text()).toContain("Practice");
    expect(document.activeElement.textContent.trim()).toBe("Start");
    expect(toastState.toasts.map((t) => t.message)).toContain(
      "This quiz is no longer in progress.",
    );
  });
});

describe("Quiz feedback", () => {
  it.each([
    [true, "✓"],
    [false, "✗"],
  ])("marks a %s answer with %s, not just color", async (correct, mark) => {
    answerQuiz.mockResolvedValue({ correct });
    wrapper = await startQuizPage();

    await answer(wrapper);

    expect(wrapper.get(".quiz-choice").text()).toBe(`${mark} bread`);
  });
});

describe("Quiz answers", () => {
  it("stay focusable while an answer is checked, ignoring more clicks", async () => {
    answerQuiz.mockReturnValue(new Promise(() => {}));
    wrapper = await startQuizPage();

    await wrapper.get(".quiz-choice").trigger("click");
    await wrapper.findAll(".quiz-choice")[1].trigger("click");

    for (const choice of wrapper.findAll(".quiz-choice")) {
      expect(choice.attributes("disabled")).toBeUndefined();
      expect(choice.attributes("aria-disabled")).toBe("true");
    }
    expect(answerQuiz).toHaveBeenCalledTimes(1);
  });

  it("keep Pause focusable while an answer is checked, ignoring clicks on it", async () => {
    quizStarting(2);
    answerQuiz.mockReturnValue(new Promise(() => {}));
    wrapper = await startQuizPage();

    await wrapper.get(".quiz-choice").trigger("click");
    const pause = wrapper.get(".quiz-meta button");
    await pause.trigger("click");

    expect(pause.attributes("disabled")).toBeUndefined();
    expect(pause.attributes("aria-disabled")).toBe("true");
    expect(pauseQuiz).not.toHaveBeenCalled();
  });
});

describe("Quiz timer", () => {
  it("labels the time left for screen readers", async () => {
    quizStarting(2);
    wrapper = await startQuizPage();
    expect(wrapper.get(".quiz-timer").text()).toBe("Time left: 4:10");
    expect(wrapper.get(".quiz-timer .visually-hidden").text()).toBe("Time left:");
  });
});

describe("Quiz language", () => {
  it("marks the question word as Italian", async () => {
    wrapper = await startQuizPage();
    expect(wrapper.get(".quiz-word").attributes("lang")).toBe("it");
  });
});

describe("Quiz headings", () => {
  it("has one h1, with the question word and New best! as h2s under it", async () => {
    submitQuiz.mockResolvedValue({ score: 1, time_seconds: 10, is_new_best: true });
    wrapper = await startQuizPage();
    expect(wrapper.findAll("h1").map((h) => h.text())).toEqual(["Timed Quiz"]);
    expect(wrapper.get(".quiz-word").element.tagName).toBe("H2");

    await answer(wrapper);
    await vi.advanceTimersByTimeAsync(500);
    expect(wrapper.findAll("h2").map((h) => h.text())).toEqual(["New best!"]);
  });
});

describe("Quiz focus", () => {
  it("moves focus to each new question, Resume, and the results", async () => {
    quizStarting(2);
    pauseQuiz.mockResolvedValue({ seconds_remaining: 200, pauses_remaining: 0 });
    resumeQuiz.mockResolvedValue({ seconds_remaining: 200, pauses_remaining: 0 });
    submitQuiz.mockResolvedValue({ score: 2, time_seconds: 50, is_new_best: false });
    wrapper = await startQuizPage();
    expect(document.activeElement.textContent).toBe("word 0");

    await wrapper.get(".quiz-meta button").trigger("click");
    await flushPromises();
    expect(document.activeElement.textContent).toBe("Resume");
    expect(document.activeElement.closest(".quiz-paused")).not.toBeNull();

    await wrapper.get(".quiz-paused button").trigger("click");
    await flushPromises();
    expect(document.activeElement.textContent).toBe("word 0");

    await answer(wrapper);
    await vi.advanceTimersByTimeAsync(1000);
    expect(document.activeElement.textContent).toBe("word 1");

    await answer(wrapper);
    await vi.advanceTimersByTimeAsync(1000);
    expect(document.activeElement.classList).toContain("quiz-results");
  });
});
