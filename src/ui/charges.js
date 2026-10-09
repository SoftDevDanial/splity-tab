// The Charges block (C4, R15): Service charge and SST as percent fields, and the hint under them.
// createCharges() returns { el, update(bill) }.
import { el, setValue } from "./dom.js";

function percentCell(id, label) {
  const input = el("input", { id, type: "text", inputmode: "decimal", autocomplete: "off", "aria-describedby": "charges-hint" });
  const cell = el("div", {},
    el("label", { class: "label", for: id }, label, el("span", { class: "sr-only" }, " in percent")),
    el("span", { class: "field percent" }, input, el("span", { class: "unit", "aria-hidden": "true" }, "%")));
  return { cell, input };
}

export function createCharges() {
  const service = percentCell("rate-service", "Service charge");
  const sst = percentCell("rate-sst", "SST");
  const section = el("section", { class: "block", "aria-labelledby": "h-charges" },
    el("h2", { class: "block-title", id: "h-charges" }, "Charges"),
    el("div", { class: "cells" }, service.cell, sst.cell),
    el("p", { class: "hint", id: "charges-hint" }, "Set a charge to 0 if your bill already includes it."));

  function update(bill) {
    setValue(service.input, bill.serviceText);
    setValue(sst.input, bill.sstText);
  }

  return { el: section, update };
}
