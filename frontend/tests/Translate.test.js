// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

// The real API modules load auth.js, which needs Auth0 settings that CI
// doesn't have.
vi.mock("../src/api/translate", () => ({ translateText: vi.fn() }));
vi.mock("../src/api/tts", () => ({ synthesizeSpeech: vi.fn() }));
vi.mock("../src/api/stt", () => ({ transcribeSpeech: vi.fn() }));
vi.mock("../src/api/users", () => ({ getMe: vi.fn() }));
vi.mock("../src/stores/announceStore", () => ({ announce: vi.fn() }));

import { translateText } from "../src/api/translate";
import { synthesizeSpeech } from "../src/api/tts";
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

  it("keeps the speaker button, disabled, while its audio loads", async () => {
    translateText.mockResolvedValue({ translated_text: "ciao" });
    synthesizeSpeech.mockReturnValue(new Promise(() => {}));
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    await wrapper.get("textarea").setValue("hello");
    await wrapper.get(".btn-accent").trigger("click");
    await flushPromises();

    await wrapper.get('[aria-label="Listen to translation"]').trigger("click");

    const speaker = wrapper.find('[aria-label="Listen to translation"]');
    expect(speaker.exists()).toBe(true);
    expect(speaker.attributes("disabled")).toBeDefined();
  });
});
