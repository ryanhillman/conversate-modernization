// Lesson text marks italics, bold, and Italian with <i>, <strong>, and <it>.
// Tags can nest, e.g. <i><it>essere</it></i>.
const TAG = /(<\/?(?:i|strong|it)>)/g;

// Splits marked-up text into runs of plain text, each with the tags around it.
export function parseRichText(text) {
  const open = { i: 0, strong: 0, it: 0 };
  const segments = [];
  for (const part of (text || "").split(TAG)) {
    if (part === "") continue;
    const tag = part.match(/^<(\/?)(i|strong|it)>$/);
    if (tag) {
      open[tag[2]] = Math.max(0, open[tag[2]] + (tag[1] ? -1 : 1));
    } else {
      segments.push({
        text: part,
        italic: open.i > 0,
        bold: open.strong > 0,
        italian: open.it > 0,
      });
    }
  }
  return segments;
}
