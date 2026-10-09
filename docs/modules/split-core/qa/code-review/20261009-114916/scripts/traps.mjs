// Finds in-bounds allocateByWeight inputs where a float allocator (Math.floor(a * w / W) then the same
// leftover rule) disagrees with the exact BigInt result. Deterministic (mulberry32, fixed seed).
import { pathToFileURL } from "node:url";
const root = process.argv[2];
const { allocateByWeight } = await import(pathToFileURL(`${root}/src/core/allocate.js`).href);
const { mulberry32, randomInt } = await import(pathToFileURL(`${root}/tests/support/rng.js`).href);

const floatAlloc = (amount, weights) => {
  const W = weights.reduce((a, b) => a + b, 0);
  const floors = weights.map((w) => Math.floor((amount * w) / W));
  let left = amount - floors.reduce((a, b) => a + b, 0);
  return floors.map((f, i) => (left > 0 && weights[i] > 0 ? (left--, f + 1) : f));
};

const next = mulberry32(7);
const found = [];
let tries = 0;
while (found.length < 4 && tries < 2_000_000) {
  tries += 1;
  const amount = randomInt(next, 100_000_000, 279_999_972);
  const total = randomInt(next, 300_000_000, 499_999_950);
  const first = randomInt(next, 1, total - 1);
  const weights = [first, total - first];
  const exact = allocateByWeight(amount, weights);
  const naive = floatAlloc(amount, weights);
  if (exact[0] !== naive[0]) found.push({ amount, weights, exact, float: naive });
}
console.log(JSON.stringify({ tries, found }, null, 1));
