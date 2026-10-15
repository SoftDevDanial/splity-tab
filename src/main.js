// Boot and wiring for the page. Holds the one `bill` value, calls split-core for every change, and asks
// each block under src/ui/ to show it. No money is computed here (split-core owns that).
import {
  newBill, addPerson, removePerson, setPersonName, setMode, setSubtotalText,
  addItem, removeItem, setItemName, setItemPriceText, toggleItemPerson, setServiceText, setSstText, personLabel,
} from "./core/bill.js";
import { computeResult } from "./core/result.js";
import { chooseSparePerson, chooseSpareRule } from "./core/spare.js";
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
import { CARD_IDS, createReceipt, hasSplits } from "./ui/receipt.js";
import { createStrip } from "./ui/strip.js";
import { createSheet } from "./ui/sheet.js";
import { createSpareChoice } from "./ui/spare-choice.js";
import { DESKTOP } from "./ui/media.js";
import { watchPointerClicks } from "./ui/dom.js";

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
 * R22, R23: copy the summary of the bill as it is now, then show how it went in every status line. A missing clipboard
 * or writeText throws inside the try, so every refusal is the one failure and nothing else changes. An answer that comes
 * after a change to the bill shows nothing (R24), because the change cleared the status and the summary the browser
 * copied is no longer the one on screen.
 */
async function copySummary() {
  const copied = bill;
  const result = computeResult(copied);
  if (!hasSplits(result)) return;
  let outcome = "ok";
  try {
    await navigator.clipboard.writeText(summaryText(result));
  } catch {
    outcome = "fail";
  }
  if (bill !== copied) return;
  view.status = outcome;
  render();
}

function commit(next) {
  if (next === bill) return;
  bill = next;
  view.status = null; // rule 10 (R24), the next change to the bill clears the copy status, and nothing else does
  save();
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
// New bill gets its icon here (Copy summary on the strip in createStrip, Splits in createSheet), because every icon but the
// sprite and the mark is built at run time (R44).
const newBillButton = document.getElementById("newBill");
newBillButton.prepend(icon("plus"));
const strip = createStrip(document.getElementById("strip"), { onCopy: copySummary });

/** The label of the bill's person `id`, for the chip of a One person choice (R51). */
function personName(id) {
  const index = bill.people.findIndex((person) => person.id === id);
  return personLabel(bill.people[index], index);
}
const receiptHandlers = { onCopy: copySummary, onSpare: () => spareChoice.open(), personName };
const card = createReceipt(document.getElementById("rbody"), { ...receiptHandlers, ids: CARD_IDS });
const splitsButton = document.getElementById("splitsBtn");
const sheet = createSheet(document.getElementById("splitsDlg"), splitsButton, receiptHandlers);
// P1 (R52, R53). Math.random goes to chooseSpareRule and to nothing else here (PD-19). The chip shown is the card's from
// 1024 px and the sheet's below it, so it is asked for when needed, never kept (PD-23).
const spareChoice = createSpareChoice(document.getElementById("spareDlg"), {
  onRule: (value) => commit(chooseSpareRule(bill, value, Math.random)),
  onPerson: (id) => commit(chooseSparePerson(bill, id)),
  card: document.getElementById("card"),
  shownChip: () => (DESKTOP.matches ? card.spareChip() : sheet.spareChip()),
  splits: splitsButton,
  makeRoom: (height) => sheet.makeRoom(height),
});
createDialog(document.getElementById("newDlg"), newBillButton, {
  onConfirm() {
    // The view state is reset with the bill (R31): a stale error flag or open state must not outlive it. The copy
    // status goes in commit, as with every change to the bill.
    const fresh = newBill();
    view.errorShown = newErrorFlags();
    view.open = openAsAtLoad(fresh, view.errorShown);
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
document.getElementById("work").append(peopleSection.el, chargesSection.el, mode.el);

// R8, the Subtotal block is in the DOM in even mode only and the Items block in by-item mode only, each after the Split
// block. A block is put back only when it is missing, because moving the block that holds the focused field drops its
// focus (R33).
const MODE_BLOCKS = [[subtotal.el, "even"], [items.el, "item"]];
function placeModeBlocks() {
  for (const [block, blockMode] of MODE_BLOCKS) {
    if (bill.mode !== blockMode) block.remove();
    else if (!block.isConnected) mode.el.after(block);
  }
}

function render() {
  const errors = visibleErrors(view.errorShown, bill);
  const result = computeResult(bill);
  peopleSection.update(bill, view.open.people);
  chargesSection.update(bill, view.open.charges);
  people.update(bill);
  mode.update(bill);
  placeModeBlocks();
  subtotal.update(bill, errors);
  items.update(bill, errors);
  charges.update(bill, errors);
  card.update(result, view.status);
  strip.update(result, view.status);
  sheet.update(result, view.status); // R50, an open sheet follows the bill and the status
  spareChoice.update(bill, result); // after the receipts, so an open P1 measures them in their new state (R52)
  notes.update(view);
  items.markFrame(); // last, so it measures the frame with every block above it in its new state (R56)
}

render();
