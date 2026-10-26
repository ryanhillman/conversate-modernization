// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
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

// jsdom has no microphone. This stands in for one whose permission prompt
// stays open until allow() is called.
function fakeMicrophone() {
  let grant;
  const track = { stop: vi.fn() };
  const recorders = [];
  const getUserMedia = vi.fn(
    () => new Promise((resolve) => (grant = () => resolve({ getTracks: () => [track] }))),
  );
  vi.stubGlobal("navigator", { mediaDevices: { getUserMedia } });
  vi.stubGlobal(
    "MediaRecorder",
    class {
      static isTypeSupported = () => true;
      constructor() {
        recorders.push(this);
      }
      addEventListener() {}
      start() {}
      stop() {}
    },
  );
  return { getUserMedia, track, recorders, allow: () => grant() };
}

afterEach(() => vi.unstubAllGlobals());

describe("Translate", () => {
  it("announces when both languages are the same", async () => {
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });

    await wrapper.get("#selectOutputLanguage").setValue("en");

    expect(wrapper.text()).toContain("Input and output language must be different.");
    expect(announce).toHaveBeenCalledWith("Input and output language must be different.");
  });

  it("marks each text box with the language it holds", async () => {
    translateText.mockResolvedValue({ translated_text: "ciao" });
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    const [input, output] = wrapper.findAll("textarea");
    expect(input.attributes("lang")).toBe("en");
    expect(output.attributes("lang")).toBeUndefined();

    await input.setValue("hello");
    await wrapper.get(".btn-accent").trigger("click");
    await flushPromises();
    expect(output.attributes("lang")).toBe("it");

    // The translation keeps its language when the pickers change afterward.
    await wrapper.get("#selectInputLanguage").setValue("it");
    await wrapper.get("#selectOutputLanguage").setValue("en");
    expect(input.attributes("lang")).toBe("it");
    expect(output.attributes("lang")).toBe("it");
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

  it("says in text, not just color, that it's recording", async () => {
    const mic = fakeMicrophone();
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });

    await wrapper.get('[aria-label="Start recording"]').trigger("click");
    mic.allow();
    await flushPromises();

    expect(wrapper.text()).toContain("Recording…");
    wrapper.unmount();
  });

  it("opens one microphone, even when the button is double-clicked", async () => {
    const mic = fakeMicrophone();
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    const button = wrapper.get('[aria-label="Start recording"]');

    await button.trigger("click");
    await button.trigger("click");
    mic.allow();
    await flushPromises();

    expect(mic.getUserMedia).toHaveBeenCalledTimes(1);
    wrapper.unmount();
  });

  it("turns the microphone off if the page is left during the permission prompt", async () => {
    const mic = fakeMicrophone();
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });

    await wrapper.get('[aria-label="Start recording"]').trigger("click");
    wrapper.unmount();
    mic.allow();
    await flushPromises();

    expect(mic.track.stop).toHaveBeenCalled();
    expect(mic.recorders).toEqual([]);
  });
});
