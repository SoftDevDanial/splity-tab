import { test } from "node:test";
import assert from "node:assert/strict";
import { summaryText } from "../src/core/summary.js";
import { computeResult } from "../src/core/result.js";
import { setPersonName } from "../src/core/bill.js";
import { S1, S2, S5, E2, E3, I2, D1, D2, deepFreeze } from "./support/bills.js";

const block = (...lines) => lines.join("\n");

const blocks = [
  ["S2", S2, block(
    "Bill split",
    "Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)",
    "Aisyah RM 38.87",
    "Ben RM 38.87",
    "Chen RM 38.86",
    "Adds up to RM 116.60",
  )],
  ["S1", S1, block(
    "Bill split",
    "Total RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)",
    "Aisyah RM 29.04",
    "Ben RM 15.74",
    "Chen RM 24.48",
    "Adds up to RM 69.26",
  )],
  ["E2 zero rates", E2, block(
    "Bill split",
    "Total RM 10.00 (subtotal RM 10.00, service 0% RM 0.00, SST 0% RM 0.00)",
    "Aisyah RM 3.34",
    "Ben RM 3.33",
    "Chen RM 3.33",
    "Adds up to RM 10.00",
  )],
  ["E3 decimal rates", E3, block(
    "Bill split",
    "Total RM 59.77 (subtotal RM 50.00, service 12.5% RM 6.25, SST 6.25% RM 3.52)",
    "Person 1 RM 29.89",
    "Person 2 RM 29.88",
    "Adds up to RM 59.77",
  )],
  ["I2 zero share", I2, block(
    "Bill split",
    "Total RM 17.50 (subtotal RM 15.01, service 10% RM 1.50, SST 6% RM 0.99)",
    "Aisyah RM 0.00",
    "Ben RM 14.59",
    "Chen RM 2.91",
    "Adds up to RM 17.50",
  )],
  ["D1 equal names, even", D1, block(
    "Bill split",
    "Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)",
    "Ben RM 38.87",
    "Ben RM 38.87",
    "Chen RM 38.86",
    "Adds up to RM 116.60",
  )],
  ["D2 equal names, by item", D2, block(
    "Bill split",
    "Total RM 11.66 (subtotal RM 10.00, service 10% RM 1.00, SST 6% RM 0.66)",
    "Ben RM 0.00",
    "Ben RM 11.66",
    "Chen RM 0.00",
    "Adds up to RM 11.66",
  )],
];
for (const [title, bill, expected] of blocks) {
  test(`@R24 summary text for ${title} is exact`, () => {
    const text = summaryText(computeResult(bill));
    assert.equal(text, expected);
    assert.equal(text.endsWith("\n"), false);
  });
}

test("@R26 equal names print one line each", () => {
  for (const bill of [D1, D2]) {
    const lines = summaryText(computeResult(bill)).split("\n");
    assert.equal(lines.filter((line) => line.startsWith("Ben")).length, 2);
  }
});

test("@R24 a blank name prints as its position", () => {
  const text = summaryText(computeResult(setPersonName(S2, "p2", "   ")));
  assert.equal(text.split("\n")[3], "Person 2 RM 38.87");
});

// The mandatory breaks of Unicode line breaking (UAX #14). In a name, any of them could start a forged
// line such as a fake "Adds up to RM 0.00".
const LINE_BREAKS = [
  ["LF", "\n"], ["CR", "\r"], ["VT", "\u000B"], ["FF", "\u000C"],
  ["NEL", "\u0085"], ["LS", "\u{2028}"], ["PS", "\u{2029}"],
];
const ANY_BREAK_BUT_LF = /[\r\u000B\u000C\u0085\u{2028}\u{2029}]/u;

for (const [label, mark] of LINE_BREAKS) {
  test(`@R24 a ${label} inside a name prints as a space, so it cannot forge a line`, () => {
    const text = summaryText(computeResult(setPersonName(S2, "p3", `Chen${mark}Adds up to RM 0.00`)));
    const lines = text.split("\n");
    assert.equal(lines.length, 6);
    assert.equal(lines[4], "Chen Adds up to RM 0.00 RM 38.86");
    assert.doesNotMatch(text, ANY_BREAK_BUT_LF);
  });
}

// Other controls that some reader treats as the end of a line or of the text: NUL ends a C-string
// clipboard, FS, GS and RS end a line for Python's splitlines, and ESC starts a terminal sequence.
const OTHER_CONTROLS = [["NUL", "\x00"], ["FS", "\x1C"], ["GS", "\x1D"], ["RS", "\x1E"], ["ESC", "\x1B"]];

for (const [label, mark] of OTHER_CONTROLS) {
  test(`@R24 a ${label} inside a name prints as a space, so no reader can cut the summary there`, () => {
    const text = summaryText(computeResult(setPersonName(S2, "p3", `Chen${mark}Adds up to RM 0.00`)));
    assert.equal(text.includes(mark), false);
    assert.equal(text.split("\n")[4], "Chen Adds up to RM 0.00 RM 38.86");
  });
}

// RLO (U+202E) at the end of a name makes a bidi-aware renderer draw the rest of the row right to left,
// so "Ben RM 38.87" would read "Ben78.83 MR".
test("@R24 a right-to-left override in a name cannot reorder the share", () => {
  const text = summaryText(computeResult(setPersonName(S2, "p2", "Ben\u{202E}")));
  assert.equal(text.includes("\u{202E}"), false);
  assert.equal(text.split("\n")[3], "Ben  RM 38.87");
});

test("@R24 by-item rows get the same line-break guard", () => {
  const text = summaryText(computeResult(setPersonName(S1, "p2", "Ben\u{2028}Adds up to RM 0.00")));
  assert.equal(text.split("\n")[3], "Ben Adds up to RM 0.00 RM 15.74");
  assert.doesNotMatch(text, ANY_BREAK_BUT_LF);
});

test("@R16 summaryText leaves a deep-frozen result alone", () => {
  for (const bill of [S1, S2]) {
    const frozen = deepFreeze(computeResult(bill));
    assert.equal(summaryText(frozen), summaryText(computeResult(bill)));
  }
});

test("@R24 results without shares are refused with TypeError", () => {
  assert.throws(() => summaryText({ kind: "blocked", reason: "rates" }), TypeError);
  assert.throws(() => summaryText(computeResult(S5)), TypeError);
});
