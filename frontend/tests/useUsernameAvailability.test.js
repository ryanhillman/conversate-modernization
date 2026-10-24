import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { nextTick, ref } from "vue";

vi.mock("../src/api/users", () => ({ checkUsername: vi.fn() }));
// The composable registers an unmount hook, which Vue only allows inside a
// component; outside one it would just log a warning on every test.
vi.mock("vue", async (importOriginal) => ({
  ...(await importOriginal()),
  onBeforeUnmount: vi.fn(),
}));

import { checkUsername } from "../src/api/users";
import { useUsernameAvailability } from "../src/composables/useUsernameAvailability";

const DEBOUNCE_MS = 400;

async function type(username, value) {
  username.value = value;
  await nextTick();
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.clearAllMocks();
});
afterEach(() => vi.useRealTimers());

describe("useUsernameAvailability", () => {
  it("checks once, after typing pauses", async () => {
    checkUsername.mockResolvedValue({ available: true });
    const username = ref("");
    useUsernameAvailability(username);

    await type(username, "rya");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS - 1);
    await type(username, "ryan");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);

    expect(checkUsername).toHaveBeenCalledTimes(1);
    expect(checkUsername).toHaveBeenCalledWith("ryan");
  });

  it("reports taken only when the API says the name is unavailable", async () => {
    const username = ref("");
    const { takenUsername } = useUsernameAvailability(username);

    checkUsername.mockResolvedValue({ available: false });
    await type(username, "ryan_h");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);
    expect(takenUsername.value).toBe(true);

    checkUsername.mockResolvedValue({ available: true });
    await type(username, "ryan_h2");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);
    expect(takenUsername.value).toBe(false);
  });

  it("does not report a name as taken when the check fails", async () => {
    checkUsername.mockRejectedValue(new Error("network down"));
    const username = ref("");
    const { takenUsername, checking } = useUsernameAvailability(username);

    await type(username, "ryan_h");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);

    expect(takenUsername.value).toBe(false);
    expect(checking.value).toBe(false);
  });

  it("ignores a slow response that a newer keystroke has superseded", async () => {
    let resolveFirst;
    checkUsername
      .mockReturnValueOnce(new Promise((resolve) => (resolveFirst = resolve)))
      .mockResolvedValueOnce({ available: true });
    const username = ref("");
    const { takenUsername } = useUsernameAvailability(username);

    await type(username, "alice");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);
    await type(username, "alicia");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);
    resolveFirst({ available: false });
    await vi.advanceTimersByTimeAsync(0);

    expect(takenUsername.value).toBe(false);
  });

  it("skips the API for invalid names and for names the host marks as available", async () => {
    const username = ref("");
    const { validationError } = useUsernameAvailability(username, {
      skipAvailabilityCheck: (name) => name === "ryan_h",
    });

    await type(username, "ab");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);
    expect(validationError.value).toMatch(/at least 3/);

    await type(username, "ryan_h");
    await vi.advanceTimersByTimeAsync(DEBOUNCE_MS);

    expect(checkUsername).not.toHaveBeenCalled();
  });
});
