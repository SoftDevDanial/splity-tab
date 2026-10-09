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
 * True for the second and later click of a double click or double tap. `detail` is the click count (0 for a
 * key press). The first click can close the dialog or remove a row, so the next one lands on whatever slid
 * under the pointer: the handlers that do either ignore it. No timer, so a slow second click is an ordinary one.
 */
export const isRepeatClick = (event) => event.detail > 1;

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
