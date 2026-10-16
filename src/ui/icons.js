// Run-time icons (R37, R44). Each is an svg.ic (or the proof row's svg.seal) holding one <use> of a symbol in the sprite that index.html carries,
// so the drawing lives once, in the golden's sprite. Built with createElementNS, never from markup, and the href is
// "#i-" plus a fixed name from the call site, so no user text reaches an icon. Every icon is decoration
// (aria-hidden), the control around it carries the accessible name.

// The one call site of createElementNS. The namespace is a name that is never requested (R39).
function svgNode(tag, attrs) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  return node;
}

function spriteUse(className, name) {
  const svg = svgNode("svg", { class: className, "aria-hidden": "true", focusable: "false" });
  svg.append(svgNode("use", { href: `#i-${name}` }));
  return svg;
}

/**
 * @param {"x" | "plus" | "copy" | "check" | "caret" | "shuffle" | "warning" | "warning-circle" | "mark"} name a symbol of the sprite
 * @param {string} [modifier] a second class the design gives some icons ("caret-up" on Splits)
 * @returns {SVGElement} a new `svg.ic`
 */
export function icon(name, modifier) {
  return spriteUse(modifier ? `ic ${modifier}` : "ic", name);
}

/** The proof row's seal (R20), `svg.seal` of `#i-seal-check`, the one run-time icon the goldens draw without `ic`. */
export function seal() {
  return spriteUse("seal", "seal-check");
}
