// FIX CANDIDATE for RG-CR-01 (scratch copy, never in src/): the Add person click arms the guard too, so the repeat
// press of a double click cannot reach the new row's Remove button, which slides under the pointer.
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
    remove.addEventListener("click", () => { swallowRepeatClicks(); onRemove(id); });
    return { el: el("li", { class: "field person" }, input, remove), input, remove };
  }

  const add = el("button", { class: "btn btn-outline", type: "button" }, icon("plus"), "Add person");
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

  function focusName(index) {
    current[index]?.input.focus();
  }

  return { el: section, update, focusName };
}
