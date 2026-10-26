// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";

// The real API modules load auth.js, which needs Auth0 settings that CI
// doesn't have.
vi.mock("../src/api/translate", () => ({ translateText: vi.fn() }));
vi.mock("../src/api/tts", () => ({ synthesizeSpeech: vi.fn() }));
vi.mock("../src/api/stt", () => ({ transcribeSpeech: vi.fn() }));
vi.mock("../src/api/users", () => ({ getMe: vi.fn() }));
vi.mock("../src/stores/announceStore", () => ({ announce: vi.fn() }));

import { announce } from "../src/stores/announceStore";
import Translate from "../src/views/Translate.vue";

// Renders the page without loading a profile.
const RequireProfile = {
  setup(_, { slots }) {
    return () => slots.default();
  },
};

describe("Translate", () => {
  it("announces when both languages are the same", async () => {
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });

    await wrapper.get("#selectOutputLanguage").setValue("en");

    expect(wrapper.text()).toContain("Input and output language must be different.");
    expect(announce).toHaveBeenCalledWith("Input and output language must be different.");
  });
});
