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

import { answerQuiz, startQuiz, submitQuiz } from "../src/api/quiz";
import { toastState } from "../src/stores/toastStore";
import Quiz from "../src/views/Quiz.vue";

// Renders the page without loading a profile.
const RequireProfile = {
  setup(_, { slots }) {
    return () => slots.default();
  },
};

function httpError(status) {
  const error = new Error(`Request failed: ${status}`);
  error.status = status;
  return error;
}

// Starts a one-question quiz and answers it, which submits the result.
async function finishQuiz() {
  const wrapper = mount(Quiz, { global: { stubs: { RequireProfile } } });
  await wrapper.get("button").trigger("click");
  await flushPromises();
  await wrapper.get(".quiz-choice").trigger("click");
  await flushPromises();
  await vi.advanceTimersByTimeAsync(500);
  return wrapper;
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.clearAllMocks();
  vi.spyOn(console, "error").mockImplementation(() => {});
  toastState.toasts = [];
  startQuiz.mockResolvedValue({
    questions: [{ it: "pane", choices: ["bread", "cheese", "wine", "milk"] }],
    seconds_remaining: 250,
    pauses_remaining: 1,
  });
  answerQuiz.mockResolvedValue({ correct: true });
});
afterEach(() => vi.useRealTimers());

describe("Quiz submit", () => {
  it("offers to retry saving a failed result, without starting a new quiz", async () => {
    submitQuiz
      .mockRejectedValueOnce(httpError(500))
      .mockResolvedValueOnce({ score: 1, time_seconds: 10, is_new_best: false });

    const wrapper = await finishQuiz();
    expect(wrapper.text()).toContain("Could not save your result.");

    await wrapper.get("button").trigger("click");
    await flushPromises();

    expect(submitQuiz).toHaveBeenCalledTimes(2);
    expect(startQuiz).toHaveBeenCalledTimes(1);
    expect(wrapper.text()).toContain("Score: 1 / 1");
  });

  it("returns to the start screen when no quiz is in progress", async () => {
    submitQuiz.mockRejectedValueOnce(httpError(409));

    const wrapper = await finishQuiz();

    expect(wrapper.text()).toContain("Start Quiz");
    expect(toastState.toasts.map((t) => t.message)).toContain(
      "This quiz is no longer in progress.",
    );
  });
});
