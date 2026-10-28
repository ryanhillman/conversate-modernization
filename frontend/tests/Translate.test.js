import { afterEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { computeAccessibleDescription, computeAccessibleName } from "dom-accessibility-api";

vi.mock("../src/api/translate", () => ({ translateText: vi.fn() }));
vi.mock("../src/api/tts", () => ({ synthesizeSpeech: vi.fn() }));
vi.mock("../src/api/stt", () => ({ transcribeSpeech: vi.fn() }));
vi.mock("../src/stores/announceStore", () => ({ announce: vi.fn() }));

import { transcribeSpeech } from "../src/api/stt";
import { translateText } from "../src/api/translate";
import { synthesizeSpeech } from "../src/api/tts";
import { announce } from "../src/stores/announceStore";
import { toastState } from "../src/stores/toastStore";
import Translate from "../src/views/Translate.vue";
import { RequireProfile } from "./helpers";

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
      listeners = {};
      constructor() {
        recorders.push(this);
      }
      addEventListener(type, listener) {
        this.listeners[type] = listener;
      }
      start() {}
      stop() {
        this.listeners.stop?.();
      }
    },
  );
  return { getUserMedia, track, recorders, allow: () => grant() };
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

// A busy button stays focusable (aria-disabled, not disabled).
function expectBusy(button) {
  expect(button.attributes("disabled")).toBeUndefined();
  expect(button.attributes("aria-disabled")).toBe("true");
}

describe("Translate", () => {
  it("titles the page with its one h1", () => {
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    expect(wrapper.findAll("h1").map((h) => h.text())).toEqual(["Translate"]);
  });

  it("announces when both languages are the same", async () => {
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });

    await wrapper.get("#selectOutputLanguage").setValue("en");

    expect(wrapper.text()).toContain("Input and output language must be different.");
    expect(announce).toHaveBeenCalledWith("Input and output language must be different.");
  });

  it("announces when the translation arrives", async () => {
    translateText.mockResolvedValue({ translated_text: "ciao" });
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    await wrapper.get("textarea").setValue("hello");

    await wrapper.get(".btn-accent").trigger("click");
    await flushPromises();

    expect(announce).toHaveBeenCalledWith("Translation ready.");
  });

  it("announces when the transcript arrives", async () => {
    transcribeSpeech.mockResolvedValue({ transcript: "ciao" });
    const mic = fakeMicrophone();
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });

    await wrapper.get('[aria-label="Start recording"]').trigger("click");
    mic.allow();
    await flushPromises();
    await wrapper.get('[aria-label="Stop recording"]').trigger("click");
    // Reading the recording uses a FileReader, which finishes on a later task.
    await vi.waitFor(() => expect(wrapper.findAll("textarea")[0].element.value).toBe("ciao"));
    expect(announce).toHaveBeenCalledWith("Transcript added.");
    wrapper.unmount();
  });

  it("says to wait a minute when translate, listen, or record hits the rate limit", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    const limited = Object.assign(new Error("30 per 1 minute"), { status: 429 });
    const wait = "Too many requests. Try again in a minute.";
    const lastToast = () => toastState.toasts.at(-1)?.message;
    const mic = fakeMicrophone();
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    await wrapper.get("textarea").setValue("hello");

    translateText.mockRejectedValueOnce(limited);
    await wrapper.get(".btn-accent").trigger("click");
    await flushPromises();
    expect(lastToast()).toBe(wait);

    toastState.toasts = [];
    translateText.mockResolvedValueOnce({ translated_text: "ciao" });
    synthesizeSpeech.mockRejectedValueOnce(limited);
    await wrapper.get(".btn-accent").trigger("click");
    await flushPromises();
    await wrapper.get('[aria-label="Listen to translation"]').trigger("click");
    await flushPromises();
    expect(lastToast()).toBe(wait);

    toastState.toasts = [];
    transcribeSpeech.mockRejectedValueOnce(limited);
    await wrapper.get('[aria-label="Start recording"]').trigger("click");
    mic.allow();
    await flushPromises();
    await wrapper.get('[aria-label="Stop recording"]').trigger("click");
    await vi.waitFor(() => expect(lastToast()).toBe(wait));
    wrapper.unmount();
  });

  it("adds each transcript to the text, so a long message can be spoken in parts", async () => {
    transcribeSpeech.mockResolvedValue({ transcript: "come stai" });
    const mic = fakeMicrophone();
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    await wrapper.get("textarea").setValue("ciao, ");

    await wrapper.get('[aria-label="Start recording"]').trigger("click");
    mic.allow();
    await flushPromises();
    await wrapper.get('[aria-label="Stop recording"]').trigger("click");

    await vi.waitFor(() =>
      expect(wrapper.findAll("textarea")[0].element.value).toBe("ciao, come stai"),
    );
    wrapper.unmount();
  });

  it("states the recording limit before recording starts", () => {
    fakeMicrophone();
    const wrapper = mount(Translate, {
      global: { stubs: { RequireProfile } },
      attachTo: document.body,
    });
    const micButton = wrapper.get('[aria-label="Start recording"]').element;

    expect(computeAccessibleDescription(micButton)).toBe(
      "Recordings stop after 30 seconds and are added to the text.",
    );
    wrapper.unmount();
  });

  it("lets the translation be focused and selected, but not edited", () => {
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    const output = wrapper.get("#translation");

    expect(output.attributes("readonly")).toBeDefined();
    expect(output.attributes("disabled")).toBeUndefined();
  });

  it("names each text box by its visible label", () => {
    const wrapper = mount(Translate, {
      global: { stubs: { RequireProfile } },
      attachTo: document.body,
    });
    const [input, output] = wrapper.findAll("textarea");

    expect(computeAccessibleName(input.element)).toBe("Text to translate");
    expect(computeAccessibleName(output.element)).toBe("Translation");
    wrapper.unmount();
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

  it("keeps the busy Translate and Listen buttons focusable, ignoring clicks", async () => {
    let finishTranslating;
    translateText.mockReturnValueOnce(new Promise((resolve) => (finishTranslating = resolve)));
    synthesizeSpeech.mockReturnValue(new Promise(() => {}));
    const wrapper = mount(Translate, { global: { stubs: { RequireProfile } } });
    await wrapper.get("textarea").setValue("hello");

    const translate = wrapper.get(".btn-accent");
    await translate.trigger("click");
    await translate.trigger("click");
    expectBusy(translate);
    expect(translateText).toHaveBeenCalledTimes(1);

    finishTranslating({ translated_text: "ciao" });
    await flushPromises();
    const listen = wrapper.get('[aria-label="Listen to translation"]');
    await listen.trigger("click");
    await listen.trigger("click");
    expectBusy(listen);
    expect(synthesizeSpeech).toHaveBeenCalledTimes(1);
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
    expectBusy(button);
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
