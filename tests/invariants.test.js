import { test } from "node:test";
import assert from "node:assert/strict";
import { computeResult } from "../src/core/result.js";
import { sparePeople } from "../src/core/bill.js";
import { parseAmount } from "../src/core/money.js";
import { allocateEvenly, allocateByWeight } from "../src/core/allocate.js";
import { mulberry32, randomInt } from "./support/rng.js";

const SEED = 20261008;
const BILL_COUNT = 2000;

const sum = (numbers) => numbers.reduce((total, n) => total + n, 0);

// Hundredths written as text the way a person types them, e.g. 1250 -> "12.50".
const hundredthsText = (n) => `${Math.floor(n / 100)}.${String(n % 100).padStart(2, "0")}`;

function shuffled(next, list) {
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = randomInt(next, 0, i);
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

/** A non-empty random subset of the people, in random tap order. */
function randomTappers(next, people) {
  const chosen = people.filter(() => next() < 0.5).map((p) => p.id);
  if (chosen.length === 0) chosen.push(people[randomInt(next, 0, people.length - 1)].id);
  return shuffled(next, chosen);
}

// One in ten prices sits at the maximum so the sweep also visits the 2^53 corner.
const randomCents = (next) => (next() < 0.1 ? 9999999 : randomInt(next, 1, 9999999));

function randomBill(next, mode) {
  const peopleCount = randomInt(next, 2, 12);
  const itemCount = randomInt(next, 1, 50);
  const people = Array.from({ length: peopleCount }, (_, i) => ({ id: `p${i + 1}`, name: `N${i + 1}` }));
  const items = Array.from({ length: itemCount }, (_, i) => ({
    id: `i${peopleCount + i + 1}`,
    name: "",
    priceText: hundredthsText(randomCents(next)),
    who: randomTappers(next, people),
  }));
  return {
    mode,
    people,
    subtotalText: hundredthsText(randomCents(next)),
    items,
    serviceText: hundredthsText(randomInt(next, 0, 3000)),
    sstText: hundredthsText(randomInt(next, 0, 2000)),
    spare: { rule: "top" },
    nextId: peopleCount + itemCount + 1,
  };
}

function assertSafeNumbers(value, path) {
  if (typeof value === "number") {
    assert.ok(Number.isSafeInteger(value) && value >= 0, `${path} = ${value}`);
  } else if (value !== null && typeof value === "object") {
    for (const [key, inner] of Object.entries(value)) assertSafeNumbers(inner, `${path}.${key}`);
  }
}

/** The three choices every generated bill is worked out with: Top, a person who can take spare sen, a drawn order. */
function spareChoices(next, bill) {
  const eligible = sparePeople(bill);
  return [
    { rule: "top" },
    { rule: "one", personId: eligible[randomInt(next, 0, eligible.length - 1)] },
    { rule: "random", order: shuffled(next, bill.people.map((person) => person.id)) },
  ];
}

const exactFloor = (amount, weight, total) => Number((BigInt(amount) * BigInt(weight)) / BigInt(total));
const priceOf = (item) => parseAmount(item.priceText).cents;

/** Even mode: what each rule promises about the shares (R22), checked against plain arithmetic. */
function assertEvenRule(bill, spare, result, label) {
  const shares = result.rows.map((row) => row.share);
  const { total } = result.charges;
  const floor = Math.floor(total / bill.people.length);
  assert.equal(result.spare.count, total % bill.people.length, `${label} spare count`);
  if (spare.rule === "top") {
    assert.deepEqual(shares, allocateEvenly(total, bill.people.length), `${label} top is the 1.0 split`);
    assert.deepEqual(shares, [...shares].sort((a, b) => b - a), `${label} larger first`);
  } else if (spare.rule === "random") {
    assert.ok(Math.max(...shares) - Math.min(...shares) <= 1, `${label} spread`);
  } else {
    const expected = bill.people.map((person) => (person.id === spare.personId ? floor + result.spare.count : floor));
    assert.deepEqual(shares, expected, `${label} one person takes every spare sen`);
  }
}

/** By-item mode: the items column from plain arithmetic, and under Top and One person the charges column too. */
function assertItemRule(bill, spare, result, label) {
  const floors = bill.people.map(() => 0);
  const topItems = bill.people.map(() => 0);
  let itemSpare = 0;
  for (const item of bill.items) {
    const holders = bill.people.flatMap((person, index) => (item.who.includes(person.id) ? [index] : []));
    const price = priceOf(item);
    const parts = allocateEvenly(price, holders.length);
    holders.forEach((index, k) => {
      floors[index] += Math.floor(price / holders.length);
      topItems[index] += parts[k];
    });
    itemSpare += price % holders.length;
  }
  const items = result.rows.map((row) => row.items);
  const chargesAmount = result.charges.service + result.charges.sst;
  if (spare.rule === "top") {
    assert.deepEqual(items, topItems, `${label} top items are the 1.0 split`);
    assert.deepEqual(result.rows.map((row) => row.charges), allocateByWeight(chargesAmount, items), `${label} top charges`);
  } else if (spare.rule === "one") {
    const chosen = bill.people.findIndex((person) => person.id === spare.personId);
    items.forEach((value, index) => {
      assert.equal(value, index === chosen ? floors[index] + itemSpare : floors[index], `${label} items of ${index}`);
    });
    result.rows.forEach((row, index) => {
      if (index === chosen) return;
      const floor = row.items === 0 ? 0 : exactFloor(chargesAmount, row.items, result.charges.subtotal);
      assert.equal(row.charges, floor, `${label} charges of ${index}`);
    });
  } else {
    items.forEach((value, index) => assert.ok(value >= floors[index], `${label} items of ${index} keep their floor`));
  }
}

test("@R22 generated bills always add up, under every spare rule", () => {
  const next = mulberry32(SEED);
  const seen = { even: 0, item: 0 };
  for (let n = 0; n < BILL_COUNT; n += 1) {
    const mode = n % 2 === 0 ? "even" : "item";
    const bill = randomBill(next, mode);
    for (const spare of spareChoices(next, bill)) {
      const label = `bill ${n} (${mode}, ${bill.people.length} people, ${bill.items.length} items, ${spare.rule})`;
      const result = computeResult({ ...bill, spare });
      assert.equal(result.kind, mode, label);
      seen[mode] += 1;
      assertSafeNumbers(result, label);
      assert.deepEqual(result.spare, { count: result.spare.count, rule: spare.rule, personId: spare.personId ?? null }, label);
      assert.equal(result.rows.length, bill.people.length, label);
      assert.equal(result.check.share, result.charges.total, `${label} check.share`);
      assert.equal(result.rows.reduce((total, row) => total + row.share, 0), result.charges.total, label);

      if (mode === "even") {
        assertEvenRule(bill, spare, result, label);
      } else {
        assert.equal(result.check.items, result.charges.subtotal, `${label} check.items`);
        assert.equal(result.check.charges, result.charges.service + result.charges.sst, `${label} check.charges`);
        for (const row of result.rows) {
          assert.equal(row.share, row.items + row.charges, label);
          if (row.items === 0) assert.equal(row.charges, 0, `${label} zero items pays no charges`);
        }
        assertItemRule(bill, spare, result, label);
      }
    }
  }
  assert.deepEqual(seen, { even: BILL_COUNT * 3 / 2, item: BILL_COUNT * 3 / 2 });
});
