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

const weightCases = [
  [986, [2490, 1350, 2100], [414, 224, 348]],
  [10, [0, 1, 1, 1], [0, 4, 3, 3]],
  [0, [5, 7], [0, 0]],
  [249, [0, 1251, 250], [0, 208, 41]],
  [236419679, [314963010, 157876348], [157481505, 78938174]],
];
for (const [amount, weights, expected] of weightCases) {
  test(`@R8 allocateByWeight(${amount}, [${weights}])`, () => {
    const result = allocateByWeight(amount, weights);
    assert.deepEqual(result, expected);
    assert.equal(sum(result), amount);
  });
}

test("@R8 @R23 allocateByWeight stays exact when amount times weight passes 2^53", () => {
  const weights = [49999995, 49999995, ...Array(10).fill(39999996)];
  const expected = [27999998, 27999998, ...Array(6).fill(22399998), ...Array(4).fill(22399997)];
  assert.ok(279999972 * 49999995 > Number.MAX_SAFE_INTEGER);
  assert.deepEqual(allocateByWeight(279999972, weights), expected);
});

test("@R8 a zero weight always gets 0 and a single weight gets everything", () => {
  assert.deepEqual(allocateByWeight(7, [0, 0, 3]), [0, 0, 7]);
  assert.deepEqual(allocateByWeight(7, [4]), [7]);
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
