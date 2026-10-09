// The Subtotal block (C2, R9), shown in even mode only. createSubtotal() returns { el, update(bill) }.
import { el, setValue } from "./dom.js";

export function createSubtotal() {
  const input = el("input", { id: "subtotal", type: "text", inputmode: "decimal", autocomplete: "off" });
  const field = el("span", { class: "field money" }, el("span", { class: "unit", "aria-hidden": "true" }, "RM"), input);
  const section = el("section", { class: "block", "aria-labelledby": "h-subtotal" },
    el("h2", { class: "block-title", id: "h-subtotal" },
      el("label", { for: "subtotal" }, "Subtotal", el("span", { class: "sr-only" }, " in RM"))),
    el("div", { class: "cells" }, field));

  function update(bill) {
    section.hidden = bill.mode !== "even";
    setValue(input, bill.subtotalText);
  }

  return { el: section, update };
}
