// P03. Prototype pollution through parsed bills, stray keys, and input mutation (R16).
import * as bill from "../../../../../../../src/core/bill.js";
import { computeResult, billCharges } from "../../../../../../../src/core/result.js";
import { summaryText } from "../../../../../../../src/core/summary.js";
import { allocateByWeight, allocateEvenly } from "../../../../../../../src/core/allocate.js";
import { parseAmount, parseRate, formatMoney, formatRate } from "../../../../../../../src/core/money.js";
import { S1, S2, deepFreeze } from "./fixtures.mjs";

const snapshot = () => ({
  object: Object.getOwnPropertyNames(Object.prototype).sort().join(","),
  array: Object.getOwnPropertyNames(Array.prototype).sort().join(","),
  string: Object.getOwnPropertyNames(String.prototype).sort().join(","),
  fn: Object.getOwnPropertyNames(Function.prototype).sort().join(","),
});
const before = snapshot();

// Hostile JSON: own __proto__ keys at every object level, constructor.prototype payloads, stray keys,
// and a __proto__ that carries Bill fields (to prove the core never reads them through the payload).
const hostile = () => JSON.parse(`{
  "__proto__": {"polluted": "bill-proto", "mode": "even", "people": [], "isAdmin": true},
  "constructor": {"prototype": {"polluted": "ctor"}},
  "prototype": {"polluted": "proto"},
  "mode": "item",
  "people": [
    {"id": "p1", "name": "A", "__proto__": {"polluted": "person-proto", "name": "HIJACK"}, "constructor": {"prototype": {"x": 1}}},
    {"id": "p2", "name": "B", "toString": "boom", "valueOf": 7},
    {"id": "p3", "name": "C", "hasOwnProperty": "no"}
  ],
  "subtotalText": "10.00",
  "items": [
    {"id": "i4", "name": "T", "priceText": "1.00", "who": ["p1"], "__proto__": {"who": ["p2"], "polluted": "item-proto"}, "stray": 1},
    {"id": "i5", "name": "U", "priceText": "2.00", "who": ["p2", "p3"], "constructor": {"prototype": {"polluted": "item-ctor"}}}
  ],
  "serviceText": "10", "sstText": "6", "nextId": 6, "extra": {"__proto__": {"polluted": "extra"}}
}`);

const BILL_KEYS = "mode,people,subtotalText,items,serviceText,sstText,nextId";
const actions = [
  ["addPerson", (b) => bill.addPerson(b)],
  ["removePerson p3", (b) => bill.removePerson(b, "p3")],
  ["setPersonName p1", (b) => bill.setPersonName(b, "p1", "Z")],
  ["setPersonName __proto__ id", (b) => bill.setPersonName(b, "__proto__", "Z")],
  ["setMode even", (b) => bill.setMode(b, "even")],
  ["setMode __proto__", (b) => bill.setMode(b, "__proto__")],
  ["setSubtotalText", (b) => bill.setSubtotalText(b, "1")],
  ["setServiceText", (b) => bill.setServiceText(b, "1")],
  ["setSstText", (b) => bill.setSstText(b, "1")],
  ["addItem", (b) => bill.addItem(b)],
  ["removeItem i4", (b) => bill.removeItem(b, "i4")],
  ["setItemName i4", (b) => bill.setItemName(b, "i4", "Z")],
  ["setItemPriceText i4", (b) => bill.setItemPriceText(b, "i4", "3")],
  ["toggleItemPerson i4 p2", (b) => bill.toggleItemPerson(b, "i4", "p2")],
  ["toggleItemPerson constructor", (b) => bill.toggleItemPerson(b, "constructor", "constructor")],
];

let problems = 0;
console.log("== P03a: every action on a hostile parsed bill ==");
for (const [title, act] of actions) {
  const input = hostile();
  const out = act(input);
  const keys = Object.keys(out).join(",");
  const proto = Object.getPrototypeOf(out) === Object.prototype;
  const ownProto = Object.hasOwn(out, "__proto__");
  const same = out === input;
  const ok = same || (keys === BILL_KEYS && proto && !ownProto);
  if (!ok) problems += 1;
  console.log(`${ok ? "OK  " : "FAIL"} ${title.padEnd(30)} ${same ? "same reference (no change)" : `keys=${keys} protoIsObject=${proto} ownProtoKey=${ownProto}`}`);
}

console.log("\n== P03b: computeResult and summaryText on the hostile bill (own fields only, no __proto__ fields read) ==");
const hb = hostile();
const res = computeResult(hb);
console.log(`kind=${res.kind} rows=${JSON.stringify(res.rows)} check=${JSON.stringify(res.check)}`);
console.log("person p1 label (own name 'A', __proto__ payload name 'HIJACK'):", bill.personLabel(hb.people[0], 0));
console.log("item i4 holders come from own who [p1], not __proto__ who [p2]:", JSON.stringify(res.rows.map((r) => r.items)));
const text = summaryText(res);
console.log(text.split("\n").join(" | "));
const evenRes = computeResult(bill.setMode(hostile(), "even"));
console.log(`even on hostile: kind=${evenRes.kind} shares=${evenRes.rows.map((r) => r.share)}`);

console.log("\n== P03c: global prototypes after all of the above ==");
const after = snapshot();
for (const k of Object.keys(before)) {
  const same = before[k] === after[k];
  if (!same) problems += 1;
  console.log(`${same ? "OK  " : "FAIL"} ${k}.prototype own names unchanged`);
}
for (const probe of [{}, [], "", () => 0]) {
  const v = probe.polluted ?? probe.isAdmin ?? probe.x;
  if (v !== undefined) problems += 1;
  console.log(`${v === undefined ? "OK  " : "FAIL"} ${Array.isArray(probe) ? "[]" : typeof probe}.polluted/isAdmin/x is ${v}`);
}

console.log("\n== P03d: what still carries stray keys after an action (shared by reference, documented) ==");
const touched = bill.setPersonName(hostile(), "p2", "Q");
touched.people.forEach((p, i) => console.log(`people[${i}] keys=${Object.keys(p).join(",")}`));
touched.items.forEach((it, i) => console.log(`items[${i}] keys=${Object.keys(it).join(",")}`));

console.log("\n== P03e: mutation, every exported function on deep-frozen and on write-trapping proxies ==");
const writes = [];
function trap(value, path = "$") {
  if (value === null || typeof value !== "object") return value;
  return new Proxy(value, {
    get(t, k, r) { const v = Reflect.get(t, k, r); return typeof k === "symbol" ? v : trap(v, `${path}.${String(k)}`); },
    set(t, k) { writes.push(`set ${path}.${String(k)}`); return true; },
    defineProperty(t, k) { writes.push(`define ${path}.${String(k)}`); return true; },
    deleteProperty(t, k) { writes.push(`delete ${path}.${String(k)}`); return true; },
    setPrototypeOf() { writes.push(`setPrototypeOf ${path}`); return true; },
    preventExtensions() { writes.push(`preventExtensions ${path}`); return true; },
  });
}
const calls = (b) => [
  () => bill.addPerson(b), () => bill.removePerson(b, "p3"), () => bill.setPersonName(b, "p1", "Z"),
  () => bill.addItem(b), () => bill.removeItem(b, b.items[0]?.id ?? "i4"), () => bill.setItemName(b, b.items[0]?.id ?? "i4", "Z"),
  () => bill.setItemPriceText(b, b.items[0]?.id ?? "i4", "1"), () => bill.toggleItemPerson(b, b.items[0]?.id ?? "i4", "p2"),
  () => bill.setSubtotalText(b, "1"), () => bill.setServiceText(b, "1"), () => bill.setSstText(b, "1"),
  () => bill.setMode(b, "even"), () => bill.setMode(b, "item"), () => bill.personLabel(b.people[0], 0),
  () => b.items.length ? bill.itemLabel(b.items[0], 0) : "", () => computeResult(b),
];
let thrown = 0;
for (const [name, make] of [["S1", S1], ["S2", S2], ["hostile", hostile]]) {
  const frozen = deepFreeze(make());
  for (const c of calls(frozen)) { try { c(); } catch (e) { thrown += 1; console.log(`THROW on frozen ${name}: ${e.message}`); } }
  const proxied = trap(make());
  for (const c of calls(proxied)) { try { c(); } catch (e) { thrown += 1; console.log(`THROW on proxy ${name}: ${e.message}`); } }
}
const r1 = computeResult(S1());
const r2 = computeResult(S2());
for (const r of [r1, r2]) { summaryText(deepFreeze(structuredClone(r))); summaryText(trap(structuredClone(r))); }
allocateByWeight(10, trap([1, 2, 3])); allocateByWeight(10, Object.freeze([1, 2, 3]));
allocateEvenly(10, 3); billCharges(100, 10, 6); parseAmount("1"); parseRate("1", 30); formatMoney(1); formatRate(1);
console.log(`throws on frozen or proxied input: ${thrown}; write attempts seen by proxies: ${writes.length}`);
if (writes.length) console.log(writes.slice(0, 20).join("\n"));
problems += thrown + writes.length;

console.log("\n== P03f: shared frozen constants and fresh outputs ==");
const e1 = parseAmount(""), e2 = parseAmount("  ");
console.log(`parse EMPTY results are the same frozen object: ${e1 === e2} frozen=${Object.isFrozen(e1)}`);
console.log(`LIMITS frozen=${Object.isFrozen(bill.LIMITS)}; newBill() fresh each call: ${bill.newBill() !== bill.newBill() && bill.newBill().people !== bill.newBill().people}`);
const rr = computeResult(S2());
console.log(`computeResult output shares nothing mutable with a second call: ${rr.rows !== computeResult(S2()).rows && rr.charges !== computeResult(S2()).charges}`);

console.log(`\nP03 RESULT: ${problems === 0 ? "PASS" : "FAIL"} (problems: ${problems})`);
