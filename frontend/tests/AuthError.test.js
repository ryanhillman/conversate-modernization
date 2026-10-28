import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { ref } from "vue";

vi.mock("@auth0/auth0-vue", () => ({
  useAuth0: () => ({ error: ref(new Error("Login failed")) }),
}));

import AuthError from "../src/components/AuthError.vue";

describe("AuthError", () => {
  it("moves focus to the page content when closed", async () => {
    const main = document.createElement("main");
    main.id = "main";
    main.tabIndex = -1;
    document.body.append(main);
    const wrapper = mount(AuthError, { attachTo: main });

    const close = wrapper.get('button[aria-label="Close"]');
    close.element.focus();
    await close.trigger("click");

    expect(wrapper.find(".alert").exists()).toBe(false);
    expect(document.activeElement).toBe(main);
    wrapper.unmount();
    main.remove();
  });
});
