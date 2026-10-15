// Unit tests for plainNameField in src/ui/dom.js (split-app R62 (1), R33), the one helper both name fields call. In the
// browser a key or insert_text puts the new text before the caret into text that is already plain, so no browser test
// can leave a removed character after the caret. A drop that selects what it dropped can, so this table does (qa.md
// "plainNameField puts the caret where the text went in", code review CR-R6). Importing dom.js touches no DOM, so a
// stand-in input is enough.
import test from "node:test";
import assert from "node:assert/strict";
import { plainNameField } from "../src/ui/dom.js";

const ROWS = [
  // [value, selectionStart, plain, caret, case]
  ["Be\u{202E}n", 2, "Ben", 2, "a removed character after the caret only, none before it"],
  ["Ben\u{202E}", 3, "Ben", 3, "the same at the end of the text"],
  ["\u{202E}Be\u{202E}n", 3, "Ben", 2, "one removed character before the caret and one after it"],
  ["\u{2028}\u{2029}Be\u{0000}n\u{200E}", 4, "Ben", 2, "two removed characters before the caret and two after it"],
  ["Be\u{202E}x\u{2067}n", 5, "Bexn", 3, "what an insert at the caret leaves, the caret after the x"],
  ["\u{202E}\u{2067}", 1, "", 0, "a name made only of removed characters, the plain text is empty"],
];

/** `text` with every code point outside printable ASCII written U+XXXX, for the test names. */
const spelled = (text) => [...text]
  .map((char) => (char >= " " && char <= "~" ? char : `U+${char.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`))
  .join("");

/** The field as an input event left it. Its setSelectionRange records each call. */
function standIn(value, selectionStart) {
  const calls = [];
  return { value, selectionStart, calls, setSelectionRange(start, end) { calls.push([start, end]); } };
}

for (const [value, selectionStart, plain, caret, why] of ROWS) {
  test(`@R62 @R33 plainNameField of "${spelled(value)}" with the caret at ${selectionStart}, ${why}`, () => {
    const input = standIn(value, selectionStart);
    const returned = plainNameField(input);
    assert.deepEqual({ returned, value: input.value, calls: input.calls },
      { returned: plain, value: plain, calls: [[caret, caret]] });
  });
}
