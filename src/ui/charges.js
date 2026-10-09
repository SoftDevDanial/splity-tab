// The Charges block (C4, R15): Service charge and SST as percent fields, and the hint under them.
// createCharges({ onInput(kind, text), onLeave(kind, text) }) returns { el, update(bill, errors) };
// `kind` is "service" or "sst".
import { LIMITS } from "../core/bill.js";
import { el, setValue } from "./dom.js";
import { createErrorSlot } from "./field-error.js";
import { onFieldLeave } from "./field-leave.js";

export function createCharges({ onInput, onLeave }) {
  function percentCell(kind, id, label, maxPercent) {
    const input = el("input", { id, type: "text", inputmode: "decimal", autocomplete: "off", "aria-describedby": "charges-hint" });
    input.addEventListener("input", () => onInput(kind, input.value));
    onFieldLeave(input, (text) => onLeave(kind, text));
    const cell = el("div", {},
      el("label", { class: "label", for: id }, label, el("span", { class: "sr-only" }, " in percent")),
      el("span", { class: "field percent" }, input, el("span", { class: "unit", "aria-hidden": "true" }, "%")));
    const error = createErrorSlot(cell, input, {
      id: `${id}-error`, message: `Enter a rate from 0 to ${maxPercent}`, describedBy: ["charges-hint"],
    });
    return { cell, input, error };
  }

  const service = percentCell("service", "rate-service", "Service charge", LIMITS.serviceMaxPercent);
  const sst = percentCell("sst", "rate-sst", "SST", LIMITS.sstMaxPercent);
  const section = el("section", { class: "block", "aria-labelledby": "h-charges" },
    el("h2", { class: "block-title", id: "h-charges" }, "Charges"),
    el("div", { class: "cells" }, service.cell, sst.cell),
    el("p", { class: "hint", id: "charges-hint" }, "Set a charge to 0 if your bill already includes it."));

  function update(bill, errors) {
    setValue(service.input, bill.serviceText);
    setValue(sst.input, bill.sstText);
    service.error.set(errors.service);
    sst.error.set(errors.sst);
  }

  return { el: section, update };
}
