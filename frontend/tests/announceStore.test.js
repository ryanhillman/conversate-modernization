import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { announce, announcement } from "../src/stores/announceStore";

beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

describe("announce", () => {
  it("clears the region, then sets the message", () => {
    announce("Correct");
    expect(announcement.value).toBe("");
    vi.advanceTimersByTime(50);
    expect(announcement.value).toBe("Correct");
  });

  it("re-announces the same message by clearing it first", () => {
    announce("Incorrect");
    vi.advanceTimersByTime(50);
    announce("Incorrect");
    expect(announcement.value).toBe("");
    vi.advanceTimersByTime(50);
    expect(announcement.value).toBe("Incorrect");
  });

  it("keeps only the latest of rapid messages", () => {
    announce("Correct");
    announce("Lesson complete!");
    vi.advanceTimersByTime(50);
    expect(announcement.value).toBe("Lesson complete!");
  });
});
