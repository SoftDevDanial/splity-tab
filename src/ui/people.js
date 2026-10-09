// The People block (C1, R4 to R7): one row per person (name field and remove button), then "Add person".
// createPeople({ onName(id, text), onAdd(), onRemove(id) }) returns { el, update(bill), focusName(index) }.
// It writes DOM and reports gestures; the bill is changed by the caller.
import { LIMITS, personLabel } from "../core/bill.js";
import { block, el, swallowRepeatClicks, setAttr, setValue, rowsFor, reconcileChildren } from "./dom.js";
import { icon } from "./icons.js";

export function createPeople({ onName, onAdd, onRemove }) {
  const rows = new Map();
  let current = [];

  function createRow(id) {
    const input = el("input", { type: "text", maxlength: String(LIMITS.personNameMax), autocomplete: "off" });
    const remove = el("button", { class: "icon-btn", type: "button" }, icon("x"));
    input.addEventListener("input", () => onName(id, input.value));
    // Removing a row slides the next control under the pointer (the next row's Remove, or Add person for the last
    // row), so the rest of a double click must not reach it (swallowRepeatClicks).
    remove.addEventListener("click", () => { swallowRepeatClicks(); onRemove(id); });
    return { el: el("li", { class: "field person" }, input, remove), input, remove };
  }

  const add = el("button", { class: "btn btn-outline", type: "button" }, icon("plus"), "Add person");
  // The new row's Remove button slides under the right end of this button, so the rest of a double click must not
  // reach it and take the blank row away again (swallowRepeatClicks, RG-CR-01).
  add.addEventListener("click", () => { swallowRepeatClicks(); onAdd(); });
  const addCell = el("li", {}, add);
  const list = el("ul", { class: "cells" });
  const section = block("h-people", "People", list);

  function update(bill) {
    current = rowsFor(rows, bill.people.map((person) => person.id), createRow);
    current.forEach((row, index) => {
      const person = bill.people[index];
      setValue(row.input, person.name);
      setAttr(row.input, "aria-label", `Person ${index + 1} name`);
      setAttr(row.input, "placeholder", `Person ${index + 1}`);
      setAttr(row.remove, "aria-label", `Remove ${personLabel(person, index)}`);
      row.remove.disabled = bill.people.length <= LIMITS.minPeople;
    });
    add.disabled = bill.people.length >= LIMITS.maxPeople;
    reconcileChildren(list, [...current.map((row) => row.el), addCell]);
  }

  /** Puts the cursor in the name field at `index` (R6, R7, R27 move focus here). */
  function focusName(index) {
    current[index]?.input.focus();
  }

  return { el: section, update, focusName };
}
