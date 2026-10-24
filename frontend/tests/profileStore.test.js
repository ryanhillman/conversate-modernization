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
    getMe.mockResolvedValue({ user_name: "ryan_h" });

    await loadProfile();
    await loadProfile();

    expect(getMe).toHaveBeenCalledTimes(1);
    expect(profile.value).toEqual({ user_name: "ryan_h" });
  });

  it("shares one request between simultaneous loads", async () => {
    const { getMe, loadProfile } = await load();
    getMe.mockResolvedValue({ user_name: "ryan_h" });

    await Promise.all([loadProfile(), loadProfile(), loadProfile()]);

    expect(getMe).toHaveBeenCalledTimes(1);
  });

  it("retries after a failed load", async () => {
    const { getMe, loadProfile, profile } = await load();
    getMe.mockRejectedValueOnce(new Error("down")).mockResolvedValue({ user_name: "ryan_h" });

    await expect(loadProfile()).rejects.toThrow("down");
    expect(profile.value).toBeNull();
    await loadProfile();

    expect(getMe).toHaveBeenCalledTimes(2);
    expect(profile.value).toEqual({ user_name: "ryan_h" });
  });

  it("fetches again after the profile is cleared", async () => {
    const { getMe, loadProfile, setProfile, clearProfile, profile } = await load();
    getMe.mockResolvedValue({ user_name: "ryan_h" });

    setProfile({ user_name: "renamed" });
    await loadProfile();
    expect(getMe).not.toHaveBeenCalled();
    expect(profile.value).toEqual({ user_name: "renamed" });

    clearProfile();
    await loadProfile();
    expect(getMe).toHaveBeenCalledTimes(1);
  });
});
