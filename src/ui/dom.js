// Small DOM helpers shared by every block under src/ui/.
// User text reaches the page only through textContent, the value property, or the aria-label and
// placeholder attributes (R37). Nothing here parses markup.
// R33 (typing never loses its place) rests on reconcileChildren: it never re-inserts a node that is already
// in place, and re-inserting a focused input drops its focus and its IME state. The setters also skip a write
// of an equal value, which is belt and braces (measured in Chromium: writing an equal value moves nothing).
import { isRepeatPress } from "./repeat.js";

/**
 * Creates an element. `attrs` maps names to strings.
 * Children are nodes or strings (a string becomes a text node). `null`, `false`, `undefined` and "" are
 * skipped, so a conditional child needs no branch at the call site.
 */
export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  node.append(...children.filter((child) => child !== null && child !== false && child !== undefined && child !== ""));
  return node;
}

/** Sets an attribute to a string, or removes it for `null`. Writes only when the value differs. */
export function setAttr(node, name, value) {
  if (value === null) {
    if (node.hasAttribute(name)) node.removeAttribute(name);
  } else if (node.getAttribute(name) !== value) {
    node.setAttribute(name, value);
  }
}

// What the window saw of the pointer (R57 (b)), written by watchPointerClicks and read by isRepeatClick.
let lastPressWasTap = false;
let lastClick = null; // { event, place: { timeStamp, x, y } }
let clickBeforeLast = null;

/**
 * Called once at boot (src/main.js). Records the pointer type of the last pointerdown and the last two clicks with a
 * click count above 0, for isRepeatClick. On window in the capture phase, so both run before the guard below can cancel
 * an event: a click the guard cancels still counts as the previous pointer click.
 */
export function watchPointerClicks() {
  // Read from pointerdown, not from the click, because WebKit gives a tap's click the pointerType "mouse" (spec R57 (b)).
  window.addEventListener("pointerdown", (event) => { lastPressWasTap = event.pointerType !== "mouse"; }, true);
  window.addEventListener("click", (event) => {
    if (event.detail < 1) return;
    clickBeforeLast = lastClick;
    lastClick = { event, place: { timeStamp: event.timeStamp, x: event.clientX, y: event.clientY } };
  }, true);
}

/**
 * True for the second and later press of a double click, triple click or double tap: the mousedown or click `event`
 * by the one rule `isRepeatPress` (R57 (b)). A key press (count 0) and a mouse click of its own (count 1) never are.
 * A Remove button tests it itself, whether or not a guard is armed (R7, RG-CR-08), for a layout move that no click armed.
 * In 1.0 the error line a price field shows when it is left put a chip's repeat press on its item's Remove. Since v1.1.0
 * the error sits under the item's row and moves the toggles down, and the test stays as the backstop (task A8).
 */
export function isRepeatClick(event) {
  // The window listener records a click before anyone judges it, so a click must not be compared with itself.
  const previous = lastClick?.event === event ? clickBeforeLast : lastClick;
  const press = { detail: event.detail, tap: lastPressWasTap, timeStamp: event.timeStamp, x: event.clientX, y: event.clientY };
  return isRepeatPress(press, previous && previous.place);
}

const GUARDED = ["mousedown", "click", "keydown"];
const isRepeat = (event) => (event.type === "keydown" ? event.repeat : isRepeatClick(event));

/**
 * A click that moves the layout under the pointer arms this guard, because the rest of its double click, triple
 * click or double tap would land on whatever is drawn there next: the row or control that took a removed row's place,
 * the person row that pushed "Add person" down (below 1024 px it sits under the list), the backdrop of the dialog that
 * had just opened (it shut again), or whatever was under a dialog that has closed.
 * The armers are the click on every Remove, on Add person and on Add item (nothing slides under that one, it arms so
 * the rule stays one rule), and the clicks that open and close the New bill dialog and the Splits sheet. The guard
 * protects only what arms it, and no click can arm it for a layout move that is not a click (the error line of a price
 * field, RG-CR-08). So a Remove also
 * ignores a repeat press itself (`isRepeatClick`), and the guard covers everything else, Add person included, which has no
 * count test. "Dismiss note" moves the rows and arms nothing, its repeat press lands on a heading or a div (BUILD.md, call 18).
 * The guard cancels the repeat presses and clicks at the document, in the capture phase, before any control sees
 * them. A cancelled press also keeps focus where the app put it. It also cancels a held key's repeats (a keydown with
 * `repeat` true, R57 (a)), so a held Enter cannot press the control that the click moved focus to. It is gone at the
 * first press that is not a repeat, so a press of its own is never held back. Nothing is scheduled.
 */
export function swallowRepeatClicks() {
  const guard = (event) => {
    if (!isRepeat(event)) {
      for (const type of GUARDED) document.removeEventListener(type, guard, true);
      return;
    }
    event.stopPropagation();
    event.preventDefault();
  };
  for (const type of GUARDED) document.addEventListener(type, guard, true);
}

/**
 * Calls `close` for a click on the backdrop of the modal `dialog`, which native showModal() ignores (R30, R50, R52).
 * The backdrop belongs to the dialog element, so a press on the dialog element at a point outside its box is a press on
 * the backdrop. A click goes to the common ancestor of where the press began and ended, so selecting the dialog's text
 * and letting go over the backdrop also targets the dialog. Only a press that began on the backdrop counts.
 */
export function closeOnBackdropClick(dialog, close) {
  const onBackdrop = (event) => {
    const box = dialog.getBoundingClientRect();
    return event.target === dialog
      && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom);
  };
  let pressBeganOnBackdrop = false;
  dialog.addEventListener("mousedown", (event) => { pressBeganOnBackdrop = onBackdrop(event); });
  dialog.addEventListener("click", (event) => {
    const began = pressBeganOnBackdrop;
    pressBeganOnBackdrop = false;
    if (began && onBackdrop(event)) close();
  });
}

export function setText(node, text) {
  if (node.textContent !== text) node.textContent = text;
}

export function setValue(input, text) {
  if (input.value !== text) input.value = text;
}

export function setChecked(input, checked) {
  if (input.checked !== checked) input.checked = checked;
}

/**
 * Returns one row per key, in key order. Rows for keys that are gone are dropped from `rows`, and a new
 * row is made by `create(key)` for a key not seen before, so a row (and the input in it) lives as long as
 * its key does.
 */
export function rowsFor(rows, keys, create) {
  for (const key of [...rows.keys()]) if (!keys.includes(key)) rows.delete(key);
  return keys.map((key) => {
    if (!rows.has(key)) rows.set(key, create(key));
    return rows.get(key);
  });
}

/**
 * Makes `parent`'s children exactly `desired`, in order. Children that are not wanted are removed, a child
 * that is already in place is not touched, and only a missing one is inserted. Moving or re-inserting a
 * node drops its focus, so a focused control must never be re-inserted (R33).
 */
export function reconcileChildren(parent, desired) {
  const wanted = new Set(desired);
  for (const child of [...parent.children]) if (!wanted.has(child)) child.remove();
  desired.forEach((node, index) => {
    if (parent.children[index] !== node) parent.insertBefore(node, parent.children[index] ?? null);
  });
}
