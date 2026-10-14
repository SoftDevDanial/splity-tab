// The inline error under an amount or rate field (R10, R14, R15), shared by Subtotal, item prices and
// the two rates so their markup cannot drift apart. createFieldError is the v1.1.0 form of the goldens, which the
// rates use since task A6 and the Subtotal since task A7. createErrorSlot is the 1.0 form that the prices keep until
// task A8 moves them to createFieldError, and it goes with them.
import { el, setAttr } from "./dom.js";
import { icon } from "./icons.js";

export const AMOUNT_ERROR = "Enter an amount like 12.50";

/**
 * The v1.1.0 error (R10, rule 13). `p.err` holds the warning-circle icon and the message, stays in the DOM and carries
 * `hidden` while no error shows. While one shows, the field's wrapper has class `is-bad` and the input `aria-invalid`
 * "true", otherwise "false".
 * @param {HTMLElement} wrapper the field's `div.field`
 * @param {HTMLInputElement} input the field it describes
 * @param {{ id: string, message: string, hint?: string }} options with a `hint` id the input names the error only
 *   while it shows, after the hint (the rates, rule 13). Without one it names the error at all times (CG-P6).
 * @returns {{ el: HTMLParagraphElement, set(shown: boolean): void }} `el` is the paragraph, for the caller to place
 */
export function createFieldError(wrapper, input, { id, message, hint }) {
  const paragraph = el("p", { class: "err", id }, icon("warning-circle"), message);

  function set(shown) {
    setAttr(paragraph, "hidden", shown ? null : "");
    wrapper.classList.toggle("is-bad", shown);
    setAttr(input, "aria-invalid", String(shown));
    setAttr(input, "aria-describedby", hint === undefined ? id : [hint, ...(shown ? [id] : [])].join(" "));
  }

  set(false);
  return { el: paragraph, set };
}

/**
 * The 1.0 error (the prices until task A8).
 * @param {HTMLElement} host the element the paragraph is the last child of
 * @param {HTMLInputElement} input the field it describes
 * @param {{ id: string, message: string }} options
 * @returns {{ set(shown: boolean): void }} shows or removes `p.error` and sets `aria-invalid` and
 *   `aria-describedby` to its id. With no error the paragraph is not in the DOM and neither attribute is set.
 */
export function createErrorSlot(host, input, { id, message }) {
  const paragraph = el("p", { class: "error", id }, message);

  function set(shown) {
    if (shown) {
      if (host.lastElementChild !== paragraph) host.append(paragraph);
    } else {
      paragraph.remove();
    }
    setAttr(input, "aria-invalid", shown ? "true" : null);
    setAttr(input, "aria-describedby", shown ? id : null);
  }

  return { set };
}
