import { describe, expect, it } from "vitest";
import { formatTime } from "../src/utils/formatTime";

describe("formatTime", () => {
  it("formats seconds as m:ss", () => {
    expect(formatTime(0)).toBe("0:00");
    expect(formatTime(65)).toBe("1:05");
    expect(formatTime(600)).toBe("10:00");
  });

  it("rounds fractional seconds and clamps negatives to zero", () => {
    expect(formatTime(59.6)).toBe("1:00");
    expect(formatTime(-5)).toBe("0:00");
  });
});
