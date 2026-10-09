import { test } from "node:test";
import assert from "node:assert/strict";
import { billCharges, computeResult } from "../src/core/result.js";
import { toggleItemPerson } from "../src/core/bill.js";
import {
  buildBill, deepFreeze, S1, S2, S5, E1, E2, E3, I2, I3, I4, MAX_E, MAX_I, D1, D2,
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
  ["item", "10", "6", "100", [], "no-items"],
  ["item", "10", "6", "", [{ price: "", who: [] }], "prices"],
  ["item", "10", "6", "", [{ price: "15.90", who: ["p1"] }, { price: "abc", who: ["p1"] }], "prices"],
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

test("@R23 the MAX-I charges split needs BigInt (a float product is off)", () => {
  // 279999972 x 49999995 is above 2^53, so a float implementation drifts on exactly these weights.
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
