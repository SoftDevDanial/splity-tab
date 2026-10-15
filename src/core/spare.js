// Choosing who takes the spare sen (R29 to R31). It sits beside bill.js and not in it because Pick again needs
// computeResult, and result.js already imports bill.js, so the same functions in bill.js would be an import cycle.
// The random source is an argument the caller passes: core has no random source of its own (R25).
import { newBill, sparePeople } from "./bill.js";
import { computeResult } from "./result.js";

/** @typedef {() => number} RandomSource a number from 0 up to but not including 1 */

// Pick again stops here (R31, ruled CG-P3): on a bill where no order can change the rows a loop would never end.
const MAX_DRAWS = 64;

// The Bill fields as newBill lists them, the one list (bill.js), read here because billWith stays private.
const BILL_FIELDS = Object.keys(newBill());

/**
 * The bill with another spare choice, built from BILL_FIELDS only and never spread, so a stray or __proto__ key on
 * a parsed bill is not copied (threat model, object integrity).
 */
function withSpare(bill, spare) {
  return Object.fromEntries(BILL_FIELDS.map((field) => [field, field === "spare" ? spare : bill[field]]));
}

/** Fisher and Yates over every person's id in list order, one number from `random` for each step (R29). */
function drawOrder(bill, random) {
  const order = bill.people.map((person) => person.id);
  for (let i = order.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  return order;
}

/**
 * Sets the rule (R29). One person takes the first person who can (R28), At random draws a new order.
 * Returns the same bill for the rule already set, an unknown rule, or One person with nobody to pick.
 * @param {import("./bill.js").Bill} bill
 * @param {string} rule "top", "one" or "random"
 * @param {RandomSource} random only read for "random"
 * @returns {import("./bill.js").Bill}
 */
export function chooseSpareRule(bill, rule, random) {
  if (rule === bill.spare.rule) return bill;
  if (rule === "top") return withSpare(bill, { rule: "top" });
  if (rule === "one") {
    const [first] = sparePeople(bill);
    return first === undefined ? bill : withSpare(bill, { rule: "one", personId: first });
  }
  if (rule === "random") return withSpare(bill, { rule: "random", order: drawOrder(bill, random) });
  return bill;
}

/**
 * Picks the one person who takes every spare sen (R30). Returns the same bill for a person who cannot take
 * one, who is already chosen, or who is not on the bill.
 * @param {import("./bill.js").Bill} bill
 * @param {string} personId
 * @returns {import("./bill.js").Bill}
 */
export function chooseSparePerson(bill, personId) {
  const alreadyChosen = bill.spare.rule === "one" && bill.spare.personId === personId;
  if (alreadyChosen || !sparePeople(bill).includes(personId)) return bill;
  return withSpare(bill, { rule: "one", personId });
}

const ROW_FIELDS = ["share", "items", "charges"];
const rowsDiffer = (rows, other) => rows.some((row, i) => ROW_FIELDS.some((field) => row[field] !== other[i][field]));

/**
 * Draws a new At random order until the rows change, at most MAX_DRAWS times (R31). Returns the same bill
 * when the rule is not At random, when there are no shares to change, and when every draw leaves the rows as
 * they are.
 * @param {import("./bill.js").Bill} bill
 * @param {RandomSource} random
 * @returns {import("./bill.js").Bill}
 */
export function pickAgain(bill, random) {
  if (bill.spare.rule !== "random") return bill;
  const current = computeResult(bill);
  if (current.kind !== "even" && current.kind !== "item") return bill;
  for (let draw = 0; draw < MAX_DRAWS; draw += 1) {
    const candidate = withSpare(bill, { rule: "random", order: drawOrder(bill, random) });
    if (rowsDiffer(computeResult(candidate).rows, current.rows)) return candidate;
  }
  return bill;
}
