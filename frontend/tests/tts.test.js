import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../src/api/http", () => ({ api: vi.fn() }));

// The cache lives in module scope, so each test imports a fresh copy.
async function load() {
  vi.resetModules();
  const { api } = await import("../src/api/http");
  const { synthesizeSpeech } = await import("../src/api/tts");
  return { api, synthesizeSpeech };
}

describe("synthesizeSpeech cache", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shares one request for repeated text in the same language", async () => {
    const { api, synthesizeSpeech } = await load();
    api.mockResolvedValue({ audio_content: "abc" });

    const first = synthesizeSpeech("ciao", "it");
    const second = synthesizeSpeech("ciao", "it");

    expect(second).toBe(first);
    expect(api).toHaveBeenCalledTimes(1);
    await expect(first).resolves.toEqual({ audio_content: "abc" });
  });

  it("keys on language as well as text", async () => {
    const { api, synthesizeSpeech } = await load();
    api.mockResolvedValue({ audio_content: "abc" });

    synthesizeSpeech("ciao", "it");
    synthesizeSpeech("ciao", "en");

    expect(api).toHaveBeenCalledTimes(2);
  });

  it("does not cache a failed request", async () => {
    const { api, synthesizeSpeech } = await load();
    api.mockRejectedValueOnce(new Error("down")).mockResolvedValue({ audio_content: "abc" });

    await expect(synthesizeSpeech("ciao", "it")).rejects.toThrow("down");
    await expect(synthesizeSpeech("ciao", "it")).resolves.toEqual({ audio_content: "abc" });
    expect(api).toHaveBeenCalledTimes(2);
  });

  it("evicts the least recently used clip past 100 entries", async () => {
    const { api, synthesizeSpeech } = await load();
    api.mockResolvedValue({ audio_content: "abc" });

    synthesizeSpeech("first", "it");
    for (let i = 0; i < 99; i++) synthesizeSpeech(`word ${i}`, "it");
    synthesizeSpeech("first", "it"); // reused, so now the most recent
    synthesizeSpeech("word 99", "it"); // 101st clip evicts the least recent: "word 0"
    expect(api).toHaveBeenCalledTimes(101);

    synthesizeSpeech("first", "it");
    expect(api).toHaveBeenCalledTimes(101); // still cached
    synthesizeSpeech("word 0", "it");
    expect(api).toHaveBeenCalledTimes(102); // was evicted
  });
});
