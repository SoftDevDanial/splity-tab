// Boot and wiring for the page. Holds the one `bill` value, calls split-core for every change, and asks
// each block under src/ui/ to show it. No money is computed here (split-core owns that).
import {
  newBill, addPerson, removePerson, setPersonName, setMode, setSubtotalText,
  addItem, removeItem, setItemName, setItemPriceText, toggleItemPerson, setServiceText, setSstText,
} from "./core/bill.js";
import { computeResult } from "./core/result.js";
import { summaryText } from "./core/summary.js";
import { getStorage, loadDraft, saveDraft } from "./draft.js";
import { flagsFor, newErrorFlags, typedInto, leftField, forgetPrice, visibleErrors } from "./errors.js";
import { createDialog } from "./ui/dialog.js";
import { createNote } from "./ui/note.js";
import { createPeople } from "./ui/people.js";
import { createMode } from "./ui/mode.js";
import { createSubtotal } from "./ui/subtotal.js";
import { createItems } from "./ui/items.js";
import { createCharges } from "./ui/charges.js";
import { createPanel } from "./ui/panel.js";

// Boot (R2, R26 to R28). A cold boot is a new bill and writes nothing. A readable draft is shown as it was.
// An unreadable one starts a new bill, saves it at once so a reload does not show the note again, and shows the note.
const storage = getStorage();
const loaded = loadDraft(storage);
let bill = loaded.state === "ok" ? loaded.bill : newBill();
const view = { errorShown: flagsFor(bill), status: null, noteShown: loaded.state === "unreadable" };
if (view.noteShown) saveDraft(storage, bill);

const hasShares = (result) => result.kind === "even" || result.kind === "item";

/** R22, R23: copy the summary of the bill as it is now. Any refusal is shown as a failure, nothing else changes. */
async function copySummary() {
  const result = computeResult(bill);
  if (!hasShares(result)) return;
  let outcome = "ok";
  try {
    await navigator.clipboard.writeText(summaryText(result));
  } catch {
    outcome = "fail";
  }
  // The panel may have turned into a message while the browser decided (R24): then there is no status to set.
  if (!hasShares(computeResult(bill))) return;
  view.status = outcome;
  render();
}

function commit(next) {
  if (next === bill) return;
  bill = next;
  saveDraft(storage, bill);
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
const mode = createMode({ onMode: (value) => commit(setMode(bill, value)) });
const subtotal = createSubtotal({
  onInput(text) {
    typedInto(view.errorShown, "subtotal", text);
    commit(setSubtotalText(bill, text));
  },
  onLeave(text) {
    leftField(view.errorShown, "subtotal", text);
    render();
  },
});
const items = createItems({
  onName: (id, text) => commit(setItemName(bill, id, text)),
  onPrice(id, text) {
    typedInto(view.errorShown, "price", text, id);
    commit(setItemPriceText(bill, id, text));
  },
  onPriceLeave(id, text) {
    leftField(view.errorShown, "price", text, id);
    render();
  },
  onToggle: (itemId, personId) => commit(toggleItemPerson(bill, itemId, personId)),
  onAdd() {
    commit(addItem(bill));
    items.focusName(bill.items.length - 1);
  },
  onRemove(id) {
    const position = bill.items.findIndex((item) => item.id === id);
    forgetPrice(view.errorShown, id);
    commit(removeItem(bill, id));
    if (bill.items.length === 0) items.focusAdd();
    else items.focusName(Math.min(position, bill.items.length - 1));
  },
});
const chargeSetters = { service: setServiceText, sst: setSstText };
const charges = createCharges({
  onInput(kind, text) {
    typedInto(view.errorShown, kind, text);
    commit(chargeSetters[kind](bill, text));
  },
  onLeave(kind, text) {
    leftField(view.errorShown, kind, text);
    render();
  },
});
const panel = createPanel(document.querySelector(".tape"), { onCopy: copySummary });
createDialog(document.querySelector("dialog"), document.querySelector(".bar .btn"), {
  onConfirm() {
    // The view state is reset with the bill (R31): a stale error flag or copy status must not outlive it.
    view.errorShown = newErrorFlags();
    view.status = null;
    commit(newBill());
  },
});
const note = createNote(document.querySelector(".bar"), {
  onDismiss() {
    view.noteShown = false;
    render();
    people.focusName(0);
  },
});
document.querySelector(".inputs").append(people.el, mode.el, subtotal.el, items.el, charges.el);

function render() {
  const errors = visibleErrors(view.errorShown, bill);
  people.update(bill);
  mode.update(bill);
  subtotal.update(bill, errors);
  items.update(bill, errors);
  charges.update(bill, errors);
  const result = computeResult(bill);
  if (!hasShares(result)) view.status = null;
  panel.update(result, view.status);
  note.update(view.noteShown);
}

render();
