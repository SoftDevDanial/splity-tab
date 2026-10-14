// Unit tests for src/ui/repeat.js (split-app R57 (b)): the one rule that says whether a press is the repeat of a
// double click, triple click or double tap. A browser gesture cannot hit the 500 ms and 22 px edges to the
// millisecond or the pixel, so this table (qa.md "@R57 @node") pins them. One test per row, so each is seen failing.
import test from "node:test";
import assert from "node:assert/strict";
import { isRepeatPress } from "../src/ui/repeat.js";

const CLICK_TIME = 1000; // the previous pointer click's timeStamp, the rows give the press's time after it
const AT_100 = { timeStamp: CLICK_TIME, x: 100, y: 100 };

const ROWS = [
  // [previous, detail, tap, after (ms), x, y, repeat, why]
  [AT_100, 2, false, 5000, 300, 300, true, "repeat (point 1)"],
  [AT_100, 3, true, 0, 100, 100, true, "repeat (point 1)"],
  [AT_100, 1, false, 10, 100, 100, false, "not a repeat (a mouse goes by its count only)"],
  [AT_100, 0, true, 10, 100, 100, false, "not a repeat (a key press)"],
  [AT_100, 1, true, 0, 100, 100, true, "repeat (point 2)"],
  [AT_100, 1, true, 499.9, 122, 78, true, "repeat (point 2, every edge inside)"],
  [AT_100, 1, true, 500, 100, 100, false, "not a repeat (500 ms is not less than 500)"],
  [AT_100, 1, true, 10, 122.5, 100, false, "not a repeat (more than 22 px across)"],
  [AT_100, 1, true, 10, 100, 123, false, "not a repeat (more than 22 px down)"],
  [null, 1, true, 10, 100, 100, false, "not a repeat (no previous pointer click)"],
];

for (const [previous, detail, tap, after, x, y, repeat, why] of ROWS) {
  const pointer = tap ? "a tap" : "a mouse";
  const where = previous === null ? "no previous click" : `${after} ms after a click at (100, 100)`;
  test(`@R57 b count ${detail}, ${pointer}, ${where}, at (${x}, ${y}): ${why}`, () => {
    const press = { detail, tap, timeStamp: CLICK_TIME + after, x, y };
    assert.equal(isRepeatPress(press, previous), repeat, why);
  });
}
