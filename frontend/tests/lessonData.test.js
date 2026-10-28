import { describe, expect, it } from "vitest";
import { LESSONS } from "../src/data/lessons";
import { parseRichText } from "../src/utils/richText";

// Every string in the lesson data that's shown as rich text.
function richTextStrings(lesson) {
  const strings = [lesson.menuTitle, lesson.title];
  for (const section of lesson.sections) {
    if (section.html) strings.push(section.html);
    if (section.items) strings.push(...section.items);
  }
  if (lesson.practiceInstructions) strings.push(lesson.practiceInstructions);
  strings.push(...lesson.questions.map((q) => q.prompt));
  return strings;
}

const words = (text) => text.toLowerCase().match(/[a-zàèéìòù]+/g) || [];

// Words that are also English, so they can appear unmarked in English text.
const ALSO_ENGLISH = new Set(["a", "i", "in", "are", "me"]);
// Names keep their spelling in the English translations.
const NAMES = new Set(["paolo", "marco", "maria", "federico", "margherita", "valentino"]);

// Italian words the lessons teach: conjugation tables, Italian answers, and
// everything already marked as Italian.
function italianVocabulary() {
  const vocab = new Set();
  for (const lesson of LESSONS) {
    for (const section of lesson.sections) {
      for (const row of section.rows || [])
        words(`${row[0]} ${row[1]}`).forEach((w) => vocab.add(w));
    }
    if (lesson.answerLang === "it") {
      lesson.questions.flatMap((q) => q.correctAnswers).forEach((a) => vocab.add(a.toLowerCase()));
    }
    for (const text of richTextStrings(lesson)) {
      parseRichText(text)
        .filter((s) => s.italian)
        .forEach((s) => words(s.text).forEach((w) => vocab.add(w)));
    }
  }
  return vocab;
}

describe("lesson data", () => {
  it("uses only <i>, <strong>, and <it>, each closed in order", () => {
    for (const lesson of LESSONS) {
      for (const text of richTextStrings(lesson)) {
        const stack = [];
        for (const [, closing, tag] of text.matchAll(/<(\/?)([^>]*)>/g)) {
          expect(["i", "strong", "it"], text).toContain(tag);
          if (closing) expect(stack.pop(), text).toBe(tag);
          else stack.push(tag);
        }
        expect(stack, text).toEqual([]);
      }
    }
  });

  it("never ends a lesson's content with a heading, which would leave it empty", () => {
    for (const lesson of LESSONS) {
      expect(lesson.sections.at(-1).t, lesson.slug).not.toBe("h");
    }
  });

  it("says which language each lesson's answers are typed in", () => {
    for (const lesson of LESSONS.filter((l) => l.questions.length)) {
      expect(["it", "en"], lesson.slug).toContain(lesson.answerLang);
    }
  });

  it("marks every Italian word it teaches wherever it appears", () => {
    const vocab = italianVocabulary();
    const unmarked = [];
    for (const lesson of LESSONS) {
      for (const text of richTextStrings(lesson)) {
        for (const segment of parseRichText(text).filter((s) => !s.italian)) {
          for (const word of words(segment.text)) {
            if (vocab.has(word) && !ALSO_ENGLISH.has(word) && !NAMES.has(word)) {
              unmarked.push(`${word} in "${text}"`);
            }
          }
        }
      }
    }
    expect(unmarked).toEqual([]);
  });
});
