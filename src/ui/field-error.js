// The inline error under an amount or rate field (R10, R14, R15), shared by Subtotal, item prices and the two rates so
// their markup cannot drift apart.
import { el, setAttr } from "./dom.js";
import { icon } from "./icons.js";

export const AMOUNT_ERROR = "Enter an amount like 12.50";

/**
 * The error of the goldens (R10, rule 13). `p.err` holds the warning-circle icon and the message, stays in the DOM and
 * carries `hidden` while no error shows. While one shows, the field's wrapper has class `is-bad` and the input
 * `aria-invalid` "true", otherwise "false".
 * @param {HTMLElement} wrapper the field's `div.field`
 * @param {HTMLInputElement} input the field it describes
 * @param {{ id: string, message: string, hint?: string }} options with a `hint` id the input names the error only
 *   while it shows, after the hint (the rates, rule 13). Without one it names the error at all times (CG-P6).
 * @returns {{ el: HTMLParagraphElement, set(shown: boolean): void, rename(id: string): void }} `el` is the paragraph,
 *   for the caller to place. `rename` gives it a new id, which the next `set` names, for a price whose id is its item's
 *   position (`ie{j}`, R14).
 */
export function createFieldError(wrapper, input, { id, message, hint }) {
  const paragraph = el("p", { class: "err", id }, icon("warning-circle"), message);

  function set(shown) {
    setAttr(paragraph, "hidden", shown ? null : "");
    wrapper.classList.toggle("is-bad", shown);
    setAttr(input, "aria-invalid", String(shown));
    setAttr(input, "aria-describedby", hint === undefined ? paragraph.id : [hint, ...(shown ? [paragraph.id] : [])].join(" "));
  }

  function rename(next) {
    setAttr(paragraph, "id", next);
  }

  set(false);
  return { el: paragraph, set, rename };
}
