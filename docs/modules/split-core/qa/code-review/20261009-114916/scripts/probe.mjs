// Read-only probes against split-core. Prints findings to stdout.
// No backslash escapes in this file: special characters are built from code points.
import { pathToFileURL } from "node:url";
const root = process.argv[2];
const load = (rel) => import(pathToFileURL(`${root}/${rel}`).href);
const money = await load("src/core/money.js");
const alloc = await load("src/core/allocate.js");
const bill = await load("src/core/bill.js");
const result = await load("src/core/result.js");
const summary = await load("src/core/summary.js");
const fixtures = await load("tests/support/bills.js");

const ch = (code) => String.fromCodePoint(code);
const LF = ch(10), CR = ch(13), TAB = ch(9), NBSP = ch(0xa0), LS = ch(0x2028), PS = ch(0x2029), NEL = ch(0x85);
const out = (label, value) => console.log(`${label}: ${typeof value === "string" ? value : JSON.stringify(value)}`);

console.log("== P1 independent recompute of S1 and S2 (BigInt, no core code) ==");
{
  const halfUp = (n, bp) => (n * BigInt(bp) + 5000n) / 10000n;
  const s2sub = 10000n, s2svc = halfUp(s2sub, 1000), s2base = s2sub + s2svc, s2sst = halfUp(s2base, 600);
  const s2tot = s2base + s2sst;
  const per = s2tot / 3n, extra = s2tot % 3n;
  out("S2 subtotal/service/sst/total", [s2sub, s2svc, s2sst, s2tot].map(String));
  out("S2 shares", [0, 1, 2].map((i) => String(per + (BigInt(i) < extra ? 1n : 0n))));
  const aisyah = 1590n + 900n, ben = 1350n, chen = 1200n + 900n;
  const sub = aisyah + ben + chen, svc = halfUp(sub, 1000), base = sub + svc, sst = halfUp(base, 600);
  const charges = svc + sst;
  const w = [aisyah, ben, chen];
  const floors = w.map((x) => (charges * x) / sub);
  let left = charges - floors.reduce((a, b) => a + b, 0n);
  const parts = floors.map((f) => (left-- > 0n ? f + 1n : f));
  out("S1 subtotal/service/sst/total", [sub, svc, sst, base + sst].map(String));
  out("S1 floors before leftover", floors.map(String));
  out("S1 charge parts", parts.map(String));
  out("S1 shares", w.map((x, i) => String(x + parts[i])));
  out("core S1", result.computeResult(fixtures.S1).rows.map((r) => r.share));
  out("core S2", result.computeResult(fixtures.S2).rows.map((r) => r.share));
}

console.log("== P2 applyRate largest product claim (result.js comment, BUILD.md) ==");
out("service product 499999950 x 3000", 499999950 * 3000);
out("sst product 649999935 x 2000 (the comment's stated max)", 649999935 * 2000);
out("service product is larger", 499999950 * 3000 > 649999935 * 2000);

console.log("== P3 spec 'charges x weight can reach about 1.4e16' ==");
out("MAX-I weights product 279999972 x 49999995", 279999972 * 49999995);
out("one person holds all 50 items: 279999972 x 499999950", 279999972 * 499999950);

console.log("== P4 does a float allocator get MAX-I wrong? (R23 claim, result.test.js title) ==");
{
  const floatAlloc = (amount, weights) => {
    const W = weights.reduce((a, b) => a + b, 0);
    const floors = weights.map((w) => Math.floor((amount * w) / W));
    let left = amount - floors.reduce((a, b) => a + b, 0);
    return floors.map((f, i) => (left > 0 && weights[i] > 0 ? (left--, f + 1) : f));
  };
  const weights = [49999995, 49999995, ...Array(10).fill(39999996)];
  const exact = alloc.allocateByWeight(279999972, weights);
  const naive = floatAlloc(279999972, weights);
  out("exact", exact);
  out("float", naive);
  out("float equals exact on MAX-I", JSON.stringify(exact) === JSON.stringify(naive));
  out("float on R8 trap row 236419679", floatAlloc(236419679, [314963010, 157876348]));
  out("exact on R8 trap row", alloc.allocateByWeight(236419679, [314963010, 157876348]));
  out("naive floors on R8 trap row (spec says [157481506, 78938173])",
    [314963010, 157876348].map((w) => Math.floor((236419679 * w) / (314963010 + 157876348))));
}

console.log("== P5 stray keys survive on untouched nested objects (bill.js header, BUILD.md) ==");
{
  const parsed = JSON.parse(
    '{"mode":"even","people":[{"id":"p1","name":"A"},{"id":"p2","name":"B","x":1,"__proto__":{"polluted":true}}],' +
    '"subtotalText":"","items":[{"id":"i3","name":"","priceText":"","who":[],"stray":1}],"serviceText":"10",' +
    '"sstText":"6","nextId":4}',
  );
  const next = bill.setPersonName(bill.setMode(parsed, "item"), "p1", "Z");
  out("people[1] keys after two actions", Object.keys(next.people[1]));
  out("people[1] has own __proto__", Object.hasOwn(next.people[1], "__proto__"));
  out("items[0] keys after two actions", Object.keys(next.items[0]));
  out("people[1] is the parsed object", next.people[1] === parsed.people[1]);
  out("global prototype polluted", ({}).polluted === undefined ? "no" : "YES");
}

console.log("== P6 unknown mode ==");
{
  const b = bill.setSubtotalText(bill.newBill(), "10");
  out("computeResult mode 'bogus'", result.computeResult({ ...b, mode: "bogus" }));
}

console.log("== P7 parsing edge cases ==");
const cases = [
  ["NBSP+12.50", NBSP + "12.50"], ["12.50+LF", "12.50" + LF], ["0.", "0."], [".", "."], ["00.5", "00.5"],
  ["1e6 zeros then 1", "0".repeat(1000000) + "1"], ["arabic-indic 3", ch(0x663)], ["1_000", "1_000"],
  ["12.5 0", "12.5 0"], ["099999.99", "099999.99"], ["9 nines", "9".repeat(9)], ["10 nines", "9".repeat(10)],
  ["6.", "6."], ["TAB", TAB], ["1+LS", "1" + LS], ["+0", "+0"], ["0.0", "0.0"], ["30.", "30."], ["030.00", "030.00"],
];
for (const [label, t] of cases) {
  out(`parseAmount ${label}`, money.parseAmount(t));
  out(`parseRate ${label}, 30`, money.parseRate(t, 30));
}
{
  const t0 = performance.now();
  money.parseAmount("1".repeat(5_000_000) + "x");
  out("ms for 5e6 digits + x", Math.round(performance.now() - t0));
}

console.log("== P8 line separators other than CR/LF reach the summary ==");
{
  const b = bill.setPersonName(fixtures.S2, "p3", "Chen" + LS + "Adds up to RM 0.00");
  const text = summary.summaryText(result.computeResult(b));
  out("summary contains U+2028", text.includes(LS));
  const lines = [];
  let cur = "";
  for (const c of text) {
    if (c === LF || c === CR || c === LS || c === PS || c === NEL) { lines.push(cur); cur = ""; } else cur += c;
  }
  lines.push(cur);
  out("lines when U+2028 renders as a break", lines);
}

console.log("== P9 addPerson id after a removal ==");
{
  let b = bill.addPerson(bill.addPerson(bill.newBill()));
  b = bill.removePerson(b, "p3");
  b = bill.addPerson(b);
  out("ids", b.people.map((p) => p.id));
}

console.log("== P10 R22 sweep: item bills past 2^53 and float-floor divergence ==");
{
  const { mulberry32, randomInt } = await load("tests/support/rng.js");
  const hundredthsText = (n) => `${Math.floor(n / 100)}.${String(n % 100).padStart(2, "0")}`;
  const shuffled = (next, list) => {
    const c = [...list];
    for (let i = c.length - 1; i > 0; i -= 1) { const j = randomInt(next, 0, i); [c[i], c[j]] = [c[j], c[i]]; }
    return c;
  };
  const randomTappers = (next, people) => {
    const chosen = people.filter(() => next() < 0.5).map((p) => p.id);
    if (chosen.length === 0) chosen.push(people[randomInt(next, 0, people.length - 1)].id);
    return shuffled(next, chosen);
  };
  const randomCents = (next) => (next() < 0.1 ? 9999999 : randomInt(next, 1, 9999999));
  const next = mulberry32(20261008);
  let over = 0, itemBills = 0, floatWrong = 0;
  for (let n = 0; n < 2000; n += 1) {
    const mode = n % 2 === 0 ? "even" : "item";
    const pc = randomInt(next, 2, 12), ic = randomInt(next, 1, 50);
    const people = Array.from({ length: pc }, (_, i) => ({ id: `p${i + 1}`, name: `N${i + 1}` }));
    const items = Array.from({ length: ic }, (_, i) => ({
      id: `i${pc + i + 1}`, name: "", priceText: hundredthsText(randomCents(next)), who: randomTappers(next, people),
    }));
    const b = {
      mode, people, subtotalText: hundredthsText(randomCents(next)), items,
      serviceText: hundredthsText(randomInt(next, 0, 3000)), sstText: hundredthsText(randomInt(next, 0, 2000)),
      nextId: pc + ic + 1,
    };
    if (mode !== "item") continue;
    itemBills += 1;
    const r = result.computeResult(b);
    const chg = r.charges.service + r.charges.sst;
    const maxW = Math.max(...r.rows.map((row) => row.items));
    if (chg * maxW > Number.MAX_SAFE_INTEGER) over += 1;
    const W = r.check.items;
    const naive = r.rows.map((row) => Math.floor((chg * row.items) / W));
    const exactFloors = r.rows.map((row) => Number((BigInt(chg) * BigInt(row.items)) / BigInt(W)));
    if (naive.some((v, i) => v !== exactFloors[i])) floatWrong += 1;
  }
  out("item bills", itemBills);
  out("item bills with charges x max weight above 2^53", over);
  out("item bills where a float floor differs from the exact floor", floatWrong);
}
