// Run-time icons (R37, R44). Each is an svg.ic holding one <use> of a symbol in the sprite that index.html carries,
// so the drawing lives once, in the golden's sprite. Built with createElementNS, never from markup, and the href is
// "#i-" plus a fixed name from the call site, so no user text reaches an icon. Every icon is decoration
// (aria-hidden), the control around it carries the accessible name.

// The one call site of createElementNS. The namespace is a name that is never requested (R39).
function svgNode(tag, attrs) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  return node;
}

/**
 * @param {"x" | "plus" | "copy" | "check" | "caret" | "shuffle" | "warning" | "warning-circle" | "mark"} name a symbol of the sprite
 * @param {string} [modifier] a second class the design gives some icons ("caret-up" on Splits)
 * @returns {SVGElement} a new `svg.ic`
 */
export function icon(name, modifier) {
  const svg = svgNode("svg", { class: modifier ? `ic ${modifier}` : "ic", "aria-hidden": "true", focusable: "false" });
  svg.append(svgNode("use", { href: `#i-${name}` }));
  return svg;
}
