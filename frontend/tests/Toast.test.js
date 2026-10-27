// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import Toast from "../src/components/Toast.vue";
import { showToast, toastState } from "../src/stores/toastStore";

let main;

beforeEach(() => {
  toastState.toasts = [];
  main = document.createElement("main");
  main.id = "main";
  main.tabIndex = -1;
  document.body.append(main);
});
afterEach(() => main.remove());

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
});
