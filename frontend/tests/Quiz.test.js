// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

vi.mock("../src/api/quiz", () => ({
  startQuiz: vi.fn(),
  answerQuiz: vi.fn(),
  pauseQuiz: vi.fn(),
  resumeQuiz: vi.fn(),
  submitQuiz: vi.fn(),
}));
// The profile store imports this; the real one loads auth.js, which needs
// Auth0 settings that CI doesn't have.
vi.mock("../src/api/users", () => ({ getMe: vi.fn() }));

import { answerQuiz, pauseQuiz, resumeQuiz, startQuiz, submitQuiz } from "../src/api/quiz";
import { toastState } from "../src/stores/toastStore";
import Quiz from "../src/views/Quiz.vue";

// Renders the page without loading a profile.
const RequireProfile = {
  setup(_, { slots }) {
    return () => slots.default();
  },
};

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
  vi.clearAllMocks();
  vi.spyOn(console, "error").mockImplementation(() => {});
  toastState.toasts = [];
  quizStarting(1);
  answerQuiz.mockResolvedValue({ correct: true });
});
afterEach(() => {
  wrapper?.unmount();
  vi.useRealTimers();
});

describe("Quiz submit", () => {
  it("offers to retry saving a failed result, without starting a new quiz", async () => {
    submitQuiz
      .mockRejectedValueOnce(httpError(500))
      .mockResolvedValueOnce({ score: 1, time_seconds: 10, is_new_best: false });

    wrapper = await finishQuiz();
    expect(wrapper.text()).toContain("Could not save your result.");
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

    expect(wrapper.text()).toContain("Start Quiz");
    expect(document.activeElement.textContent).toBe("Start Quiz");
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

describe("Quiz language", () => {
  it("marks the question word as Italian", async () => {
    wrapper = await startQuizPage();
    expect(wrapper.get(".quiz-word").attributes("lang")).toBe("it");
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
