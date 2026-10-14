import { test } from "node:test";
import assert from "node:assert/strict";
import {
  parseAmount, parseRate, formatMoney, formatRate, formatAmount, AMOUNT_MIN_CENTS, AMOUNT_MAX_CENTS,
} from "../src/core/money.js";
import { mulberry32, randomInt } from "./support/rng.js";

const INVALID = { ok: false, empty: false };
const EMPTY = { ok: false, empty: true };

test("@R1 amount bounds are exported as the contract says", () => {
  assert.equal(AMOUNT_MIN_CENTS, 1);
  assert.equal(AMOUNT_MAX_CENTS, 9999999);
});

const validAmounts = [
  ["12", 1200],
  ["12.5", 1250],
  ["12.50", 1250],
  ["0.01", 1],
  ["99999.99", 9999999],
  ["1.15", 115],
  ["4.35", 435],
  ["0.29", 29],
  [" 12.50 ", 1250],
  ["007", 700],
  ["12.", 1200],
  ["0000000012.50", 1250],
];
for (const [text, cents] of validAmounts) {
  test(`@R1 parseAmount(${JSON.stringify(text)}) is ${cents} cents`, () => {
    assert.deepEqual(parseAmount(text), { ok: true, cents });
  });
}

const invalidAmounts = [
  "0", "0.00", "100000", "99999.991", "12.505", "13.505", "-5", "+5", "1,000", ".5",
  "1e3", "0x10", "Infinity", "NaN", "abc", "12 50", "１２",
];
for (const text of invalidAmounts) {
  test(`@R1 @R2 parseAmount(${JSON.stringify(text)}) is invalid, not empty`, () => {
    assert.deepEqual(parseAmount(text), INVALID);
  });
}

test("@R1 @R2 a 401-character amount is invalid and does not throw", () => {
  const text = "1" + "0".repeat(400);
  assert.deepEqual(parseAmount(text), INVALID);
  assert.deepEqual(parseRate(text, 30), INVALID);
});

/** Runs `read` with a spy on the global Number, so a test can see which strings were converted. */
function conversionsDuring(read) {
  const converted = [];
  const realNumber = globalThis.Number;
  globalThis.Number = new Proxy(realNumber, {
    apply(target, self, args) {
      converted.push(args[0]);
      return Reflect.apply(target, self, args);
    },
  });
  try {
    return { result: read(), converted };
  } finally {
    globalThis.Number = realNumber;
  }
}

// The cap never changes a result (a longer whole part is above the ceiling anyway), so only a spy on
// the conversion can tell whether it ran first. The positive controls prove the spy is not blind.
test("@R1 @R3 a whole part longer than the ceiling's is refused before any numeric conversion", () => {
  const tooLong = [
    () => parseAmount("1" + "0".repeat(400)),
    () => parseAmount("100000"),
    () => parseRate("100", 30),
  ];
  for (const read of tooLong) {
    const { result, converted } = conversionsDuring(read);
    assert.deepEqual(result, INVALID);
    assert.deepEqual(converted, []);
  }
  assert.ok(conversionsDuring(() => parseAmount("99999.99")).converted.includes("99999"));
  assert.ok(conversionsDuring(() => parseRate("30", 30)).converted.includes("30"));
});

for (const text of ["", "   "]) {
  test(`@R2 ${JSON.stringify(text)} is reported as empty by both parsers`, () => {
    assert.deepEqual(parseAmount(text), EMPTY);
    assert.deepEqual(parseRate(text, 30), EMPTY);
  });
}

test("@R2 the parsers never throw and always return a well-formed result", () => {
  const alphabet = [..."0123456789.,-+ eE%abc１"];
  const next = mulberry32(20261008);
  for (let n = 0; n < 500; n += 1) {
    const length = randomInt(next, 0, 12);
    let text = "";
    for (let k = 0; k < length; k += 1) text += alphabet[randomInt(next, 0, alphabet.length - 1)];
    const amount = parseAmount(text);
    const rate = parseRate(text, 30);
    if (amount.ok) {
      assert.deepEqual(Object.keys(amount), ["ok", "cents"], text);
      assert.ok(Number.isSafeInteger(amount.cents) && amount.cents >= 1 && amount.cents <= 9999999, text);
    } else {
      assert.deepEqual(Object.keys(amount), ["ok", "empty"], text);
      assert.equal(typeof amount.empty, "boolean", text);
    }
    if (rate.ok) {
      assert.deepEqual(Object.keys(rate), ["ok", "bp"], text);
      assert.ok(Number.isSafeInteger(rate.bp) && rate.bp >= 0 && rate.bp <= 3000, text);
    } else {
      assert.deepEqual(Object.keys(rate), ["ok", "empty"], text);
      assert.equal(typeof rate.empty, "boolean", text);
    }
  }
});

const validRates = [
  ["0", 30, 0],
  ["10", 30, 1000],
  ["6", 20, 600],
  ["6.5", 20, 650],
  ["6.25", 20, 625],
  ["30", 30, 3000],
  ["30.00", 30, 3000],
  ["20", 20, 2000],
  ["0.01", 30, 1],
  ["6.", 20, 600],
  ["06", 20, 600],
];
for (const [text, max, bp] of validRates) {
  test(`@R3 parseRate(${JSON.stringify(text)}, ${max}) is ${bp} bp`, () => {
    assert.deepEqual(parseRate(text, max), { ok: true, bp });
  });
}

const invalidRates = [
  ["30.01", 30],
  ["20.01", 20],
  ["25", 20],
  ["-1", 30],
  ["6.255", 20],
  ["10%", 30],
];
for (const [text, max] of invalidRates) {
  test(`@R3 parseRate(${JSON.stringify(text)}, ${max}) is invalid`, () => {
    assert.deepEqual(parseRate(text, max), INVALID);
  });
}

const money = [
  [0, "RM 0.00"],
  [1, "RM 0.01"],
  [10, "RM 0.10"],
  [100, "RM 1.00"],
  [3887, "RM 38.87"],
  [11660, "RM 116.60"],
  [99999, "RM 999.99"],
  [100000, "RM 1,000.00"],
  [119387, "RM 1,193.87"],
  [15599999, "RM 155,999.99"],
  [779999922, "RM 7,799,999.22"],
];
for (const [cents, text] of money) {
  test(`@R4 formatMoney(${cents}) is ${JSON.stringify(text)}`, () => {
    assert.equal(formatMoney(cents), text);
  });
}

const amounts = [
  [0, "0.00"],
  [2490, "24.90"],
  [98940, "989.40"],
  [99999, "999.99"],
  [100000, "1,000.00"],
  [102390, "1,023.90"],
  [119387, "1,193.87"],
  [100000000, "1,000,000.00"],
  [779999922, "7,799,999.22"],
];
for (const [cents, text] of amounts) {
  test(`@R34 formatAmount(${cents}) is ${JSON.stringify(text)}`, () => {
    assert.equal(formatAmount(cents), text);
  });
}

test("@R34 @R4 formatMoney is RM, a space and formatAmount, for 1000 seeded values", () => {
  const next = mulberry32(20261013);
  for (let n = 0; n < 1000; n += 1) {
    const cents = randomInt(next, 0, 779999922);
    assert.equal(formatMoney(cents), `RM ${formatAmount(cents)}`, String(cents));
  }
});

const rates = [
  [0, "0%"],
  [600, "6%"],
  [1000, "10%"],
  [650, "6.5%"],
  [625, "6.25%"],
  [605, "6.05%"],
  [3000, "30%"],
];
for (const [bp, text] of rates) {
  test(`@R5 formatRate(${bp}) is ${JSON.stringify(text)}`, () => {
    assert.equal(formatRate(bp), text);
  });
}

test("@R5 a typed 10.00 round-trips to 10%", () => {
  assert.equal(formatRate(parseRate("10.00", 30).bp), "10%");
});
