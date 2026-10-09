// P08. Money that does not add up: computeResult against an independent BigInt reference, seeded.
// The reference shares no code with src/core: its own grammar scan, BigInt maths and allocation.
// Usage: node p08-reference-diff.mjs <count> <mixed|valid> <seed>
import { computeResult } from "../../../../../../../src/core/result.js";
import { rng, randInt, ch } from "./fixtures.mjs";

const N = Number(process.argv[2] ?? 100000);
const VALID = process.argv[3] === "valid";
const SEED = Number(process.argv[4] ?? 4242);
const INVALID = { ok: false, empty: false };

function refRead(text, maxH) {
  const t = text.trim();
  if (t === "") return { ok: false, empty: true };
  let i = 0;
  while (i < t.length && t.charCodeAt(i) >= 48 && t.charCodeAt(i) <= 57) i += 1;
  if (i === 0) return INVALID;
  let frac = "";
  if (i < t.length) {
    if (t[i] !== ".") return INVALID;
    frac = t.slice(i + 1);
    if (frac.length > 2) return INVALID;
    for (const c of frac) if (c < "0" || c > "9") return INVALID;
  }
  const v = BigInt(t.slice(0, i)) * 100n + BigInt(frac.padEnd(2, "0"));
  return v <= BigInt(maxH) ? { ok: true, v } : INVALID;
}
const refAmount = (t) => { const r = refRead(t, 9999999); return r.ok && r.v < 1n ? INVALID : r; };
const half = (n) => (n + 5000n) / 10000n;
function refCharges(sub, s, t) {
  const service = half(sub * s);
  const sstBase = sub + service;
  const sst = half(sstBase * t);
  return { subtotal: sub, serviceBp: s, service, sstBp: t, sstBase, sst, total: sstBase + sst };
}
function refEven(a, n) {
  const base = a / BigInt(n), extra = a % BigInt(n);
  return Array.from({ length: n }, (_, i) => (BigInt(i) < extra ? base + 1n : base));
}
function refWeight(a, w) {
  const W = w.reduce((s, x) => s + x, 0n);
  const f = w.map((x) => (a * x) / W);
  let left = a - f.reduce((s, x) => s + x, 0n);
  return f.map((x, i) => (left > 0n && w[i] > 0n ? (left -= 1n, x + 1n) : x));
}
const num = (o) => JSON.parse(JSON.stringify(o, (k, v) => (typeof v === "bigint" ? Number(v) : v)));
const label = (p, i) => (p.name.trim() === "" ? `Person ${i + 1}` : p.name.trim());

function refResult(b) {
  const s = refRead(b.serviceText, 3000), t = refRead(b.sstText, 2000);
  if (!s.ok || !t.ok) return { kind: "blocked", reason: "rates" };
  if (b.mode === "even") {
    const sub = refAmount(b.subtotalText);
    if (!sub.ok) return { kind: "blocked", reason: "subtotal" };
    const charges = refCharges(sub.v, s.v, t.v);
    const shares = refEven(charges.total, b.people.length);
    return num({ kind: "even", charges, rows: b.people.map((p, i) => ({ name: label(p, i), share: shares[i] })), check: { share: shares.reduce((x, y) => x + y, 0n) } });
  }
  if (b.items.length === 0) return { kind: "blocked", reason: "no-items" };
  const prices = b.items.map((it) => refAmount(it.priceText));
  if (!prices.every((p) => p.ok)) return { kind: "blocked", reason: "prices" };
  const charges = refCharges(prices.reduce((x, p) => x + p.v, 0n), s.v, t.v);
  const holders = b.items.map((it) => b.people.map((p, i) => (it.who.includes(p.id) ? i : -1)).filter((i) => i >= 0));
  const unassigned = holders.filter((h) => h.length === 0).length;
  if (unassigned) return num({ kind: "unassigned", count: unassigned, charges });
  const items = b.people.map(() => 0n);
  holders.forEach((h, k) => refEven(prices[k].v, h.length).forEach((part, j) => { items[h[j]] += part; }));
  const parts = refWeight(charges.service + charges.sst, items);
  const rows = b.people.map((p, i) => ({ name: label(p, i), items: items[i], charges: parts[i], share: items[i] + parts[i] }));
  const sum = (xs) => xs.reduce((x, y) => x + y, 0n);
  return num({ kind: "item", charges, rows, check: { items: sum(items), charges: sum(parts), share: sum(rows.map((r) => r.share)) } });
}

const centsText = (cents) => `${Math.floor(cents / 100)}.${String(cents % 100).padStart(2, "0")}`;
const floatAlloc = (a, w) => {
  const W = w.reduce((s, x) => s + x, 0);
  const f = w.map((x) => Math.floor((a * x) / W));
  let left = a - f.reduce((s, x) => s + x, 0);
  return f.map((x, i) => (left > 0 && w[i] > 0 ? (left -= 1, x + 1) : x));
};

// Generator: valid, boundary and broken texts, both modes, MAX-heavy so products pass 2^53 often.
const r = rng(SEED);
const pick = (xs) => xs[randInt(r, 0, xs.length - 1)];
const SP = [" ", ch(0x09), ch(0xa0), ch(0x3000), ch(0xfeff), ch(0x2028)];
function amountText() {
  if (VALID) return r() < 0.5 ? "99999.99" : centsText(randInt(r, 1, 9999999));
  const k = r();
  if (k < 0.35) return "99999.99";
  if (k < 0.75) return centsText(randInt(r, 1, 9999999));
  if (k < 0.8) return `${pick(SP)}${randInt(r, 0, 99999)}${pick([".", "", ".5", ".05"])}${pick(SP)}`;
  if (k < 0.85) return `${"0".repeat(randInt(r, 1, 30))}${randInt(r, 1, 99999)}`;
  return pick(["", "0", "0.00", "100000", "99999.991", "1.234", "-1", "+1", "1e3", ".5", "1,000", "abc", "１２", "99999.99.0"]);
}
function rateText(max) {
  if (VALID) return r() < 0.4 ? String(max) : centsText(randInt(r, 0, max * 100));
  const k = r();
  if (k < 0.3) return String(max);
  if (k < 0.8) return centsText(randInt(r, 0, max * 100));
  if (k < 0.85) return `${pick(SP)}${randInt(r, 0, max)}${pick(SP)}`;
  return pick(["", `${max}.01`, "-0", "10%", "1e1", String(max + 1)]);
}
function genBill() {
  const people = Array.from({ length: randInt(r, 2, 12) }, (_, i) => ({ id: `p${i + 1}`, name: pick(["", " ", "Ben", "Ben", `X${i}`, `${ch(0x2028)}Y`]) }));
  const nItems = !VALID && r() < 0.05 ? 0 : randInt(r, 1, 50);
  const items = Array.from({ length: nItems }, (_, i) => {
    const who = people.filter(() => r() < (r() < 0.5 ? 0.15 : 0.6)).map((p) => p.id);
    if (who.length === 0 && (VALID || r() < 0.97)) who.push(pick(people).id);
    return { id: `i${100 + i}`, name: "", priceText: amountText(), who: who.sort(() => r() - 0.5) };
  });
  return {
    mode: r() < (VALID ? 0.2 : 0.4) ? "even" : "item", people, subtotalText: amountText(), items,
    serviceText: rateText(30), sstText: rateText(20), nextId: 200,
  };
}

const kinds = {};
let diffs = 0, invariantBad = 0, over53 = 0, floatWouldDiffer = 0;
for (let n = 0; n < N; n += 1) {
  const b = genBill();
  const got = computeResult(b);
  const want = refResult(b);
  kinds[got.kind] = (kinds[got.kind] ?? 0) + 1;
  if (JSON.stringify(got) !== JSON.stringify(want)) {
    diffs += 1;
    if (diffs <= 3) console.log("DIFF", JSON.stringify(b).slice(0, 300), "\n got", JSON.stringify(got).slice(0, 300), "\n want", JSON.stringify(want).slice(0, 300));
  }
  if (got.kind === "even" || got.kind === "item") {
    const c = got.charges;
    let ok = got.check.share === c.total && got.rows.every((row) => Number.isSafeInteger(row.share) && row.share >= 0);
    if (got.kind === "item") {
      ok &&= got.check.items === c.subtotal && got.check.charges === c.service + c.sst;
      ok &&= got.rows.every((row) => row.items > 0 || row.charges === 0);
      const weights = got.rows.map((row) => row.items);
      if (weights.some((w) => BigInt(c.service + c.sst) * BigInt(w) > 2n ** 53n)) over53 += 1;
      if (JSON.stringify(floatAlloc(c.service + c.sst, weights)) !== JSON.stringify(got.rows.map((row) => row.charges))) floatWouldDiffer += 1;
    } else {
      const s = got.rows.map((row) => row.share);
      ok &&= s.every((x, i) => i === 0 || (x <= s[i - 1] && s[0] - x <= 1));
    }
    if (!ok) invariantBad += 1;
  }
}
console.log(`pass: ${VALID ? "valid" : "mixed"}  seed: ${SEED}  bills: ${N}  kinds: ${JSON.stringify(kinds)}`);
console.log(`by-item bills with some charges x weight above 2^53: ${over53}`);
console.log(`by-item bills where a float allocator would have given a different split: ${floatWouldDiffer}`);
console.log(`differences from the independent BigInt reference: ${diffs}`);
console.log(`R22 invariant violations: ${invariantBad}`);

// Reachable BigInt trap, end to end through computeResult (built from the R8 trap row 61846725).
const trapItems = [];
for (const [pid, total] of [["p1", 49676084], ["p2", 322894546]]) {
  let left = total;
  while (left > 0) { const c = Math.min(left, 9999999); trapItems.push({ id: `i${trapItems.length + 3}`, name: "", priceText: centsText(c), who: [pid] }); left -= c; }
}
const trapBill = { mode: "item", people: [{ id: "p1", name: "A" }, { id: "p2", name: "B" }], subtotalText: "", items: trapItems, serviceText: "10", sstText: "6", nextId: 99 };
const tr = computeResult(trapBill);
console.log(`\nreachable trap bill: ${trapItems.length} items, subtotal ${tr.charges.subtotal}, charges ${tr.charges.service + tr.charges.sst}`);
console.log(`core charges split ${JSON.stringify(tr.rows.map((x) => x.charges))}; float allocator would give ${JSON.stringify(floatAlloc(tr.charges.service + tr.charges.sst, tr.rows.map((x) => x.items)))}; reference ${JSON.stringify(refResult(trapBill).rows.map((x) => x.charges))}`);

console.log(`\nP08 RESULT: ${diffs === 0 && invariantBad === 0 ? "PASS" : "FAIL"}`);
