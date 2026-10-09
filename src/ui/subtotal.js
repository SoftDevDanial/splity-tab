// The Subtotal block (C2, R9, R10), shown in even mode only.
// createSubtotal({ onInput(text), onLeave(text) }) returns { el, update(bill, errors) }.
import { block, el, setValue } from "./dom.js";
import { AMOUNT_ERROR, createErrorSlot } from "./field-error.js";
import { onFieldLeave } from "./field-leave.js";

export function createSubtotal({ onInput, onLeave }) {
  const input = el("input", { id: "subtotal", type: "text", inputmode: "decimal", autocomplete: "off" });
  input.addEventListener("input", () => onInput(input.value));
  onFieldLeave(input, onLeave);
  const field = el("span", { class: "field money" }, el("span", { class: "unit", "aria-hidden": "true" }, "RM"), input);
  const section = block("h-subtotal", el("label", { for: "subtotal" }, "Subtotal", el("span", { class: "sr-only" }, " in RM")),
    el("div", { class: "cells" }, field));
  const error = createErrorSlot(section, input, { id: "subtotal-error", message: AMOUNT_ERROR });

  function update(bill, errors) {
    section.hidden = bill.mode !== "even";
    setValue(input, bill.subtotalText);
    error.set(errors.subtotal);
  }

  return { el: section, update };
}
