import { test } from "node:test";
import assert from "node:assert/strict";
import { chooseSpareRule, chooseSparePerson, pickAgain } from "../src/core/spare.js";
import { computeResult } from "../src/core/result.js";
import { buildBill, withSpare, S2, I2, I3 } from "./support/bills.js";
import { mulberry32, scripted, constant } from "./support/rng.js";

const TOP = { rule: "top" };
const one = (personId) => ({ rule: "one", personId });
const random = (...order) => ({ rule: "random", order });

// ---- R29 chooseSpareRule ----

// bill, spare before, scripted numbers, rule, spare after. The draws are worked by hand in qa.md.
const ruleCases = [
  ["S2", S2, TOP, [], "one", one("p1")],
  ["I2", I2, TOP, [], "one", one("p2")],
  ["S2", S2, TOP, [0.9, 0.1], "random", random("p2", "p1", "p3")],
  ["S2", S2, TOP, [0, 0], "random", random("p2", "p3", "p1")],
  ["S2", S2, one("p2"), [], "top", TOP],
];
for (const [title, bill, before, numbers, rule, after] of ruleCases) {
  test(`@R29 choosing "${rule}" on ${title} with spare ${JSON.stringify(before)} gives ${JSON.stringify(after)}`, () => {
    const source = scripted(...numbers);
    const next = chooseSpareRule(withSpare(bill, before), rule, source);
    assert.deepEqual(next.spare, after);
    assert.equal(source.calls, numbers.length);
  });
}

test("@R29 the draw is a Fisher and Yates shuffle that takes one number for each step, from the end", () => {
  const twelve = buildBill({ names: Array.from({ length: 12 }, (_, k) => `P${k + 1}`) });
  const source = constant(0);
  const { order } = chooseSpareRule(twelve, "random", source).spare;
  assert.equal(source.calls, 11);
  // A 0 swaps the last place with the first every step: the first entry ends last, the rest move up one.
  assert.deepEqual(order, ["p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p1"]);
});

test("@R29 a number just under 1 stays inside the list (no swap)", () => {
  const next = chooseSpareRule(S2, "random", scripted(0.9999999, 0.9999999));
  assert.deepEqual(next.spare.order, ["p1", "p2", "p3"]);
});

test("@R29 the drawn order holds every person once, also a person on no item", () => {
  const source = mulberry32(20261014);
  for (let n = 0; n < 200; n += 1) {
    const { order } = chooseSpareRule(I2, "random", source).spare;
    assert.deepEqual([...order].sort(), ["p1", "p2", "p3"]);
  }
});

test("@R29 choosing the rule already set, an unknown rule or One person with nobody to pick changes nothing", () => {
  const drawn = withSpare(S2, random("p2", "p3", "p1"));
  const never = scripted();
  assert.equal(chooseSpareRule(drawn, "random", never), drawn);
  assert.equal(chooseSpareRule(S2, "top", never), S2);
  assert.equal(chooseSpareRule(drawn, "split", never), drawn);
  assert.equal(chooseSpareRule(drawn, "toString", never), drawn);
  const nobody = buildBill({ mode: "item", names: ["Aisyah", "Ben"], items: [{ price: "1.00", who: [] }] });
  assert.equal(chooseSpareRule(nobody, "one", never), nobody);
  assert.equal(never.calls, 0);
});

// ---- R30 chooseSparePerson ----

const personCases = [
  ["S2", S2, one("p1"), "p2", one("p2")],
  ["S2", S2, TOP, "p3", one("p3")],
  ["S2", S2, random("p2", "p3", "p1"), "p1", one("p1")],
];
for (const [title, bill, before, id, after] of personCases) {
  test(`@R30 choosing ${id} on ${title} with spare ${JSON.stringify(before)} gives ${JSON.stringify(after)}`, () => {
    assert.deepEqual(chooseSparePerson(withSpare(bill, before), id).spare, after);
  });
}

test("@R30 a person who cannot take spare sen, is already chosen or is unknown changes nothing", () => {
  const onI2 = withSpare(I2, one("p2"));
  assert.equal(chooseSparePerson(onI2, "p1"), onI2);
  const chosen = withSpare(S2, one("p2"));
  assert.equal(chooseSparePerson(chosen, "p2"), chosen);
  assert.equal(chooseSparePerson(S2, "p9"), S2);
  assert.equal(chooseSparePerson(S2, "__proto__"), S2);
});

// ---- R31 pickAgain ----

const rowsOf = (bill) => computeResult(bill).rows;

test("@R31 Pick again draws until the splits change", () => {
  const bill = withSpare(S2, random("p2", "p3", "p1"));
  // The first draw gives [p3, p2, p1], the same two people get the spare sen, so the rows stay. The second gives [p1, p3, p2].
  const source = scripted(0, 0.5, 0.5, 0.5);
  const next = pickAgain(bill, source);
  assert.deepEqual(next.spare, random("p1", "p3", "p2"));
  assert.deepEqual(rowsOf(next).map((row) => row.share), [3887, 3886, 3887]);
  assert.equal(source.calls, 4);
});

test("@R31 a new order that moves money between items and charges counts as a change, even at equal shares", () => {
  const bill = buildBill({
    mode: "item", names: ["Aisyah", "Ben", "Chen"],
    items: [{ price: "0.01", who: ["p1", "p2"] }, { price: "0.05", who: ["p2", "p3"] }],
  });
  const current = withSpare(bill, random("p1", "p2", "p3"));
  const next = pickAgain(current, scripted(0.5, 0.9));
  assert.deepEqual(next.spare, random("p1", "p3", "p2"));
  assert.deepEqual(rowsOf(next).map((row) => row.share), rowsOf(current).map((row) => row.share));
  assert.notDeepEqual(rowsOf(next), rowsOf(current));
});

const noDraw = [
  ["the S2 bill with spare top", S2],
  ["the S2 bill with spare one p2", withSpare(S2, one("p2"))],
  ["the S2 bill with spare random and an empty subtotal (blocked)", withSpare(buildBill({ names: ["A", "B", "C"] }), random("p1", "p2", "p3"))],
];
for (const [title, bill] of noDraw) {
  test(`@R31 ${title}: Pick again returns the same bill and draws nothing`, () => {
    const source = constant(0);
    assert.equal(pickAgain(bill, source), bill);
    assert.equal(source.calls, 0);
  });
}

test("@R31 an unassigned item blocks Pick again like any result without shares", () => {
  const bill = withSpare(buildBill({ mode: "item", names: ["A", "B"], items: [{ price: "1.00", who: [] }] }), random("p1", "p2"));
  const source = constant(0);
  assert.equal(pickAgain(bill, source), bill);
  assert.equal(source.calls, 0);
});

test("@R31 with no spare sen no order can change the splits: 64 draws, then the same bill", () => {
  const even = buildBill({ subtotal: "1.00", service: "0", sst: "0" });
  const bill = withSpare(even, random("p1", "p2"));
  const source = constant(0);
  assert.equal(pickAgain(bill, source), bill);
  assert.equal(source.calls, 64);
});

test("@R31 a source that always gives the same number cannot change a bill whose order it reproduces, and stops at 64 draws", () => {
  const bill = withSpare(S2, random("p2", "p3", "p1"));
  const source = constant(0);
  assert.equal(pickAgain(bill, source), bill);
  assert.equal(source.calls, 64 * 2);
});

test("@R31 the first order that changes the rows is taken, and no number is drawn after it", () => {
  const source = scripted(0.9, 0.9);
  const next = pickAgain(withSpare(S2, random("p2", "p3", "p1")), source);
  assert.deepEqual(next.spare, random("p1", "p2", "p3"));
  assert.equal(source.calls, 2);
});
