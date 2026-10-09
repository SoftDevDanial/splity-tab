// Boot and wiring for the page. Holds the one `bill` value, calls split-core for every change, and asks
// each block under src/ui/ to show it. No money is computed here (split-core owns that).
import { newBill, addPerson, removePerson, setPersonName } from "./core/bill.js";
import { computeResult } from "./core/result.js";
import { createPeople } from "./ui/people.js";
import { createMode } from "./ui/mode.js";
import { createSubtotal } from "./ui/subtotal.js";
import { createCharges } from "./ui/charges.js";
import { createPanel } from "./ui/panel.js";

let bill = newBill();

function commit(next) {
  if (next === bill) return;
  bill = next;
  render();
}

const people = createPeople({
  onName: (id, text) => commit(setPersonName(bill, id, text)),
  onAdd() {
    commit(addPerson(bill));
    people.focusName(bill.people.length - 1);
  },
  onRemove(id) {
    const position = bill.people.findIndex((person) => person.id === id);
    commit(removePerson(bill, id));
    // The row now at the same position, or the one above when the last row went (R34).
    people.focusName(Math.min(position, bill.people.length - 1));
  },
});
const mode = createMode();
const subtotal = createSubtotal();
const charges = createCharges();
const panel = createPanel(document.querySelector(".tape"));
document.querySelector(".inputs").append(people.el, mode.el, subtotal.el, charges.el);

function render() {
  people.update(bill);
  mode.update(bill);
  subtotal.update(bill);
  charges.update(bill);
  panel.update(computeResult(bill));
}

render();
