import { test } from "node:test";
import assert from "node:assert/strict";
import { billCharges, computeResult } from "../src/core/result.js";
import { allocateEvenly, allocateByWeight } from "../src/core/allocate.js";
import { toggleItemPerson, setMode, setSubtotalText } from "../src/core/bill.js";
import {
  buildBill, deepFreeze, withSpare, S1, S2, S5, W1, E1, E2, E3, I2, I3, I4, MAX_E, MAX_I, D1, D2,
} from "./support/bills.js";

const charges = (subtotal, serviceBp, service, sstBp, sstBase, sst, total) => (
  { subtotal, serviceBp, service, sstBp, sstBase, sst, total }
);
const repeat = (value, times) => Array(times).fill(value);

// subtotal, serviceBp, sstBp, service, sstBase, sst, total
const chargeRows = [
  [10000, 1000, 600, 1000, 11000, 660, 11660],
  [5940, 1000, 600, 594, 6534, 392, 6926],
  [8765, 1000, 600, 877, 9642, 579, 10221],
  [5, 1000, 0, 1, 6, 0, 6],
  [25, 1000, 0, 3, 28, 0, 28],
  [4, 1000, 0, 0, 4, 0, 4],
  [1000, 0, 0, 0, 1000, 0, 1000],
  [5000, 1250, 625, 625, 5625, 352, 5977],
  [9999999, 3000, 2000, 3000000, 12999999, 2600000, 15599999],
  [499999950, 3000, 2000, 149999985, 649999935, 129999987, 779999922],
];
for (const [subtotal, sbp, tbp, service, base, sst, total] of chargeRows) {
  test(`@R6 billCharges(${subtotal}, ${sbp}, ${tbp}) totals ${total}`, () => {
    assert.deepEqual(billCharges(subtotal, sbp, tbp), charges(subtotal, sbp, service, tbp, base, sst, total));
  });
}

const blockedRows = [
  ["even", "", "6", "100", [], "rates"],
  ["even", "31", "6", "", [], "rates"],
  ["item", "10", "20.01", "", [], "rates"],
  ["even", "10", "6", "", [], "subtotal"],
  ["even", "10", "6", "0", [], "subtotal"],
  ["even", "10", "6", "12.505", [], "subtotal"],
  ["item", "10", "6", "100", [], "no-prices"],
  ["item", "10", "6", "", [{ price: "", who: [] }], "no-prices"],
  ["item", "10", "6", "", [{ price: "abc", who: ["p1"] }, { price: "", who: [] }], "no-prices"],
  ["item", "10", "6", "", [{ price: "15.90", who: ["p1"] }, { price: "abc", who: ["p1"] }], "prices"],
  ["item", "10", "6", "", [{ price: "15.90", who: ["p1"] }, { price: "", who: [] }], "prices"],
  ["item", "", "6", "", [{ price: "15.90", who: ["p1"] }], "rates"],
];
blockedRows.forEach(([mode, service, sst, subtotal, items, reason], n) => {
  test(`@R18 blocking row ${n + 1} is "${reason}"`, () => {
    const bill = buildBill({ mode, service, sst, subtotal, items });
    assert.deepEqual(computeResult(bill), { kind: "blocked", reason });
  });
});

test("@R18 rates outrank every other rule and a rate of 0 is not a block", () => {
  assert.equal(computeResult(buildBill({ mode: "item", service: "bad", items: [] })).reason, "rates");
  assert.equal(computeResult(buildBill({ subtotal: "10", service: "0", sst: "0" })).kind, "even");
});

test("@R18 @R20 even mode ignores broken items", () => {
  const bill = buildBill({
    names: ["Aisyah", "Ben", "Chen"], subtotal: "100.00", items: [{ price: "abc", who: [] }],
  });
  const result = computeResult(bill);
  assert.equal(result.kind, "even");
  assert.deepEqual(result.rows.map((r) => r.share), [3887, 3887, 3886]);
});

test("@R18 @R21 by-item mode ignores a broken subtotal", () => {
  const result = computeResult(buildBill({
    mode: "item", names: ["Aisyah", "Ben"], subtotal: "abc", items: [{ price: "10.00", who: ["p1"] }],
  }));
  assert.equal(result.kind, "item");
});

test("@R19 unassigned items are counted and the charges are still known", () => {
  const result = computeResult(S5);
  assert.equal(result.kind, "unassigned");
  assert.equal(result.count, 1);
  assert.deepEqual(result.charges, charges(5940, 1000, 594, 600, 6534, 392, 6926));
});

test("@R19 two unassigned items give a count of 2", () => {
  const bill = toggleItemPerson(toggleItemPerson(S1, "i5", "p2"), "i6", "p3");
  const result = computeResult(bill);
  assert.equal(result.kind, "unassigned");
  assert.equal(result.count, 2);
});

const evenCases = [
  ["S2", S2, ["Aisyah", "Ben", "Chen"], charges(10000, 1000, 1000, 600, 11000, 660, 11660), [3887, 3887, 3886]],
  ["E1", E1, ["A", "B", "C", "D"], charges(8765, 1000, 877, 600, 9642, 579, 10221), [2556, 2555, 2555, 2555]],
  ["E2", E2, ["Aisyah", "Ben", "Chen"], charges(1000, 0, 0, 0, 1000, 0, 1000), [334, 333, 333]],
  ["E3", E3, ["Person 1", "Person 2"], charges(5000, 1250, 625, 625, 5625, 352, 5977), [2989, 2988]],
  [
    "MAX-E", MAX_E, Array.from({ length: 12 }, (_, i) => `Person ${i + 1}`),
    charges(9999999, 3000, 3000000, 2000, 12999999, 2600000, 15599999),
    [...repeat(1300000, 11), 1299999],
  ],
];
for (const [title, bill, names, expectedCharges, shares] of evenCases) {
  test(`@R20 @R23 even result for ${title}`, () => {
    const result = computeResult(bill);
    assert.equal(result.kind, "even");
    assert.deepEqual(result.charges, expectedCharges);
    assert.deepEqual(result.rows, names.map((name, i) => ({ name, share: shares[i] })));
    assert.deepEqual(result.check, { share: expectedCharges.total });
  });
}

// rows are [name, items, charges, share]
const itemCases = [
  [
    "S1", S1, charges(5940, 1000, 594, 600, 6534, 392, 6926),
    [["Aisyah", 2490, 414, 2904], ["Ben", 1350, 224, 1574], ["Chen", 2100, 348, 2448]],
    { items: 5940, charges: 986, share: 6926 },
  ],
  [
    "I2", I2, charges(1501, 1000, 150, 600, 1651, 99, 1750),
    [["Aisyah", 0, 0, 0], ["Ben", 1251, 208, 1459], ["Chen", 250, 41, 291]],
    { items: 1501, charges: 249, share: 1750 },
  ],
  [
    "I3", I3, charges(1001, 1000, 100, 600, 1101, 66, 1167),
    [["Aisyah", 501, 84, 585], ["Ben", 0, 0, 0], ["Chen", 500, 82, 582]],
    { items: 1001, charges: 166, share: 1167 },
  ],
  [
    "I4", I4, charges(10, 0, 0, 0, 10, 0, 10),
    [["Aisyah", 4, 0, 4], ["Ben", 3, 0, 3], ["Chen", 3, 0, 3]],
    { items: 10, charges: 0, share: 10 },
  ],
  [
    "MAX-I", MAX_I, charges(499999950, 3000, 149999985, 2000, 649999935, 129999987, 779999922),
    Array.from({ length: 12 }, (_, i) => (i < 2
      ? [`Person ${i + 1}`, 49999995, 27999998, 77999993]
      : i < 8
        ? [`Person ${i + 1}`, 39999996, 22399998, 62399994]
        : [`Person ${i + 1}`, 39999996, 22399997, 62399993])),
    { items: 499999950, charges: 279999972, share: 779999922 },
  ],
];
for (const [title, bill, expectedCharges, rows, check] of itemCases) {
  test(`@R21 @R23 by-item result for ${title}`, () => {
    const result = computeResult(bill);
    assert.equal(result.kind, "item");
    assert.deepEqual(result.charges, expectedCharges);
    assert.deepEqual(result.rows, rows.map(([name, items, chargePart, share]) => (
      { name, items, charges: chargePart, share }
    )));
    assert.deepEqual(result.check, check);
  });
}

test("@R21 a shared item's leftover sen follow the people list, not the tap order", () => {
  assert.deepEqual(I3.items[0].who, ["p3", "p1"]);
  const rows = computeResult(I3).rows;
  assert.equal(rows[0].items, 501);
  assert.equal(rows[2].items, 500);
});

test("@R21 a person on no item gets a row of zeros", () => {
  const row = computeResult(I2).rows[0];
  assert.deepEqual(row, { name: "Aisyah", items: 0, charges: 0, share: 0 });
});

test("@R23 MAX-I charges are exact at the bound", () => {
  assert.ok(279999972 * 49999995 > Number.MAX_SAFE_INTEGER);
  const rows = computeResult(MAX_I).rows;
  assert.equal(rows[0].charges, 27999998);
  assert.equal(rows[11].charges, 22399997);
});

test("@R26 D1: two people called Ben give two even rows", () => {
  const result = computeResult(D1);
  assert.equal(result.kind, "even");
  assert.deepEqual(result.rows, [
    { name: "Ben", share: 3887 }, { name: "Ben", share: 3887 }, { name: "Chen", share: 3886 },
  ]);
  assert.deepEqual(result.check, { share: 11660 });
});

test("@R26 D2: two people called Ben give two by-item rows, only the tapped one pays", () => {
  const result = computeResult(D2);
  assert.equal(result.kind, "item");
  assert.deepEqual(result.charges, charges(1000, 1000, 100, 600, 1100, 66, 1166));
  assert.deepEqual(result.rows, [
    { name: "Ben", items: 0, charges: 0, share: 0 },
    { name: "Ben", items: 1000, charges: 166, share: 1166 },
    { name: "Chen", items: 0, charges: 0, share: 0 },
  ]);
  assert.deepEqual(result.check, { items: 1000, charges: 166, share: 1166 });
});

test("@R16 computeResult leaves a deep-frozen bill alone", () => {
  for (const bill of [S1, S2, S5]) {
    const frozen = deepFreeze(structuredClone(bill));
    assert.doesNotThrow(() => computeResult(frozen));
    assert.deepEqual(computeResult(frozen), computeResult(bill));
  }
});

// ---- Spare sen (R32, R33) ----
const TOP = { rule: "top" };
const one = (personId) => ({ rule: "one", personId });
const random = (...order) => ({ rule: "random", order });
// An even row is its share, a by-item row is [items, charges, share].
const shape = (row) => ("items" in row ? [row.items, row.charges, row.share] : row.share);

// title, bill, spare choice, expected rows, spare.count (the R32 table of spec.md)
const spareTable = [
  ["S2", S2, TOP, [3887, 3887, 3886], 2],
  ["S2", S2, one("p2"), [3886, 3888, 3886], 2],
  ["S2", S2, random("p2", "p3", "p1"), [3886, 3887, 3887], 2],
  ["S1", S1, TOP, [[2490, 414, 2904], [1350, 224, 1574], [2100, 348, 2448]], 1],
  ["S1", S1, one("p2"), [[2490, 413, 2903], [1350, 225, 1575], [2100, 348, 2448]], 1],
  ["S1", S1, random("p3", "p1", "p2"), [[2490, 413, 2903], [1350, 224, 1574], [2100, 349, 2449]], 1],
  ["I3", I3, TOP, [[501, 84, 585], [0, 0, 0], [500, 82, 582]], 2],
  ["I3", I3, one("p3"), [[500, 82, 582], [0, 0, 0], [501, 84, 585]], 2],
  ["I3", I3, random("p2", "p3", "p1"), [[500, 83, 583], [0, 0, 0], [501, 83, 584]], 2],
  ["W1", W1, TOP, [[98940, 16425, 115365], [1350, 224, 1574], [2100, 348, 2448]], 1],
];
for (const [title, bill, spare, rows, count] of spareTable) {
  test(`@R32 @R20 @R21 ${title} with spare ${JSON.stringify(spare)} gives ${JSON.stringify(rows)} and ${count} spare sen`, () => {
    const result = computeResult(withSpare(bill, spare));
    assert.deepEqual(result.rows.map(shape), rows);
    assert.equal(result.spare?.count, count);
    assert.equal(result.check.share, result.charges.total);
  });
}

test("@R32 Top of the list leaves every 1.0 result as it was (the allocators are the reference)", () => {
  assert.deepEqual(computeResult(S2).rows.map((row) => row.share), allocateEvenly(11660, 3));
  assert.deepEqual(computeResult(S1).rows.map((row) => row.charges), allocateByWeight(986, [2490, 1350, 2100]));
  assert.deepEqual(computeResult(I2).rows.map((row) => row.charges), allocateByWeight(249, [0, 1251, 250]));
});

test("@R32 One person also takes the spare sen of an item they did not have", () => {
  const bill = buildBill({
    mode: "item", names: ["Aisyah", "Ben", "Chen"], service: "0", sst: "0",
    items: [{ price: "0.01", who: ["p1", "p2"] }, { price: "1.00", who: ["p3"] }],
  });
  assert.deepEqual(computeResult(withSpare(bill, TOP)).rows.map(shape), [[1, 0, 1], [0, 0, 0], [100, 0, 100]]);
  const result = computeResult(withSpare(bill, one("p3")));
  assert.deepEqual(result.rows.map(shape), [[0, 0, 0], [0, 0, 0], [101, 0, 101]]);
  assert.equal(result.spare?.count, 1);
});

test("@R32 At random walks the drawn order once across the whole bill and wraps round its end", () => {
  const bill = buildBill({
    mode: "item", names: ["Aisyah", "Ben", "Chen"], service: "0", sst: "0",
    items: [0, 1, 2].map(() => ({ price: "0.01", who: ["p1", "p3"] })),
  });
  // Item 1 goes to p1 (cursor on p2), item 2 skips p2 for p3 (cursor wraps to p1), item 3 goes to p1.
  const result = computeResult(withSpare(bill, random("p1", "p2", "p3")));
  assert.deepEqual(result.rows.map(shape), [[2, 0, 2], [0, 0, 0], [1, 0, 1]]);
  assert.equal(result.spare?.count, 3);
});

test("@R32 @R33 One person falls back to Top of the list while the chosen person has nothing, and the choice is kept", () => {
  const chosen = withSpare(I2, one("p1"));
  const result = computeResult(chosen);
  assert.deepEqual(result.rows, computeResult(I2).rows);
  assert.deepEqual(result.spare, { count: 2, rule: "top", personId: null });
  assert.deepEqual(chosen.spare, one("p1"));
  const even = computeResult(setMode(setSubtotalText(chosen, "100.00"), "even"));
  assert.deepEqual(even.rows.map(shape), [3888, 3886, 3886]);
  assert.deepEqual(even.spare, { count: 2, rule: "one", personId: "p1" });
});

const namedRule = [
  ["S2", S2, TOP, { count: 2, rule: "top", personId: null }],
  ["S2", S2, one("p2"), { count: 2, rule: "one", personId: "p2" }],
  ["S2", S2, random("p2", "p3", "p1"), { count: 2, rule: "random", personId: null }],
  ["E2", E2, TOP, { count: 1, rule: "top", personId: null }],
];
for (const [title, bill, spare, expected] of namedRule) {
  test(`@R33 the result of ${title} with spare ${JSON.stringify(spare)} names ${JSON.stringify(expected)}`, () => {
    assert.deepEqual(computeResult(withSpare(bill, spare)).spare, expected);
  });
}

test("@R33 a blocked result and an unassigned result carry no spare", () => {
  for (const result of [computeResult(buildBill({ subtotal: "" })), computeResult(S5)]) {
    assert.equal(Object.hasOwn(result, "spare"), false, result.kind);
  }
});
