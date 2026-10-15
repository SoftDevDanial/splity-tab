// The copy status line (C6, R22 to R24). The status is one value in src/main.js, null, "ok" or "fail", and every status
// paragraph present shows it the same way: the card's #cardStatus, the sheet's p.status (task A12) and the strip's
// #stripStatus. This module is that one way, so the three lines cannot drift apart.
import { setAttr } from "./dom.js";
import { icon } from "./icons.js";

const COPY_STATUS = {
  ok: { icon: "check", text: "Summary copied", className: "status" },
  fail: { icon: "warning-circle", text: "Could not copy. Your browser blocked the clipboard.", className: "status is-fail" },
};
const NO_STATUS = { icon: null, text: "", className: "status" };

/**
 * Makes the p.status `paragraph` show `status` (null, "ok" or "fail"), the check or the warning circle and then the
 * text, or no child at all for null, which `.status:empty` hides. A paragraph that already shows it is left alone, so a
 * render that is not a copy attempt does not make the live line speak again.
 */
export function showCopyStatus(paragraph, status) {
  const shown = COPY_STATUS[status] ?? NO_STATUS;
  setAttr(paragraph, "class", shown.className);
  if (paragraph.textContent !== shown.text) paragraph.replaceChildren(...(shown.icon ? [icon(shown.icon), shown.text] : []));
}
