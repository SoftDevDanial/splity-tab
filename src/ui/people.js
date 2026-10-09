// The People block (C1, R4 to R7): one row per person (name field and remove button), then "Add person".
// createPeople() returns { el, update(bill) }. It writes DOM only; the bill is changed by the caller.
import { LIMITS, personLabel } from "../core/bill.js";
import { el, setAttr, setValue, rowsFor, reconcileChildren } from "./dom.js";
import { icon } from "./icons.js";

function createRow() {
  const input = el("input", { type: "text", maxlength: String(LIMITS.personNameMax), autocomplete: "off" });
  const remove = el("button", { class: "icon-btn", type: "button" }, icon("x"));
  return { el: el("li", { class: "field person" }, input, remove), input, remove };
}

export function createPeople() {
  const rows = new Map();
  const add = el("button", { class: "btn btn-outline", type: "button" }, icon("plus"), "Add person");
  const addCell = el("li", {}, add);
  const list = el("ul", { class: "cells" });
  const section = el("section", { class: "block", "aria-labelledby": "h-people" },
    el("h2", { class: "block-title", id: "h-people" }, "People"), list);

  function update(bill) {
    const people = rowsFor(rows, bill.people.map((person) => person.id), createRow);
    people.forEach((row, index) => {
      const person = bill.people[index];
      setValue(row.input, person.name);
      setAttr(row.input, "aria-label", `Person ${index + 1} name`);
      setAttr(row.input, "placeholder", `Person ${index + 1}`);
      setAttr(row.remove, "aria-label", `Remove ${personLabel(person, index)}`);
      row.remove.disabled = bill.people.length <= LIMITS.minPeople;
    });
    add.disabled = bill.people.length >= LIMITS.maxPeople;
    reconcileChildren(list, [...people.map((row) => row.el), addCell]);
  }

  return { el: section, update };
}
