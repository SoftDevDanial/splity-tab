// Seeded generator for tests. A fixed seed keeps a failing sweep reproducible.

/**
 * mulberry32: small, fast and good enough for test data.
 * @param {number} seed
 * @returns {() => number} next float in [0, 1)
 */
export function mulberry32(seed) {
  let state = seed >>> 0;
  return function next() {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * A random source that returns `numbers` in turn and counts its calls, so a test scripts a draw and checks how
 * many numbers it took. A call past the list throws, so a draw that takes more than the script says is red.
 * @returns {(() => number) & { calls: number }}
 */
export function scripted(...numbers) {
  const next = () => {
    if (next.calls >= numbers.length) throw new Error(`scripted source asked for number ${next.calls + 1} of ${numbers.length}`);
    next.calls += 1;
    return numbers[next.calls - 1];
  };
  next.calls = 0;
  return next;
}

/** A source that always returns `value` and counts its calls: the worst case for Pick again (R31). */
export function constant(value) {
  const next = () => {
    next.calls += 1;
    return value;
  };
  next.calls = 0;
  return next;
}

/** Integer in [min, max], both inclusive. */
export function randomInt(next, min, max) {
  return min + Math.floor(next() * (max - min + 1));
}
