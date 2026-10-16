// The Charges content (C4, R15): h2.blk-h.solo#chargesH, then div.charges with one cell per rate (label.lbl, the
// div.field.pct and its p.err) and p.hint#chargeHint. createChargesSection (src/ui/sections.js) puts it in its body.
// createCharges({ onInput(kind, text), onLeave(kind, text) }) returns { content, update(bill, errors) }, where content
// is that list of nodes and `kind` is "service" or "sst". It writes DOM and reports gestures; the bill is changed by
// the caller.
import { LIMITS } from "../core/bill.js";
import { el, setValue } from "./dom.js";
import { createFieldError } from "./field-error.js";
import { onFieldLeave } from "./field-leave.js";

const HINT_ID = "chargeHint";

export function createCharges({ onInput, onLeave }) {
  function rateCell(kind, id, label, maxPercent) {
    const input = el("input", { type: "text", id, inputmode: "decimal", autocomplete: "off" });
    input.addEventListener("input", () => onInput(kind, input.value));
    onFieldLeave(input, (text) => onLeave(kind, text));
    const field = el("div", { class: "field pct" }, input, el("span", { class: "unit", "aria-hidden": "true" }, "%"));
    const error = createFieldError(field, input, { id: `${id}Err`, message: `Enter a rate from 0 to ${maxPercent}`, hint: HINT_ID });
    return { cell: el("div", {}, el("label", { class: "lbl", for: id }, label), field, error.el), input, error };
  }

  const service = rateCell("service", "svc", "Service charge", LIMITS.serviceMaxPercent);
  const sst = rateCell("sst", "sst", "SST", LIMITS.sstMaxPercent);
  const heading = el("h2", { class: "blk-h solo", id: "chargesH" }, "Charges");
  const rates = el("div", { class: "charges" }, service.cell, sst.cell,
    el("p", { class: "hint", id: HINT_ID }, "Set a charge to 0 if your bill already includes it."));

  function update(bill, errors) {
    setValue(service.input, bill.serviceText);
    setValue(sst.input, bill.sstText);
    service.error.set(errors.service);
    sst.error.set(errors.sst);
  }

  return { content: [heading, rates], update };
}
