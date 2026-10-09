// P06. Runtime check that the core touches no network, storage, clock, random, timer, locale, float
// parsing or dynamic-code facility, and imports nothing outside src/core/. Traps are installed BEFORE
// the core is loaded (dynamic import), so module evaluation is covered too. A negative control at the
// end proves the traps fire.
import module from "node:module";

const CORE = new URL("../../../../../../../src/core/", import.meta.url).href;
const resolved = [];
module.registerHooks({
  resolve(specifier, context, next) {
    const out = next(specifier, context);
    if (context.parentURL?.startsWith(CORE)) resolved.push(`${context.parentURL.slice(CORE.length)} -> ${out.url.startsWith(CORE) ? out.url.slice(CORE.length) : out.url}`);
    return out;
  },
});

const hits = [];
const G = globalThis;
const GLOBALS = [
  "fetch", "XMLHttpRequest", "WebSocket", "EventSource", "navigator", "localStorage", "sessionStorage", "indexedDB",
  "document", "window", "Date", "performance", "setTimeout", "setInterval", "setImmediate", "queueMicrotask",
  "requestAnimationFrame", "crypto", "Intl", "eval", "Function", "WebAssembly", "Worker", "process", "Buffer",
  "structuredClone", "Atomics", "SharedArrayBuffer", "FinalizationRegistry", "WeakRef", "console",
  "parseFloat", "parseInt",
];
const saved = new Map();
let armed = false;
for (const name of GLOBALS) {
  const desc = Object.getOwnPropertyDescriptor(G, name);
  saved.set(name, desc);
  const real = desc ? ("value" in desc ? desc.value : desc.get?.call(G)) : undefined;
  Object.defineProperty(G, name, { configurable: true, get() { if (armed) hits.push(`global ${name}`); return real; } });
}
const realRandom = Math.random;
Math.random = function () { if (armed) hits.push("Math.random"); return realRandom(); };
const realNumberParseFloat = Number.parseFloat;
const realNumberParseInt = Number.parseInt;
Number.parseFloat = function (...a) { if (armed) hits.push("Number.parseFloat"); return realNumberParseFloat(...a); };
Number.parseInt = function (...a) { if (armed) hits.push("Number.parseInt"); return realNumberParseInt(...a); };
const PROTO_METHODS = [
  [String.prototype, "localeCompare"], [String.prototype, "toLocaleUpperCase"], [String.prototype, "toLocaleLowerCase"],
  [String.prototype, "normalize"], [Number.prototype, "toLocaleString"], [Number.prototype, "toFixed"],
  [Number.prototype, "toPrecision"], [Array.prototype, "toLocaleString"], [Array.prototype, "sort"],
  [BigInt.prototype, "toLocaleString"], [Object.prototype, "toLocaleString"],
];
for (const [proto, key] of PROTO_METHODS) {
  const real = proto[key];
  Object.defineProperty(proto, key, { configurable: true, writable: true, value: function (...a) { if (armed) hits.push(`${key}`); return real.apply(this, a); } });
}

armed = true;
const money = await import(`${CORE}money.js`);
const allocate = await import(`${CORE}allocate.js`);
const bill = await import(`${CORE}bill.js`);
const result = await import(`${CORE}result.js`);
const summary = await import(`${CORE}summary.js`);
// Workload: every export, both modes, every blocking path, the summary.
let b = bill.newBill();
for (let i = 0; i < 12; i += 1) b = bill.addPerson(b);
b = bill.setPersonName(b, "p1", ` A${String.fromCodePoint(0x2028)}B `);
b = bill.setSubtotalText(b, "99999.99");
const evenRes = result.computeResult(b);
summary.summaryText(evenRes);
b = bill.setMode(b, "item");
for (let i = 0; i < 50; i += 1) { b = bill.addItem(b); const id = b.items.at(-1).id; b = bill.setItemPriceText(b, id, "99999.99"); b = bill.setItemName(b, id, "x"); b = bill.toggleItemPerson(b, id, b.people[i % 12].id); }
const itemRes = result.computeResult(b);
summary.summaryText(itemRes);
result.computeResult(bill.setServiceText(b, "31"));
result.computeResult(bill.setItemPriceText(b, b.items[0].id, "x"));
result.computeResult(bill.removeItem(b, b.items[0].id));
bill.removePerson(b, "p3"); bill.personLabel(b.people[0], 0); bill.itemLabel(b.items[0], 0);
money.parseAmount("  12.50 "); money.parseRate("6.25", 20); money.formatMoney(779999922); money.formatRate(625);
allocate.allocateEvenly(10, 3); allocate.allocateByWeight(10, [1, 2, 3]); result.billCharges(100, 1000, 600);
try { summary.summaryText({ kind: "blocked" }); } catch { /* expected TypeError */ }
const coreHits = hits.slice();
// Negative control: the same traps must fire for code that does use these facilities.
void G.Date; void G.fetch; Math.random(); "a".localeCompare("b"); [2, 1].sort(); (5).toFixed(1); void G.parseFloat; Number.parseFloat("1");
armed = false;
const controlHits = hits.slice(coreHits.length);

for (const [name, desc] of saved) { if (desc) Object.defineProperty(G, name, desc); else delete G[name]; }
Math.random = realRandom;
Number.parseFloat = realNumberParseFloat;
Number.parseInt = realNumberParseInt;
console.log(`core exports: ${[money, allocate, bill, result, summary].map((m) => Object.keys(m).join(",")).join(" | ")}`);
console.log(`even total ${evenRes.charges.total}, item total ${itemRes.charges.total}`);
console.log("imports resolved from inside src/core/:\n  " + resolved.join("\n  "));
const outside = resolved.filter((l) => !/-> [a-z]+\.js$/.test(l));
console.log(`imports leaving src/core/: ${outside.length}`);
console.log(`ambient accesses while the core loaded and ran: ${coreHits.length}${coreHits.length ? `\n  ${[...new Set(coreHits)].join("\n  ")}` : ""}`);
console.log(`negative control (probe code touching Date, fetch, Math.random, localeCompare, sort, toFixed, parseFloat, Number.parseFloat): ${controlHits.length} hits: ${controlHits.join(", ")}`);
console.log(`P06 RESULT: ${coreHits.length === 0 && outside.length === 0 && controlHits.length === 8 ? "PASS" : "CHECK"}`);
