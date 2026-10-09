// P04. Precision near the ceilings: exhaustive parse and format over every valid amount, every rate,
// and allocateByWeight / allocateEvenly near Number.MAX_SAFE_INTEGER against BigInt.
import { parseAmount, parseRate, formatMoney, formatRate } from "../../../../../../../src/core/money.js";
import { allocateByWeight, allocateEvenly } from "../../../../../../../src/core/allocate.js";
import { billCharges } from "../../../../../../../src/core/result.js";
import { rng, randInt } from "./fixtures.mjs";

let bad = 0;
const note = (ok, msg) => { if (!ok) bad += 1; console.log(`${ok ? "OK  " : "FAIL"} ${msg}`); };

// P04a. Every amount 0.01 to 99999.99 in every accepted spelling, and the format round trip.
let amountBad = 0, roundBad = 0;
for (let c = 1; c <= 9999999; c += 1) {
  const w = (c - (c % 100)) / 100, f = c % 100;
  const ff = String(f).padStart(2, "0");
  const forms = [`${w}.${ff}`];
  if (f % 10 === 0) forms.push(`${w}.${ff[0]}`);
  if (f === 0) forms.push(`${w}`, `${w}.`);
  for (const t of forms) { const p = parseAmount(t); if (!p.ok || p.cents !== c) amountBad += 1; }
  const back = parseAmount(formatMoney(c).slice(3));
  if (!back.ok || back.cents !== c) roundBad += 1;
}
note(amountBad === 0, `parseAmount exact on all 9,999,999 amounts in every spelling (mismatches ${amountBad})`);
note(roundBad === 0, `parseAmount(formatMoney(c)) === c for every valid c (mismatches ${roundBad})`);
note(!parseAmount("100000.00").ok && !parseAmount("99999.991").ok && !parseAmount("0.00").ok, "just past each amount bound is invalid");

// P04b. Every rate 0.00 to max, and max + 0.01, for both ceilings.
let rateBad = 0;
for (const max of [30, 20]) {
  for (let bp = 0; bp <= max * 100; bp += 1) {
    const t = `${(bp - (bp % 100)) / 100}.${String(bp % 100).padStart(2, "0")}`;
    const p = parseRate(t, max);
    if (!p.ok || p.bp !== bp) rateBad += 1;
    const f = parseRate(formatRate(bp).slice(0, -1), max);
    if (!f.ok || f.bp !== bp) rateBad += 1;
  }
  if (parseRate(`${max}.01`, max).ok) rateBad += 1;
}
note(rateBad === 0, `parseRate and formatRate exact over 0..3000 and 0..2000 bp, and max+0.01 refused (mismatches ${rateBad})`);

// P04c. allocateByWeight near the safe-integer ceiling against BigInt.
const MAX = Number.MAX_SAFE_INTEGER;
const r = rng(53);
const big = () => MAX - randInt(r, 0, 1e6);
function refWeight(a, w) {
  const A = BigInt(a), W = w.reduce((s, x) => s + BigInt(x), 0n);
  const f = w.map((x) => (A * BigInt(x)) / W);
  let left = A - f.reduce((s, x) => s + x, 0n);
  return f.map((x, i) => (left > 0n && w[i] > 0 ? (left -= 1n, x + 1n) : x)).map(Number);
}
let weightBad = 0;
for (let n = 0; n < 200000; n += 1) {
  const a = n % 3 === 0 ? big() : randInt(r, 0, 1e9) * randInt(r, 1, 9e6);
  const w = Array.from({ length: randInt(r, 1, 12) }, () => (r() < 0.2 ? 0 : r() < 0.5 ? big() : randInt(r, 1, 1e9)));
  if (w.every((x) => x === 0)) w[0] = 1;
  const got = allocateByWeight(a, w);
  const want = refWeight(a, w);
  const sum = got.reduce((s, x) => s + BigInt(x), 0n);
  if (JSON.stringify(got) !== JSON.stringify(want) || sum !== BigInt(a) || !got.every(Number.isSafeInteger)) weightBad += 1;
}
note(weightBad === 0, `allocateByWeight equals BigInt on 200000 inputs with amounts and weights up to 2^53 - 1 (mismatches ${weightBad})`);
const twelveMax = allocateByWeight(MAX, Array(12).fill(MAX));
note(twelveMax.reduce((s, x) => s + BigInt(x), 0n) === BigInt(MAX), `weights summing past 2^53 (12 x MAX) still add up: ${JSON.stringify(twelveMax.slice(0, 2))}...`);

// P04d. allocateEvenly near the ceiling.
let evenBad = 0;
for (let n = 0; n < 200000; n += 1) {
  const a = n % 2 ? big() : randInt(r, 0, 1e9) * randInt(r, 1, 9e6);
  const k = randInt(r, 1, 100);
  const got = allocateEvenly(a, k);
  const sum = got.reduce((s, x) => s + BigInt(x), 0n);
  const base = BigInt(a) / BigInt(k);
  if (sum !== BigInt(a) || !got.every((x, i) => BigInt(x) === base + (BigInt(i) < BigInt(a) % BigInt(k) ? 1n : 0n))) evenBad += 1;
}
note(evenBad === 0, `allocateEvenly exact on 200000 inputs up to 2^53 - 1 (mismatches ${evenBad})`);
for (const [title, f] of [
  ["allocateEvenly(2^53, 2)", () => allocateEvenly(2 ** 53, 2)],
  ["allocateByWeight(2^53, [1])", () => allocateByWeight(2 ** 53, [1])],
  ["allocateByWeight(1, [2^53])", () => allocateByWeight(1, [2 ** 53])],
  ["allocateByWeight(1, [NaN])", () => allocateByWeight(1, [NaN])],
  ["allocateEvenly(1, Infinity)", () => allocateEvenly(1, Infinity)],
  ["allocateByWeight(1, [1n])", () => allocateByWeight(1, [1n])],
]) {
  let threw = "";
  try { f(); } catch (e) { threw = e.constructor.name; }
  note(threw === "RangeError", `${title} throws ${threw || "nothing"}`);
}
const sparse = [1, , 2];
let sparseOut;
try { sparseOut = allocateByWeight(10, sparse); } catch (e) { sparseOut = e.constructor.name; }
console.log(`INFO allocateByWeight(10, [1, <hole>, 2]) gives ${JSON.stringify(sparseOut)} with length ${sparseOut.length} (holes skip every()/map(); not reachable from computeResult, whose weights come from Array.map)`);

// P04e. Where Number stops being exact in billCharges (applyRate), versus the reachable maximum.
const half = (n) => (n + 5000n) / 10000n;
let firstBadSubtotal = null;
for (const sub of [499999950, 1e12, 3e12, 3.0024e12, 3.1e12, 1e13, 1e14]) {
  const c = billCharges(sub, 3000, 2000);
  const service = half(BigInt(sub) * 3000n), sst = half((BigInt(sub) + service) * 2000n);
  const exact = BigInt(c.service) === service && BigInt(c.sst) === sst && Number.isSafeInteger(c.total);
  if (!exact && firstBadSubtotal === null) firstBadSubtotal = sub;
  console.log(`INFO billCharges(${sub}, 3000, 2000) exact=${exact} total=${c.total}`);
}
console.log(`INFO reachable subtotal maximum is 50 x 9999999 = 499999950. First inexact subtotal tried: ${firstBadSubtotal} (needs about ${Math.ceil(Number(firstBadSubtotal) / 9999999)} max-price items)`);

console.log(`\nP04 RESULT: ${bad === 0 ? "PASS" : "FAIL"} (failures ${bad})`);
