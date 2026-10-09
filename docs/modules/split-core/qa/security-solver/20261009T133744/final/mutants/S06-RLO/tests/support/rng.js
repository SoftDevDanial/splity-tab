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

/** Integer in [min, max], both inclusive. */
export function randomInt(next, min, max) {
  return min + Math.floor(next() * (max - min + 1));
}
