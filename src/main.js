// Boot and wiring for the page. Holds the one `bill` value, calls split-core for every change, and asks
// each block under src/ui/ to show it. No money is computed here (split-core owns that).
import { newBill } from "./core/bill.js";
import { computeResult } from "./core/result.js";
import { createPeople } from "./ui/people.js";
import { createMode } from "./ui/mode.js";
import { createSubtotal } from "./ui/subtotal.js";
import { createCharges } from "./ui/charges.js";
import { createPanel } from "./ui/panel.js";

let bill = newBill();

const people = createPeople();
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
