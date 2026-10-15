// Security finder (read-only), v1.1.0 regression --full (2026-10-16), split-core. Threat rows: object integrity (spare
// included), correct shares under every spare rule, availability of Pick again, precision of the charges division, and
// clipboard text integrity with the one class (R35, R24).
// Copied from qa/security/20261015-222146/c1_core.mjs, sections (a) to (c) unchanged. Added (d) plainName and
// NAME_CONTROLS, and (e) the BILL_FIELDS copies of billWith and withSpare (9277412). Run from this folder,
// node c1_core.mjs, which writes c1_core-results.json here by a relative name.
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const here = fileURLToPath(new URL(".", import.meta.url)).replace(/[\\/]+$/, "").toLowerCase();
if (process.cwd().replace(/[\\/]+$/, "").toLowerCase() !== here) throw new Error("run from " + here);

const root = new URL("../../../../../../", import.meta.url);
const bill = await import(new URL("src/core/bill.js", root));
const { computeResult } = await import(new URL("src/core/result.js", root));
const { summaryText } = await import(new URL("src/core/summary.js", root));
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
  setPersonName: bill.setPersonName(hostile, "p1", "Z"), setItemName: bill.setItemName(hostile, "i4", "y"),
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
const maxItems = { mode: "item", people: twelve.people, subtotalText: "", serviceText: "30", sstText: "20",
  items: Array.from({ length: 50 }, (_, k) => ({ id: `i${k + 13}`, name: "", priceText: "99999.99", who: twelve.people.map((p) => p.id) })),
  spare: twelve.spare, nextId: 63 };
draws = 0;
t0 = performance.now();
pickAgain(maxItems, constant);
out.pickAgain_max_bill_constant_source = { draws, ms: Math.round(performance.now() - t0) };

// (c) Precision and the sums, as in step 5 (seeded generator, 40,000 by-item bills, all three rules).
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

// (d) plainName and NAME_CONTROLS (R35, R24). Every code point but the surrogates is deleted by plainName exactly when it
// is one of the 79 the spec lists, and summaryText replaces exactly those with a space (A c B in Ben's row of the S2
// result). Then idempotence, lone surrogates, a 4.5M name, the shared g flag (lastIndex) through replace, and the .test
// hazard of a g-flagged shared RegExp (code review CR-R3, accepted, no .test or .exec caller in src/).
const LISTED = new Set([...Array(0x20).keys(), ...Array.from({ length: 0x21 }, (_, i) => 0x7f + i), 0x2028, 0x2029, 0x61c, 0x200e,
  0x200f, 0x202a, 0x202b, 0x202c, 0x202d, 0x202e, 0x2066, 0x2067, 0x2068, 0x2069]);
const S2 = { mode: "even", people: [{ id: "p1", name: "Aisyah" }, { id: "p2", name: "Ben" }, { id: "p3", name: "Chen" }],
  subtotalText: "100.00", items: [], serviceText: "10", sstText: "6", spare: { rule: "top" }, nextId: 4 };
const s2Result = computeResult(S2);
let deleted = 0;
const wrong = [], summaryWrong = [];
t0 = performance.now();
for (let c = 0; c <= 0x10ffff; c += 1) {
  if (c >= 0xd800 && c <= 0xdfff) continue;
  const text = "A" + String.fromCodePoint(c) + "B";
  const plainText = bill.plainName(text);
  const isDeleted = plainText === "AB";
  if (isDeleted) deleted += 1;
  if (isDeleted !== LISTED.has(c) || (!isDeleted && plainText !== text)) { if (wrong.length < 5) wrong.push(c.toString(16)); }
  const row = summaryText({ ...s2Result, rows: [s2Result.rows[0], { ...s2Result.rows[1], name: text }, s2Result.rows[2]] }).split("\n")[3];
  const wantRow = `${LISTED.has(c) ? "A B" : text} ${s2Result.rows[1].share === 3887 ? "RM 38.87" : "?"}`;
  if (row !== wantRow) { if (summaryWrong.length < 5) summaryWrong.push(c.toString(16)); }
}
const sweepMs = Math.round(performance.now() - t0);
const lone = "\ud83d\u0000\ude00";
const long = "‮".repeat(4_500_000) + "x";
t0 = performance.now();
const longPlain = bill.plainName(long);
const longMs = Math.round(performance.now() - t0);
bill.NAME_CONTROLS.lastIndex = 2;
const plainAfterSet = bill.plainName("‮A‮B");
const summaryAfterSet = summaryText({ ...s2Result, rows: [s2Result.rows[0], { ...s2Result.rows[1], name: "‮B‮en" }, s2Result.rows[2]] });
const lastIndexAfterReplace = bill.NAME_CONTROLS.lastIndex;
const testFirst = bill.NAME_CONTROLS.test("‮");
const testSecond = bill.NAME_CONTROLS.test("‮");
const lastIndexAfterTests = bill.NAME_CONTROLS.lastIndex;
bill.NAME_CONTROLS.lastIndex = 0;
out.plainName = {
  listed: LISTED.size, deleted, wrong_code_points: wrong, summary_rows_wrong: summaryWrong, s2_ben_share: s2Result.rows[1].share, sweepMs,
  flags: bill.NAME_CONTROLS.flags, source: bill.NAME_CONTROLS.source, frozen: Object.isFrozen(bill.NAME_CONTROLS),
  idempotent: ["", "A\u0000 ‮B", lone, "\u0085", "x​y"].every((t) => bill.plainName(bill.plainName(t)) === bill.plainName(t)),
  lone_surrogates_joined_into_one_emoji: bill.plainName(lone) === "\u{1f600}",
  long_4_5M_rlo: { ms: longMs, result: longPlain },
  after_lastIndex_set_to_2: { plain: plainAfterSet, summary_row: summaryAfterSet.split("\n")[3], lastIndexAfterReplace },
  test_twice_on_rlo: { first: testFirst, second: testSecond, lastIndexAfter: lastIndexAfterTests },
  empty_name_label: bill.personLabel({ id: "p2", name: bill.plainName("‮⁦\u0000") }, 1),
};

// (e) BILL_FIELDS (9277412). billWith and withSpare build from Object.keys(newBill()). Of the outputs of (a) that are new
// bills, every one has exactly the known keys and none copied the parsed bill's own __proto__, constructor or extra.
const fresh = Object.values(outputs).filter((b) => b !== hostile);
const own = (b, key) => Object.prototype.hasOwnProperty.call(b, key);
out.bill_fields = {
  newBill_keys: Object.keys(bill.newBill()).join(","), equals_known: Object.keys(bill.newBill()).join(",") === KNOWN,
  new_outputs: fresh.length, with_known_keys: fresh.filter((b) => Object.keys(b).join(",") === KNOWN).length,
  own_proto_copied: fresh.some((b) => own(b, "__proto__")), constructor_copied: fresh.some((b) => own(b, "constructor")),
  extra_copied: fresh.some((b) => own(b, "extra")),
};

out.pollution = { objectProtoUnchanged: Object.getOwnPropertyNames(Object.prototype).join(",") === protoBefore, polluted: ({}).polluted ?? null };
writeFileSync("c1_core-results.json", JSON.stringify(out, null, 1));
console.log(JSON.stringify({ ...out, plainName: { ...out.plainName, long_4_5M_rlo: { ms: longMs, result: longPlain } } }, null, 1));
