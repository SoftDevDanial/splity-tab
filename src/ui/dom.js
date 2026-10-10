// Small DOM helpers shared by every block under src/ui/.
// User text reaches the page only through textContent, the value property, or the aria-label and
// placeholder attributes (R37). Nothing here parses markup.
// R33 (typing never loses its place) rests on reconcileChildren: it never re-inserts a node that is already
// in place, and re-inserting a focused input drops its focus and its IME state. The setters also skip a write
// of an equal value, which is belt and braces (measured in Chromium: writing an equal value moves nothing).

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

/** A `section.block` named by its heading `h2.block-title#id`. `title` is text or a node (the Subtotal label). */
export function block(id, title, ...children) {
  return el("section", { class: "block", "aria-labelledby": id }, el("h2", { class: "block-title", id }, title), ...children);
}

/** Sets an attribute to a string, or removes it for `null`. Writes only when the value differs. */
export function setAttr(node, name, value) {
  if (value === null) {
    if (node.hasAttribute(name)) node.removeAttribute(name);
  } else if (node.getAttribute(name) !== value) {
    node.setAttribute(name, value);
  }
}

/**
 * True for the second and later press of a double click, triple click or double tap. `detail` is the click
 * count (0 for a key press), so a slow second click is an ordinary one: there is no timer.
 * A Remove button tests it itself, whether or not a guard is armed (RG-CR-08): the error line a price field shows when
 * it is left pushes the chips down, and the repeat press of a double click on a chip then lands on that item's Remove.
 */
export const isRepeatClick = (event) => event.detail > 1;

/**
 * A click that moves the layout under the pointer arms this guard, because the rest of its double click, triple
 * click or double tap would land on whatever is drawn there next: the control that took a removed row's place (for
 * the last person that is "Add person", and a blank person was saved), the Remove button of the row that "Add
 * person" has just added (it slides under the right end of that button, and the blank row went again), the backdrop
 * of the dialog that had just opened (it shut again), or whatever was under a dialog that has closed.
 * The armers are the click on every Remove, on Add person and on Add item (nothing slides under that one, it arms so
 * the rule stays one rule), and the clicks that open and close the dialog. The guard protects only what arms it, and a
 * layout move that is not a click cannot arm anything (the price error line, RG-CR-08). So a Remove also ignores a
 * repeat press itself (`isRepeatClick`), and the guard covers everything else, Add person included, which has no
 * count test. "Dismiss note" moves the rows and arms nothing, its repeat press lands on a heading or a div (BUILD.md, call 18).
 * The guard cancels the repeat presses and clicks at the document, in the capture phase, before any control sees
 * them. A cancelled press also keeps focus where the app put it. It is gone at the first press that is not a
 * repeat, so a click or key press of its own (count 1 or 0) is never held back. No timer.
 */
export function swallowRepeatClicks() {
  const guard = (event) => {
    if (!isRepeatClick(event)) {
      document.removeEventListener("mousedown", guard, true);
      document.removeEventListener("click", guard, true);
      return;
    }
    event.stopPropagation();
    event.preventDefault();
  };
  document.addEventListener("mousedown", guard, true);
  document.addEventListener("click", guard, true);
}

export function setText(node, text) {
  if (node.textContent !== text) node.textContent = text;
}

export function setValue(input, text) {
  if (input.value !== text) input.value = text;
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
