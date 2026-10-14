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
import { createNotes } from "./ui/note.js";
import { createPeople } from "./ui/people.js";
import { createMode } from "./ui/mode.js";
import { createSubtotal } from "./ui/subtotal.js";
import { createItems } from "./ui/items.js";
import { createCharges } from "./ui/charges.js";
import { createPeopleSection, createChargesSection } from "./ui/sections.js";
import { icon } from "./ui/icons.js";
import { createPanel, hasShares } from "./ui/panel.js";
import { blockedReceipt } from "./ui/receipt.js";
import { reconcileChildren, watchPointerClicks } from "./ui/dom.js";

watchPointerClicks(); // R57 (b): every repeat check reads what these window listeners record from the first press on

// Boot (R2, R26 to R28, R46, R48). A cold boot is a new bill and writes nothing. A readable draft is shown as it was.
// An unreadable one starts a new bill, saves it at once so a reload does not show the note again, and shows the note.
// A failed boot read shows the save warning in the first render. `storage` is null while the getter fails.
let storage = getStorage();
const loaded = loadDraft(storage);
let bill = loaded.state === "ok" ? loaded.bill : newBill();
const errorShown = flagsFor(bill);
const view = {
  errorShown, status: null, noteShown: loaded.state === "unreadable", saveFailing: loaded.state === "failed",
  open: openAsAtLoad(bill, errorShown),
};
if (view.noteShown) save();

/**
 * R48 (1): which sections are open when a bill is loaded, and again after Start new bill (R31). People for a bill that
 * is still `newBill()` (CG-P4), Charges when a rate shows its error (R10 (b)). Never saved.
 */
function openAsAtLoad(loadedBill, errorShown) {
  // Equal bills give equal JSON here, because the decoder builds every bill in core's key order (D12).
  return { people: JSON.stringify(loadedBill) === JSON.stringify(newBill()), charges: errorShown.service || errorShown.sst };
}

/**
 * R46, R47: one save attempt, and the latest attempt decides whether the warning shows. While the storage object
 * could not be obtained, each attempt reads the getter again, so storage that comes back clears the warning (SW6).
 */
function save() {
  if (storage === null) storage = getStorage();
  view.saveFailing = !saveDraft(storage, bill);
}

/**
 * R24: the copy status lives only while the shares table does. This is the one place that writes
 * `view.status`, so the three ways it can go stale (a bill change that removes the table, a clipboard answer
 * that arrives after that, Start new bill) cannot bring it back with the table.
 */
function setStatus(next) {
  view.status = hasShares(computeResult(bill)) ? next : null;
}

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
  setStatus(outcome);
  render();
}

function commit(next) {
  if (next === bill) return;
  bill = next;
  save();
  setStatus(view.status);
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

// R10 for the subtotal, every item price and both rates. `kind` picks the parser and the bill setter, `id` is
// the item id for a price. Typing may clear the field's error flag, leaving the field may set it.
const AMOUNT_SETTERS = {
  subtotal: (current, text) => setSubtotalText(current, text),
  price: (current, text, id) => setItemPriceText(current, id, text),
  service: (current, text) => setServiceText(current, text),
  sst: (current, text) => setSstText(current, text),
};

function amountTyped(kind, text, id) {
  typedInto(view.errorShown, kind, text, id);
  commit(AMOUNT_SETTERS[kind](bill, text, id));
}

function amountLeft(kind, text, id) {
  leftField(view.errorShown, kind, text, id);
  render();
}

const subtotal = createSubtotal({
  onInput: (text) => amountTyped("subtotal", text),
  onLeave: (text) => amountLeft("subtotal", text),
});
const items = createItems({
  onName: (id, text) => commit(setItemName(bill, id, text)),
  onPrice: (id, text) => amountTyped("price", text, id),
  onPriceLeave: (id, text) => amountLeft("price", text, id),
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
const charges = createCharges({ onInput: (kind, text) => amountTyped(kind, text), onLeave: (kind, text) => amountLeft(kind, text) });
// The shell's static buttons get their icons here, because every icon but the sprite and the mark is built at run time (R44).
const newBillButton = document.getElementById("newBill");
newBillButton.prepend(icon("plus"));
document.getElementById("splitsBtn").append(icon("caret", "caret-up"));
document.getElementById("stripCopy").prepend(icon("copy"));
const receipt = document.getElementById("rbody");
const panel = createPanel(receipt, { onCopy: copySummary });
createDialog(document.getElementById("newDlg"), newBillButton, {
  onConfirm() {
    // The view state is reset with the bill (R31): a stale error flag, copy status or open state must not outlive it.
    const fresh = newBill();
    view.errorShown = newErrorFlags();
    view.open = openAsAtLoad(fresh, view.errorShown);
    setStatus(null);
    commit(fresh);
  },
});
const notes = createNotes(document.getElementById("notes"), {
  onDismiss() {
    view.noteShown = false;
    render();
    newBillButton.focus(); // rule 12
  },
});
// R48 (1): after load only a header row (and Start new bill) opens or folds a section. A fold is not a change, so nothing is saved.
function toggleSection(key) {
  view.open[key] = !view.open[key];
  render();
}
const peopleSection = createPeopleSection(people.content, () => toggleSection("people"));
const chargesSection = createChargesSection(charges.content, () => toggleSection("charges"));
document.getElementById("work").append(peopleSection.el, chargesSection.el, mode.el, subtotal.el, items.el);

function render() {
  const errors = visibleErrors(view.errorShown, bill);
  const result = computeResult(bill);
  peopleSection.update(bill, view.open.people);
  chargesSection.update(bill, view.open.charges);
  people.update(bill);
  mode.update(bill);
  subtotal.update(bill, errors);
  items.update(bill, errors);
  charges.update(bill, errors);
  if (result.kind === "blocked") reconcileChildren(receipt, blockedReceipt(result.reason));
  else panel.update(result, view.status);
  notes.update(view);
}

render();
