// The Subtotal block (R9, R10), div.blk#evenBlock, in the DOM in even mode only (R8, the caller places it).
// createSubtotal({ onInput(text), onLeave(text) }) returns { el, update(bill, errors) }. The field is named by its
// aria-label "Subtotal in RM" and names its error paragraph at all times, as the golden does (CG-P6).
import { el, setValue } from "./dom.js";
import { AMOUNT_ERROR, createFieldError } from "./field-error.js";
import { onFieldLeave } from "./field-leave.js";

export function createSubtotal({ onInput, onLeave }) {
  const input = el("input", { type: "text", id: "evenSub", inputmode: "decimal", autocomplete: "off", placeholder: "0.00",
    "aria-label": "Subtotal in RM" });
  input.addEventListener("input", () => onInput(input.value));
  onFieldLeave(input, onLeave);
  const field = el("div", { class: "field money sub-field", id: "evenField" },
    el("span", { class: "unit", "aria-hidden": "true" }, "RM"), input);
  const error = createFieldError(field, input, { id: "evenErr", message: AMOUNT_ERROR });
  const block = el("div", { class: "blk", id: "evenBlock" },
    el("label", { class: "blk-h solo", for: "evenSub" }, "Subtotal"), field, error.el);

  function update(bill, errors) {
    setValue(input, bill.subtotalText);
    error.set(errors.subtotal);
  }

  return { el: block, update };
}
