// P04e. Where billCharges (applyRate, Number maths) stops being exact, with non-round subtotals,
// against the reachable maximum subtotal 50 x 9,999,999 = 499,999,950.
import { billCharges } from "../../../../../../../src/core/result.js";
import { rng, randInt } from "./fixtures.mjs";

const half = (n) => (n + 5000n) / 10000n;
/** "exact", "inexact" (wrong integer) or "non-integer" (a fraction escaped applyRate). */
const verdict = (sub, s, t) => {
  const c = billCharges(sub, s, t);
  if (![c.service, c.sst, c.total].every(Number.isInteger)) return ["non-integer", c];
  const service = half(BigInt(sub) * BigInt(s));
  const sst = half((BigInt(sub) + service) * BigInt(t));
  const ok = BigInt(c.service) === service && BigInt(c.sst) === sst && BigInt(c.total) === BigInt(sub) + service + sst;
  return [ok ? "exact" : "inexact", c];
};
const r = rng(7);
let reachableBad = 0;
for (let n = 0; n < 1000000; n += 1) {
  const sub = randInt(r, 1, 499999950);
  if (verdict(sub, randInt(r, 0, 3000), randInt(r, 0, 2000))[0] !== "exact") reachableBad += 1;
}
console.log(`reachable range (1..499999950), 1,000,000 random subtotals and rates: not exact ${reachableBad}`);
for (const sub of [499999950, 499999949]) console.log(`subtotal ${sub} at 3000/2000: ${verdict(sub, 3000, 2000)[0]}`);

// The smallest decade where a random non-round subtotal stops being exact at 30% and 20%.
for (let e = 9; e <= 15; e += 1) {
  const counts = { exact: 0, inexact: 0, "non-integer": 0 };
  let example = null;
  for (let n = 0; n < 20000; n += 1) {
    const sub = Math.floor(10 ** e * (1 + r() * 8.9)) + 1;
    const [v, c] = verdict(sub, 3000, 2000);
    counts[v] += 1;
    if (v !== "exact") example ??= `${sub} gives service ${c.service}, total ${c.total}`;
  }
  console.log(`subtotals in [1e${e}, 1e${e + 1}) (about ${(10 ** e / 9999999).toExponential(1)}+ max-price items): ${JSON.stringify(counts)}${example ? `; e.g. ${example}` : ""}`);
}
