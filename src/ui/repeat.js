// The one definition of a repeat press (R57 (b), ruled by the owner 2026-10-14, "Time + place"). Pure, and its import
// touches no DOM, so tests/repeat.test.js checks its edges under node --test. `isRepeatClick` in dom.js builds the two
// records from real events and asks this rule, and the repeat guard and a Remove's own check both go through it.

/** Less than this many ms after the previous pointer click, a tap may be the second half of a double tap. */
const REPEAT_TAP_MS = 500;
/** Each of x and y within this many px of the previous click, a square the size of one 44 px touch target (`--tap`). */
const REPEAT_TAP_PX = 22;

/**
 * Is this press the repeat of a double click, triple click or double tap?
 * press: { detail, tap, timeStamp, x, y }, the event's click count, whether its pointerdown was not a mouse, its
 * timeStamp and clientX, clientY. previous: { timeStamp, x, y } of the previous pointer click, or null.
 * A click count above 1 is a repeat, as both engines count a mouse double click (1.0's rule). A tap with click count 1
 * is a repeat when it comes soon after the previous click and near it, because WebKit gives each tap count 1.
 * A key press (count 0) and a mouse press with count 1 never are. Time is compared, nothing is scheduled.
 */
export function isRepeatPress(press, previous) {
  if (press.detail > 1) return true;
  if (!press.tap || press.detail !== 1 || previous === null) return false;
  return press.timeStamp - previous.timeStamp < REPEAT_TAP_MS
    && Math.abs(press.x - previous.x) <= REPEAT_TAP_PX
    && Math.abs(press.y - previous.y) <= REPEAT_TAP_PX;
}
