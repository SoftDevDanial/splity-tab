// Small DOM helpers shared by every block under src/ui/.
// User text reaches the page only through textContent, the value property, or the aria-label and
// placeholder attributes (R37). Nothing here parses markup.
// The setters skip a write when nothing changed. That is what keeps a block from touching the input the
// user is typing in (R33): its value already equals the bill, so it is never written.

/**
 * Creates an element. `attrs` maps names to strings (`true` writes an empty value, `null`/`false` skip).
 * Children are nodes or strings (a string becomes a text node). `null`, `false` and "" are skipped, so a
 * conditional child needs no branch at the call site.
 */
export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attrs)) {
    if (value !== null && value !== false && value !== undefined) node.setAttribute(name, value === true ? "" : value);
  }
  node.append(...children.filter((child) => child !== null && child !== false && child !== undefined && child !== ""));
  return node;
}

/** Sets an attribute, or removes it for `null`/`false`. Writes only when the value differs. */
export function setAttr(node, name, value) {
  if (value === null || value === false) {
    if (node.hasAttribute(name)) node.removeAttribute(name);
    return;
  }
  const text = value === true ? "" : String(value);
  if (node.getAttribute(name) !== text) node.setAttribute(name, text);
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
