import { describe, expect, it } from "vitest";
import { parseRichText, plainText } from "../src/utils/richText";

describe("parseRichText", () => {
  it("marks Italian, including inside italics and bold", () => {
    expect(
      parseRichText("Use <i><it>essere</it></i> and <strong><it>avere</it></strong>."),
    ).toEqual([
      { text: "Use ", italic: false, bold: false, italian: false },
      { text: "essere", italic: true, bold: false, italian: true },
      { text: " and ", italic: false, bold: false, italian: false },
      { text: "avere", italic: false, bold: true, italian: true },
      { text: ".", italic: false, bold: false, italian: false },
    ]);
  });

  it("keeps italics that aren't Italian", () => {
    expect(parseRichText("<it>Lo legge.</it> <i>(Reads it.)</i>")).toEqual([
      { text: "Lo legge.", italic: false, bold: false, italian: true },
      { text: " ", italic: false, bold: false, italian: false },
      { text: "(Reads it.)", italic: true, bold: false, italian: false },
    ]);
  });
});

describe("plainText", () => {
  it("drops the markup", () => {
    expect(plainText("<it>Avere</it> and <it>Essere</it>")).toBe("Avere and Essere");
  });
});
