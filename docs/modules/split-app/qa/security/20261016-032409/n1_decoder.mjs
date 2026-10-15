// Security finder (read-only), step 5 of v1.1.0. Hostile drafts through the real decoder, src/draft.js (D1 to D14).
// Rerun 2026-10-16 (v1.1.0 regression --full), copied from qa/security/20261015-222146/ with two changes. Run it from this
// folder (node n1_decoder.mjs). It writes n1_decoder-results.json here by a relative name. The cases are unchanged.
// Run from anywhere: node docs/modules/split-app/qa/security/20261015-222146/n1_decoder.mjs
// Writes n1_decoder-results.json beside this file. Imports the shipped module, changes no project file.
// Every special character is built with String.fromCodePoint, never written as escape text.
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = new URL("../../../../../../", import.meta.url);
if (process.cwd().toLowerCase() !== fileURLToPath(new URL(".", import.meta.url)).slice(0, -1).toLowerCase()) throw new Error("run from this folder");
const { decodeDraft, encodeDraft } = await import(new URL("src/draft.js", root));
const { computeResult } = await import(new URL("src/core/result.js", root));
const { summaryText } = await import(new URL("src/core/summary.js", root));
const { chooseSpareRule, pickAgain, chooseSparePerson } = await import(new URL("src/core/spare.js", root));

const cp = (...codes) => String.fromCodePoint(...codes);
const RLO = cp(0x202e), NUL = cp(0), LS = cp(0x2028), PS = cp(0x2029), CR = cp(13), LF = cp(10), ACUTE = cp(0x301);
const LINE_RE = new RegExp([CR + LF, CR, LF, LS, PS].join("|"), "u");
const CONTROL_RE = new RegExp("[" + "\\p{Cc}" + "\\p{Zl}" + "\\p{Zp}" + "\\p{Bidi_Control}" + "]", "u");
const FAMILY = [0x1f468, 0x200d, 0x1f469, 0x200d, 0x1f467, 0x200d, 0x1f466].map((c) => cp(c)).join("");

const S2 = () => ({ mode: "even", people: [{ id: "p1", name: "Aisyah" }, { id: "p2", name: "Ben" }, { id: "p3", name: "Chen" }],
  subtotalText: "100.00", items: [], serviceText: "10", sstText: "6", spare: { rule: "top" }, nextId: 4 });
const S1 = () => ({ mode: "item", people: [{ id: "p1", name: "Aisyah" }, { id: "p2", name: "Ben" }, { id: "p3", name: "Chen" }],
  subtotalText: "", items: [{ id: "i4", name: "Nasi", priceText: "24.90", who: ["p1"] }, { id: "i5", name: "Teh", priceText: "13.50", who: ["p2", "p3"] }],
  serviceText: "10", sstText: "6", spare: { rule: "top" }, nextId: 6 });
const env = (bill, version = 2) => JSON.stringify({ version, bill });
const withBill = (patch, base = S2) => env(Object.assign(base(), patch));
const drop = (key, bill) => { const copy = { ...bill }; delete copy[key]; return copy; };

const protoKeysBefore = Object.getOwnPropertyNames(Object.prototype).join(",");
const arrayKeysBefore = Object.getOwnPropertyNames(Array.prototype).join(",");

// [name, text, expected "A" (accepted) or "R" (rejected), or "?" (either, but never a throw)]
const cases = [
  ["base v2 S2", env(S2()), "A"],
  ["base v2 S1", env(S1()), "A"],
  ["base v1 S2 (D14 top)", env(drop("spare", S2()), 1), "A"],
  ["v1 with hostile spare is ignored (D14)", env({ ...S2(), spare: { rule: "random", order: ["x"] } }, 1), "A"],
  ["v1 with spare null (D14)", env({ ...S2(), spare: null }, 1), "A"],
  ["v2 no spare", env(drop("spare", S2())), "R"],
  ["v2 spare null", withBill({ spare: null }), "R"],
  ["v2 spare array", withBill({ spare: [] }), "R"],
  ["v2 spare string top", withBill({ spare: "top" }), "R"],
  ["spare top with extra keys and own __proto__", env(S2()).replace('{"rule":"top"}', '{"rule":"top","extra":1,"__proto__":{"polluted":1},"constructor":{"prototype":{"polluted":1}}}'), "A"],
  ["spare one p2", withBill({ spare: { rule: "one", personId: "p2" } }), "A"],
  ["spare one p2 with stray order", withBill({ spare: { rule: "one", personId: "p2", order: ["p1", "p2", "p3"] } }), "A"],
  ["spare one unknown p9", withBill({ spare: { rule: "one", personId: "p9" } }), "R"],
  ["spare one number 2", withBill({ spare: { rule: "one", personId: 2 } }), "R"],
  ["spare one missing personId", withBill({ spare: { rule: "one" } }), "R"],
  ["spare one personId __proto__", withBill({ spare: { rule: "one", personId: "__proto__" } }), "R"],
  ["spare one personId array [p2]", withBill({ spare: { rule: "one", personId: ["p2"] } }), "R"],
  ["spare one, person on no item, item mode (readable, R61)", withBill({ spare: { rule: "one", personId: "p1" }, items: [{ id: "i4", name: "Teh", priceText: "13.51", who: ["p2", "p3"] }] }, S1), "A"],
  ["spare random ok", withBill({ spare: { rule: "random", order: ["p2", "p3", "p1"] } }), "A"],
  ["spare random with stray personId", withBill({ spare: { rule: "random", order: ["p2", "p3", "p1"], personId: "p1" } }), "A"],
  ["spare random missing order", withBill({ spare: { rule: "random" } }), "R"],
  ["order drops an id", withBill({ spare: { rule: "random", order: ["p1", "p2"] } }), "R"],
  ["order repeats an id", withBill({ spare: { rule: "random", order: ["p1", "p2", "p2"] } }), "R"],
  ["order adds an id", withBill({ spare: { rule: "random", order: ["p1", "p2", "p3", "p4"] } }), "R"],
  ["order invents an id", withBill({ spare: { rule: "random", order: ["p1", "p2", "p9"] } }), "R"],
  ["order numbers", withBill({ spare: { rule: "random", order: [1, 2, 3] } }), "R"],
  ["order array-like object", withBill({ spare: { rule: "random", order: { 0: "p1", 1: "p2", 2: "p3", length: 3 } } }), "R"],
  ["order holds __proto__", withBill({ spare: { rule: "random", order: ["p1", "p2", "__proto__"] } }), "R"],
  ["order nested arrays", withBill({ spare: { rule: "random", order: [["p1"], ["p2"], ["p3"]] } }), "R"],
  ["order 1e6 entries", withBill({ spare: { rule: "random", order: Array(1e6).fill("p1") } }), "R"],
  ["rule TOP", withBill({ spare: { rule: "TOP" } }), "R"],
  ["rule constructor", withBill({ spare: { rule: "constructor" } }), "R"],
  ["rule __proto__", withBill({ spare: { rule: "__proto__" } }), "R"],
  ["rule toString", withBill({ spare: { rule: "toString" } }), "R"],
  ["rule missing", withBill({ spare: {} }), "R"],
  ["version 3", env(S2(), 3), "R"],
  ["version string 2", env(S2(), "2"), "R"],
  ["version 2.0 literal", env(S2()).replace('"version":2', '"version":2.0'), "A"],
  ["version 1.5", env(S2(), 1.5), "R"],
  ["version true", env(S2(), true), "R"],
  ["version only through own __proto__", JSON.stringify({ bill: S2() }).replace("{", '{"__proto__":{"version":2},'), "R"],
  ["mode only through own __proto__", env(drop("mode", S2())).replace('"bill":{', '"bill":{"__proto__":{"mode":"even"},'), "R"],
  ["mode unknown 'item '", withBill({ mode: "item " }), "R"],
  ["mode toString", withBill({ mode: "toString" }), "R"],
  ["mode missing", env(drop("mode", S2())), "R"],
  ["people 1", withBill({ people: [{ id: "p1", name: "A" }], nextId: 2 }), "R"],
  ["people 0 in even mode", withBill({ people: [], nextId: 1 }), "R"],
  ["people 13", withBill({ people: Array.from({ length: 13 }, (_, i) => ({ id: `p${i + 1}`, name: "" })), nextId: 14 }), "R"],
  ["people object with length", withBill({ people: { 0: { id: "p1", name: "" }, 1: { id: "p2", name: "" }, length: 2 } }), "R"],
  ["duplicate person id", withBill({ people: [{ id: "p1", name: "A" }, { id: "p1", name: "B" }, { id: "p3", name: "C" }] }), "R"],
  ["person with own __proto__ and extra key", env(S2()).replace('{"id":"p1","name":"Aisyah"}', '{"id":"p1","name":"Aisyah","__proto__":{"polluted":1},"admin":true}'), "A"],
  ["person id 'p1 '", withBill({ people: [{ id: "p1 ", name: "A" }, { id: "p2", name: "B" }] }), "R"],
  ["person id P1", withBill({ people: [{ id: "P1", name: "A" }, { id: "p2", name: "B" }] }), "R"],
  ["person id 11 digits", withBill({ people: [{ id: "p00000000001", name: "A" }, { id: "p2", name: "B" }] }), "R"],
  ["person id number", withBill({ people: [{ id: 1, name: "A" }, { id: "p2", name: "B" }] }), "R"],
  ["person id p0 (regex allows 0)", withBill({ people: [{ id: "p0", name: "A" }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "A"],
  ["name 21 ascii", withBill({ people: [{ id: "p1", name: "x".repeat(21) }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "R"],
  ["name 20 family emoji (220 UTF-16 units)", withBill({ people: [{ id: "p1", name: FAMILY.repeat(20) }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "A"],
  ["name with CR", withBill({ people: [{ id: "p1", name: "A" + CR + "B" }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "R"],
  ["name with LF", withBill({ people: [{ id: "p1", name: "A" + LF + "B" }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "R"],
  ["name with LS (readable, summary prints a space)", withBill({ people: [{ id: "p1", name: "A" + LS + "Adds up to RM 0" }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "A"],
  ["name with NUL (readable)", withBill({ people: [{ id: "p1", name: "Adds up to RM 0.00" + NUL }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "A"],
  ["name with RLO (readable)", withBill({ people: [{ id: "p1", name: "Ben" + RLO }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "A"],
  ["name null", withBill({ people: [{ id: "p1", name: null }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "R"],
  ["who not an array", withBill({ items: [{ id: "i4", name: "x", priceText: "1", who: "p1" }] }, S1), "R"],
  ["who repeats", withBill({ items: [{ id: "i4", name: "x", priceText: "1", who: ["p1", "p1"] }] }, S1), "R"],
  ["who unknown id", withBill({ items: [{ id: "i4", name: "x", priceText: "1", who: ["p9"] }] }, S1), "R"],
  ["who number", withBill({ items: [{ id: "i4", name: "x", priceText: "1", who: [1] }] }, S1), "R"],
  ["who __proto__", withBill({ items: [{ id: "i4", name: "x", priceText: "1", who: ["__proto__"] }] }, S1), "R"],
  ["who toString", withBill({ items: [{ id: "i4", name: "x", priceText: "1", who: ["toString"] }] }, S1), "R"],
  ["who 1e6 x p1", withBill({ items: [{ id: "i4", name: "x", priceText: "1", who: Array(1e6).fill("p1") }] }, S1), "R"],
  ["item with own __proto__ and extra", env(S1()).replace('{"id":"i4",', '{"__proto__":{"polluted":1},"x":1,"id":"i4",'), "A"],
  ["item id duplicate", withBill({ items: [{ id: "i4", name: "a", priceText: "1", who: [] }, { id: "i4", name: "b", priceText: "1", who: [] }] }, S1), "R"],
  ["item priceText number", withBill({ items: [{ id: "i4", name: "a", priceText: 1, who: [] }] }, S1), "R"],
  ["item priceText missing", withBill({ items: [{ id: "i4", name: "a", who: [] }] }, S1), "R"],
  ["item name 41", withBill({ items: [{ id: "i4", name: "y".repeat(41), priceText: "1", who: [] }] }, S1), "R"],
  ["items 51", withBill({ items: Array.from({ length: 51 }, (_, i) => ({ id: `i${i + 4}`, name: "", priceText: "", who: [] })), nextId: 60 }, S1), "R"],
  ["items 50", withBill({ items: Array.from({ length: 50 }, (_, i) => ({ id: `i${i + 4}`, name: "", priceText: "1", who: ["p1"] })), nextId: 60 }, S1), "A"],
  ["items object", withBill({ items: {} }, S1), "R"],
  ["nextId stale (= highest id)", withBill({ nextId: 3 }), "R"],
  ["nextId 4.5", withBill({ nextId: 4.5 }), "R"],
  ["nextId string", withBill({ nextId: "4" }), "R"],
  ["nextId 1e300", withBill({ nextId: 1e300 }), "R"],
  ["nextId 1000000000 (edge, SEC-03 residual)", withBill({ nextId: 1000000000 }), "A"],
  ["nextId 1000000001", withBill({ nextId: 1000000001 }), "R"],
  ["nextId 0", withBill({ nextId: 0 }), "R"],
  ["nextId -1", withBill({ nextId: -1 }), "R"],
  ["subtotalText missing", env(drop("subtotalText", S2())), "R"],
  ["serviceText number", withBill({ serviceText: 10 }), "R"],
  ["top-level array", JSON.stringify([{ version: 2, bill: S2() }]), "R"],
  ["top-level null", "null", "R"],
  ["empty text", "", "R"],
  ["truncated", env(S2()).slice(0, -5), "R"],
  ["trailing garbage", env(S2()) + "x", "R"],
  ["BOM prefixed", cp(0xfeff) + env(S2()), "R"],
  ["bill array", JSON.stringify({ version: 2, bill: [] }), "R"],
];

const big = (n) => "x".repeat(n);
const deep = (n) => "[".repeat(n) + "]".repeat(n);
cases.push(
  ["4.5M-char subtotalText", withBill({ subtotalText: big(4_500_000) }), "A"],
  ["4.5M-char ascii name (D8 rejects)", withBill({ people: [{ id: "p1", name: big(4_500_000) }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "R"],
  ["4.5M combining marks, 1 grapheme name (D8 passes)", withBill({ people: [{ id: "p1", name: "a" + ACUTE.repeat(4_500_000) }, { id: "p2", name: "B" }, { id: "p3", name: "C" }] }), "A"],
  ["unknown key with 100k nesting", env({ ...S2(), junk: 0 }).replace('"junk":0', `"junk":${deep(100_000)}`), "?"],
  ["unknown key with 1M nesting", env({ ...S2(), junk: 0 }).replace('"junk":0', `"junk":${deep(1_000_000)}`), "?"],
);

const KNOWN_BILL = ["mode", "people", "subtotalText", "items", "serviceText", "sstText", "spare", "nextId"];
function shapeProblems(bill) {
  const problems = [];
  const keys = (o) => Object.keys(o).join(",");
  if (Object.getPrototypeOf(bill) !== Object.prototype) problems.push("bill proto");
  if (keys(bill) !== KNOWN_BILL.join(",")) problems.push(`bill keys ${keys(bill)}`);
  for (const p of bill.people) if (keys(p) !== "id,name" || Object.getPrototypeOf(p) !== Object.prototype) problems.push(`person keys ${keys(p)}`);
  for (const i of bill.items) if (keys(i) !== "id,name,priceText,who" || Object.getPrototypeOf(i) !== Object.prototype) problems.push(`item keys ${keys(i)}`);
  const want = { top: "rule", one: "rule,personId", random: "rule,order" }[bill.spare.rule];
  if (keys(bill.spare) !== want || Object.getPrototypeOf(bill.spare) !== Object.prototype) problems.push(`spare keys ${keys(bill.spare)}`);
  return problems;
}

const rows = [];
for (const [name, text, expected] of cases) {
  const t0 = performance.now();
  let out, threw = null;
  try { out = decodeDraft(text); } catch (error) { threw = String(error); }
  const ms = Math.round(performance.now() - t0);
  const got = threw ? "THREW" : out.ok ? "A" : "R";
  const row = { name, chars: text.length, expected, got, ms, pass: expected === "?" ? got !== "THREW" : got === expected };
  if (out?.ok) {
    row.shape = shapeProblems(out.bill);
    row.spare = Object.keys(out.bill.spare).join(",");
    if (row.shape.length) row.pass = false;
    try {
      const t1 = performance.now();
      const result = computeResult(out.bill);
      row.result = result.kind;
      if (result.kind === "even" || result.kind === "item") {
        const summary = summaryText(result);
        row.summaryLines = summary.split(LINE_RE).length;
        row.summaryHasControl = CONTROL_RE.test(summary.split(LF).join(""));
        row.summaryChars = summary.length;
        if (row.summaryLines !== 3 + result.rows.length || row.summaryHasControl) row.pass = false;
      }
      const again = decodeDraft(encodeDraft(out.bill));
      row.roundTrip = again.ok;
      if (!again.ok) row.pass = false;
      let draws = 0;
      const rnd = () => { draws += 1; return 0.5; };
      chooseSpareRule(out.bill, "random", rnd); pickAgain(out.bill, rnd); chooseSparePerson(out.bill, "p2");
      row.coreDraws = draws;
      row.coreMs = Math.round(performance.now() - t1);
    } catch (error) { row.coreThrew = String(error); row.pass = false; }
  }
  rows.push(row);
}

const pollution = {
  objectProtoUnchanged: Object.getOwnPropertyNames(Object.prototype).join(",") === protoKeysBefore,
  arrayProtoUnchanged: Object.getOwnPropertyNames(Array.prototype).join(",") === arrayKeysBefore,
  polluted: ({}).polluted ?? null, adminOnPlainObject: ({}).admin ?? null,
};
const summary = { node: process.version, cases: rows.length, pass: rows.filter((r) => r.pass).length,
  fail: rows.filter((r) => !r.pass).map((r) => r.name), pollution };
writeFileSync("n1_decoder-results.json", JSON.stringify({ summary, rows }, null, 1));
console.log(JSON.stringify(summary, null, 1));
for (const r of rows) console.log(`${r.pass ? "ok  " : "FAIL"} ${r.got} (want ${r.expected}) ${String(r.ms).padStart(6)} ms ${r.chars} chars  ${r.name}${r.spare ? "  spare keys " + r.spare : ""}${r.coreMs !== undefined ? "  core " + r.coreMs + " ms" : ""}`);
