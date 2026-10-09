import { test } from "node:test";
import assert from "node:assert/strict";
import { computeResult } from "../src/core/result.js";
import { mulberry32, randomInt } from "./support/rng.js";

const SEED = 20261008;
const BILL_COUNT = 2000;

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

test("@R22 generated bills always add up", () => {
  const next = mulberry32(SEED);
  const seen = { even: 0, item: 0 };
  for (let n = 0; n < BILL_COUNT; n += 1) {
    const mode = n % 2 === 0 ? "even" : "item";
    const bill = randomBill(next, mode);
    const label = `bill ${n} (${mode}, ${bill.people.length} people, ${bill.items.length} items)`;
    const result = computeResult(bill);
    assert.equal(result.kind, mode, label);
    seen[mode] += 1;
    assertSafeNumbers(result, label);
    assert.equal(result.rows.length, bill.people.length, label);
    assert.equal(result.check.share, result.charges.total, `${label} check.share`);
    assert.equal(result.rows.reduce((total, row) => total + row.share, 0), result.charges.total, label);

    if (mode === "even") {
      const shares = result.rows.map((row) => row.share);
      assert.ok(Math.max(...shares) - Math.min(...shares) <= 1, `${label} spread`);
      assert.deepEqual(shares, [...shares].sort((a, b) => b - a), `${label} larger first`);
    } else {
      assert.equal(result.check.items, result.charges.subtotal, `${label} check.items`);
      assert.equal(result.check.charges, result.charges.service + result.charges.sst, `${label} check.charges`);
      for (const row of result.rows) {
        assert.equal(row.share, row.items + row.charges, label);
        if (row.items === 0) assert.equal(row.charges, 0, `${label} zero items pays no charges`);
      }
    }
  }
  assert.deepEqual(seen, { even: BILL_COUNT / 2, item: BILL_COUNT / 2 });
});
