import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../src/api/users", () => ({ getMe: vi.fn() }));

// The profile lives in module scope, so each test imports a fresh copy.
async function load() {
  vi.resetModules();
  const { getMe } = await import("../src/api/users");
  const store = await import("../src/stores/profileStore");
  return { getMe, ...store };
}

describe("profileStore", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches the profile once and reuses it", async () => {
    const { getMe, loadProfile, profile } = await load();
    getMe.mockResolvedValue({ username: "ryan_h" });

    await loadProfile();
    await loadProfile();

    expect(getMe).toHaveBeenCalledTimes(1);
    expect(profile.value).toEqual({ username: "ryan_h" });
  });

  it("shares one request between simultaneous loads", async () => {
    const { getMe, loadProfile } = await load();
    getMe.mockResolvedValue({ username: "ryan_h" });

    await Promise.all([loadProfile(), loadProfile(), loadProfile()]);

    expect(getMe).toHaveBeenCalledTimes(1);
  });

  it("retries after a failed load", async () => {
    const { getMe, loadProfile, profile } = await load();
    getMe.mockRejectedValueOnce(new Error("down")).mockResolvedValue({ username: "ryan_h" });

    await expect(loadProfile()).rejects.toThrow("down");
    expect(profile.value).toBeNull();
    await loadProfile();

    expect(getMe).toHaveBeenCalledTimes(2);
    expect(profile.value).toEqual({ username: "ryan_h" });
  });

  it("uses a profile set from another response without fetching", async () => {
    const { getMe, loadProfile, setProfile, profile } = await load();
    getMe.mockResolvedValue({ username: "ryan_h" });

    setProfile({ username: "renamed" });
    await loadProfile();

    expect(getMe).not.toHaveBeenCalled();
    expect(profile.value).toEqual({ username: "renamed" });
  });
});
