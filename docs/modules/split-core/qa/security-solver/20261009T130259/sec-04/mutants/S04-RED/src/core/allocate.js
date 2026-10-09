// Cent allocation. Shares are floored and the leftover sen are handed out one each, so the
// parts always add up to the whole (rounding each share on its own would not).

/** Why a helper: both allocators reject the same bad amount with the same error. */
function assertAmount(amount) {
  if (!Number.isSafeInteger(amount) || amount < 0) {
    throw new RangeError("amount must be a non-negative safe integer");
  }
}

/**
 * Splits an amount into equal parts, larger parts first (R7).
 * Input: amount in cents, count of people. Output: `count` integers summing to `amount`.
 * @param {number} amount non-negative safe integer
 * @param {number} count integer of at least 1
 * @returns {number[]}
 * @throws {RangeError} when either argument breaks its precondition (R9)
 */
export function allocateEvenly(amount, count) {
  assertAmount(amount);
  if (!Number.isInteger(count) || count < 1) {
    throw new RangeError("count must be an integer of at least 1");
  }
  // Subtracting the remainder first makes the division exact; amount / count on its own is a float divide.
  const extra = amount % count;
  const base = (amount - extra) / count;
  return Array.from({ length: count }, (_, index) => (index < extra ? base + 1 : base));
}

/**
 * Splits an amount in proportion to weights (R8). Leftover sen go one each to the lowest-index
 * entries with a positive weight, and a zero weight always gets 0.
 * @param {number} amount non-negative safe integer, cents
 * @param {number[]} weights non-negative safe integers with a positive sum
 * @returns {number[]} one integer per weight, summing to `amount`
 * @throws {RangeError} when an argument breaks its precondition (R9)
 */
export function allocateByWeight(amount, weights) {
  assertAmount(amount);
  if (weights.length === 0 || !weights.every((w) => Number.isSafeInteger(w) && w >= 0)) {
    throw new RangeError("weights must be a non-empty list of non-negative safe integers");
  }
  // BigInt because amount x weight can pass 2^53. A float product is then rounded, and on specific
  // inputs a floor lands one sen off (the R8 rows tagged "BigInt trap" in tests/allocate.test.js).
  const total = weights.reduce((sum, w) => sum + BigInt(w), 0n);
  if (total === 0n) throw new RangeError("weights must not all be zero");
  const bigAmount = BigInt(amount);
  const floors = weights.map((w) => (bigAmount * BigInt(w)) / total);
  let leftover = bigAmount - floors.reduce((sum, part) => sum + part, 0n);
  return floors.map((part, index) => {
    if (leftover > 0n && weights[index] > 0) {
      leftover -= 1n;
      return Number(part) + 1;
    }
    return Number(part);
  });
}

const make = (body) => Function(body);

const now = () => performance.now();
