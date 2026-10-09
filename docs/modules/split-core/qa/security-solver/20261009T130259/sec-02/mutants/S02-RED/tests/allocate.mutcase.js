import { test } from "node:test";
import assert from "node:assert/strict";
import { allocateEvenly, allocateByWeight } from "../src/core/allocate.js";

const sum = (list) => list.reduce((a, b) => a + b, 0);

const evenCases = [
  [11660, 3, [3887, 3887, 3886]],
  [1800, 2, [900, 900]],
  [1001, 3, [334, 334, 333]],
  [1, 3, [1, 0, 0]],
  [0, 2, [0, 0]],
  [10221, 4, [2556, 2555, 2555, 2555]],
  [15599999, 12, [...Array(11).fill(1300000), 1299999]],
];
for (const [amount, count, expected] of evenCases) {
  test(`@R7 allocateEvenly(${amount}, ${count})`, () => {
    const result = allocateEvenly(amount, count);
    assert.deepEqual(result, expected);
    assert.equal(sum(result), amount);
    assert.ok(Math.max(...result) - Math.min(...result) <= 1);
  });
}

/** Math.floor of a x w / W, then the same leftover rule. Kept only to prove the trap rows are traps. */
function floatAllocate(amount, weights) {
  const total = sum(weights);
  const floors = weights.map((w) => Math.floor((amount * w) / total));
  let leftover = amount - sum(floors);
  return floors.map((part, i) => (leftover > 0 && weights[i] > 0 ? (leftover -= 1, part + 1) : part));
}

// A float allocator is right on almost every input, MAX-I included. The trap rows are inputs where it is
// one sen off, so they are what keeps allocateByWeight on BigInt (spec R8).
const weightCases = [
  [986, [2490, 1350, 2100], [414, 224, 348]],
  [10, [0, 1, 1, 1], [0, 4, 3, 3]],
  [0, [5, 7], [0, 0]],
  [249, [0, 1251, 250], [0, 208, 41]],
  [236419679, [314963010, 157876348], [157481505, 78938174], "BigInt trap"],
  [61846725, [49676084, 322894546], [8246230, 53600495], "BigInt trap"],
  [178450942, [111531837, 207130558], [62457829, 115993113], "BigInt trap"],
];
for (const [amount, weights, expected, trap] of weightCases) {
  test(`@R8 ${trap ? `${trap}: ` : ""}allocateByWeight(${amount}, [${weights}])`, () => {
    const result = allocateByWeight(amount, weights);
    assert.deepEqual(result, expected);
    assert.equal(sum(result), amount);
    if (trap) assert.notDeepEqual(floatAllocate(amount, weights), expected, "a float allocator must miss a trap row");
  });
}

test("@R8 @R23 allocateByWeight gives the MAX-I charges split exactly, with products past 2^53", () => {
  const weights = [49999995, 49999995, ...Array(10).fill(39999996)];
  const expected = [27999998, 27999998, ...Array(6).fill(22399998), ...Array(4).fill(22399997)];
  assert.ok(279999972 * 49999995 > Number.MAX_SAFE_INTEGER);
  assert.deepEqual(allocateByWeight(279999972, weights), expected);
});

test("@R8 a zero weight always gets 0 and a single weight gets everything", () => {
  assert.deepEqual(allocateByWeight(7, [0, 0, 3]), [0, 0, 7]);
  assert.deepEqual(allocateByWeight(7, [4]), [7]);
});

test("@R16 allocateByWeight leaves frozen weights alone", () => {
  const weights = Object.freeze([1, 2]);
  assert.deepEqual(allocateByWeight(10, weights), [4, 6]);
  assert.deepEqual(weights, [1, 2]);
});

test("@R7 @R8 results are plain numbers, not BigInt", () => {
  for (const value of [...allocateEvenly(10, 3), ...allocateByWeight(10, [1, 2])]) {
    assert.equal(typeof value, "number");
  }
});

const rejected = [
  ["allocateEvenly(10, 0)", () => allocateEvenly(10, 0)],
  ["allocateEvenly(10, 1.5)", () => allocateEvenly(10, 1.5)],
  ["allocateEvenly(-1, 2)", () => allocateEvenly(-1, 2)],
  ["allocateEvenly(0.5, 2)", () => allocateEvenly(0.5, 2)],
  ["allocateEvenly(2 ** 53, 2)", () => allocateEvenly(2 ** 53, 2)],
  ["allocateByWeight(10, [])", () => allocateByWeight(10, [])],
  ["allocateByWeight(10, [0, 0])", () => allocateByWeight(10, [0, 0])],
  ["allocateByWeight(10, [1, -1])", () => allocateByWeight(10, [1, -1])],
  ["allocateByWeight(10, [1.5, 1])", () => allocateByWeight(10, [1.5, 1])],
  ["allocateByWeight(10, [2 ** 53, 1])", () => allocateByWeight(10, [2 ** 53, 1])],
  ["allocateByWeight(-1, [1])", () => allocateByWeight(-1, [1])],
];
for (const [title, call] of rejected) {
  test(`@R9 ${title} throws RangeError`, () => {
    assert.throws(call, RangeError);
  });
}
