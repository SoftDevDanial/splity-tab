// When an inline error shows (R10, CG-3). View-state rules, never saved. `newErrorFlags`, `flagsFor` and `visibleErrors`
// are pure. `typedInto`, `leftField` and `forgetPrice` update the flags object they are given and return nothing.
// Only text that is not empty and fails its parser may show an error (ruling 1). The error appears when
// the field is left, a restored field shows it at once, and while typing it goes as soon as the text is
// valid or empty and stays gone until the field is next left. The receipt does not use these flags: it
// always follows the current text (R10, R16).
import { LIMITS } from "./core/bill.js";
import { parseAmount, parseRate } from "./core/money.js";

const READERS = {
  subtotal: parseAmount,
  price: parseAmount,
  service: (text) => parseRate(text, LIMITS.serviceMaxPercent),
  sst: (text) => parseRate(text, LIMITS.sstMaxPercent),
};

function isBad(kind, text) {
  const read = READERS[kind](text);
  return !read.ok && !read.empty;
}

/** The `errorShown` view state: one flag per amount and rate field, and one per item price by item id. */
export function newErrorFlags() {
  return { subtotal: false, service: false, sst: false, price: {} };
}

const getFlag = (flags, kind, id) => (kind === "price" ? flags.price[id] === true : flags[kind]);

function setFlag(flags, kind, id, value) {
  if (kind === "price") flags.price[id] = value;
  else flags[kind] = value;
}

/** R10 (b): flags for a bill read from storage, so a restored bad field shows its error at once. */
export function flagsFor(bill) {
  const flags = newErrorFlags();
  flags.subtotal = isBad("subtotal", bill.subtotalText);
  flags.service = isBad("service", bill.serviceText);
  flags.sst = isBad("sst", bill.sstText);
  for (const item of bill.items) flags.price[item.id] = isBad("price", item.priceText);
  return flags;
}

/** R10 (c): call on every input event. `id` is the item id for a price. */
export function typedInto(flags, kind, text, id) {
  if (!isBad(kind, text)) setFlag(flags, kind, id, false);
}

/** R10 (a): call when the field loses focus. */
export function leftField(flags, kind, text, id) {
  if (isBad(kind, text)) setFlag(flags, kind, id, true);
}

/** A removed item takes its flag with it, so no stale flag waits for a later item. */
export function forgetPrice(flags, id) {
  delete flags.price[id];
}

/** The errors on screen now. A flag counts only while its text is still bad. */
export function visibleErrors(flags, bill) {
  return {
    subtotal: getFlag(flags, "subtotal") && isBad("subtotal", bill.subtotalText),
    service: getFlag(flags, "service") && isBad("service", bill.serviceText),
    sst: getFlag(flags, "sst") && isBad("sst", bill.sstText),
    price: Object.fromEntries(bill.items.map((item) => [item.id, getFlag(flags, "price", item.id) && isBad("price", item.priceText)])),
  };
}
