// The People content (C1, R4 to R7, R42): the heading row (h2.blk-h#peopleH and "Add person") and ul.people#peopleList,
// one li.field.person per person (name field and Remove). createPeopleSection (src/ui/sections.js) puts it in its body.
// createPeople({ onName(id, text), onAdd(), onRemove(id) }) returns { content, update(bill), focusName(index) }, where
// content is that list of nodes. It writes DOM and reports gestures; the bill is changed by the caller.
import { LIMITS, personLabel } from "../core/bill.js";
import { el, isRepeatClick, swallowRepeatClicks, setAttr, setValue, rowsFor, reconcileChildren } from "./dom.js";
import { icon } from "./icons.js";

export function createPeople({ onName, onAdd, onRemove }) {
  const rows = new Map();
  let current = [];

  function createRow(id) {
    const input = el("input", { type: "text", maxlength: String(LIMITS.personNameMax), autocomplete: "off" });
    const remove = el("button", { type: "button", class: "icon-btn" }, icon("x"));
    input.addEventListener("input", () => onName(id, input.value));
    // Removing a row moves the rows after it, so the next row's Remove can slide under the pointer and the rest of a
    // double click must not reach it (swallowRepeatClicks). The repeat test is the backstop for a layout move no click
    // armed, the same line as in items.js (RG-CR-08).
    remove.addEventListener("click", (event) => { swallowRepeatClicks(); if (!isRepeatClick(event)) onRemove(id); });
    return { el: el("li", { class: "field person" }, input, remove), input, remove };
  }

  const add = el("button", { type: "button", class: "btn btn-ghost", id: "addPerson" }, icon("plus"), "Add person");
  // Below 1024 px this button sits under the list, so a new person can push it down a row and the rest of a double
  // press would land on that row. It arms the guard like every control that adds or removes a row (R6, RG-CR-01).
  add.addEventListener("click", () => { swallowRepeatClicks(); onAdd(); });
  const head = el("div", { class: "blk-head" }, el("h2", { class: "blk-h", id: "peopleH" }, "People"), add);
  const list = el("ul", { class: "people", id: "peopleList", "aria-labelledby": "peopleH" });

  function update(bill) {
    current = rowsFor(rows, bill.people.map((person) => person.id), createRow);
    const atFewest = bill.people.length <= LIMITS.minPeople;
    current.forEach((row, index) => {
      const person = bill.people[index];
      setValue(row.input, person.name);
      setAttr(row.input, "aria-label", `Person ${index + 1} name`);
      setAttr(row.input, "placeholder", `Person ${index + 1}`);
      setAttr(row.remove, "aria-label", `Remove ${personLabel(person, index)}`);
      row.remove.disabled = atFewest;
    });
    add.disabled = bill.people.length >= LIMITS.maxPeople;
    reconcileChildren(list, current.map((row) => row.el));
  }

  /** Puts the cursor in the name field at `index` (R6, R7, R27 move focus here). */
  function focusName(index) {
    current[index]?.input.focus();
  }

  return { content: [head, list], update, focusName };
}
