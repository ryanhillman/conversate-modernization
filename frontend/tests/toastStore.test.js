import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { clearErrorToasts, dismissToast, showToast, toastState } from "../src/stores/toastStore";

const messages = () => toastState.toasts.map((t) => t.message);

beforeEach(() => {
  vi.useFakeTimers();
  toastState.toasts = [];
});
afterEach(() => vi.useRealTimers());

describe("toastStore", () => {
  it("keeps an error until it's dismissed", () => {
    showToast("Could not save.", "error");
    vi.advanceTimersByTime(60_000);
    expect(messages()).toEqual(["Could not save."]);

    dismissToast(toastState.toasts[0].id);
    expect(messages()).toEqual([]);
  });

  it("hides a success message after 3.5 seconds", () => {
    showToast("Saved", "success");
    vi.advanceTimersByTime(3499);
    expect(messages()).toEqual(["Saved"]);
    vi.advanceTimersByTime(1);
    expect(messages()).toEqual([]);
  });

  it("clears errors but leaves success messages", () => {
    showToast("Could not save.", "error");
    showToast("Saved", "success");
    clearErrorToasts();
    expect(messages()).toEqual(["Saved"]);
  });
});
