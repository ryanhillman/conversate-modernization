// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import Toast from "../src/components/Toast.vue";
import { showToast, toastState } from "../src/stores/toastStore";

beforeEach(() => {
  toastState.toasts = [];
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
});
