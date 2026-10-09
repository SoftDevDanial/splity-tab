// MUTANT M2 of src/ui/dom.js (scratch copy, never in src/): the guard removes its mousedown listener twice and never
// its click listener. The click guard then stays armed for good.
export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  node.append(...children.filter((child) => child !== null && child !== false && child !== undefined && child !== ""));
  return node;
}

export function block(id, title, ...children) {
  return el("section", { class: "block", "aria-labelledby": id }, el("h2", { class: "block-title", id }, title), ...children);
}

export function setAttr(node, name, value) {
  if (value === null) {
    if (node.hasAttribute(name)) node.removeAttribute(name);
  } else if (node.getAttribute(name) !== value) {
    node.setAttribute(name, value);
  }
}

const isRepeatClick = (event) => event.detail > 1;

export function swallowRepeatClicks() {
  const guard = (event) => {
    if (!isRepeatClick(event)) {
      document.removeEventListener("mousedown", guard, true);
      document.removeEventListener("mousedown", guard, true);
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

export function rowsFor(rows, keys, create) {
  for (const key of [...rows.keys()]) if (!keys.includes(key)) rows.delete(key);
  return keys.map((key) => {
    if (!rows.has(key)) rows.set(key, create(key));
    return rows.get(key);
  });
}

export function reconcileChildren(parent, desired) {
  const wanted = new Set(desired);
  for (const child of [...parent.children]) if (!wanted.has(child)) child.remove();
  desired.forEach((node, index) => {
    if (parent.children[index] !== node) parent.insertBefore(node, parent.children[index] ?? null);
  });
}
