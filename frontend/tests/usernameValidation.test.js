import { describe, expect, it } from "vitest";
import { usernameError } from "../src/utils/usernameValidation";

describe("usernameError", () => {
  it("accepts letters, numbers, and _ . -", () => {
    expect(usernameError("ryan_h")).toBeNull();
    expect(usernameError("a.b-c_1")).toBeNull();
  });

  it("trims before checking length", () => {
    expect(usernameError("  ab  ")).toMatch(/at least 3/);
    expect(usernameError("  abc  ")).toBeNull();
  });

  it("rejects names that are too short or too long", () => {
    expect(usernameError("")).toMatch(/at least 3/);
    expect(usernameError(null)).toMatch(/at least 3/);
    expect(usernameError("a".repeat(101))).toMatch(/at most 100/);
  });

  it("rejects other characters", () => {
    expect(usernameError("ryan h")).toMatch(/may only contain/);
    expect(usernameError("ryan!")).toMatch(/may only contain/);
  });
});
