// The bill maths and the single entry point that turns a Bill into what the screen shows.
// Money is split in divisions (R32): floor parts first, then the spare sen by the bill's spare choice.
import { parseAmount, parseRate } from "./money.js";
import { allocateByWeight } from "./allocate.js";
import { LIMITS, personLabel, sparePeople } from "./bill.js";

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
 *   | { kind: "even", charges: Charges, rows: EvenRow[], check: { share: number }, spare: SpareResult }
 *   | { kind: "item", charges: Charges, rows: ItemRow[],
 *       check: { items: number, charges: number, share: number }, spare: SpareResult }
 * } Result
 */
/** @typedef {{ count: number, rule: "top" | "one" | "random", personId: string | null }} SpareResult */

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

/**
 * The floor part of every weight, before any spare sen (R32): the exact R8 floor of amount x weight / total.
 * allocateByWeight leaves its leftover with the lowest index that has weight, so with the rest of the weight
 * placed first, the last entry is the exact floor whatever the leftover does. That keeps the BigInt division
 * in allocate.js, its one home.
 */
function floorParts(amount, weights) {
  const total = sum(weights);
  return weights.map((weight) => allocateByWeight(amount, [total - weight, weight])[1]);
}

// What each spare choice does with a division's spare sen (R32). `recipients(members, count)` names who takes
// `count` spare sen of a division whose members are `members` (person indexes in list order). One entry per
// rule, so the division maths below is written once. At random keeps a cursor, so divisions must be asked in
// the R32 order, items in list order and then the charges.
const TOP = { rule: "top", personId: null, recipients: (members, count) => members.slice(0, count) };

function onePerson(bill, personId) {
  const chosen = bill.people.findIndex((person) => person.id === personId);
  return { rule: "one", personId, recipients: (members, count) => Array(count).fill(chosen) };
}

function atRandom(bill, order) {
  const drawn = order.map((id) => bill.people.findIndex((person) => person.id === id));
  let cursor = 0;
  return {
    rule: "random",
    personId: null,
    recipients(members, count) {
      const taken = [];
      for (let n = 0; n < count; n += 1) {
        // R27 keeps every member in `order`, so the search always lands.
        const ahead = drawn.findIndex((_, k) => members.includes(drawn[(cursor + k) % drawn.length]));
        const at = (cursor + ahead) % drawn.length;
        taken.push(drawn[at]);
        cursor = (at + 1) % drawn.length;
      }
      return taken;
    },
  };
}

/** The rule in effect. A chosen person who cannot take spare sen (R28) means Top, and the stored choice stays. */
function spareRule(bill) {
  const { spare } = bill;
  if (spare.rule === "one" && sparePeople(bill).includes(spare.personId)) return onePerson(bill, spare.personId);
  return spare.rule === "random" ? atRandom(bill, spare.order) : TOP;
}

/**
 * One division of R32: `amount` over `members` in floor parts by `weights` (equal when left out), then its
 * spare sen, the amount less those parts, one each to the rule's recipients. Adds into `totals`, one slot per
 * person, and returns how many spare sen the division had.
 */
function divide(amount, members, rule, totals, weights = members.map(() => 1)) {
  const floors = floorParts(amount, weights);
  members.forEach((person, k) => {
    totals[person] += floors[k];
  });
  const spare = amount - sum(floors);
  rule.recipients(members, spare).forEach((person) => {
    totals[person] += 1;
  });
  return spare;
}

const nobody = (bill) => bill.people.map(() => 0);
const spareResult = (count, rule) => ({ count, rule: rule.rule, personId: rule.personId });

function evenResult(bill, serviceBp, sstBp) {
  const subtotal = parseAmount(bill.subtotalText);
  if (!subtotal.ok) return blocked("subtotal");
  const charges = billCharges(subtotal.cents, serviceBp, sstBp);
  const rule = spareRule(bill);
  const shares = nobody(bill);
  const spare = divide(charges.total, bill.people.map((_, index) => index), rule, shares);
  const rows = bill.people.map((person, index) => ({ name: personLabel(person, index), share: shares[index] }));
  return { kind: "even", charges, rows, check: { share: sum(shares) }, spare: spareResult(spare, rule) };
}

/** Indexes into `people` of those on an item, in list order so Top of the list reads the same as 1.0. */
function holderIndexes(bill, item) {
  const indexes = [];
  bill.people.forEach((person, index) => {
    if (item.who.includes(person.id)) indexes.push(index);
  });
  return indexes;
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

  const rule = spareRule(bill);
  const items = nobody(bill);
  let spare = 0;
  holders.forEach((members, itemIndex) => {
    spare += divide(prices[itemIndex], members, rule, items);
  });
  // The charges follow what each person's items came to, spare sen included (R21 point 4). Someone with
  // no items pays no charges, so only people with items are members.
  const payers = bill.people.map((_, index) => index).filter((index) => items[index] > 0);
  const chargeParts = nobody(bill);
  spare += divide(charges.service + charges.sst, payers, rule, chargeParts, payers.map((index) => items[index]));
  const rows = bill.people.map((person, index) => ({
    name: personLabel(person, index),
    items: items[index],
    charges: chargeParts[index],
    share: items[index] + chargeParts[index],
  }));
  const check = { items: sum(items), charges: sum(chargeParts), share: sum(rows.map((row) => row.share)) };
  return { kind: "item", charges, rows, check, spare: spareResult(spare, rule) };
}

/**
 * Turns a Bill into what the screen shows (R18 to R22, R32, R33). Blocking rules apply in order:
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
