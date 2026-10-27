// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

// The real modules load auth.js, which needs Auth0 settings that CI doesn't
// have.
vi.mock("../src/api/users", () => ({
  getMe: vi.fn(),
  checkUsername: vi.fn(),
  createMe: vi.fn(),
  updateUsername: vi.fn(),
  resetStats: vi.fn(),
  deleteMe: vi.fn(),
}));
vi.mock("../src/auth", () => ({ logout: vi.fn() }));
vi.mock("vue-router", () => ({ useRouter: () => ({ push: vi.fn() }) }));

import { checkUsername, createMe, resetStats, updateUsername } from "../src/api/users";
import AccountActions from "../src/components/username/AccountActions.vue";
import SetUsername from "../src/components/username/SetUsername.vue";

// A busy button stays focusable (aria-disabled, not disabled), and a second
// click does nothing.
async function expectBusyAfterTwoClicks(button, request) {
  await button.trigger("click");
  await button.trigger("click");
  expect(button.attributes("disabled")).toBeUndefined();
  expect(button.attributes("aria-disabled")).toBe("true");
  expect(request).toHaveBeenCalledTimes(1);
}

async function typeAvailableName(wrapper) {
  checkUsername.mockResolvedValue({ available: true });
  await wrapper.get("input").setValue("new_name");
  await vi.advanceTimersByTimeAsync(400);
  await flushPromises();
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.clearAllMocks();
});
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("busy username buttons", () => {
  it("keeps Save username focusable while it saves", async () => {
    createMe.mockReturnValue(new Promise(() => {}));
    const wrapper = mount(SetUsername);
    await typeAvailableName(wrapper);

    await expectBusyAfterTwoClicks(wrapper.get("button"), createMe);
  });

  it("keeps Update username focusable while it saves", async () => {
    updateUsername.mockReturnValue(new Promise(() => {}));
    const wrapper = mount(AccountActions);
    await typeAvailableName(wrapper);

    await expectBusyAfterTwoClicks(wrapper.findAll("button")[0], updateUsername);
  });

  it("moves focus to the box after a rename, since the cleared box disables Update", async () => {
    updateUsername.mockResolvedValue({ username: "new_name" });
    const wrapper = mount(AccountActions, { attachTo: document.body });
    await typeAvailableName(wrapper);

    const update = wrapper.findAll("button")[0];
    update.element.focus();
    await update.trigger("click");
    await flushPromises();

    expect(update.attributes("disabled")).toBeDefined();
    expect(document.activeElement).toBe(wrapper.get("input").element);
    wrapper.unmount();
  });

  it("keeps Reset progress focusable while it resets", async () => {
    vi.stubGlobal("confirm", () => true);
    resetStats.mockReturnValue(new Promise(() => {}));
    const wrapper = mount(AccountActions);

    await expectBusyAfterTwoClicks(wrapper.findAll("button")[1], resetStats);
  });
});
