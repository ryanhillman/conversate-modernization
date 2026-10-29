import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import Toast from "../src/components/Toast.vue";
import { showToast, toastState } from "../src/stores/toastStore";

let main;
// jsdom has no ResizeObserver; this one lets a test report a resize.
let resized;

beforeEach(() => {
  toastState.toasts = [];
  main = document.createElement("main");
  main.id = "main";
  main.tabIndex = -1;
  document.body.append(main);
  vi.stubGlobal(
    "ResizeObserver",
    class {
      constructor(callback) {
        resized = callback;
      }
      observe() {}
      disconnect() {}
    },
  );
});
afterEach(() => {
  main.remove();
  vi.unstubAllGlobals();
  document.documentElement.style.removeProperty("--toast-space");
});

describe("Toast", () => {
  it("lets an error be dismissed", async () => {
    showToast("Could not save.", "error");
    const wrapper = mount(Toast);

    await wrapper.get('button[aria-label="Dismiss"]').trigger("click");

    expect(toastState.toasts).toEqual([]);
  });

  it("gives a success message no Dismiss button", () => {
    showToast("Saved", "success");
    const wrapper = mount(Toast);
    expect(wrapper.find("button").exists()).toBe(false);
  });

  it("moves focus to the next Dismiss button, then to the page, as toasts close", async () => {
    showToast("First error.", "error");
    showToast("Second error.", "error");
    const wrapper = mount(Toast, { attachTo: document.body });

    const first = wrapper.findAll("button")[0];
    first.element.focus();
    await first.trigger("click");
    await flushPromises();
    expect(document.activeElement.closest(".toast-item").textContent).toContain("Second error.");

    await wrapper.get("button").trigger("click");
    await flushPromises();
    expect(document.activeElement).toBe(main);
    wrapper.unmount();
  });

  it("keeps room above the toasts, so focus doesn't land behind them", async () => {
    showToast("Could not save.", "error");
    const wrapper = mount(Toast);
    const container = wrapper.get(".toast-stack").element;
    container.getBoundingClientRect = () => ({ top: window.innerHeight - 100 });

    const space = () => document.documentElement.style.getPropertyValue("--toast-space");

    resized();
    expect(space()).toBe("100px");

    toastState.toasts = [];
    resized();
    expect(space()).toBe("");
  });

  it("scrolls a focused control out from under a new toast", () => {
    const button = document.createElement("button");
    main.append(button);
    button.focus();
    button.getBoundingClientRect = () => ({ top: window.innerHeight - 50 });
    button.scrollIntoView = vi.fn();
    showToast("Could not save.", "error");
    const wrapper = mount(Toast);
    wrapper.get(".toast-stack").element.getBoundingClientRect = () => ({
      top: window.innerHeight - 100,
    });

    resized();
    expect(button.scrollIntoView).toHaveBeenCalledWith({ block: "nearest" });
  });
});
