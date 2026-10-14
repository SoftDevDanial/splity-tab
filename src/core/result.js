// The bill maths and the single entry point that turns a Bill into what the screen shows.
import { parseAmount, parseRate } from "./money.js";
import { allocateEvenly, allocateByWeight } from "./allocate.js";
import { LIMITS, personLabel } from "./bill.js";

/**
 * @typedef {{ subtotal: number, serviceBp: number, service: number,
 *             sstBp: number, sstBase: number, sst: number, total: number }} Charges
 */
/** @typedef {{ name: string, share: number }} EvenRow */
/** @typedef {{ name: string, items: number, charges: number, share: number }} ItemRow */
/**
 * @typedef {
 *   | { kind: "blocked", reason: "rates" | "subtotal" | "no-prices" | "prices" }
 *   | { kind: "unassigned", count: number, charges: Charges }
 *   | { kind: "even", charges: Charges, rows: EvenRow[], check: { share: number } }
 *   | { kind: "item", charges: Charges, rows: ItemRow[],
 *       check: { items: number, charges: number, share: number } }
 * } Result
 */

const BASIS_POINTS = 10000;

/**
 * amount x bp / 10000 rounded half up. Remainder arithmetic keeps the division exact. Within the spec's
 * bounds the largest product is the service step, 499,999,950 x 3000 (about 1.5e12), far below 2^53,
 * so Number is exact here.
 */
function applyRate(amount, bp) {
  const shifted = amount * bp + BASIS_POINTS / 2;
  return (shifted - (shifted % BASIS_POINTS)) / BASIS_POINTS;
}

/**
 * Service charge, then SST on subtotal plus service (R6).
 * @param {number} subtotal cents
 * @param {number} serviceBp
 * @param {number} sstBp
 * @returns {Charges}
 */
export function billCharges(subtotal, serviceBp, sstBp) {
  const service = applyRate(subtotal, serviceBp);
  const sstBase = subtotal + service;
  const sst = applyRate(sstBase, sstBp);
  return { subtotal, serviceBp, service, sstBp, sstBase, sst, total: sstBase + sst };
}

const sum = (numbers) => numbers.reduce((total, n) => total + n, 0);
const blocked = (reason) => ({ kind: "blocked", reason });

function evenResult(bill, serviceBp, sstBp) {
  const subtotal = parseAmount(bill.subtotalText);
  if (!subtotal.ok) return blocked("subtotal");
  const charges = billCharges(subtotal.cents, serviceBp, sstBp);
  const shares = allocateEvenly(charges.total, bill.people.length);
  const rows = bill.people.map((person, index) => ({ name: personLabel(person, index), share: shares[index] }));
  return { kind: "even", charges, rows, check: { share: sum(shares) } };
}

/** Indexes into `people` of those on an item, in list order so leftover sen go to the top of the list. */
function holderIndexes(bill, item) {
  const indexes = [];
  bill.people.forEach((person, index) => {
    if (item.who.includes(person.id)) indexes.push(index);
  });
  return indexes;
}

/** Each person's own items: every price split evenly over the people on it. */
function itemTotals(bill, prices, holders) {
  const totals = bill.people.map(() => 0);
  holders.forEach((indexes, itemIndex) => {
    const parts = allocateEvenly(prices[itemIndex], indexes.length);
    indexes.forEach((personIndex, k) => {
      totals[personIndex] += parts[k];
    });
  });
  return totals;
}

function itemResult(bill, serviceBp, sstBp) {
  const parsed = bill.items.map((item) => parseAmount(item.priceText));
  // "No items" and "every price invalid" share one message (RULINGS-v1.1.0 row c), so one reason.
  if (!parsed.some((price) => price.ok)) return blocked("no-prices");
  if (!parsed.every((price) => price.ok)) return blocked("prices");
  const prices = parsed.map((price) => price.cents);
  const charges = billCharges(sum(prices), serviceBp, sstBp);

  const holders = bill.items.map((item) => holderIndexes(bill, item));
  const unassigned = holders.filter((indexes) => indexes.length === 0).length;
  // The summary stays visible while items are untapped (ruling 3e), so the charges ride along.
  if (unassigned > 0) return { kind: "unassigned", count: unassigned, charges };

  const items = itemTotals(bill, prices, holders);
  const chargeParts = allocateByWeight(charges.service + charges.sst, items);
  const rows = bill.people.map((person, index) => ({
    name: personLabel(person, index),
    items: items[index],
    charges: chargeParts[index],
    share: items[index] + chargeParts[index],
  }));
  const check = { items: sum(items), charges: sum(chargeParts), share: sum(rows.map((row) => row.share)) };
  return { kind: "item", charges, rows, check };
}

/**
 * Turns a Bill into what the screen shows (R18 to R22). Blocking rules apply in order:
 * rates, then the subtotal (even) or no-prices and prices (by item). Even mode ignores items and
 * by-item mode ignores the subtotal.
 * @param {import("./bill.js").Bill} bill
 * @returns {Result}
 */
export function computeResult(bill) {
  const service = parseRate(bill.serviceText, LIMITS.serviceMaxPercent);
  const sst = parseRate(bill.sstText, LIMITS.sstMaxPercent);
  if (!service.ok || !sst.ok) return blocked("rates");
  return bill.mode === "even"
    ? evenResult(bill, service.bp, sst.bp)
    : itemResult(bill, service.bp, sst.bp);
}
