// The inline error under an amount or rate field (R10, R14, R15), shared by Subtotal, item prices and
// the two rates so their markup cannot drift apart.
import { el, setAttr } from "./dom.js";

export const AMOUNT_ERROR = "Enter an amount like 12.50";

/**
 * @param {HTMLElement} host the element the paragraph is the last child of
 * @param {HTMLInputElement} input the field it describes
 * @param {{ id: string, message: string, describedBy?: string[] }} options `describedBy` ids stay on the
 *   input after the error id, and alone when no error shows (the rates keep pointing at the hint)
 * @returns {{ set(shown: boolean): void }} shows or removes `p.error` and sets `aria-invalid` and
 *   `aria-describedby`. With no error the paragraph is not in the DOM.
 */
export function createErrorSlot(host, input, { id, message, describedBy = [] }) {
  const paragraph = el("p", { class: "error", id }, message);

  function set(shown) {
    if (shown) {
      if (host.lastElementChild !== paragraph) host.append(paragraph);
      setAttr(input, "aria-invalid", "true");
      setAttr(input, "aria-describedby", [id, ...describedBy].join(" "));
    } else {
      paragraph.remove();
      setAttr(input, "aria-invalid", null);
      setAttr(input, "aria-describedby", describedBy.length > 0 ? describedBy.join(" ") : null);
    }
  }

  return { set };
}
