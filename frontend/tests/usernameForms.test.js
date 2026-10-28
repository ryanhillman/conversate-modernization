import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { computeAccessibleName } from "dom-accessibility-api";

vi.mock("../src/api/users", () => ({
  getMe: vi.fn(),
  checkUsername: vi.fn(),
  createMe: vi.fn(),
  updateUsername: vi.fn(),
  resetProgress: vi.fn(),
  deleteMe: vi.fn(),
}));
vi.mock("vue-router", () => ({ useRouter: () => ({ push: vi.fn() }) }));

import { checkUsername, createMe, resetProgress, updateUsername } from "../src/api/users";
import AccountActions from "../src/components/account/AccountActions.vue";
import SetUsername from "../src/components/account/SetUsername.vue";
import { toastState } from "../src/stores/toastStore";

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
    resetProgress.mockReturnValue(new Promise(() => {}));
    const wrapper = mount(AccountActions);

    await expectBusyAfterTwoClicks(wrapper.findAll("button")[1], resetProgress);
  });
});

describe("SetUsername", () => {
  it("names the username box by its visible label", () => {
    const wrapper = mount(SetUsername, { attachTo: document.body });

    expect(computeAccessibleName(wrapper.get("input").element)).toBe("Username");
    wrapper.unmount();
  });
});

describe("AccountActions", () => {
  it("names the rename box by its visible label", () => {
    const wrapper = mount(AccountActions, { attachTo: document.body });

    expect(computeAccessibleName(wrapper.get("input").element)).toBe("New username");
    wrapper.unmount();
  });
});

describe.each([
  ["SetUsername", SetUsername],
  ["AccountActions", AccountActions],
])("%s", (_, form) => {
  it("says the name is taken when someone takes it before Save, not a generic error", async () => {
    const taken = new Error("username already exists");
    taken.status = 409;
    createMe.mockRejectedValue(taken);
    updateUsername.mockRejectedValue(taken);
    toastState.toasts = [];
    const wrapper = mount(form);
    await typeAvailableName(wrapper);

    await wrapper.get("button").trigger("click");
    await flushPromises();

    expect(wrapper.get(".form-error").text()).toBe("That username is taken");
    expect(toastState.toasts).toEqual([]);
  });

  it("marks the box invalid and points it at the error only while one shows", async () => {
    const wrapper = mount(form);
    const input = wrapper.get("input");
    expect(input.attributes("aria-describedby")).toBeUndefined();
    expect(input.attributes("aria-invalid")).toBeUndefined();

    checkUsername.mockResolvedValue({ available: false });
    await input.setValue("taken_name");
    await vi.advanceTimersByTimeAsync(400);
    await flushPromises();

    const error = wrapper.get(`#${input.attributes("aria-describedby")}`);
    expect(error.text()).toBe("That username is taken");
    expect(input.attributes("aria-invalid")).toBe("true");
  });
});
