import { describe, expect, it } from "vitest";
import { isAnswerCorrect, isLessonComplete, normalizeAnswer } from "../src/utils/grading";

describe("normalizeAnswer", () => {
  it("trims and lowercases, treating missing values as empty", () => {
    expect(normalizeAnswer("  Abbiamo ")).toBe("abbiamo");
    expect(normalizeAnswer(undefined)).toBe("");
  });
});

describe("isAnswerCorrect", () => {
  it("ignores capitalization and surrounding spaces", () => {
    expect(isAnswerCorrect(" ABBIAMO ", ["abbiamo"])).toBe(true);
  });

  it("ignores end punctuation and extra spaces, but not accents", () => {
    expect(isAnswerCorrect("Good  evening !", ["good evening"])).toBe(true);
    expect(isAnswerCorrect("hello?!", ["hello"])).toBe(true);
    expect(isAnswerCorrect("e", ["è"])).toBe(false);
  });

  it("accepts any of several correct answers", () => {
    expect(isAnswerCorrect("good evening", ["good evening", "evening"])).toBe(true);
    expect(isAnswerCorrect("evening", ["good evening", "evening"])).toBe(true);
  });

  it("rejects wrong and empty answers", () => {
    expect(isAnswerCorrect("avete", ["abbiamo"])).toBe(false);
    expect(isAnswerCorrect("   ", [""])).toBe(false);
  });
});

describe("isLessonComplete", () => {
  const questions = [
    { id: "q1", correctAnswers: ["abbiamo"] },
    { id: "q2", correctAnswers: ["sono"] },
  ];

  it("is complete only when every answer is correct", () => {
    expect(isLessonComplete(questions, { q1: "abbiamo", q2: "Sono" })).toBe(true);
    expect(isLessonComplete(questions, { q1: "abbiamo", q2: "siamo" })).toBe(false);
    expect(isLessonComplete(questions, { q1: "abbiamo" })).toBe(false);
  });

  it("is never complete for a lesson with no questions", () => {
    expect(isLessonComplete([], {})).toBe(false);
  });
});
