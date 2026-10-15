// Security finder (read-only), step 5 of v1.1.0, split-core. Threat rows: object integrity (spare included), correct
// shares under every spare rule, availability of Pick again, precision of the charges division.
// node docs/modules/split-core/qa/security/20261015-222146/c1_core.mjs   (writes c1_core-results.json beside it)
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = new URL("../../../../../../", import.meta.url);
const bill = await import(new URL("src/core/bill.js", root));
const { computeResult } = await import(new URL("src/core/result.js", root));
const { allocateByWeight } = await import(new URL("src/core/allocate.js", root));
const { chooseSpareRule, chooseSparePerson, pickAgain } = await import(new URL("src/core/spare.js", root));

const out = {};
const protoBefore = Object.getOwnPropertyNames(Object.prototype).join(",");

// (a) Object integrity. Bills parsed from JSON with own "__proto__", "constructor" and extra keys at every level go
// through every action that builds a bill or a spare. Every output must hold only the known keys on Object.prototype.
const hostile = JSON.parse(`{"__proto__":{"polluted":1},"constructor":{"prototype":{"polluted":1}},"extra":1,
  "mode":"item","people":[{"id":"p1","name":"A","__proto__":{"polluted":1}},{"id":"p2","name":"B"},{"id":"p3","name":"C"}],
  "subtotalText":"","items":[{"id":"i4","name":"x","priceText":"0.05","who":["p1","p2"],"__proto__":{"polluted":1}}],
  "serviceText":"10","sstText":"6","spare":{"rule":"random","order":["p2","p3","p1"],"__proto__":{"polluted":1},"extra":1},"nextId":5}`);
const KNOWN = "mode,people,subtotalText,items,serviceText,sstText,spare,nextId";
const spareKeys = { top: "rule", one: "rule,personId", random: "rule,order" };
const rnd = () => 0.42;
const outputs = {
  chooseTop: chooseSpareRule(hostile, "top", rnd), chooseOne: chooseSpareRule(hostile, "one", rnd),
  chooseSame: chooseSpareRule(hostile, "random", rnd), choosePerson: chooseSparePerson(hostile, "p1"),
  pickAgain: pickAgain(hostile, Math.random), addPerson: bill.addPerson(hostile), removePerson: bill.removePerson(hostile, "p2"),
  setMode: bill.setMode(hostile, "even"), addItem: bill.addItem(hostile), toggle: bill.toggleItemPerson(hostile, "i4", "p3"),
};
out.integrity = Object.fromEntries(Object.entries(outputs).map(([name, b]) => {
  const same = b === hostile;
  return [name, {
    sameReference: same,
    keys: same ? "input returned" : (Object.keys(b).join(",") === KNOWN ? "known" : Object.keys(b).join(",")),
    proto: Object.getPrototypeOf(b) === Object.prototype,
    spare: Object.keys(b.spare).join(",") === spareKeys[b.spare.rule] ? "known" : Object.keys(b.spare).join(","),
    spareProto: Object.getPrototypeOf(b.spare) === Object.prototype,
  }];
}));
out.integrity_note = "chooseSame returns the input (rule already random), so its keys are the parsed object's, by design (R29 same reference)";

// (b) Availability. Pick again on a bill where no order changes the rows (2 people, 0 spare sen) and on one where a
// change is possible but the source always gives the same number.
let draws = 0;
const constant = () => { draws += 1; return 0; };
const evenTwo = { mode: "even", people: [{ id: "p1", name: "A" }, { id: "p2", name: "B" }], subtotalText: "1.00", items: [],
  serviceText: "0", sstText: "0", spare: { rule: "random", order: ["p1", "p2"] }, nextId: 3 };
let t0 = performance.now();
const same = pickAgain(evenTwo, constant);
out.pickAgain_no_change = { sameReference: same === evenTwo, draws, ms: Math.round(performance.now() - t0) };
draws = 0;
const twelve = { mode: "even", people: Array.from({ length: 12 }, (_, i) => ({ id: `p${i + 1}`, name: "" })), subtotalText: "100.05",
  items: [], serviceText: "10", sstText: "6", spare: { rule: "random", order: Array.from({ length: 12 }, (_, i) => `p${i + 1}`) }, nextId: 13 };
t0 = performance.now();
const stuck = pickAgain(twelve, constant);
out.pickAgain_constant_source = { sameReference: stuck === twelve, draws, ms: Math.round(performance.now() - t0) };
// The largest by-item bill (50 items, 12 people) under At random: the worst case of 64 draws, each a full computeResult.
const maxItems = { mode: "item", people: twelve.people, subtotalText: "", serviceText: "30", sstText: "20",
  items: Array.from({ length: 50 }, (_, k) => ({ id: `i${k + 13}`, name: "", priceText: "99999.99", who: twelve.people.map((p) => p.id) })),
  spare: twelve.spare, nextId: 63 };
draws = 0;
t0 = performance.now();
pickAgain(maxItems, constant);
out.pickAgain_max_bill_constant_source = { draws, ms: Math.round(performance.now() - t0) };

// (c) Precision and the sums. Seeded generator (test side only), by-item bills with prices up to 99,999.99 and rates
// up to 30% and 20%. Under Top the charges column must equal allocateByWeight(service + sst, items) (R21 (4)), which is
// BigInt. Under all three rules R22's sums must hold and every value must be a safe non-negative integer.
let seed = 20261015;
const next = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
const pick = (n) => Math.floor(next() * n);
let compared = 0, mismatches = 0, sumFails = 0, beyond53 = 0;
const firstFails = [];
for (let n = 0; n < 40000; n += 1) {
  const people = Array.from({ length: 2 + pick(11) }, (_, i) => ({ id: `p${i + 1}`, name: "" }));
  const items = Array.from({ length: 1 + pick(50) }, (_, k) => {
    const who = people.filter(() => next() < 0.4).map((p) => p.id);
    return { id: `i${k + 20}`, name: "", priceText: (1 + pick(9999999)).toString().padStart(3, "0").replace(/(\d{2})$/, ".$1"),
      who: who.length ? who : [people[pick(people.length)].id] };
  });
  const order = people.map((p) => p.id).sort(() => next() - 0.5);
  const base = { mode: "item", people, subtotalText: "", items, serviceText: String(pick(31)), sstText: String(pick(21)),
    spare: { rule: "top" }, nextId: 100 };
  for (const spare of [{ rule: "top" }, { rule: "one", personId: people[pick(people.length)].id }, { rule: "random", order }]) {
    const r = computeResult({ ...base, spare });
    if (r.kind !== "item") continue;
    const values = r.rows.flatMap((row) => [row.items, row.charges, row.share]);
    const ok = r.check.share === r.charges.total && r.check.items === r.charges.subtotal
      && r.check.charges === r.charges.service + r.charges.sst && values.every((v) => Number.isSafeInteger(v) && v >= 0)
      && r.rows.every((row) => row.items > 0 || row.charges === 0);
    if (!ok) { sumFails += 1; if (firstFails.length < 3) firstFails.push({ n, spare: spare.rule }); }
    if (spare.rule === "top") {
      compared += 1;
      const want = allocateByWeight(r.charges.service + r.charges.sst, r.rows.map((row) => row.items));
      if (r.charges.service + r.charges.sst > 0 && Math.max(...r.rows.map((row) => row.items)) * (r.charges.service + r.charges.sst) > 2 ** 53) beyond53 += 1;
      if (want.some((v, i) => v !== r.rows[i].charges)) { mismatches += 1; if (firstFails.length < 3) firstFails.push({ n, kind: "top mismatch" }); }
    }
  }
}
out.precision = { bills: 40000, compared_top: compared, mismatches_vs_bigint: mismatches, sum_failures_all_rules: sumFails,
  top_bills_with_products_past_2_53: beyond53, firstFails };
out.pollution = { objectProtoUnchanged: Object.getOwnPropertyNames(Object.prototype).join(",") === protoBefore, polluted: ({}).polluted ?? null };
writeFileSync(fileURLToPath(new URL("c1_core-results.json", import.meta.url)), JSON.stringify(out, null, 1));
console.log(JSON.stringify(out, null, 1));
